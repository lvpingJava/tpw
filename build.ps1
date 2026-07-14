# =============================================================================
#  躺平王服务端 - 一键自动化打包脚本（集成增量更新系统）
#
#  用法:
#    .\build.ps1                                    # 从 update_config.json 读取版本
#    .\build.ps1 -Version "6.5.0.0"                 # 指定版本号，自动推导目标目录
#    .\build.ps1 -Version "6.5.0.0" -SkipManifest   # 跳过清单生成（仅重新打包）
#    .\build.ps1 -TargetDir "D:\test_py\tpw\打包\tpw6.5.0.0"  # 手动指定目标目录
#
#  完整流程: 更新版本 → 生成清单 → Nuitka编译 → 复制资源 → 验证 → 提示Git操作
# =============================================================================
param(
    [string]$Version = "",                          # 版本号，如 "6.5.0.0"
    [string]$TargetDir = "",                        # 输出目录（可从 Version 自动推导）
    [switch]$SkipManifest = $false                  # 跳过清单生成步骤
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$DistDir = Join-Path $ScriptDir "tpw_server.dist"
$BuildDir = Join-Path $ScriptDir "tpw_server.build"
$ConfigPath = Join-Path $ScriptDir "update_config.json"
$VerFilePath = Join-Path $ScriptDir "models\tpwVer.txt"

# ── 读取配置 ──────────────────────────────────────────────────
$config = Get-Content $ConfigPath -Raw -Encoding UTF8 | ConvertFrom-Json

# 版本号优先级: 命令行参数 > 配置文件 > 默认值
if (-not $Version) {
    $Version = $config.version
    if (-not $Version) { $Version = "0.0.0" }
}

# 目标目录优先级: 命令行参数 > 从版本号自动推导
if (-not $TargetDir) {
    $TargetDir = "D:\test_py\tpw\打包\tpw$Version"
}

# ── 颜色辅助函数 ──────────────────────────────────────────────
function Write-Step([string]$msg) {
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] $msg" -ForegroundColor Yellow
}
function Write-OK([string]$msg) {
    Write-Host "  ✓ $msg" -ForegroundColor Green
}
function Write-Fail([string]$msg) {
    Write-Host "  ✗ $msg" -ForegroundColor Red
}
function Write-Warn([string]$msg) {
    Write-Host "  ⚠ $msg" -ForegroundColor Magenta
}
function Write-Info([string]$msg) {
    Write-Host "    $msg" -ForegroundColor Gray
}

# ── 打印 Banner ────────────────────────────────────────────────
Write-Host ""
Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     躺平王服务端 - 自动化打包脚本 v2.0       ║" -ForegroundColor Cyan
Write-Host "║     已集成增量更新系统                       ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host "  版本号  : $Version" -ForegroundColor White
Write-Host "  输出目录: $TargetDir" -ForegroundColor Gray
Write-Host ""

# =====================================================================
#  Step 0: 打包前准备（版本号 + 清单生成）
# =====================================================================
if (-not $SkipManifest) {
    Write-Step "[0/6] 打包前准备..."

    # 0a. 更新 update_config.json 中的版本号
    $config.version = $Version
    $config | ConvertTo-Json -Depth 10 | Set-Content $ConfigPath -Encoding UTF8
    Write-OK "update_config.json 版本 → $Version"

    # 0b. 更新 models/tpwVer.txt（旧版本号文件，保持兼容）
    if (Test-Path (Split-Path $VerFilePath)) {
        $Version | Set-Content $VerFilePath -Encoding UTF8 -NoNewline
        Write-OK "models/tpwVer.txt 版本 → $Version"
    } else {
        Write-Warn "models/tpwVer.txt 目录不存在，跳过"
    }

    # 0c. 生成增量更新清单 (manifest.json)
    Write-Info "正在生成 manifest.json ..."
    $builderScript = Join-Path $ScriptDir "incremental_update\builder.py"
    $pythonExe = Join-Path $ScriptDir ".venv\Scripts\python.exe"

    if (-not (Test-Path $pythonExe)) {
        Write-Fail "虚拟环境未找到: $pythonExe"
        Write-Info "请先激活虚拟环境: .\.venv\Scripts\Activate.ps1"
        exit 1
    }

    $builderPy = Join-Path $ScriptDir "incremental_update\builder.py"
    $manifestResult = & $pythonExe $builderPy --version $Version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Fail "清单生成失败！"
        Write-Host $manifestResult
        exit 1
    }
    Write-OK "manifest.json 已生成（版本 $Version）"

    # 0d. 统计清单文件数
    $manifestPath = Join-Path $ScriptDir "manifest.json"
    if (Test-Path $manifestPath) {
        $manifest = Get-Content $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
        $manifestFileCount = ($manifest.files | Get-Member -MemberType NoteProperty).Count
        Write-OK "清单包含 $manifestFileCount 个文件"
    }
} else {
    Write-Step "[0/6] 跳过打包前准备 (--SkipManifest)"
}

# =====================================================================
#  Step 1: 清理旧构建产物
# =====================================================================
Write-Step "[1/6] 清理旧构建产物..."
$toRemove = @($DistDir, $BuildDir)
foreach ($path in $toRemove) {
    if (Test-Path $path) {
        Remove-Item -Recurse -Force $path -ErrorAction SilentlyContinue
        Write-OK "已删除: $(Split-Path $path -Leaf)"
    }
}

# =====================================================================
#  Step 2: Nuitka 编译打包
# =====================================================================
Write-Step "[2/6] Nuitka 编译打包中 (约 3-8 分钟)..."
$iconPath = Join-Path $ScriptDir "models\tpwlogo.png"
$certPath = Join-Path $ScriptDir "certifi\cacert.pem"
$mainScript = Join-Path $ScriptDir "tpw_server.py"

$nuitkaArgs = @(
    "--standalone",
    "--remove-output",
    "--enable-plugin=pyqt5",
    "--mingw64",
    "--windows-icon-from-ico=$iconPath",
    "--output-filename=躺平王服务端",
    "--include-data-files=$certPath=certifi\cacert.pem",
    "--assume-yes-for-downloads",
    $mainScript
)

# 执行 Nuitka
python -m nuitka @nuitkaArgs

if ($LASTEXITCODE -ne 0) {
    Write-Fail "Nuitka 编译失败！退出码: $LASTEXITCODE"
    exit 1
}
Write-OK "Nuitka 编译完成"

# =====================================================================
#  Step 3: 准备目标目录
# =====================================================================
Write-Step "[3/6] 准备目标目录..."
if (Test-Path $TargetDir) {
    Write-Info "清空已有目录..."
    Remove-Item -Recurse -Force $TargetDir -ErrorAction SilentlyContinue
}
New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null
Write-OK "目标目录就绪"

# =====================================================================
#  Step 4: 复制 Nuitka 编译产物
# =====================================================================
Write-Step "[4/6] 复制程序文件..."
Copy-Item -Path "$DistDir\*" -Destination $TargetDir -Recurse -Force

$exeCount = (Get-ChildItem -Path $TargetDir -Filter "*.exe").Count
$dllCount = (Get-ChildItem -Path $TargetDir -Filter "*.dll").Count
$pydCount = (Get-ChildItem -Path $TargetDir -Filter "*.pyd").Count
Write-OK "已复制: $exeCount 个 exe, $dllCount 个 dll, $pydCount 个 pyd"

# =====================================================================
#  Step 5: 复制资源文件 + 增量更新相关文件
# =====================================================================
Write-Step "[5/6] 复制资源文件..."

# --- 5a. 复制完整资源目录 ---
$resourceDirs = @(
    "手牌",          # 卡牌识别模板
    "快速手牌",      # 快速卡牌模板
    "场景",          # 场景图片
    "暗月",          # 暗月场景图片
    "models",        # 版本文件/图标/动画
    "配置"           # DMPJ.DLL, DmReg.dll
)

foreach ($dir in $resourceDirs) {
    $src = Join-Path $ScriptDir $dir
    $dst = Join-Path $TargetDir $dir
    if (Test-Path $src) {
        Copy-Item -Path $src -Destination $dst -Recurse -Force
        $fileCount = (Get-ChildItem -Path $dst -Recurse -File).Count
        Write-OK "资源目录: $dir ($fileCount 个文件)"
    } else {
        Write-Warn "跳过 (不存在): $dir"
    }
}

# --- 5b. 复制 OCR 引擎 ---
$ocrSrc = Join-Path $ScriptDir "matplotlibes"
$ocrDst = Join-Path $TargetDir "matplotlibes"
if (Test-Path $ocrSrc) {
    if (-not (Test-Path $ocrDst)) {
        New-Item -ItemType Directory -Force -Path $ocrDst | Out-Null
    }
    $matpExe = Join-Path $ocrSrc "matp.exe"
    if (Test-Path $matpExe) {
        Copy-Item -Path $matpExe -Destination $ocrDst -Force
        Write-OK "OCR引擎: matp.exe"
    }
    $modelsSrc = Join-Path $ocrSrc "models"
    if (Test-Path $modelsSrc) {
        Copy-Item -Path $modelsSrc -Destination $ocrDst -Recurse -Force
        $modelCount = (Get-ChildItem -Path (Join-Path $ocrDst "models") -File).Count
        Write-OK "OCR模型: models/ ($modelCount 个文件)"
    }
}

# --- 5c. 复制原生 DLL ---
$otherSrc = Join-Path $ScriptDir "other"
if (Test-Path $otherSrc) {
    Get-ChildItem -Path $otherSrc -Filter "*.dll" | ForEach-Object {
        Copy-Item -Path $_.FullName -Destination $TargetDir -Force
        Write-OK "原生DLL: $($_.Name)"
    }
    $tessSrc = Join-Path $otherSrc "tess_model"
    if (Test-Path $tessSrc) {
        $tessDst = Join-Path $TargetDir "other\tess_model"
        New-Item -ItemType Directory -Force -Path (Split-Path $tessDst) | Out-Null
        Copy-Item -Path $tessSrc -Destination $tessDst -Recurse -Force
        Write-OK "Tesseract模型: other/tess_model/"
    }
}

# --- 5d. 复制根级别资源文件 ---
$rootFiles = @(
    "tools_64.dll",
    "handle.exe",
    "rec_word_dict.txt",
    "ocr_a_reference.png"
)
foreach ($file in $rootFiles) {
    $src = Join-Path $ScriptDir $file
    if (Test-Path $src) {
        Copy-Item -Path $src -Destination $TargetDir -Force
        Write-OK "根目录文件: $file"
    }
}

# --- 5e. 复制增量更新系统核心文件 ---
Write-Host "  ── 增量更新系统 ──" -ForegroundColor Gray
# manifest.json: 版本清单，增量更新的核心
$manifestSrc = Join-Path $ScriptDir "manifest.json"
if (Test-Path $manifestSrc) {
    Copy-Item -Path $manifestSrc -Destination $TargetDir -Force
    Write-OK "manifest.json (版本 $Version)"
} else {
    Write-Fail "manifest.json 不存在！请先运行 builder.py 生成清单"
}

# update_config.json: 包含 CDN 地址，供运行时读取
$configSrc = Join-Path $ScriptDir "update_config.json"
if (Test-Path $configSrc) {
    Copy-Item -Path $configSrc -Destination $TargetDir -Force
    Write-OK "update_config.json (服务器地址配置)"
}

# incremental_update 模块由 Nuitka 编译到 exe 中，无需额外复制 Python 源码

# --- 5f. 创建运行时需要的空目录 ---
$runtimeDirs = @("log", "临时卡牌")
foreach ($dir in $runtimeDirs) {
    $dst = Join-Path $TargetDir $dir
    if (-not (Test-Path $dst)) {
        New-Item -ItemType Directory -Force -Path $dst | Out-Null
        Write-OK "运行时目录: $dir (已创建)"
    }
}

# =====================================================================
#  Step 6: 打包后验证
# =====================================================================
Write-Step "[6/6] 打包后验证..."

$allOk = $true
$totalFiles = (Get-ChildItem -Path $TargetDir -Recurse -File).Count
$totalDirs = (Get-ChildItem -Path $TargetDir -Recurse -Directory).Count
$totalSize = [math]::Round(((Get-ChildItem -Path $TargetDir -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB), 2)

Write-Info "总文件: $totalFiles 个, 子目录: $totalDirs 个, 大小: $totalSize MB"

# 关键文件检查列表
Write-Host ""
Write-Host "  关键文件检查:" -ForegroundColor Gray
$keyFiles = @(
    @{Path="躺平王服务端.exe";          Desc="主程序"},
    @{Path="manifest.json";             Desc="增量更新清单"},
    @{Path="update_config.json";        Desc="更新服务器配置"},
    @{Path="certifi\cacert.pem";        Desc="SSL证书"},
    @{Path="手牌";                       Desc="手牌识别数据"},
    @{Path="场景";                       Desc="场景图片"},
    @{Path="models\tpwVer.txt";         Desc="版本号文件"},
    @{Path="models\tpwlogo.png";        Desc="程序图标"},
    @{Path="matplotlibes\matp.exe";     Desc="OCR引擎"},
    @{Path="matplotlibes\models\besdet.onnx"; Desc="OCR模型"},
    @{Path="配置";                       Desc="DLL配置"}
)

foreach ($item in $keyFiles) {
    $checkPath = Join-Path $TargetDir $item.Path
    if (Test-Path $checkPath) {
        Write-Host "    ✓ $($item.Path)  [$($item.Desc)]" -ForegroundColor Green
    } else {
        Write-Host "    ✗ $($item.Path)  缺失! [$($item.Desc)]" -ForegroundColor Red
        $allOk = $false
    }
}

# ── 增量更新兼容性验证 ──
Write-Host ""
Write-Host "  增量更新兼容性检查:" -ForegroundColor Gray

# 验证 manifest.json 内容完整性
$pkgManifestPath = Join-Path $TargetDir "manifest.json"
if (Test-Path $pkgManifestPath) {
    $pkgManifest = Get-Content $pkgManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $pkgVersion = $pkgManifest.version
    $pkgFileCount = ($pkgManifest.files | Get-Member -MemberType NoteProperty).Count

    Write-Host "    ✓ 清单版本: $pkgVersion" -ForegroundColor Green
    Write-Host "    ✓ 清单文件数: $pkgFileCount" -ForegroundColor Green

    # 抽查几个资源目录是否在清单中
    $samplePaths = @("models/tpwVer.txt", "models/tpwlogo.png", "手牌", "场景")
    foreach ($sp in $samplePaths) {
        $found = $false
        foreach ($prop in ($pkgManifest.files | Get-Member -MemberType NoteProperty)) {
            if ($prop.Name -like "$sp/*" -or $prop.Name -eq $sp) {
                $found = $true
                break
            }
        }
        if ($found) {
            Write-Host "    ✓ 清单包含: $sp" -ForegroundColor Green
        } else {
            # 检查该路径是否实际有文件
            $spCheck = Join-Path $TargetDir $sp
            if (Test-Path $spCheck) {
                Write-Host "    ⚠ 清单缺少: $sp (已打包但不在清单中)" -ForegroundColor Yellow
            }
        }
    }
} else {
    Write-Fail "manifest.json 缺失，增量更新功能将无法正常工作！"
    $allOk = $false
}

# 验证 update_config.json 中的 server_url
$pkgConfigPath = Join-Path $TargetDir "update_config.json"
if (Test-Path $pkgConfigPath) {
    $pkgConfig = Get-Content $pkgConfigPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $serverUrl = $pkgConfig.server_url
    if ($serverUrl) {
        Write-Host "    ✓ CDN地址: $serverUrl" -ForegroundColor Green
    } else {
        Write-Warn "server_url 为空，将使用硬编码默认值"
    }
}

# ── 最终汇总 ──────────────────────────────────────────────────
Write-Host ""
if ($allOk) {
    Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║            打包完成！所有检查通过            ║" -ForegroundColor Green
    Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Green
} else {
    Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Red
    Write-Host "║       打包完成，但存在缺失项，请检查！       ║" -ForegroundColor Red
    Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Red
}
Write-Host ""
Write-Host "  输出路径 : $TargetDir" -ForegroundColor White
Write-Host "  版本号   : $Version" -ForegroundColor White
Write-Host "  总文件数 : $totalFiles 个" -ForegroundColor White
Write-Host "  总大小   : $totalSize MB" -ForegroundColor White
Write-Host ""
Write-Host "  可直接运行: $TargetDir\躺平王服务端.exe" -ForegroundColor Cyan
Write-Host ""

# ── 下一步操作提示 ────────────────────────────────────────────
Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║            发布更新到用户端                   ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Step A: 提交 Git（manifest.json + update_config.json）" -ForegroundColor White
Write-Host "    git add manifest.json update_config.json models/tpwVer.txt" -ForegroundColor Gray
Write-Host "    git commit -m ""v${Version}: 发布更新""" -ForegroundColor Gray
Write-Host "    git push origin master" -ForegroundColor Gray
Write-Host ""
Write-Host "  Step B: 刷新 CDN 缓存（浏览器打开）" -ForegroundColor White
Write-Host "    https://purge.jsdelivr.net/gh/lvpingJava/tpw@master/manifest.json" -ForegroundColor Gray
Write-Host ""
Write-Host "  Step C: 用户端点击「增量更新」即可获取更新" -ForegroundColor White
Write-Host "    仅下载变更文件，无需重新下载完整安装包" -ForegroundColor Gray
Write-Host ""

