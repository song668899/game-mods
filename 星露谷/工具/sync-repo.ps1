# 单向同步：D:\星露谷MOD 工作区 → D:\game-mods\星露谷（镜像，只进仓库的内容）
# 用法：powershell -ExecutionPolicy Bypass -File 工具\sync-repo.ps1
# 方向固定为工作区 → 仓库，绝不反向；压缩包/组装暂存不入库。
$ErrorActionPreference = 'Stop'
$src = 'D:\星露谷MOD'
$dst = 'D:\game-mods\星露谷'

if (-not (Test-Path $src)) { throw "源不存在: $src" }
New-Item -ItemType Directory -Path $dst -Force | Out-Null

$common = @('/MIR', '/NFL', '/NDL', '/NJH', '/NP', '/R:1', '/W:1')

robocopy "$src\文档" "$dst\文档" @common /XD stage 输出 __pycache__ | Out-Null
if ($LASTEXITCODE -ge 8) { throw "robocopy 文档 失败: $LASTEXITCODE" }

robocopy "$src\工具" "$dst\工具" @common /XD __pycache__ | Out-Null
if ($LASTEXITCODE -ge 8) { throw "robocopy 工具 失败: $LASTEXITCODE" }

robocopy "$src\发布" "$dst\发布" @common /XD stage 输出 __pycache__ | Out-Null
if ($LASTEXITCODE -ge 8) { throw "robocopy 发布 失败: $LASTEXITCODE" }

# MOD上传：只同步说明类文件，压缩包与产物一律不入库
robocopy "$src\MOD上传" "$dst\MOD上传" @common /XF *.zip *.7z *.rar | Out-Null
if ($LASTEXITCODE -ge 8) { throw "robocopy MOD上传 失败: $LASTEXITCODE" }

Copy-Item "$src\README.md" "$dst\README.md" -Force
Write-Host "同步完成 → $dst"
