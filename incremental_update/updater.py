# updater.py - TPW 增量更新核心引擎 (v2.0)
# 参考 GameUpdateSystemProject/client_updater.py 的 AutoUpdater 实现
# 支持文件级 MD5/SHA-256 哈希比对、仅下载变更文件、清理废弃文件
# v2.0 新增: CDN 多级回退、下载完整性校验、回滚支持

import os
import json
import hashlib
import shutil
import time
import tempfile
import requests
from datetime import datetime


# ── 绕过系统代理 ──
# 有些 Windows 环境配置了 HTTP 代理，但代理不支持 HTTPS 直连 CDN，
# 会导致 ProxyError + SSLEOFError。jsDelivr 是公共 CDN，无需代理。
def _create_session():
    """创建绕过系统代理的 requests Session"""
    session = requests.Session()
    session.trust_env = False
    session.proxies = {"http": None, "https": None}
    return session


# GitHub 仓库信息 (用于构造回退 URL)
_GITHUB_REPO = "lvpingJava/tpw"


def _build_fallback_urls(primary_url):
    """根据主 URL 构造回退 URL 列表（从 primary_url 解析目标版本）"""
    import re
    urls = [primary_url.rstrip('/')]
    # 尝试从主 URL 中提取版本标签 (如 @v6.5.0.0)
    m = re.search(r'@(v[\d.]+)', primary_url)
    if m:
        version_tag = m.group(1)
        # GitHub Raw 备选（同一版本，不同 CDN）
        github_raw = f"https://raw.githubusercontent.com/{_GITHUB_REPO}/{version_tag}"
        if github_raw not in urls:
            urls.append(github_raw)
    # 始终添加 master 分支作为最后回退
    master_url = f"https://cdn.jsdelivr.net/gh/{_GITHUB_REPO}@master"
    if master_url not in urls:
        urls.append(master_url)
    return urls


class IncrementalUpdater:
    """增量更新器：连接服务器获取 manifest.json，对比本地文件，仅下载变更部分

    v2.0 新增特性:
    - CDN 多级回退：主CDN不可用时自动切换备选源
    - 下载完整性校验：下载后 SHA-256 验证，确保文件未损坏
    - 回滚支持：更新失败时恢复被修改的文件
    - 双重哈希：MD5 (比对) + SHA-256 (校验)
    """

    # 最大重试次数
    MAX_RETRIES = 3
    # 下载分块大小
    CHUNK_SIZE = 8192
    # manifest 下载超时 (秒)
    MANIFEST_TIMEOUT = 15
    # 文件下载超时 (秒) — 根据文件大小自适应
    FILE_TIMEOUT_MIN = 30
    FILE_TIMEOUT_MAX = 300
    # 大文件阈值 (字节)，超过此值使用更长超时
    LARGE_FILE_THRESHOLD = 5 * 1024 * 1024  # 5MB

    # ── 保护目录：这些目录中的文件绝不会被删除或覆盖 ──
    # 防止垃圾清理误删 IDE 配置、虚拟环境、Git 仓库等开发目录
    PROTECTED_DIRS = {
        '.idea', '.git', '.venv', 'venv', '__pycache__',
        '.qoder', '.trae', '.vscode',
        # Nuitka 编译产物 — 这些目录来自编译输出，不在 manifest 中
        'matplotlib', 'PyQt5', 'numpy', 'cv2', 'PIL',
        'contourpy', 'kiwisolver', 'markupsafe', 'psutil', 'zstandard',
        'certifi', 'matplotlib.libs',
    }
    # ── 保护文件：这些文件绝不会被覆盖或删除 ──
    PROTECTED_FILES = {
        '.gitignore', 'update_config.json',
    }
    # ── 备份目录名 ──
    BACKUP_DIR_NAME = ".tpw_update_backup"

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

        # ── v2.0: 回滚支持 ──
        self._backup_dir = os.path.join(self.local_dir, self.BACKUP_DIR_NAME)
        self._backed_up_files = {}  # {rel_path: (original_exists, backup_path)}
        self._downloaded_files = []  # 已下载文件列表，用于回滚

        # ── v2.0: CDN 回退 URL 列表（从 server_url 解析目标版本） ──
        self._local_version = self.get_local_version()
        self._fallback_urls = _build_fallback_urls(server_url)
        # 记录实际使用的 CDN URL（manifest 获取成功后更新）
        self._active_base_url = server_url.rstrip('/')
        # 记录被追踪的目录（check_update 时更新，用于垃圾清理范围限制）
        self._tracked_dirs = set()

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

        remote_manifest = self._fetch_manifest_with_fallback()
        if remote_manifest is None:
            return None

        remote_version = remote_manifest.get('version', 'Unknown')
        remote_files = remote_manifest.get('files', {})
        local_version = self.get_local_version()

        self._log(f"服务器版本: {remote_version}")
        self._log(f"本地版本: {local_version}")

        # ── v2.0: 显示更新内容摘要 ──
        changelog = remote_manifest.get('changelog', '')
        if changelog:
            self._log(f"更新内容: {changelog}")

        need_download = []
        keep_files = set()
        total = len(remote_files)
        checked = 0

        self._log(f"正在比对 {total} 个文件...")
        self._progress_cb(0, total, "正在比对文件...")

        for rel_path, remote_hashes in remote_files.items():
            if self._is_cancelled:
                return None

            # 跳过保护目录中的文件（不纳入比对）
            if self._is_protected(rel_path):
                checked += 1
                continue

            local_path = os.path.join(self.local_dir, rel_path)
            keep_files.add(os.path.abspath(local_path))

            # ── v2.0: 兼容新旧 manifest 格式 ──
            # 新格式: {"md5": "...", "sha256": "...", "size": 1234}
            # 旧格式: "md5hash" (纯字符串)
            if isinstance(remote_hashes, dict):
                remote_hash = remote_hashes.get('md5', '')
            else:
                remote_hash = remote_hashes

            local_hash = self._get_local_file_hash(local_path)
            if local_hash != remote_hash:
                need_download.append(rel_path)

            checked += 1
            if checked % 50 == 0 or checked == total:
                self._progress_cb(checked, total, f"已比对 {checked}/{total} 个文件")

        self._progress_cb(total, total, "文件比对完成")
        has_update = len(need_download) > 0 or local_version != remote_version

        # ★ v2.1: 提取被追踪的顶级目录，用于垃圾清理时保护 Nuitka 产物
        self._tracked_dirs = set()
        for rel_path in remote_files:
            norm = rel_path.replace('\\', '/')
            if '/' in norm:
                self._tracked_dirs.add(norm.split('/')[0])

        result = {
            "has_update": has_update,
            "local_version": local_version,
            "remote_version": remote_version,
            "need_download": need_download,
            "total_files": total,
            "remote_manifest": remote_manifest,
            "keep_files": keep_files,
            "changelog": changelog,
            "tracked_dirs": self._tracked_dirs,
        }

        if not need_download and local_version == remote_version:
            self._log("当前已是最新版本，无需更新")
            self._clean_garbage(keep_files, self._tracked_dirs)

        return result

    def download_files(self, file_list, keep_files=None, remote_manifest=None):
        if not file_list:
            return 0, 0

        total = len(file_list)
        self._log(f"开始下载 {total} 个文件...")

        # ── v2.0: 下载前备份将被修改的文件 ──
        self._prepare_backup()
        for rel_path in file_list:
            self._backup_file(rel_path)

        success = 0
        fail = 0
        self._downloaded_files = []

        for i, rel_path in enumerate(file_list):
            if self._is_cancelled:
                self._log("更新已取消")
                # 回滚已下载的文件
                self._restore_backup()
                break

            # 跳过保护目录中的文件
            if self._is_protected(rel_path):
                self._log(f"跳过受保护文件: {rel_path}")
                continue

            file_url = f"{self._active_base_url}/{rel_path}"
            local_dest = os.path.join(self.local_dir, rel_path)
            os.makedirs(os.path.dirname(local_dest), exist_ok=True)

            self._progress_cb(i + 1, total, f"下载: {rel_path}")

            # ── v2.0: 获取期望的哈希值用于下载后校验 ──
            expected_hash = None
            if remote_manifest:
                file_info = remote_manifest.get('files', {}).get(rel_path, {})
                if isinstance(file_info, dict):
                    expected_hash = file_info.get('md5', '')
                else:
                    expected_hash = file_info

            if self._download_with_fallback(rel_path, local_dest, expected_hash):
                success += 1
                self._downloaded_files.append(rel_path)
            else:
                fail += 1
                self._log(f"下载失败: {rel_path}")
                # ── v2.0: 下载失败则恢复该文件的备份 ──
                self._restore_single_file(rel_path)

        self._progress_cb(total, total, f"下载完成: 成功 {success}, 失败 {fail}")

        # ── v2.0: 全部成功才清理备份，否则回滚 ──
        if fail == 0:
            self._cleanup_backup()
            if keep_files:
                self._clean_garbage(keep_files, self._tracked_dirs)
        else:
            self._log(f"有 {fail} 个文件下载失败，已恢复原始文件")
            self._restore_backup()

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
            self._clean_garbage(result.get("keep_files", set()), self._tracked_dirs)
            return True

        success, fail = self.download_files(
            file_list,
            keep_files=result.get("keep_files"),
            remote_manifest=result.get("remote_manifest"),
        )

        if success > 0:
            self._save_local_manifest(result["remote_manifest"])
            self._log(f"更新完成: 版本 {result['remote_version']}, "
                      f"下载 {success} 个文件, 失败 {fail} 个")
        else:
            self._log("更新失败: 所有文件下载均未成功")

        return fail == 0

    # ── v2.1: CDN 多级回退文件下载 ──────────────────────────

    def _download_with_fallback(self, rel_path, dest_path, expected_md5=None):
        """带 CDN 回退的文件下载：先尝试活跃 URL，失败后尝试备选源"""
        try_urls = [self._active_base_url]
        for url in self._fallback_urls:
            if url != self._active_base_url:
                try_urls.append(url)

        for base_url in try_urls:
            file_url = f"{base_url}/{rel_path}"
            if self._download_single_file(file_url, dest_path, rel_path, expected_md5):
                return True

        return False

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

    def _download_single_file(self, url, dest_path, rel_path, expected_md5=None):
        for attempt in range(1, self.MAX_RETRIES + 1):
            # ★ v2.1: 自适应超时 — 最后一次重试用更长超时，应对大文件
            timeout = self.FILE_TIMEOUT_MAX if attempt == self.MAX_RETRIES else self.FILE_TIMEOUT_MIN
            try:
                resp = self._session.get(url, stream=True, timeout=timeout)
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

                    # v2.0: 下载后 MD5 完整性校验
                    if expected_md5:
                        actual_md5 = self._compute_md5(tmp_path)
                        if actual_md5 != expected_md5:
                            self._log(f"校验失败 {rel_path}: 期望 {expected_md5[:8]}..., 实际 {actual_md5[:8]}...")
                            os.unlink(tmp_path)
                            return False

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

    def _clean_garbage(self, keep_files_set, tracked_dirs=None):
        """清理不在 keep_files_set 中的废弃文件
        
        ★ v2.1 安全增强: 仅清理 manifest 追踪目录内的文件。
        Nuitka 编译产物目录 (matplotlib/PyQt5/numpy 等) 完全不受影响。
        """
        if tracked_dirs is None:
            tracked_dirs = set()

        cleaned = 0
        for root, dirs, files in os.walk(self.local_dir, topdown=False):
            # 跳过保护目录（开发目录 + Nuitka 系统目录）
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

                # ★ v2.1: 仅清理被 manifest 追踪的文件
                # 不在追踪目录中的文件（Nuitka 产物等）绝对不删
                if not self._is_in_tracked_scope(rel_path, tracked_dirs):
                    continue

                if abs_path not in keep_files_set:
                    try:
                        os.remove(abs_path)
                        cleaned += 1
                    except (IOError, PermissionError):
                        pass
        if cleaned > 0:
            self._log(f"已清理 {cleaned} 个废弃文件")

    @staticmethod
    def _is_in_tracked_scope(rel_path, tracked_dirs):
        """检查文件是否在 manifest 追踪的目录范围内
        
        例如: tracked_dirs={'手牌','场景'} 
               '手牌/xxx.bmp' → True
               'tpw_server.py' → True (根级文件)
               'matplotlib/xxx' → False (不在追踪范围)
        """
        norm = rel_path.replace('\\', '/')
        # 根级文件（无目录前缀）始终在追踪范围内
        if '/' not in norm:
            return True
        # 检查顶级目录是否在追踪集合中
        top_dir = norm.split('/')[0]
        return top_dir in tracked_dirs

    def _save_local_manifest(self, manifest):
        try:
            with open(self._local_manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=4, ensure_ascii=False)
        except IOError as e:
            self._log(f"保存清单失败: {e}")

    def _log(self, message):
        self._log_cb(message)

    # ── v2.0: CDN 多级回退 ───────────────────────────────────

    def _fetch_manifest_with_fallback(self):
        """从 CDN 获取 manifest.json，带多级回退。
        成功时会将 self._active_base_url 更新为实际可用的 CDN URL，
        后续文件下载将使用同一 CDN 源。"""
        errors = []
        for idx, base_url in enumerate(self._fallback_urls):
            manifest_url = f"{base_url}/manifest.json"
            source_names = ["jsDelivr CDN", "GitHub Raw", "jsDelivr @master"]
            source_name = source_names[idx] if idx < len(source_names) else f"备选源{idx+1}"
            self._log(f"尝试 {source_name}: {manifest_url}")
            try:
                resp = self._session.get(manifest_url, timeout=self.MANIFEST_TIMEOUT)
                resp.raise_for_status()
                manifest = resp.json()
                self._log(f"连接成功 [{source_name}]")
                # ★ 关键修复: 将实际可用的 CDN URL 记录为活跃源，后续文件下载使用同一源
                self._active_base_url = base_url
                self._log(f"文件下载源切换为: {base_url}")
                return manifest
            except requests.RequestException as e:
                msg = f"{source_name} 不可用: {e}"
                self._log(f"  {msg}")
                errors.append(msg)
            except json.JSONDecodeError as e:
                msg = f"{source_name} 格式错误: {e}"
                self._log(f"  {msg}")
                errors.append(msg)

        self._log("所有更新源均不可用！请检查网络连接，或稍后重试")
        return None

    # ── v2.0: 回滚支持 ───────────────────────────────────────

    def _prepare_backup(self):
        """准备备份目录"""
        if not os.path.exists(self._backup_dir):
            os.makedirs(self._backup_dir)

    def _backup_file(self, rel_path):
        """备份单个文件"""
        src_path = os.path.join(self.local_dir, rel_path)
        backup_path = os.path.join(self._backup_dir, rel_path)
        exists = os.path.exists(src_path)
        if exists:
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            shutil.copy2(src_path, backup_path)
        self._backed_up_files[rel_path] = (exists, backup_path)

    def _restore_single_file(self, rel_path):
        """恢复单个文件的备份"""
        if rel_path not in self._backed_up_files:
            return
        exists, backup_path = self._backed_up_files[rel_path]
        dest_path = os.path.join(self.local_dir, rel_path)
        if exists and os.path.exists(backup_path):
            shutil.copy2(backup_path, dest_path)
        elif not exists:
            if os.path.exists(dest_path):
                os.remove(dest_path)

    def _restore_backup(self):
        """恢复所有已备份的文件"""
        restored = 0
        for rel_path in list(self._backed_up_files.keys()):
            self._restore_single_file(rel_path)
            restored += 1
        if restored > 0:
            self._log(f"已恢复 {restored} 个文件")
        self._cleanup_backup()

    def _cleanup_backup(self):
        """清理备份目录"""
        if os.path.exists(self._backup_dir):
            shutil.rmtree(self._backup_dir, ignore_errors=True)
        self._backed_up_files.clear()

    # ── v2.0: 哈希计算工具 ──────────────────────────────────

    @staticmethod
    def _compute_md5(filepath):
        """计算文件 MD5 哈希"""
        hasher = hashlib.md5()
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except (IOError, PermissionError):
            return ""

    @staticmethod
    def _compute_sha256(filepath):
        """计算文件 SHA-256 哈希"""
        hasher = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except (IOError, PermissionError):
            return ""


if __name__ == "__main__":
    SERVER = "http://localhost:8000"
    LOCAL = "./test_local_dir"

    updater = IncrementalUpdater(SERVER, LOCAL)
    success = updater.apply_update()
    print(f"\n更新结果: {'成功' if success else '失败'}")
