# TPW 增量更新系统 - 完整操作手册

---

## 一、系统架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                        开发者工作流                               │
│                                                                 │
│  修改资源文件 → 更新版本号 → 生成manifest.json → Git提交推送       │
│       │                                                         │
│       ▼                                                         │
│  GitHub仓库 (lvpingJava/tpw) ──→ jsDelivr CDN 自动同步           │
│                                      │                          │
│                                      ▼                          │
│                        用户端增量更新系统                          │
│                                                                 │
│  点击"更新" → 下载manifest.json → MD5比对 → 仅下载变更文件        │
│                                → 清理废弃文件 → 重启生效           │
└─────────────────────────────────────────────────────────────────┘
```

### 核心文件

| 文件 | 职责 |
|------|------|
| `incremental_update/builder.py` | 清单构建器 v2.0：扫描目录，生成 manifest.json（MD5 + SHA-256 双重哈希） |
| `incremental_update/updater.py` | 增量更新引擎 v2.0：CDN多级回退 + 下载校验 + 回滚支持 |
| `incremental_update/gui_updater.py` | PyQt5 更新对话框 v2.0：变更日志 + 重试 + 双进度条 |
| `update_config.json` | 统一配置文件（服务器地址、版本号、扫描规则、更新日志） |
| `tpw_server.py` | 主程序入口，`pushButton_7` 绑定 `incremental_update()` 方法 |

### 核心原理

> **文件级 MD5/SHA-256 双重哈希比对**，而非二进制 diff/patch。客户端对比本地文件哈希与服务器 manifest.json 中的哈希，不同的才下载。实现简单、健壮，无需维护二进制 patch 文件。
>
> **v2.0 新特性**：
> - **CDN 多级回退**：jsDelivr → GitHub Raw → jsDelivr @master，主CDN不可用时自动切换
> - **下载完整性校验**：下载后 SHA-256 验证，确保文件未损坏或被篡改
> - **回滚支持**：更新失败时自动恢复原始文件，保证程序可用
> - **变更日志展示**：更新对话框显示本次更新内容

---

## 二、开发者发布更新流程

### 流程图

```
修改文件 → 修改版本号 → 构建清单 → 提交Git → 推送 → (打Tag) → CDN自动同步
```

### 第 1 步：修改资源文件

在项目根目录下直接修改需要更新的文件，常见场景：

| 场景 | 修改目录 | 示例 |
|------|---------|------|
| 更新手牌识别数据 | `手牌/` | 新增或替换 `.bmp` 模板图片 |
| 更新场景图片 | `场景/` | 替换场景识别图 |
| 更新配置 | `配置/` | 修改 DLL 或配置文件 |
| 修改 Python 脚本 | 根目录 | 修改 `tpw_server.py`、`DmTool.py` 等 |
| 更新 Web 服务 | `flaskr/` | 修改 `webServer.py` 等 |

> **注意**：修改范围必须在 `update_config.json` 中 `include_dirs` 和 `root_scripts` 所列范围内，否则不会被纳入清单。

### 第 2 步：更新版本号

修改 `update_config.json` 中的 `version` 字段，建议使用 `主版本.次版本.修订.构建号` 格式：

```json
{
    "version": "6.4.9.8",
    ...
}
```

> 版本号递增规则示例：`6.4.9.7` → `6.4.9.8`(小修复) 或 `6.5.0.0`(功能更新)

### 第 3 步：生成清单文件 (manifest.json)

打开终端，在项目根目录执行：

```powershell
# 方式一：命令行指定版本号（推荐）
py .\incremental_update\builder.py --version "6.4.9.8"

# 方式二：附带更新日志
py .\incremental_update\builder.py --version "6.4.9.8" --changelog "更新手牌识别数据"

# 方式三：从 update_config.json 读取版本号
py .\incremental_update\builder.py --config update_config.json
```

生成的 `manifest.json` 结构（v2.0 格式，包含 MD5 + SHA-256）：

```json
{
    "version": "6.4.9.8",
    "build_time": "2026-07-14 15:30:00",
    "changelog": "更新手牌识别数据",
    "files": {
        "手牌/手牌1/某卡牌.bmp": {"md5": "a1b2c3d4...", "sha256": "e5f6g7h8..."},
        "场景/某场景.bmp": {"md5": "12345678...", "sha256": "abcdef12..."},
        ...
    }
}
```

### 第 4 步：提交到 Git 并推送

```powershell
git add -A
git commit -m "更新手牌数据 v6.4.9.8"
git push origin master
```

### 第 5 步（可选）：打版本 Tag

如需精确版本管理或回滚：

```powershell
git tag v6.4.9.8
git push origin v6.4.9.8
```

### 第 6 步：验证 CDN 同步

推送后等待 1-2 分钟，在浏览器中验证：

```
https://cdn.jsdelivr.net/gh/lvpingJava/tpw@master/manifest.json
```

> jsDelivr 的缓存刷新时间通常为 **24 小时内**（首次访问后），新文件可能需等缓存过期。可以用 `purge.jsdelivr.net` 手动刷新：
> ```
> https://purge.jsdelivr.net/gh/lvpingJava/tpw@master/manifest.json
> ```

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

> ⚠️ **这是经历过严重事故后加入的关键保护**：早期版本将 `local_dir` 设为项目根目录，垃圾清理器遍历删除时误删了 `.idea/`、`.git/`、`.venv/` 等开发目录。

`updater.py` 中定义了以下保护规则（[updater.py](file:///d:/test_py/tpw/tpw2-master/incremental_update/updater.py#L35-L42)）：

```python
PROTECTED_DIRS = {
    '.idea', '.git', '.venv', 'venv', '__pycache__',
    '.qoder', '.trae', '.vscode',
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
    "server_url": "https://cdn.jsdelivr.net/gh/lvpingJava/tpw@master",
    "version": "6.4.9.8",

    "include_dirs": [
        "配置", "手牌", "场景", "快速手牌", "暗月",
        "models", "flaskr", "ui", "matplotlibes", "wxauto",
        "other", "certifi"
    ],

    "include_globs": [
        "*.py", "*.txt", "*.dll", "*.exe",
        "*.bmp", "*.png", "*.gif", "*.tif", "*.jpg", "*.jpeg",
        "*.json", "*.sql", "*.pem", "*.spec", "*.ui"
    ],

    "exclude_patterns": [
        "__pycache__", "*.pyc", "*.log", "*.zip",
        "临时*", ".git*", ".idea*", "*.md",
        "test*.py"
    ],

    "root_scripts": [
        "tpw_server.py", "webServer.py", "DmTool.py", ...
    ]
}
```

| 字段 | 说明 |
|------|------|
| `server_url` | CDN 地址，格式 `https://cdn.jsdelivr.net/gh/{用户}/{仓库}@{分支}` |
| `version` | 当前版本号，**每次发布需手动更新** |
| `include_dirs` | 要扫描的目录列表（相对于项目根目录） |
| `include_globs` | 文件匹配模式（glob 语法） |
| `exclude_patterns` | 排除模式，不会进入 manifest |
| `root_scripts` | 根目录下的关键 Python 脚本 |

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

`build.ps1` 已与增量更新系统深度集成，**一条命令完成**：版本号更新 → 清单生成 → Nuitka 编译 → 资源复制 → 兼容性验证。

### 8.2 打包命令

```powershell
# 激活虚拟环境（必须先执行）
cd d:\test_py\tpw\tpw2-master
.\.venv\Scripts\Activate.ps1

# ── 方式一：指定版本号一键打包（推荐） ──
.\build.ps1 -Version "6.5.0.0"

# ── 方式二：快捷更新模式（跳过编译+自动ZIP，资源小更新用） ──
.\build.ps1 -Version "6.5.0.0" -QuickUpdate

# ── 方式三：附带更新日志 ──
.\build.ps1 -Version "6.5.0.0" -QuickUpdate -Changelog "修复手牌识别Bug，新增暗月场景"

# ── 方式四：从 update_config.json 读取版本 ──
.\build.ps1

# ── 方式五：指定输出目录 ──
.\build.ps1 -Version "6.5.0.0" -TargetDir "D:\test_py\tpw\打包\tpw6.5.0.0"

# ── 方式六：仅重新打包，跳过清单生成（调试用） ──
.\build.ps1 -Version "6.5.0.0" -SkipManifest
```

### 8.3 脚本执行流程（7 步）

```
┌──────────────────────────────────────────────────────────────────┐
│  Step 0: 打包前准备                                               │
│    ├─ 更新 update_config.json 版本号 + changelog                  │
│    ├─ 更新 models/tpwVer.txt 版本号                               │
│    └─ 运行 builder.py 生成 manifest.json（MD5 + SHA-256）         │
├──────────────────────────────────────────────────────────────────┤
│  Step 1: 清理旧构建产物                                           │
│    └─ 删除 tpw_server.dist/ 和 tpw_server.build/                  │
├──────────────────────────────────────────────────────────────────┤
│  Step 2: Nuitka 编译打包 (约 3-8 分钟，可用 -SkipNuitka 跳过)     │
│    └─ Python 源码 → 躺平王服务端.exe (含所有依赖)                  │
├──────────────────────────────────────────────────────────────────┤
│  Step 3: 准备目标目录                                             │
│    └─ 创建/清空 D:\test_py\tpw\打包\tpw{版本号}                   │
├──────────────────────────────────────────────────────────────────┤
│  Step 4: 复制 Nuitka 产物（-SkipNuitka 时跳过）                   │
│    └─ exe + dll + pyd 文件                                        │
├──────────────────────────────────────────────────────────────────┤
│  Step 5: 复制资源文件 + 增量更新文件                               │
│    ├─ 资源目录: 手牌/场景/配置/models/暗月/快速手牌                │
│    ├─ OCR引擎: matplotlibes/matp.exe + models/                    │
│    ├─ 原生DLL: other/*.dll + tess_model                           │
│    ├─ ★ manifest.json     (增量更新清单 v2.0)                     │
│    ├─ ★ update_config.json (CDN地址配置)                          │
│    └─ 运行时目录: log/ + 临时卡牌/                                 │
├──────────────────────────────────────────────────────────────────┤
│  Step 6: 打包后验证                                               │
│    ├─ 关键文件存在性检查                                          │
│    ├─ manifest.json 内容完整性检查 (SHA-256 自校验)               │
│    ├─ update_config.json CDN 地址检查                             │
│    └─ 显示下一步 Git 操作提示                                     │
├──────────────────────────────────────────────────────────────────┤
│  Step 7: ZIP 分发（-CreateZip 或 -QuickUpdate 时）                │
│    └─ 自动压缩打包目录为 .zip 文件                                │
└──────────────────────────────────────────────────────────────────┘
```

### 8.4 打包后发布流程

打包完成后脚本会提示下一步操作：

```powershell
# Step A: 提交清单到 Git（必须执行，这是增量更新的关键）
git add manifest.json update_config.json models/tpwVer.txt
git commit -m "v6.5.0.0: 发布更新"
git push origin master

# Step B: 刷新 CDN 缓存（浏览器打开）
# https://purge.jsdelivr.net/gh/lvpingJava/tpw@master/manifest.json

# Step C: 将打包目录分发给新用户（首次安装用）
# D:\test_py\tpw\打包\tpw6.5.0.0\  →  压缩后分发
```

### 8.5 打包产物与增量更新的关系

| 文件 | 在打包目录中 | 在 Git/CDN 中 | 作用 |
|------|:-----------:|:-----------:|------|
| `躺平王服务端.exe` | ✓ | ✗ | 主程序（Nuitka 编译，不上传 Git） |
| `manifest.json` | ✓ | ✓ | 增量更新清单，**必须在 CDN 上** |
| `update_config.json` | ✓ | ✓ | CDN 地址配置 |
| `手牌/`, `场景/`, etc. | ✓ | ✓ | 资源文件，副本同时存在于打包目录和 CDN |

> **关键理解**：用户端增量更新下载的文件来自 **CDN**（GitHub + jsDelivr），而非打包目录。打包目录仅用于首次安装分发。因此 `manifest.json` **必须推送到 GitHub**，否则用户端无法检测更新。

### 8.6 典型工作场景

**场景 1：更新手牌识别数据**
```powershell
# 1. 修改手牌图片（替换/新增 .bmp 文件）
# 2. 快捷打包（跳过编译，仅更新资源）
.\build.ps1 -Version "6.4.9.8" -QuickUpdate -Changelog "更新手牌数据"
# 3. 推送清单到 Git
git add manifest.json update_config.json models/tpwVer.txt
git commit -m "v6.4.9.8: 更新手牌数据"
git push origin master
git tag v6.4.9.8; git push origin v6.4.9.8
# 4. 完成！已有用户点击「增量更新」仅下载变更的手牌图片
```

**场景 2：只更新 Python 脚本（不涉及资源文件）**
```powershell
# 修改 tpw_server.py / DmTool.py 等
.\build.ps1 -Version "6.5.0.0"
git add manifest.json update_config.json models/tpwVer.txt
git commit -m "v6.5.0.0: 优化识别逻辑"
git push origin master
git tag v6.5.0.0; git push origin v6.5.0.0
# 注意：py 脚本编译进了 exe，只有新用户需要重新下载完整安装包
# 已有用户通过增量更新不会获得脚本变更（因为脚本在 exe 内部）
```

> ⚠️ **重要**：Python 脚本被 Nuitka 编译进 .exe，不在 manifest.json 的扫描范围内。修改 Python 代码后，增量更新**无法**推送脚本变更到已有用户——他们需要重新下载完整安装包。只有 `配置/`、`手牌/`、`场景/` 等资源目录的变更才能通过增量更新推送。

---

## 九、快速参考命令

```powershell
cd d:\test_py\tpw\tpw2-master
.\.venv\Scripts\Activate.ps1

# ── 一键打包发布（推荐） ──
.\build.ps1 -Version "6.5.0.0"

# ── 开发者操作 ──

# 仅生成清单（不打包）
py .\incremental_update\builder.py --version "6.4.9.8"

# 从配置文件读取并生成清单
py .\incremental_update\builder.py --config update_config.json

# Git 提交清单（打包后执行）
git add manifest.json update_config.json models/tpwVer.txt
git commit -m "v6.4.9.8: 更新手牌识别数据"
git push origin master

# 打版本标签（可选）
git tag v6.4.9.8
git push origin v6.4.9.8

# ── 验证操作 ──

# 检查 CDN 是否同步（浏览器打开）
# https://cdn.jsdelivr.net/gh/lvpingJava/tpw@master/manifest.json

# 手动刷新 CDN 缓存（浏览器打开）
# https://purge.jsdelivr.net/gh/lvpingJava/tpw@master/manifest.json

# ── 紧急恢复 ──

# 如果更新器误删了开发文件
git checkout -- .

# 如果 .venv 被破坏
# 重建步骤见下文"venv 重建指南"
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
> 📦 对应版本: v6.5.0.0+
> 🔧 基于 `incremental_update/` 模块 v2.0 (SHA-256 + CDN回退 + 回滚支持)
> 📦 打包脚本: `build.ps1` v3.0（已集成增量更新 + QuickUpdate快捷模式）
