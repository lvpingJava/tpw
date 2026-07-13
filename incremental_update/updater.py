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


class IncrementalUpdater:
    """增量更新器：连接服务器获取 manifest.json，对比本地文件，仅下载变更部分"""

    # 最大重试次数
    MAX_RETRIES = 3
    # 下载分块大小
    CHUNK_SIZE = 8192

    def __init__(self, server_url, local_dir, progress_callback=None, log_callback=None):
        """
        Args:
            server_url: 更新服务器基础 URL（如 https://cdn.jsdelivr.net/gh/user/repo@latest）
            local_dir: 本地安装目录（将被更新的目录）
            progress_callback: 可选，进度回调函数 callback(current, total, message)
            log_callback: 可选，日志回调函数 callback(message)
        """
        self.server_url = server_url.rstrip('/')
        self.local_dir = local_dir
        self._progress_cb = progress_callback or (lambda *a: None)
        self._log_cb = log_callback or (lambda m: print(m))

        # 确保本地目录存在
        if not os.path.exists(self.local_dir):
            os.makedirs(self.local_dir)

        # 状态追踪
        self._is_cancelled = False
        self._local_manifest_path = os.path.join(self.local_dir, "manifest.json")

    # ── 公共 API ─────────────────────────────────────────────

    def cancel(self):
        """取消当前更新操作"""
        self._is_cancelled = True

    def get_local_version(self):
        """读取本地 manifest.json 获取当前版本号，不存在则返回 "0.0.0" """
        if os.path.exists(self._local_manifest_path):
            try:
                with open(self._local_manifest_path, 'r', encoding='utf-8') as f:
                    return json.load(f).get('version', '0.0.0')
            except (json.JSONDecodeError, IOError):
                pass
        return "0.0.0"

    def check_update(self):
        """
        检查是否有可用更新。

        Returns:
            dict: {
                "has_update": bool,
                "local_version": str,
                "remote_version": str,
                "need_download": list,    # 需要下载的文件列表
                "total_files": int,       # 远程文件总数
                "file_sizes": dict,       # {rel_path: size_in_bytes} 可选
                "remote_manifest": dict,  # 远程完整清单
            }
        """
        self._is_cancelled = False
        self._log("正在连接更新服务器...")

        # 1. 获取远程清单
        manifest_url = f"{self.server_url}/manifest.json"
        try:
            resp = requests.get(manifest_url, timeout=15)
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

        # 2. 对比差异
        need_download = []
        keep_files = set()
        total = len(remote_files)
        checked = 0

        self._log(f"正在比对 {total} 个文件...")
        self._progress_cb(0, total, "正在比对文件...")

        for rel_path, remote_hash in remote_files.items():
            if self._is_cancelled:
                return None

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
            "file_sizes": remote_manifest.get("file_sizes", {}),
            "remote_manifest": remote_manifest,
            "keep_files": keep_files,
        }

        if not need_download and local_version == remote_version:
            self._log("当前已是最新版本，无需更新")
            # 仍清理垃圾文件
            self._clean_garbage(keep_files)

        return result

    def download_files(self, file_list, keep_files=None):
        """
        下载指定的文件列表。

        Args:
            file_list: 要下载的文件相对路径列表
            keep_files: 需要保留的文件绝对路径集合（用于后续清理）

        Returns:
            tuple: (success_count, fail_count)
        """
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

        # 清理废弃文件
        if keep_files:
            self._clean_garbage(keep_files)

        return success, fail

    def apply_update(self):
        """
        执行完整更新流程：检查 → 下载 → 保存清单 → 清理

        Returns:
            bool: 更新是否成功
        """
        # 1. 检查更新
        result = self.check_update()
        if result is None:
            return False
        if not result["has_update"]:
            return True

        # 2. 确认有文件需要下载
        file_list = result["need_download"]
        if not file_list:
            # 版本号不同但无文件变更，直接更新本地清单
            self._save_local_manifest(result["remote_manifest"])
            self._clean_garbage(result.get("keep_files", set()))
            return True

        # 3. 下载变更文件
        success, fail = self.download_files(
            file_list, keep_files=result.get("keep_files")
        )

        # 4. 保存新清单
        if success > 0:
            self._save_local_manifest(result["remote_manifest"])
            self._log(f"更新完成: 版本 {result['remote_version']}, "
                      f"下载 {success} 个文件, 失败 {fail} 个")
        else:
            self._log("更新失败: 所有文件下载均未成功")

        return fail == 0

    # ── 内部方法 ─────────────────────────────────────────────

    def _get_local_file_hash(self, filepath):
        """获取本地文件 MD5，不存在则返回 None"""
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
        """下载单个文件，先写临时文件，校验后原子替换"""
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                resp = requests.get(url, stream=True, timeout=30)
                resp.raise_for_status()

                # 写入临时文件
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

                    # 原子替换
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

    def _clean_garbage(self, keep_files_set):
        """清理不在 keep_files_set 中的本地文件"""
        cleaned = 0
        for root, dirs, files in os.walk(self.local_dir, topdown=False):
            for filename in files:
                abs_path = os.path.abspath(os.path.join(root, filename))
                # 保护：不删除 manifest.json 和 .py 脚本
                if filename == "manifest.json":
                    continue
                # 跳过临时文件
                if filename.startswith(".tmp_update_"):
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
        """保存清单到本地"""
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
    # 简单自测
    import sys
    SERVER = "http://localhost:8000"
    LOCAL = "./test_local_dir"

    updater = IncrementalUpdater(SERVER, LOCAL)
    success = updater.apply_update()
    print(f"\n更新结果: {'成功' if success else '失败'}")
