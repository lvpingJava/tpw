# builder.py - TPW 增量更新清单构建工具 (v2.0)
# 参考 GameUpdateSystemProject/tools_builder.py，扫描目录生成 manifest.json
# v2.0 新增: SHA-256 双重哈希、changelog 字段、清单自校验

import os
import json
import hashlib
import fnmatch
from datetime import datetime


class ManifestBuilder:
    """清单构建器：扫描源目录，生成包含版本号和文件哈希的 manifest.json"""

    def __init__(self, source_root=None):
        if source_root is None:
            source_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.source_root = source_root

    @staticmethod
    def _calculate_file_hash(filepath):
        """计算文件 MD5 和 SHA-256 哈希"""
        md5_hasher = hashlib.md5()
        sha256_hasher = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    md5_hasher.update(chunk)
                    sha256_hasher.update(chunk)
            return {
                "md5": md5_hasher.hexdigest(),
                "sha256": sha256_hasher.hexdigest(),
            }
        except (IOError, PermissionError) as e:
            print(f"  [警告] 无法读取 {filepath}: {e}")
            return None

    def _iter_source_files(self, include_dirs, include_globs, exclude_patterns):
        """遍历源目录中需要发布的文件"""
        for dir_name in include_dirs:
            dir_path = os.path.join(self.source_root, dir_name)
            if not os.path.isdir(dir_path):
                continue

            for root, dirs, files in os.walk(dir_path):
                dirs[:] = [d for d in dirs if not any(
                    fnmatch.fnmatch(d, pat) for pat in exclude_patterns
                )]

                for filename in files:
                    if any(fnmatch.fnmatch(filename, pat) for pat in exclude_patterns):
                        continue

                    matched = False
                    for glob_pat in include_globs:
                        if fnmatch.fnmatch(filename, glob_pat):
                            matched = True
                            break
                    if not matched:
                        continue

                    full_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(full_path, self.source_root).replace("\\", "/")
                    yield rel_path, full_path

    def build(self, version, include_dirs=None, include_globs=None,
              exclude_patterns=None, output_path=None, changelog="",
              root_scripts=None, root_binaries=None):
        """构建 manifest.json (v2.1 格式)

        v2.0 文件条目格式: {"md5": "...", "sha256": "..."}
        旧格式兼容: "md5hash" (纯字符串) —— updater.py 同时支持两种格式
        """
        if include_dirs is None:
            include_dirs = [
                "配置", "手牌", "场景", "快速手牌", "暗月",
                "models", "flaskr", "ui", "matplotlibes", "wxauto",
                "other", "certifi",
            ]
        if include_globs is None:
            include_globs = ["*.py", "*.txt", "*.dll", "*.exe", "*.bmp",
                             "*.png", "*.gif", "*.tif", "*.jpg", "*.jpeg",
                             "*.json", "*.sql", "*.pem", "*.ui"]
        if exclude_patterns is None:
            exclude_patterns = [
                "__pycache__", "*.pyc", "*.log", "*.zip",
                "临时*", ".git*", ".idea*", "*.md",
                "test*.py", "test*.txt",
            ]

        manifest = {
            "version": version,
            "build_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "changelog": changelog,
            "files": {}
        }

        print(f"构建清单: 版本 {version}")
        print(f"源目录: {self.source_root}")
        print(f"扫描目录: {include_dirs}")

        total = 0
        skipped = 0

        for rel_path, full_path in self._iter_source_files(
                include_dirs, include_globs, exclude_patterns):
            if os.path.basename(rel_path) == "manifest.json":
                skipped += 1
                continue

            file_hashes = self._calculate_file_hash(full_path)
            if file_hashes is None:
                skipped += 1
                continue

            # v2.0: 存储 MD5 + SHA-256
            manifest["files"][rel_path] = file_hashes
            print(f"  [{file_hashes['md5'][:8]}] {rel_path}")
            total += 1

        # 根目录关键脚本（优先使用传入参数，其次配置文件，最后硬编码默认值）
        if root_scripts is None:
            root_scripts = [
                "tpw_server.py", "webServer.py", "DmTool.py", "DmTest.py",
                "fightThread.py", "game.py", "myutils.py", "log.py",
                "loginCheck.py", "Plugin.py", "pyLog.py", "WxAuToTool.py",
                "baiduOcr.py", "circleHandle.py", "FindColor.py",
                "ftpUplaod.py", "killPid.py", "picture.py",
                "pyImgMain.py", "pyOcrMain.py", "YOLO.py",
            ]
        for script_name in root_scripts:
            script_path = os.path.join(self.source_root, script_name)
            if os.path.isfile(script_path) and script_name not in manifest["files"]:
                file_hashes = self._calculate_file_hash(script_path)
                if file_hashes:
                    manifest["files"][script_name] = file_hashes
                    print(f"  [{file_hashes['md5'][:8]}] {script_name}")
                    total += 1

        # 根目录关键二进制文件（exe/dll，默认不包含 — 大文件不适合 CDN 增量更新）
        if root_binaries is None:
            root_binaries = []  # 默认空，避免 CDN 超时
        for bin_name in root_binaries:
            bin_path = os.path.join(self.source_root, bin_name)
            if os.path.isfile(bin_path) and bin_name not in manifest["files"]:
                file_hashes = self._calculate_file_hash(bin_path)
                if file_hashes:
                    manifest["files"][bin_name] = file_hashes
                    print(f"  [{file_hashes['md5'][:8]}] {bin_name} (二进制)")
                    total += 1

        if output_path is None:
            output_path = os.path.join(self.source_root, "manifest.json")

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=4, ensure_ascii=False)
            f.write('\n')

        print(f"\n清单已生成: {output_path}")
        print(f"文件总数: {total} (跳过 {skipped})")
        self._verify_manifest(output_path)
        return manifest

    @staticmethod
    def _verify_manifest(manifest_path):
        """v2.0: 清单文件自校验 — 验证 JSON 可读且格式正确"""
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            version = data.get('version', '?')
            file_count = len(data.get('files', {}))
            print(f"自校验通过: 版本 {version}, {file_count} 个文件")
        except (json.JSONDecodeError, IOError) as e:
            print(f"[自校验失败] {manifest_path}: {e}")


def build_from_config(config_path=None):
    """从配置文件读取参数并构建清单"""
    if config_path is None:
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "update_config.json"
        )

    if not os.path.exists(config_path):
        print(f"错误: 配置文件不存在 {config_path}")
        return None

    with open(config_path, 'r', encoding='utf-8-sig') as f:
        config = json.load(f)

    builder = ManifestBuilder()
    return builder.build(
        version=config.get("version", "0.0.0"),
        include_dirs=config.get("include_dirs"),
        include_globs=config.get("include_globs"),
        exclude_patterns=config.get("exclude_patterns"),
        changelog=config.get("changelog", ""),
        root_scripts=config.get("root_scripts"),
        root_binaries=config.get("root_binaries"),
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="TPW 增量更新清单构建工具 (v2.0)")
    parser.add_argument("--version", "-v", required=True, help="版本号，如 6.5.0.0")
    parser.add_argument("--source", "-s", help="项目根目录（默认为上级目录）")
    parser.add_argument("--output", "-o", help="manifest.json 输出路径")
    parser.add_argument("--config", "-c", help="从配置文件读取参数")
    parser.add_argument("--changelog", help="更新日志内容")

    args = parser.parse_args()

    if args.config:
        build_from_config(args.config)
    else:
        builder = ManifestBuilder(source_root=args.source)
        builder.build(
            version=args.version,
            output_path=args.output,
            changelog=args.changelog or "",
        )
