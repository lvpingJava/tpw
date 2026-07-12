# =============================================================================
#  躺平王服务端 - 一键自动化打包脚本
#  用法: .\build.ps1
#        .\build.ps1 -TargetDir "D:\test_py\tpw\打包\tpw6.4.9.8"
# =============================================================================
param(
    [string]$TargetDir = "D:\test_py\tpw\打包\tpw6.4.9.7"
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$DistDir = Join-Path $ScriptDir "tpw_server.dist"
$BuildDir = Join-Path $ScriptDir "tpw_server.build"

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

# ── 打印 Banner ────────────────────────────────────────────────
Write-Host ""
Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║       躺平王服务端 - 自动化打包脚本          ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host "  输出目录: $TargetDir" -ForegroundColor Gray
Write-Host ""

# ── Step 1: 清理旧构建 ────────────────────────────────────────
Write-Step "[1/5] 清理旧构建产物..."
$toRemove = @($DistDir, $BuildDir)
foreach ($path in $toRemove) {
    if (Test-Path $path) {
        Remove-Item -Recurse -Force $path -ErrorAction SilentlyContinue
        Write-OK "已删除: $(Split-Path $path -Leaf)"
    }
}

# ── Step 2: Nuitka 打包 ────────────────────────────────────────
Write-Step "[2/5] Nuitka 打包中 (约 3-8 分钟)..."
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

# 执行 Nuitka（直接调用以保留实时控制台输出）
python -m nuitka @nuitkaArgs

if ($LASTEXITCODE -ne 0) {
    Write-Fail "Nuitka 打包失败！退出码: $LASTEXITCODE"
    exit 1
}
Write-OK "Nuitka 打包完成"

# ── Step 3: 准备目标目录 ──────────────────────────────────────
Write-Step "[3/5] 准备目标目录..."
if (Test-Path $TargetDir) {
    Write-Host "  清空已有目录..." -ForegroundColor Gray
    Remove-Item -Recurse -Force $TargetDir -ErrorAction SilentlyContinue
}
New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null
Write-OK "目标目录就绪"

# ── Step 4: 复制 Nuitka 产物 ──────────────────────────────────
Write-Step "[4/5] 复制程序文件..."
# 复制 dist 中所有内容（exe, dll, pyd, 以及 Nuitka 自动包含的子目录）
Copy-Item -Path "$DistDir\*" -Destination $TargetDir -Recurse -Force

# 统计文件数量
$exeCount = (Get-ChildItem -Path $TargetDir -Filter "*.exe").Count
$dllCount = (Get-ChildItem -Path $TargetDir -Filter "*.dll").Count
$pydCount = (Get-ChildItem -Path $TargetDir -Filter "*.pyd").Count
Write-OK "已复制: $exeCount 个 exe, $dllCount 个 dll, $pydCount 个 pyd"

# ── Step 5: 复制资源文件夹 ────────────────────────────────────
Write-Step "[5/5] 复制资源文件..."

# --- 5a. 复制完整资源目录 ---
$resourceDirs = @(
    "手牌",          # 卡牌识别模板 (DmTool.py:891, tpw_server.py:510)
    "快速手牌",      # 快速卡牌模板 (DmTool.py:889)
    "场景",          # 场景图片 (DmTool.py:942)
    "暗月",          # 暗月场景图片
    "models",        # 版本文件/图标/动画 (tpw_server.py:251,284,311,648)
    "配置"           # DMPJ.DLL, DmReg.dll (tpw_server.py:324)
)

foreach ($dir in $resourceDirs) {
    $src = Join-Path $ScriptDir $dir
    $dst = Join-Path $TargetDir $dir
    if (Test-Path $src) {
        Copy-Item -Path $src -Destination $dst -Recurse -Force
        $fileCount = (Get-ChildItem -Path $dst -Recurse -File).Count
        Write-OK "资源目录: $dir ($fileCount 个文件)"
    } else {
        Write-Host "  - 跳过 (不存在): $dir" -ForegroundColor Gray
    }
}

# --- 5b. 复制 OCR 引擎 (matplotlibes/matp.exe + models/) ---
$ocrSrc = Join-Path $ScriptDir "matplotlibes"
$ocrDst = Join-Path $TargetDir "matplotlibes"
if (Test-Path $ocrSrc) {
    # 只复制 exe 和 models 目录，不复制 .py 文件（Nuitka 已处理）
    if (-not (Test-Path $ocrDst)) {
        New-Item -ItemType Directory -Force -Path $ocrDst | Out-Null
    }

    # 复制 matp.exe
    $matpExe = Join-Path $ocrSrc "matp.exe"
    if (Test-Path $matpExe) {
        Copy-Item -Path $matpExe -Destination $ocrDst -Force
        Write-OK "OCR引擎: matp.exe"
    }

    # 复制 models 目录 (ONNX 模型文件)
    $modelsSrc = Join-Path $ocrSrc "models"
    if (Test-Path $modelsSrc) {
        Copy-Item -Path $modelsSrc -Destination $ocrDst -Recurse -Force
        $modelCount = (Get-ChildItem -Path (Join-Path $ocrDst "models") -File).Count
        Write-OK "OCR模型: models/ ($modelCount 个文件)"
    }
}

# --- 5c. 复制原生 DLL (other/ 目录) ---
$otherSrc = Join-Path $ScriptDir "other"
if (Test-Path $otherSrc) {
    # tools_64.dll, op_x64.dll 放到 exe 同级目录
    Get-ChildItem -Path $otherSrc -Filter "*.dll" | ForEach-Object {
        Copy-Item -Path $_.FullName -Destination $TargetDir -Force
        Write-OK "原生DLL: $($_.Name)"
    }

    # tess_model 放到 other\tess_model
    $tessSrc = Join-Path $otherSrc "tess_model"
    if (Test-Path $tessSrc) {
        $tessDst = Join-Path $TargetDir "other\tess_model"
        New-Item -ItemType Directory -Force -Path (Split-Path $tessDst) | Out-Null
        Copy-Item -Path $tessSrc -Destination $tessDst -Recurse -Force
        Write-OK "Tesseract模型: other/tess_model/"
    }
}

# --- 5d. 复制项目根级别资源文件 ---
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

# ── 最终统计 ──────────────────────────────────────────────────
Write-Host ""
Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║            打包完成！                        ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

$totalFiles = (Get-ChildItem -Path $TargetDir -Recurse -File).Count
$totalDirs = (Get-ChildItem -Path $TargetDir -Recurse -Directory).Count
$totalSize = [math]::Round(((Get-ChildItem -Path $TargetDir -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1MB), 2)

Write-Host "  输出路径 : $TargetDir" -ForegroundColor White
Write-Host "  总文件数 : $totalFiles 个" -ForegroundColor White
Write-Host "  子目录数 : $totalDirs 个" -ForegroundColor White
Write-Host "  总大小   : $totalSize MB" -ForegroundColor White
Write-Host ""

# 验证关键文件
Write-Host "  关键文件检查:" -ForegroundColor Gray
$keyFiles = @(
    "躺平王服务端.exe",
    "certifi\cacert.pem",
    "手牌",
    "场景",
    "models\tpwVer.txt",
    "models\tpwlogo.png",
    "matplotlibes\matp.exe",
    "matplotlibes\models\besdet.onnx",
    "配置\DmReg.dll"
)
foreach ($key in $keyFiles) {
    $checkPath = Join-Path $TargetDir $key
    if (Test-Path $checkPath) {
        Write-Host "    ✓ $key" -ForegroundColor Green
    } else {
        Write-Host "    ✗ $key  (缺失!)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "  可直接运行: $TargetDir\躺平王服务端.exe" -ForegroundColor Cyan
Write-Host ""

