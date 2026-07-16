# =============================================================================
#  躺平王服务端 - 一键自动化打包脚本（集成增量更新系统）v3.0
#
#  用法:
#    .\build.ps1                                    # 从 update_config.json 读取版本
#    .\build.ps1 -Version "6.5.0.0"                 # 指定版本号，自动推导目标目录
#    .\build.ps1 -Version "6.5.0.0" -SkipManifest   # 跳过清单生成（仅重新打包）
#    .\build.ps1 -Version "6.5.0.0" -SkipNuitka     # 跳过编译（仅更新资源+清单）
#    .\build.ps1 -Version "6.5.0.0" -CreateZip      # 打包后自动创建 ZIP 分发包
#    .\build.ps1 -Version "6.5.0.0" -QuickUpdate    # 快捷模式: 跳过编译+自动ZIP (资源小更新用)
#    .\build.ps1 -Version "6.5.0.0" -QuickUpdate -AutoTag  # ★ 一键发布: 打包+ZIP+自动Git提交推送+创建标签
#    .\build.ps1 -Version "6.5.0.0" -Changelog "更新手牌数据"  # 附带更新日志
#    .\build.ps1 -TargetDir "D:\test_py\tpw\打包\tpw6.5.0.0"  # 手动指定目标目录
#    .\build.ps1 -Version "6.5.0.0" -DryRun          # 试运行: 仅生成清单不打包
#
#  完整流程: 更新版本 → 生成清单 → Nuitka编译 → 复制资源 → 验证 → ZIP打包 → [AutoTag: Git提交推送+创建标签]
# =============================================================================
param(
    [string]$Version = "",                          # 版本号，如 "6.5.0.0"
    [string]$TargetDir = "",                        # 输出目录（可从 Version 自动推导）
    [string]$Changelog = "",                        # 更新日志内容（写入 update_config.json 和 manifest.json）
    [switch]$SkipManifest = $false,                 # 跳过清单生成步骤
    [switch]$SkipNuitka = $false,                   # 跳过 Nuitka 编译（仅更新资源文件）
    [switch]$CreateZip = $false,                    # 打包后自动创建 ZIP 分发包
    [switch]$QuickUpdate = $false,                  # 快捷模式: 跳过编译 + 自动ZIP（等同于 -SkipNuitka -CreateZip）
    [switch]$DryRun = $false,                       # 试运行：仅生成清单和配置，不真正打包（用于预览）
    [switch]$AutoTag = $false                       # 自动提交、推送 master 并创建/推送版本标签 v{Version}
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$DistDir = Join-Path $ScriptDir "tpw_server.dist"
$BuildDir = Join-Path $ScriptDir "tpw_server.build"
$ConfigPath = Join-Path $ScriptDir "update_config.json"
$VerFilePath = Join-Path $ScriptDir "models\tpwVer.txt"

# ── QuickUpdate 快捷模式 ──
if ($QuickUpdate) { $SkipNuitka = $true; $CreateZip = $true }
if ($DryRun)     { Write-Warn "试运行模式: 仅生成清单和配置，不进行实际打包"; $totalSteps = 1 }

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
Write-Host "║     躺平王服务端 - 自动化打包脚本 v3.0       ║" -ForegroundColor Cyan
Write-Host "║     已集成增量更新 + 自动ZIP分发              ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host "  版本号  : $Version" -ForegroundColor White
Write-Host "  输出目录: $TargetDir" -ForegroundColor Gray
if ($SkipNuitka)   { Write-Host "  跳过编译: 是 (仅更新资源)" -ForegroundColor Magenta }
if ($CreateZip)    { Write-Host "  自动ZIP: 是" -ForegroundColor Magenta }
if ($QuickUpdate)  { Write-Host "  模式: 快捷更新 (跳过编译 + 自动ZIP)" -ForegroundColor Magenta }
if ($AutoTag)      { Write-Host "  自动发布: 是 (提交→推送→创建标签)" -ForegroundColor Magenta }
if ($DryRun)       { Write-Host "  试运行: 是 (不执行打包)" -ForegroundColor Magenta }
if ($Changelog)    { Write-Host "  更新日志: $Changelog" -ForegroundColor Gray }
Write-Host ""
$totalSteps = 7

# =====================================================================
#  Step 0: 打包前准备（版本号 + 清单生成）
# =====================================================================
if (-not $SkipManifest) {
    Write-Step "[0/7] 打包前准备..."

    # 0a. 更新 update_config.json 中的版本号
    $config.version = $Version
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($ConfigPath, ($config | ConvertTo-Json -Depth 10), $utf8NoBom)
    Write-OK "update_config.json 版本 → $Version"

    # 0b. 更新 models/tpwVer.txt（旧版本号文件，保持兼容）
    if (Test-Path (Split-Path $VerFilePath)) {
        [System.IO.File]::WriteAllText($VerFilePath, $Version, (New-Object System.Text.UTF8Encoding $false))
        Write-OK "models/tpwVer.txt 版本 → $Version"
    } else {
        Write-Warn "models/tpwVer.txt 目录不存在，跳过"
    }

    # 0b2. 更新 server_url 使用版本 tag（@v{version} 无 CDN 缓存问题）
    $config.server_url = "https://cdn.jsdelivr.net/gh/lvpingJava/tpw@v$Version"
    # 0b3. 更新 changelog（如果指定）
    if ($Changelog) {
        $config.changelog = $Changelog
    }
    [System.IO.File]::WriteAllText($ConfigPath, ($config | ConvertTo-Json -Depth 10), $utf8NoBom)
    Write-OK "server_url → @v$Version"
    if ($Changelog) { Write-OK "changelog → $Changelog" }

    # 0c. 生成增量更新清单 (manifest.json)
    Write-Info "正在生成 manifest.json ..."
    $pythonExe = Join-Path $ScriptDir ".venv\Scripts\python.exe"
    # 尝试多个可能的 Python 路径
    if (-not (Test-Path $pythonExe)) {
        $pythonExe = Get-Command python -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source
    }

    if (-not $pythonExe -or -not (Test-Path $pythonExe)) {
        Write-Fail "Python 未找到！请先激活虚拟环境: .\.venv\Scripts\Activate.ps1"
        Write-Info "或确保 python 在系统 PATH 中"
        exit 1
    }

    $builderPy = Join-Path $ScriptDir "incremental_update\builder.py"
    $builderArgs = @($builderPy, "--version", $Version, "--config", $ConfigPath)
    if ($Changelog) {
        $builderArgs += "--changelog"
        $builderArgs += $Changelog
    }
    $manifestResult = & $pythonExe @builderArgs 2>&1
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
    Write-Step "[0/$totalSteps] 跳过打包前准备 (--SkipManifest)"
}

# =====================================================================
#  Step 1: 清理旧构建产物
# =====================================================================
Write-Step "[1/$totalSteps] 清理旧构建产物..."
$toRemove = @($DistDir, $BuildDir)
foreach ($path in $toRemove) {
    if (Test-Path $path) {
        Remove-Item -Recurse -Force $path -ErrorAction SilentlyContinue
        Write-OK "已删除: $(Split-Path $path -Leaf)"
    }
}

# =====================================================================
#  Step 2: Nuitka 编译打包（可跳过）
# =====================================================================
if (-not $SkipNuitka) {
    Write-Step "[2/$totalSteps] Nuitka 编译打包中 (约 3-8 分钟)..."
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
        Write-Warn "提示: 如果用 --SkipNuitka 跳过编译，请确保目标目录已有 exe"
        exit 1
    }
    Write-OK "Nuitka 编译完成"
} else {
    Write-Step "[2/$totalSteps] 跳过 Nuitka 编译 (--SkipNuitka)"
}

# =====================================================================
#  Step 3: 准备目标目录
# =====================================================================
Write-Step "[3/$totalSteps] 准备目标目录..."
if (-not $SkipNuitka) {
    # 全量打包：清空重建
    if (Test-Path $TargetDir) {
        Write-Info "清空已有目录..."
        Remove-Item -Recurse -Force $TargetDir -ErrorAction SilentlyContinue
    }
    New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null
} else {
    # 资源更新：保留已有 exe/dll/pyd，仅覆盖资源
    if (-not (Test-Path $TargetDir)) {
        New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null
        Write-Warn "目标目录不存在已创建，但缺少 exe 文件！请先执行完整打包。"
    } else {
        Write-Info "保留已有编译产物，仅更新资源文件"
    }
}
Write-OK "目标目录就绪"

# =====================================================================
#  Step 4: 复制 Nuitka 编译产物（跳过则跳过）
# =====================================================================
if (-not $SkipNuitka) {
    Write-Step "[4/$totalSteps] 复制程序文件..."
    Copy-Item -Path "$DistDir\*" -Destination $TargetDir -Recurse -Force

    $exeCount = (Get-ChildItem -Path $TargetDir -Filter "*.exe").Count
    $dllCount = (Get-ChildItem -Path $TargetDir -Filter "*.dll").Count
    $pydCount = (Get-ChildItem -Path $TargetDir -Filter "*.pyd").Count
    Write-OK "已复制: $exeCount 个 exe, $dllCount 个 dll, $pydCount 个 pyd"
} else {
    Write-Step "[4/$totalSteps] 跳过程序文件复制 (--SkipNuitka)"
}

# =====================================================================
#  Step 5: 复制资源文件 + 增量更新相关文件
# =====================================================================
Write-Step "[5/$totalSteps] 复制资源文件..."

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
$manifestSrc = Join-Path $ScriptDir "manifest.json"
if (Test-Path $manifestSrc) {
    Copy-Item -Path $manifestSrc -Destination $TargetDir -Force
    Write-OK "manifest.json (版本 $Version)"
} else {
    Write-Fail "manifest.json 不存在！请先运行 builder.py 生成清单"
}

$configSrc = Join-Path $ScriptDir "update_config.json"
if (Test-Path $configSrc) {
    Copy-Item -Path $configSrc -Destination $TargetDir -Force
    Write-OK "update_config.json (服务器地址配置)"
}

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
Write-Step "[6/$totalSteps] 打包后验证..."

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
        if ($SkipNuitka -and $item.Path -eq "躺平王服务端.exe") {
            Write-Host "    ⚠ $($item.Path)  跳过 (--SkipNuitka 模式)" -ForegroundColor Yellow
        } else {
            Write-Host "    ✗ $($item.Path)  缺失! [$($item.Desc)]" -ForegroundColor Red
            $allOk = $false
        }
    }
}

# ── 增量更新兼容性验证 ──
Write-Host ""
Write-Host "  增量更新兼容性检查:" -ForegroundColor Gray

$pkgManifestPath = Join-Path $TargetDir "manifest.json"
if (Test-Path $pkgManifestPath) {
    $pkgManifest = Get-Content $pkgManifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $pkgVersion = $pkgManifest.version
    $pkgFileCount = ($pkgManifest.files | Get-Member -MemberType NoteProperty).Count

    Write-Host "    ✓ 清单版本: $pkgVersion" -ForegroundColor Green
    Write-Host "    ✓ 清单文件数: $pkgFileCount" -ForegroundColor Green

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

# =====================================================================
#  Step 7: 自动创建 ZIP 分发包（可选）
# =====================================================================
if ($CreateZip) {
    Write-Step "[7/$totalSteps] 创建 ZIP 分发包..."
    $zipPath = "D:\test_py\tpw\打包\tpw${Version}.zip"
    try {
        if (Test-Path $zipPath) {
            Remove-Item $zipPath -Force
        }
        Compress-Archive -Path "$TargetDir\*" -DestinationPath $zipPath -CompressionLevel Optimal
        $zipSizeMB = [math]::Round(((Get-Item $zipPath).Length / 1MB), 2)
        Write-OK "ZIP 分发包已创建: $zipPath ($zipSizeMB MB)"
        Write-Host "  首次用户下载此 ZIP 解压即可使用" -ForegroundColor Cyan
    } catch {
        Write-Warn "ZIP 创建失败: $_"
        Write-Info "请手动压缩: $TargetDir"
    }
}

# ── 下一步操作提示 ────────────────────────────────────────────
Write-Host ""
Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║            发布更新到用户端                   ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

if ($AutoTag) {
    # ==================================================================
    #  Step 8: 自动 Git 提交 + 推送 + 创建标签（-AutoTag）
    # ==================================================================
    Write-Step "[8/8] 自动 Git 发布 (提交 → 推送 → 创建标签 v${Version})..."

    # git 的正常进度信息写入 stderr，会导致 ErrorActionPreference="Stop" 误判。
    # 此段临时切换为 Continue 模式。
    $prevEAP = $ErrorActionPreference
    $ErrorActionPreference = "Continue"

    try {
        # 8a. 检查 Git 用户配置
        $gitName = (git config user.name 2>$null) -replace '\s+$',''
        $gitEmail = (git config user.email 2>$null) -replace '\s+$',''
        if (-not $gitName -or -not $gitEmail) {
            Write-Fail "Git 用户信息未配置！请先执行:"
            Write-Info '  git config --global user.name "Your Name"'
            Write-Info '  git config --global user.email "your@email.com"'
            exit 1
        }
        Write-OK "Git 用户: $gitName <$gitEmail>"

        # 8b. 检查是否有未提交的变更
        $gitStatus = git status --porcelain 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Fail "Git 状态检查失败！当前目录可能不是 Git 仓库"
            exit 1
        }

        $changedFiles = @($gitStatus | Where-Object { $_ -match '^\s*[MADRCU?]' })
        if ($changedFiles.Count -eq 0) {
            Write-Info "没有变更的文件，跳过提交步骤"
        } else {
            Write-Info "发现 $($changedFiles.Count) 个变更文件:"
            foreach ($f in $changedFiles) { Write-Info "    $f" }

            # 8c. 暂存关键文件
            Write-Info "正在 git add ..."
            git add manifest.json update_config.json models/tpwVer.txt 2>&1 | Out-Null
            if ($LASTEXITCODE -ne 0) {
                Write-Warn "git add 部分文件失败，尝试添加所有变更..."
                git add -A 2>&1 | Out-Null
            }

            # 8d. 提交
            $commitMsg = "v${Version}: 发布更新"
            if ($Changelog) { $commitMsg += " - $Changelog" }
            Write-Info "正在提交: $commitMsg"
            git commit -m $commitMsg 2>&1 | Out-Null
            if ($LASTEXITCODE -ne 0) {
                Write-Warn "git commit 可能没有新内容或已提交"
            } else {
                Write-OK "提交成功"
            }
        }

        # 8e. 推送到 GitHub
        Write-Info "正在推送 master 到 GitHub ..."
        $pushResult = git push origin master 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Fail "Git 推送失败！请检查网络和仓库权限"
            Write-Info "$pushResult"
            Write-Warn "你可以稍后手动执行: git push origin master"
        } else {
            Write-OK "master 已推送到 GitHub"
        }

        # 8f. 创建并推送版本标签 (★ 关键: jsDelivr CDN 依赖此标签)
        Write-Info "正在创建版本标签 v${Version} ..."
        $existingTag = git tag -l "v${Version}" 2>$null
        if ($existingTag) {
            Write-Warn "标签 v${Version} 已存在，删除旧标签后重新创建..."
            git tag -d "v${Version}" 2>&1 | Out-Null
            git push origin ":refs/tags/v${Version}" 2>&1 | Out-Null
        }

        git tag "v${Version}" 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-Fail "创建标签 v${Version} 失败！"
        } else {
            Write-OK "标签 v${Version} 已创建"
            Write-Info "正在推送标签 v${Version} 到 GitHub ..."
            $tagPushResult = git push origin "v${Version}" 2>&1
            if ($LASTEXITCODE -ne 0) {
                Write-Fail "标签推送失败！"
                Write-Info "$tagPushResult"
                Write-Warn "你可以稍后手动执行: git push origin v${Version}"
            } else {
                Write-OK "标签 v${Version} 已推送到 GitHub"
            }
        }
    } finally {
        $ErrorActionPreference = $prevEAP
    }

    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║         一键发布完成！                       ║" -ForegroundColor Green
    Write-Host "╚══════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "  CDN 地址: https://cdn.jsdelivr.net/gh/lvpingJava/tpw@v${Version}" -ForegroundColor Cyan
    Write-Host "  (jsDelivr 约 1-2 分钟后同步新标签，用户即可增量更新)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  用户端更新体验:" -ForegroundColor White
    Write-Host "    已有用户 → 点击「增量更新」仅下载变更文件" -ForegroundColor Gray
    if ($CreateZip) {
        Write-Host "    首次用户 → 下载: D:\test_py\tpw\打包\tpw${Version}.zip" -ForegroundColor Gray
    }
} else {
    # ── 未启用 AutoTag：显示手动操作提示 ──
    Write-Host "  Step A: 提交 Git 并推送 tag（tag 无 CDN 缓存问题）" -ForegroundColor White
    Write-Host "    git add manifest.json update_config.json models/tpwVer.txt" -ForegroundColor Gray
    Write-Host "    git commit -m ""v${Version}: 发布更新""" -ForegroundColor Gray
    Write-Host "    git push origin master" -ForegroundColor Gray
    Write-Host "    git tag v${Version} ; git push origin v${Version}" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  ★ 提示: 下次使用 -AutoTag 一键完成以上全部步骤" -ForegroundColor Yellow
    Write-Host "    .\build.ps1 -Version ""${Version}"" -QuickUpdate -AutoTag" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Step B: 分发完整安装包给首次用户" -ForegroundColor White
    if ($CreateZip) {
        Write-Host "    ZIP 已生成: D:\test_py\tpw\打包\tpw${Version}.zip" -ForegroundColor Gray
    } else {
        Write-Host "    手动压缩: $TargetDir  (或下次使用 -CreateZip 自动创建)" -ForegroundColor Gray
    }
    Write-Host ""
    Write-Host "  Step C: 已有用户点击「增量更新」仅下载变更文件" -ForegroundColor White
    Write-Host "    无需重新下载完整安装包" -ForegroundColor Gray
    Write-Host ""
}

