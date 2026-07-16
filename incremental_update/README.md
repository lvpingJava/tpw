# TPW 增量更新系统 - 完整操作手册

> 📅 最后更新: 2026-07-14 ｜ 📦 适用版本: v6.6.0.5+

---

## 一、系统架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                        开发者工作流                               │
│                                                                 │
│  修改资源/代码 → build.ps1 -AutoTag 一键完成                      │
│       │                                                         │
│       ▼                                                         │
│  GitHub仓库 (lvpingJava/tpw) + Git tag vX.X.X.X                 │
│       │                                                         │
│       ▼                                                         │
│  jsDelivr CDN @vX.X.X.X (无缓存，tag 推送后 1-2 分钟生效)        │
│       │                                                         │
│       ▼                                                         │
│                        用户端增量更新系统                          │
│                                                                 │
│  点击"更新" → 下载manifest.json → MD5比对 → 仅下载变更文件        │
│            → 清理废弃文件(安全模式) → 重启生效                     │
└─────────────────────────────────────────────────────────────────┘
```

### 核心文件

| 文件 | 职责 |
|------|------|
| `incremental_update/builder.py` | 清单构建器 v2.0：扫描目录，生成 manifest.json（MD5 + SHA-256 双重哈希） |
| `incremental_update/updater.py` | 增量更新引擎 v2.2：CDN多级回退 + URL编码 + 下载校验 + 回滚 + 安全垃圾清理 |
| `incremental_update/gui_updater.py` | PyQt5 更新对话框 v2.0：变更日志 + 重试 + 双进度条 |
| `update_config.json` | 统一配置文件（服务器地址、版本号、扫描规则、更新日志） |
| `build.ps1` | 一键自动化打包发布脚本 v3.1（集成 Nuitka + 增量更新 + AutoTag） |
| `tpw_server.py` | 主程序入口，`pushButton_7` 绑定增量更新方法 |

### 核心原理

> **文件级 MD5/SHA-256 双重哈希比对**，而非二进制 diff/patch。
>
> **v2.2 新特性**：
> - **CDN 多级回退**：jsDelivr @v{version} → GitHub Raw @v{version} → jsDelivr @master
> - **URL 中文编码**：自动对中文路径进行百分号编码，兼容各 CDN
> - **安全垃圾清理**：仅清理 manifest 追踪目录，保护 Nuitka 系统目录（matplotlib/PyQt5/numpy 等）
> - **下载完整性校验**：下载后 MD5 验证，临时文件+原子替换
> - **回滚支持**：更新失败时自动恢复原始文件
> - **自适应超时**：文件下载超时 30s→300s 自适应，大文件自动放宽

---

## 二、开发者发布更新流程（★ 当前版本）

### 一键发布

```powershell
# 完整发布（新版本号首次发布，含 Nuitka 编译）
.\build.ps1 -Version "6.6.0.6" -CreateZip -AutoTag

# 快捷发布（仅改资源，同版本号，跳过编译）
.\build.ps1 -Version "6.6.0.6" -QuickUpdate -AutoTag

# 试运行预览（不实际打包）
.\build.ps1 -Version "6.6.0.6" -DryRun
```

`-AutoTag` 自动完成 8 步：

```
Step 0  更新版本号 + 生成 manifest.json (MD5 + SHA-256)
Step 1  清理旧构建产物
Step 2  Nuitka 编译 → 躺平王服务端.exe（-QuickUpdate 跳过）
Step 3  准备目标目录
Step 4  复制 Nuitka 产物（-QuickUpdate 跳过）
Step 5  复制资源文件 (手牌/场景/配置/OCR/增量更新系统)
Step 6  完整性验证（manifest 内容检查 + CDN 地址检查）
Step 7  创建 ZIP 分发包（-CreateZip / -QuickUpdate 时）
Step 8  ★ git add → commit → push master → git tag v6.6.0.6 → push tag
```

### 手动操作（不使用 -AutoTag 时）

```powershell
git add manifest.json update_config.json models/tpwVer.txt
git commit -m "v6.6.0.6: 发布更新"
git push origin master
git tag v6.6.0.6 ; git push origin v6.6.0.6
```

> ⚠️ **Git tag 是必须的**：jsDelivr CDN 使用 `@v{版本号}` 路径，依赖 Git tag 存在。无 tag → CDN 404 → 回退到 @master（旧版本）。

---

## 三、用户端更新机制

### 触发方式

用户打开 **躺平王服务端** 主界面，点击 **增量更新** 按钮（`pushButton_7`）即可触发。

### 更新流程详解

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  点击"更新"   │───→│ 下载远程清单  │───→│  MD5逐文件   │───→│  仅下载变更   │
│              │    │ manifest.json│    │  哈希比对     │    │  文件         │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
                                                                    │
                                                                    ▼
                                                           ┌──────────────┐
                                                           │  清理废弃文件  │
                                                           │  (垃圾清理)   │
                                                           └──────────────┘
                                                                    │
                                                                    ▼
                                                           ┌──────────────┐
                                                           │  保存本地清单  │
                                                           │  提示重启     │
                                                           └──────────────┘
```

**步骤详解**：

1. **连接服务器**：使用绕过系统代理的 HTTP Session 请求 `{server_url}/manifest.json`
2. **版本比对**：比较远程版本号与本地 `manifest.json` 中记录的版本
3. **逐文件 MD5 比对**：遍历远程清单的每个文件，与本地对应文件的 MD5 比对
   - MD5 相同 → 跳过
   - MD5 不同 → 加入下载列表
   - 本地无此文件 → 加入下载列表
4. **下载变更文件**：从 CDN 下载每个变更文件，先写入临时文件（`.tmp_update_` 前缀），下载完成后原子替换目标文件
5. **垃圾清理**：遍历本地目录，删除**不在远程清单中**且**不在保护目录中**的废弃文件
6. **保存清单**：将远程 `manifest.json` 保存到本地，作为下次比对的基准
7. **重启提示**：弹出对话框询问是否立即重启以应用更新

### 版本感知

- 用户端会在对话框中实时显示：**本地版本 vs 服务器版本**
- 如果版本相同且无文件变更，显示 "当前已是最新版本，无需更新"
- 更新完成后显示 "更新成功！当前版本: x.x.x.x"

### 哪些文件会被下载？

**仅下载与服务器 MD5 不一致的文件**，典型场景：

| 场景 | 下载量 | 说明 |
|------|-------|------|
| 只更新了几张手牌图片 | ~几十 KB | 仅变更的 `.bmp` 文件 |
| 修改了一个 Python 脚本 | ~几 KB | 仅该 `.py` 文件 |
| 没有任何变更 | 0 | 显示"已是最新版本" |
| 全新安装（本地无 manifest） | ~全部文件 | 首次运行会下载所有清单文件 |

---

## 四、安全保护机制

### 4.1 保护目录白名单（防止误删）

> ⚠️ **多层保护机制**：
> 1. **PROTECTED_DIRS** — 开发工具目录 + Nuitka 系统目录，os.walk 直接跳过
> 2. **_tracked_dirs** — 从 manifest 提取追踪目录，垃圾清理仅在这些目录内生效
> 3. **PROTECTED_FILES** — 关键配置文件，绝不覆盖

`updater.py` 中定义的保护规则：

```python
PROTECTED_DIRS = {
    # 开发工具目录
    '.idea', '.git', '.venv', 'venv', '__pycache__',
    '.qoder', '.trae', '.vscode',
    # Nuitka 编译产物（不在 manifest 中，垃圾清理必须保护）
    'matplotlib', 'PyQt5', 'numpy', 'cv2', 'PIL',
    'contourpy', 'kiwisolver', 'markupsafe', 'psutil', 'zstandard',
    'certifi', 'matplotlib.libs',
}

PROTECTED_FILES = {
    '.gitignore', 'update_config.json',
}
```

**保护逻辑**（[updater.py](file:///d:/test_py/tpw/tpw2-master/incremental_update/updater.py#L271-L291)）：
- 路径中**任何一级目录**在 `PROTECTED_DIRS` 中 → 跳过
- 文件名在 `PROTECTED_FILES` 中 → 跳过
- 保护目录中的文件：
  - **不参与文件比对**（`check_update` 中跳过）
  - **不会被下载覆盖**（`download_files` 中跳过）
  - **不会被垃圾清理删除**（`_clean_garbage` 中跳过）

### 4.2 代理网络兼容

> ⚠️ 某些 Windows 环境配置了系统 HTTP 代理，但代理不支持 jsDelivr CDN 的 HTTPS 直连，会导致 `ProxyError` + `SSLEOFError`。

`updater.py` 中创建了**绕过系统代理**的 HTTP Session（[updater.py](file:///d:/test_py/tpw/tpw2-master/incremental_update/updater.py#L17-L22)）：

```python
def _create_session():
    session = requests.Session()
    session.trust_env = False          # 不信任系统环境变量中的代理设置
    session.proxies = {"http": None, "https": None}  # 显式禁用代理
    return session
```

### 4.3 原子文件替换

下载过程使用**临时文件 + 原子移动**机制，防止下载中断导致文件损坏：

```
下载 → .tmp_update_xxxx（临时文件） → 校验 → 移动覆盖目标文件
```

如果下载被取消或失败，临时文件会被自动清理。

### 4.4 下载重试机制

每个文件最多重试 **3 次**，重试间隔递增（2s → 4s → 6s）。

---

## 五、配置文件说明 (update_config.json)

```json
{
    "server_url": "https://cdn.jsdelivr.net/gh/lvpingJava/tpw@v6.6.0.5",
    "version": "6.6.0.5",
    "changelog": "",
    "version_file": "models/tpwVer.txt",

    "include_dirs": [
        "配置", "手牌", "场景", "快速手牌", "暗月",
        "models", "flaskr", "ui", "matplotlibes", "wxauto",
        "other", "certifi"
    ],

    "include_globs": [
        "*.py", "*.txt", "*.dll", "*.exe",
        "*.bmp", "*.png", "*.gif", "*.tif", "*.jpg", "*.jpeg",
        "*.json", "*.sql", "*.pem", "*.ui"
    ],

    "exclude_patterns": [
        "__pycache__", "*.pyc", "*.log", "*.zip",
        "临时*", ".git*", ".idea*", "*.md",
        "test*.py", "微信图片*"
    ],

    "root_scripts": [
        "tpw_server.py", "webServer.py", "DmTool.py", ...
    ],

    "root_binaries": []
}
```

| 字段 | 说明 |
|------|------|
| `server_url` | CDN 地址，格式 `@v{版本号}`（无缓存）。build.ps1 自动更新 |
| `version` | 当前版本号，build.ps1 / builder.py 自动更新 |
| `changelog` | 更新日志（通过 `-Changelog` 参数传入） |
| `version_file` | 旧版本号文件路径（保持兼容） |
| `include_dirs` | 要扫描的目录列表（相对于项目根目录） |
| `include_globs` | 文件匹配模式（glob 语法） |
| `exclude_patterns` | 排除模式（支持目录名匹配，如 `"微信图片*"`） |
| `root_scripts` | 根目录下的关键 Python 脚本 |
| `root_binaries` | 根目录 exe/dll（默认空，因文件过大不适合 CDN） |

### 新增目录/文件类型的步骤

如果需要扫描新的目录或文件类型：

1. 编辑 `update_config.json`
2. 在 `include_dirs` 中添加新目录名
3. 或在 `include_globs` 中添加新文件扩展名
4. 重新运行 builder 生成清单

---

## 六、日常维护检查清单

### 每次发布前

- [ ] 确认 `update_config.json` 中版本号已更新
- [ ] 运行 `builder.py` 生成新的 `manifest.json`
- [ ] 检查 builder 输出：文件总数是否合理、无异常警告
- [ ] `git push` 推送到 GitHub
- [ ] 等待 1-2 分钟后验证 CDN URL 可访问

### 每次发布后

- [ ] 在用户端点击"增量更新"测试
- [ ] 确认版本号显示正确
- [ ] 确认文件下载数量与预期一致
- [ ] 确认更新后程序重启正常

### 定期维护

- [ ] 检查 `PROTECTED_DIRS` 是否覆盖所有新增的开发工具目录
- [ ] 如果更换 GitHub 仓库或分支，同步修改 `update_config.json` 的 `server_url` 和 `tpw_server.py` 中的默认 URL
- [ ] 清理过期的 Git tags（如需要）

---

## 七、常见问题与解决方案

### Q1: builder 扫描文件数量异常（太多或太少）

**原因**：`include_dirs` 或 `include_globs` 配置不当。

**解决**：
- 检查 `update_config.json` 中的配置
- 用 `--version` 命令行方式指定参数测试
- 确认 `exclude_patterns` 是否正确过滤了不需要的文件

### Q2: 用户端点击更新提示"无法连接更新服务器"

**原因**：
- 网络不通或 jsDelivr CDN 被墙
- 代理拦截

**解决**：
- 检查是否能访问 `https://cdn.jsdelivr.net`
- 确认 `updater.py` 中 `_create_session()` 的代理绕过逻辑未被改动
- 检查 `server_url` 中的分支名是否正确（本仓库为 `master`，非 `main`）

### Q3: 更新后项目代码被破坏 / 文件被误删

**原因**：保护目录白名单不完整。

**解决**：
- 检查 `updater.py` 中 `PROTECTED_DIRS` 和 `PROTECTED_FILES` 是否包含所有需要保护的目录/文件
- 确认 `local_dir` 不应设为敏感目录的父目录
- **紧急恢复**：通过 `git checkout -- .` 恢复被删文件

### Q4: 更新过程中下载超时

**原因**：
- 网络不稳定
- CDN 缓存未刷新

**解决**：
- 系统内置 3 次重试机制，一般可自动恢复
- 如持续超时，手动刷新 CDN 缓存：访问 `https://purge.jsdelivr.net/gh/lvpingJava/tpw@master/manifest.json`
- 检查本地代理设置，确保 `_create_session()` 正确绕过了代理

### Q5: 用户端显示"当前已是最新版本"，但实际文件是旧的

**原因**：本地 `manifest.json` 版本号与服务器相同，但文件内容不同。

**解决**：
- 检查是否确实推送了新版本的 `manifest.json` 到 GitHub
- 让用户删除本地 `manifest.json` 后重新更新（会触发全量比对）
- CDN 缓存问题：等待 24 小时或手动刷新缓存

---

## 八、自动化打包发布（Nuitka + 增量更新）

### 8.1 概述

`build.ps1` v3.1 与增量更新系统深度集成，**一条命令完成**：版本号更新 → 清单生成 → Nuitka 编译 → 资源复制 → ZIP → 验证 → **Git 自动发布**。

### 8.2 命令速查

```powershell
# ── 一键完整发布（新版本号首次，含编译+ZIP+自动Git） ──
.\build.ps1 -Version "6.6.0.6" -CreateZip -AutoTag

# ── 快捷资源更新（同版本号，跳过编译） ──
.\build.ps1 -Version "6.6.0.6" -QuickUpdate -AutoTag

# ── 试运行预览（仅生成清单） ──
.\build.ps1 -Version "6.6.0.6" -DryRun

# ── 附带更新日志 ──
.\build.ps1 -Version "6.6.0.6" -CreateZip -AutoTag -Changelog "修复手牌识别Bug"

# ── 从配置文件读取版本号 ──
.\build.ps1
```

### 8.3 完整参数列表

| 参数 | 类型 | 说明 |
|------|------|------|
| `-Version` | string | 版本号，如 `"6.6.0.6"` |
| `-TargetDir` | string | 自定义输出目录（默认自动推导） |
| `-Changelog` | string | 更新日志 |
| `-CreateZip` | switch | 自动创建 ZIP 分发包 |
| `-AutoTag` | switch | 自动 git commit → push → tag → push tag |
| `-QuickUpdate` | switch | 快捷模式：跳过编译 + 自动ZIP |
| `-SkipNuitka` | switch | 跳过 Nuitka 编译 |
| `-SkipManifest` | switch | 跳过清单生成（调试用） |
| `-DryRun` | switch | 试运行：仅生成清单和配置 |

### 8.4 脚本执行流程（8 步）

```
┌──────────────────────────────────────────────────────────────────┐
│  Step 0: 打包前准备                                               │
│    ├─ 更新 update_config.json 版本号 + server_url + changelog    │
│    ├─ 更新 models/tpwVer.txt 版本号                               │
│    └─ 运行 builder.py 生成 manifest.json（MD5 + SHA-256）         │
├──────────────────────────────────────────────────────────────────┤
│  Step 1: 清理旧构建产物                                           │
│    └─ 删除 tpw_server.dist/ 和 tpw_server.build/                  │
├──────────────────────────────────────────────────────────────────┤
│  Step 2: Nuitka 编译 (3-8 分钟，-QuickUpdate/-SkipNuitka 跳过)    │
│    └─ Python 源码 → 躺平王服务端.exe (含所有依赖)                  │
├──────────────────────────────────────────────────────────────────┤
│  Step 3: 准备目标目录                                             │
│    └─ 创建/清空 D:\test_py\tpw\打包\tpw{版本号}                   │
├──────────────────────────────────────────────────────────────────┤
│  Step 4: 复制 Nuitka 产物（-QuickUpdate/-SkipNuitka 时跳过）      │
│    └─ exe + dll + pyd + Nuitka 系统目录                           │
├──────────────────────────────────────────────────────────────────┤
│  Step 5: 复制资源文件 + 增量更新文件                               │
│    ├─ 资源目录: 手牌/场景/配置/models/暗月/快速手牌                │
│    ├─ OCR引擎: matplotlibes/matp.exe + models/                    │
│    ├─ 原生DLL: other/*.dll + tess_model                           │
│    ├─ manifest.json     (增量更新清单)                           │
│    ├─ update_config.json (CDN地址配置)                           │
│    └─ 运行时目录: log/ + 临时卡牌/                                 │
├──────────────────────────────────────────────────────────────────┤
│  Step 6: 打包后验证                                               │
│    ├─ 关键文件存在性检查                                          │
│    ├─ manifest.json 内容完整性检查                                 │
│    └─ update_config.json CDN 地址检查                             │
├──────────────────────────────────────────────────────────────────┤
│  Step 7: ZIP 分发（-CreateZip / -QuickUpdate 时）                 │
│    └─ 自动压缩为 .zip 分发包                                      │
├──────────────────────────────────────────────────────────────────┤
│  Step 8: ★ Git 自动发布（-AutoTag 时）                            │
│    ├─ git add manifest.json update_config.json models/tpwVer.txt │
│    ├─ git commit -m "v{版本号}: 发布更新"                         │
│    ├─ git push origin master                                      │
│    ├─ git tag v{版本号}                                           │
│    └─ git push origin v{版本号}                                   │
└──────────────────────────────────────────────────────────────────┘
```

### 8.5 打包产物与增量更新的关系

| 文件 | 在打包目录中 | 在 Git/CDN 中 | 作用 |
|------|:-----------:|:-----------:|------|
| `躺平王服务端.exe` | ✓ | ✗ | 主程序（Nuitka 编译，不上传 Git） |
| `manifest.json` | ✓ | ✓ | 增量更新清单，**必须在 CDN 上** |
| `update_config.json` | ✓ | ✓ | CDN 地址配置 |
| `手牌/`, `场景/`, etc. | ✓ | ✓ | 资源文件，副本同时存在于打包目录和 CDN |

> **关键理解**：用户端增量更新下载的文件来自 **CDN**（GitHub + jsDelivr），而非打包目录。因此 `manifest.json` **必须推送到 GitHub** 且 **Git tag 必须创建**，否则 CDN 无法定位文件。

### 8.6 典型工作场景

**场景 1：更新手牌识别数据（资源变更）**
```powershell
# 修改手牌图片后，一键发布
.\build.ps1 -Version "6.6.0.6" -QuickUpdate -AutoTag -Changelog "更新手牌数据"
# 等 1-2 分钟后，用户点击「增量更新」仅下载变更的手牌图片
```

**场景 2：修改 Python 脚本（代码变更）**
```powershell
# 修改 tpw_server.py / DmTool.py 等，完整编译
.\build.ps1 -Version "6.6.0.6" -CreateZip -AutoTag -Changelog "优化识别逻辑"
# 已有用户: 增量更新会推送 .py 文件，但 exe 不会自动重编译，需下载新 ZIP
# 新用户: 下载 ZIP 获得最新 exe
```

> ⚠️ Python 脚本被 Nuitka 编译进 .exe，增量更新推送 .py 文件后**正在运行的 exe 不会自动重编译**。如需 exe 变更生效，用户必须下载完整 ZIP 重新安装。

---

## 九、快速参考命令

```powershell
# ── 一键完整发布（★ 推荐） ──
.\build.ps1 -Version "6.6.0.6" -CreateZip -AutoTag

# ── 快捷资源更新 ──
.\build.ps1 -Version "6.6.0.6" -QuickUpdate -AutoTag

# ── 试运行 ──
.\build.ps1 -Version "6.6.0.6" -DryRun

# ── 手动操作（不使用 -AutoTag 时） ──
git add manifest.json update_config.json models/tpwVer.txt
git commit -m "v6.6.0.6: 发布更新"
git push origin master
git tag v6.6.0.6 ; git push origin v6.6.0.6

# ── 验证 CDN（浏览器打开） ──
# https://cdn.jsdelivr.net/gh/lvpingJava/tpw@v6.6.0.6/manifest.json

# ── 紧急恢复 ──
git checkout -- .
```

---

## 附录 A：venv 重建指南

如果 `.venv` 被意外破坏（如 `pyvenv.cfg` 或 `__init__.py` 被删）：

```powershell
# 1. 备份旧 venv
Rename-Item .venv .venv.bak

# 2. 新建 venv
C:\Users\ZTSK\AppData\Local\Programs\Python\Python38\python.exe -m venv .venv

# 3. 安装依赖（使用清华镜像以加快速度，绕过代理）
$env:HTTP_PROXY=''; $env:HTTPS_PROXY=''; $env:http_proxy=''; $env:https_proxy=''
.venv\Scripts\python.exe -m pip install PyQt5 opencv-python numpy requests mss pygetwindow flask psutil uiautomation pillow pyperclip imageio zstandard matplotlib nuitka -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn

# 4. 安装 pywin32（使用本地 whl）
.venv\Scripts\python.exe -m pip install .\pywin32-304.0-cp38-cp38-win_amd64.whl

# 5. 验证
.venv\Scripts\python.exe -c "import win32gui,win32ui; from PyQt5 import QtWidgets; import cv2,numpy,requests; print('OK')"

# 6. 确认正常后可删除备份
Remove-Item .venv.bak -Recurse -Force
```

## 附录 B：GitHub 仓库信息

| 项目 | 值 |
|------|-----|
| 仓库地址 | `https://github.com/lvpingJava/tpw.git` |
| 主分支 | `master` |
| CDN 地址 | `https://cdn.jsdelivr.net/gh/lvpingJava/tpw@master` |
| 账号 | `lvpingJava` |
| 邮箱 | `827886863@qq.com` |

---

> 📅 最后更新: 2026-07-14
> 📦 对应版本: v6.6.0.5+
> 🔧 基于 `incremental_update/` 模块 v2.2 (URL编码 + 安全垃圾清理 + CDN回退 + 回滚支持)
> 📦 打包脚本: `build.ps1` v3.1 (集成 AutoTag + QuickUpdate + DryRun)
