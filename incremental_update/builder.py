# builder.py - TPW 增量更新清单构建工具
# 参考 GameUpdateSystemProject/tools_builder.py，扫描目录生成 manifest.json

import os
import json
import hashlib
import fnmatch
from datetime import datetime


class ManifestBuilder:
    """清单构建器：扫描源目录，生成包含版本号和文件MD5哈希的 manifest.json"""

    def __init__(self, source_root=None):
        """
        Args:
            source_root: 项目根目录（需发布的文件所在目录）。默认自动检测。
        """
        if source_root is None:
            source_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.source_root = source_root

    @staticmethod
    def _calculate_file_hash(filepath):
        """计算文件 MD5 哈希（分块读取，防止大文件撑爆内存）"""
        hasher = hashlib.md5()
        try:
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except (IOError, PermissionError) as e:
            print(f"  [警告] 无法读取 {filepath}: {e}")
            return None

    def _iter_source_files(self, include_dirs, include_globs, exclude_patterns):
        """遍历源目录中需要发布的文件，返回 (相对路径, 绝对路径) 生成器"""
        for dir_name in include_dirs:
            dir_path = os.path.join(self.source_root, dir_name)
            if not os.path.isdir(dir_path):
                continue

            for root, dirs, files in os.walk(dir_path):
                # 排除不需要的目录
                dirs[:] = [d for d in dirs if not any(
                    fnmatch.fnmatch(d, pat) for pat in exclude_patterns
                )]

                for filename in files:
                    # 排除匹配的文件
                    if any(fnmatch.fnmatch(filename, pat) for pat in exclude_patterns):
                        continue

                    # 检查是否匹配包含的 glob 模式
                    matched = False
                    for glob_pat in include_globs:
                        if fnmatch.fnmatch(filename, glob_pat):
                            matched = True
                            break
                    if not matched:
                        continue

                    full_path = os.path.join(root, filename)
                    # 相对路径统一使用正斜杠
                    rel_path = os.path.relpath(full_path, self.source_root).replace("\\", "/")
                    yield rel_path, full_path

    def build(self, version, include_dirs=None, include_globs=None,
              exclude_patterns=None, output_path=None):
        """
        构建 manifest.json

        Args:
            version: 版本号字符串，如 "6.4.9.8"
            include_dirs: 要扫描的目录列表（相对于 source_root）
            include_globs: 文件匹配模式列表，如 ["*.py", "*.txt", "*.dll"]
            exclude_patterns: 排除的 glob 模式列表
            output_path: manifest.json 输出路径，默认为 source_root 下

        Returns:
            dict: manifest 字典
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
                             "*.json", "*.sql", "*.pem", "*.spec", "*.ui"]
        if exclude_patterns is None:
            exclude_patterns = [
                "__pycache__", "*.pyc", "*.log", "*.zip",
                "临时*", ".git*", ".idea*", "*.md",
                "test*.py", "test*.txt",
            ]

        manifest = {
            "version": version,
            "build_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "files": {}
        }

        print(f"构建清单: 版本 {version}")
        print(f"源目录: {self.source_root}")
        print(f"扫描目录: {include_dirs}")

        total = 0
        skipped = 0

        for rel_path, full_path in self._iter_source_files(
                include_dirs, include_globs, exclude_patterns):
            # 跳过 manifest.json 自身
            if os.path.basename(rel_path) == "manifest.json":
                skipped += 1
                continue

            file_hash = self._calculate_file_hash(full_path)
            if file_hash is None:
                skipped += 1
                continue

            manifest["files"][rel_path] = file_hash
            print(f"  [{file_hash[:8]}] {rel_path}")
            total += 1

        # 也包含根目录下的关键脚本
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
                file_hash = self._calculate_file_hash(script_path)
                if file_hash:
                    manifest["files"][script_name] = file_hash
                    print(f"  [{file_hash[:8]}] {script_name}")
                    total += 1

        # 输出
        if output_path is None:
            output_path = os.path.join(self.source_root, "manifest.json")

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=4, ensure_ascii=False)

        print(f"\n清单已生成: {output_path}")
        print(f"文件总数: {total} (跳过 {skipped})")
        return manifest


def build_from_config(config_path=None):
    """从配置文件读取参数并构建清单"""
    if config_path is None:
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "update_config.json"
        )

    if not os.path.exists(config_path):
        print(f"错误: 配置文件不存在 {config_path}")
        print("请先创建 update_config.json，或使用命令行参数构建")
        return None

    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    builder = ManifestBuilder()
    return builder.build(
        version=config.get("version", "0.0.0"),
        include_dirs=config.get("include_dirs"),
        include_globs=config.get("include_globs"),
        exclude_patterns=config.get("exclude_patterns"),
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="TPW 增量更新清单构建工具")
    parser.add_argument("--version", "-v", required=True, help="版本号，如 6.4.9.8")
    parser.add_argument("--source", "-s", help="项目根目录（默认为上级目录）")
    parser.add_argument("--output", "-o", help="manifest.json 输出路径")
    parser.add_argument("--config", "-c", help="从配置文件读取参数")

    args = parser.parse_args()

    if args.config:
        build_from_config(args.config)
    else:
        builder = ManifestBuilder(source_root=args.source)
        builder.build(version=args.version, output_path=args.output)
