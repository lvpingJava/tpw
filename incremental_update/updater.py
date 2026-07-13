# updater.py - TPW 增量更新核心引擎
# 参考 GameUpdateSystemProject/client_updater.py 的 AutoUpdater 实现
# 支持文件级 MD5 哈希比对、仅下载变更文件、清理废弃文件

import os
import json
import hashlib
import shutil
import time
import tempfile
import requests


# ── 绕过系统代理 ──
# 有些 Windows 环境配置了 HTTP 代理，但代理不支持 HTTPS 直连 CDN，
# 会导致 ProxyError + SSLEOFError。jsDelivr 是公共 CDN，无需代理。
def _create_session():
    """创建绕过系统代理的 requests Session"""
    session = requests.Session()
    session.trust_env = False
    session.proxies = {"http": None, "https": None}
    return session


class IncrementalUpdater:
    """增量更新器：连接服务器获取 manifest.json，对比本地文件，仅下载变更部分"""

    # 最大重试次数
    MAX_RETRIES = 3
    # 下载分块大小
    CHUNK_SIZE = 8192

    # ── 保护目录：这些目录中的文件绝不会被删除或覆盖 ──
    # 防止垃圾清理误删 IDE 配置、虚拟环境、Git 仓库等开发目录
    PROTECTED_DIRS = {
        '.idea', '.git', '.venv', 'venv', '__pycache__',
        '.qoder', '.trae', '.vscode',
    }
    # ── 保护文件：这些文件绝不会被覆盖或删除 ──
    PROTECTED_FILES = {
        '.gitignore', 'update_config.json',
    }

    def __init__(self, server_url, local_dir, progress_callback=None, log_callback=None):
        """
        Args:
            server_url: 更新服务器基础 URL
            local_dir: 本地安装目录（将被更新的目录）
            progress_callback: 可选，进度回调 callback(current, total, message)
            log_callback: 可选，日志回调 callback(message)
        """
        self.server_url = server_url.rstrip('/')
        self.local_dir = local_dir
        self._progress_cb = progress_callback or (lambda *a: None)
        self._log_cb = log_callback or (lambda m: print(m))

        if not os.path.exists(self.local_dir):
            os.makedirs(self.local_dir)

        # 创建绕过系统代理的 HTTP Session
        self._session = _create_session()

        self._is_cancelled = False
        self._local_manifest_path = os.path.join(self.local_dir, "manifest.json")

    # ── 公共 API ─────────────────────────────────────────────

    def cancel(self):
        self._is_cancelled = True

    def get_local_version(self):
        if os.path.exists(self._local_manifest_path):
            try:
                with open(self._local_manifest_path, 'r', encoding='utf-8') as f:
                    return json.load(f).get('version', '0.0.0')
            except (json.JSONDecodeError, IOError):
                pass
        return "0.0.0"

    def check_update(self):
        self._is_cancelled = False
        self._log("正在连接更新服务器...")

        manifest_url = f"{self.server_url}/manifest.json"
        try:
            resp = self._session.get(manifest_url, timeout=15)
            resp.raise_for_status()
            remote_manifest = resp.json()
        except requests.RequestException as e:
            self._log(f"无法连接更新服务器: {e}")
            return None
        except json.JSONDecodeError as e:
            self._log(f"manifest.json 格式错误: {e}")
            return None

        remote_version = remote_manifest.get('version', 'Unknown')
        remote_files = remote_manifest.get('files', {})
        local_version = self.get_local_version()

        self._log(f"服务器版本: {remote_version}")
        self._log(f"本地版本: {local_version}")

        need_download = []
        keep_files = set()
        total = len(remote_files)
        checked = 0

        self._log(f"正在比对 {total} 个文件...")
        self._progress_cb(0, total, "正在比对文件...")

        for rel_path, remote_hash in remote_files.items():
            if self._is_cancelled:
                return None

            # 跳过保护目录中的文件（不纳入比对）
            if self._is_protected(rel_path):
                checked += 1
                continue

            local_path = os.path.join(self.local_dir, rel_path)
            keep_files.add(os.path.abspath(local_path))

            local_hash = self._get_local_file_hash(local_path)
            if local_hash != remote_hash:
                need_download.append(rel_path)

            checked += 1
            if checked % 50 == 0 or checked == total:
                self._progress_cb(checked, total, f"已比对 {checked}/{total} 个文件")

        self._progress_cb(total, total, "文件比对完成")
        has_update = len(need_download) > 0 or local_version != remote_version

        result = {
            "has_update": has_update,
            "local_version": local_version,
            "remote_version": remote_version,
            "need_download": need_download,
            "total_files": total,
            "remote_manifest": remote_manifest,
            "keep_files": keep_files,
        }

        if not need_download and local_version == remote_version:
            self._log("当前已是最新版本，无需更新")
            self._clean_garbage(keep_files)

        return result

    def download_files(self, file_list, keep_files=None):
        if not file_list:
            return 0, 0

        total = len(file_list)
        self._log(f"开始下载 {total} 个文件...")
        success = 0
        fail = 0

        for i, rel_path in enumerate(file_list):
            if self._is_cancelled:
                self._log("更新已取消")
                break

            # 跳过保护目录中的文件
            if self._is_protected(rel_path):
                self._log(f"跳过受保护文件: {rel_path}")
                continue

            file_url = f"{self.server_url}/{rel_path}"
            local_dest = os.path.join(self.local_dir, rel_path)
            os.makedirs(os.path.dirname(local_dest), exist_ok=True)

            self._progress_cb(i + 1, total, f"下载: {rel_path}")

            if self._download_single_file(file_url, local_dest, rel_path):
                success += 1
            else:
                fail += 1
                self._log(f"下载失败: {rel_path}")

        self._progress_cb(total, total, f"下载完成: 成功 {success}, 失败 {fail}")

        if keep_files:
            self._clean_garbage(keep_files)

        return success, fail

    def apply_update(self):
        result = self.check_update()
        if result is None:
            return False
        if not result["has_update"]:
            return True

        file_list = result["need_download"]
        if not file_list:
            self._save_local_manifest(result["remote_manifest"])
            self._clean_garbage(result.get("keep_files", set()))
            return True

        success, fail = self.download_files(
            file_list, keep_files=result.get("keep_files")
        )

        if success > 0:
            self._save_local_manifest(result["remote_manifest"])
            self._log(f"更新完成: 版本 {result['remote_version']}, "
                      f"下载 {success} 个文件, 失败 {fail} 个")
        else:
            self._log("更新失败: 所有文件下载均未成功")

        return fail == 0

    # ── 内部方法 ─────────────────────────────────────────────

    def _get_local_file_hash(self, filepath):
        if not os.path.exists(filepath):
            return None
        hasher = hashlib.md5()
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except (IOError, PermissionError):
            return None

    def _download_single_file(self, url, dest_path, rel_path):
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                resp = self._session.get(url, stream=True, timeout=30)
                resp.raise_for_status()

                tmp_fd, tmp_path = tempfile.mkstemp(
                    dir=os.path.dirname(dest_path) or self.local_dir,
                    prefix=".tmp_update_"
                )
                try:
                    with os.fdopen(tmp_fd, 'wb') as f:
                        for chunk in resp.iter_content(chunk_size=self.CHUNK_SIZE):
                            if self._is_cancelled:
                                os.unlink(tmp_path)
                                return False
                            f.write(chunk)

                    if os.path.exists(dest_path):
                        os.remove(dest_path)
                    shutil.move(tmp_path, dest_path)
                    return True

                except Exception:
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
                    raise

            except requests.RequestException as e:
                if attempt < self.MAX_RETRIES:
                    wait = attempt * 2
                    self._log(f"重试 ({attempt}/{self.MAX_RETRIES}) {rel_path}: {e}, "
                              f"等待 {wait}s")
                    time.sleep(wait)
                else:
                    self._log(f"下载失败 {rel_path}: {e}")
                    return False
            except (IOError, OSError) as e:
                self._log(f"写入失败 {rel_path}: {e}")
                return False

        return False

    def _is_protected(self, rel_path):
        """检查路径是否属于保护目录或保护文件"""
        norm = rel_path.replace('\\', '/')
        parts = norm.split('/')

        # 检查路径中任何一级目录是否为保护目录
        for part in parts[:-1]:
            if part in self.PROTECTED_DIRS:
                return True

        # 检查根级目录
        for d in self.PROTECTED_DIRS:
            if norm.startswith(d + '/') or norm.startswith(d + '\\'):
                return True

        # 检查保护文件名
        basename = os.path.basename(norm)
        if basename in self.PROTECTED_FILES:
            return True

        return False

    def _clean_garbage(self, keep_files_set):
        """清理不在 keep_files_set 中的本地文件（保护目录除外）"""
        cleaned = 0
        for root, dirs, files in os.walk(self.local_dir, topdown=False):
            # 跳过保护目录
            dirs[:] = [d for d in dirs if d not in self.PROTECTED_DIRS]

            for filename in files:
                abs_path = os.path.abspath(os.path.join(root, filename))
                rel_path = os.path.relpath(abs_path, self.local_dir)

                if filename == "manifest.json":
                    continue
                if filename.startswith(".tmp_update_"):
                    continue
                if self._is_protected(rel_path):
                    continue

                if abs_path not in keep_files_set:
                    try:
                        os.remove(abs_path)
                        cleaned += 1
                    except (IOError, PermissionError):
                        pass
        if cleaned > 0:
            self._log(f"已清理 {cleaned} 个废弃文件")

    def _save_local_manifest(self, manifest):
        try:
            with open(self._local_manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=4, ensure_ascii=False)
        except IOError as e:
            self._log(f"保存清单失败: {e}")

    def _log(self, message):
        self._log_cb(message)

    def _progress_cb(self, current, total, message):
        self._progress_cb(current, total, message)


if __name__ == "__main__":
    SERVER = "http://localhost:8000"
    LOCAL = "./test_local_dir"

    updater = IncrementalUpdater(SERVER, LOCAL)
    success = updater.apply_update()
    print(f"\n更新结果: {'成功' if success else '失败'}")
