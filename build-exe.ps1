  [CmdletBinding()]
  param(
    [string]$Entry = ".\main.py",
    [string]$Name = "ChangePass",
    [string]$Icon = "",
    [switch]$Console,
    [switch]$Offline,
    [switch]$UseSystemEnv,
    [switch]$SkipPsutil = $true
  )
  
  $ErrorActionPreference = 'Stop'
  
  function Exec {
    param(
      [Parameter(Mandatory=$true)][string]$Exe,
      [string[]]$ArgumentList = @(),
      [switch]$IgnoreFail
    )
    Write-Host ">> $Exe $($ArgumentList -join ' ')" -ForegroundColor Cyan
    & $Exe @ArgumentList
    $code = $LASTEXITCODE
    if (-not $IgnoreFail -and $code -ne 0) { throw "Command failed (exit code $code): $Exe" }
  }
  
  # Нормализуем Entry относительно папки скрипта
  if (-not [System.IO.Path]::IsPathRooted($Entry)) { $Entry = Join-Path $PSScriptRoot $Entry }
  if (-not (Test-Path $Entry)) { throw "Entry not found: $Entry" }
  
  # Python
  $py = $null
  foreach ($cand in @("python.exe","py.exe")) {
    $cmd = Get-Command $cand -ErrorAction SilentlyContinue
    if ($cmd) { $py = $cmd.Path; break }
  }
  if (-not $py) { throw "Python not found in PATH" }
  
  # Окружение
  if ($UseSystemEnv) {
    $venvPy = $py
  } else {
    $venvPy = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
    if (-not (Test-Path $venvPy)) {
      if ($Offline) { throw "Offline + no venv. Создайте .venv заранее." }
      Exec -Exe $py -ArgumentList @("-m","venv",".venv")
    }
    if (-not $Offline) {
      Exec -Exe $venvPy -ArgumentList @("-m","pip","install","-U","pip","setuptools","wheel") -IgnoreFail
    }
  }
  
  function Install-RequiredPackages {
    param([string[]]$Pkgs)
    if ($Offline) {
      Write-Host "Offline: пропуск установки пакетов." -ForegroundColor Yellow
      return
    }
    $pipInstallArgs = @("-m","pip","install") + $Pkgs
    Exec -Exe $venvPy -ArgumentList $pipInstallArgs
  }
  
  # Пакеты
  $packages = @("pyinstaller","pyqt5","requests")
  if (-not $SkipPsutil) { $packages += "psutil" }
  Install-RequiredPackages -Pkgs $packages
  
  # Проверки импортов
  Exec -Exe $venvPy -ArgumentList @("-c","import PyInstaller")
  try { Exec -Exe $venvPy -ArgumentList @("-c","import requests") } catch { throw "requests не найден. Установите его и пересоберите." }
  if (-not $SkipPsutil) {
    try { Exec -Exe $venvPy -ArgumentList @("-c","import psutil") } catch { throw "psutil не найден. Установите или включите -SkipPsutil." }
  }
  
  # Компиляция Qt-ресурсов (если есть resources.qrc)
  $qrc = Join-Path $PSScriptRoot "resources.qrc"
  if (Test-Path $qrc) {
    $outRc = Join-Path $PSScriptRoot "resources_rc.py"
    Exec -Exe $venvPy -ArgumentList @("-m","PyQt5.pyrcc_main","-o",$outRc,$qrc)
    Write-Host "Qt resources compiled: resources_rc.py" -ForegroundColor Green
  } else {
    Write-Host "resources.qrc not found, skipping Qt resources." -ForegroundColor Yellow
  }
  
  # Пути вывода
  $distDir  = Join-Path $PSScriptRoot "dist"
  $buildDir = Join-Path $PSScriptRoot "build"
  $specDir  = $PSScriptRoot
  
  # Аргументы PyInstaller — всегда один файл
  $piArgs = @(
    "-m","PyInstaller",
    "--name",$Name,
    "--onefile",
    "--optimize","2",
    "--distpath",$distDir,
    "--workpath",$buildDir,
    "--specpath",$specDir
  )
  if (-not $Console) { $piArgs += "--noconsole" }
  
  # Иконка exe (.ico обязателен)
  if ($Icon -and (Test-Path $Icon)) {
    $piArgs += @("--icon",(Resolve-Path $Icon).Path)
  } else {
    $autoIco = Join-Path $PSScriptRoot "assets\lock.ico"
    if (Test-Path $autoIco) {
      $piArgs += @("--icon",(Resolve-Path $autoIco).Path)
      Write-Host "Using exe icon: assets\lock.ico" -ForegroundColor Cyan
    } else {
      Write-Host "ICO for exe not found. Place assets\lock.ico or pass -Icon path to .ico." -ForegroundColor Yellow
    }
  }
  
  # Данные: каталог assets (для runtime-иконок и др.)
  $assetsDir = Join-Path $PSScriptRoot "assets"
  if (Test-Path $assetsDir) {
    $piArgs += @("--add-data","$assetsDir;assets")
  }
  
  # Скрытые импорты
  $piArgs += @(
    "--hidden-import","PyQt5",
    "--hidden-import","PyQt5.QtCore",
    "--hidden-import","PyQt5.QtGui",
    "--hidden-import","PyQt5.QtWidgets",
    "--hidden-import","sip",
    "--hidden-import","requests",
    "--collect-all","PyQt5",
    "--collect-submodules","requests"
  )
  
  # Не используем --strip на Windows
  if ($env:OS -notlike "*Windows*") { $piArgs += "--strip" }
  
  # Entry
  $piArgs += (Resolve-Path $Entry).Path
  
  Write-Host "Building..." -ForegroundColor Green
  Exec -Exe $venvPy -ArgumentList $piArgs
  
  # Результат (onefile)
  $exe = Join-Path $distDir "$Name.exe"
  if (-not (Test-Path $exe)) {
    $found = Get-ChildItem -Path $distDir -Filter "*.exe" -File -Recurse | Select-Object -First 1
    if ($found) { $exe = $found.FullName }
  }
  if (-not (Test-Path $exe)) { throw "EXE not found (dist: $distDir)" }
  
  Write-Host "Done: $exe" -ForegroundColor Green