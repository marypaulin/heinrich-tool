# Installs or updates Heinrich Tool on Windows: git, uv, repository, environment, shortcuts.
#
# First run (nothing on the machine yet), pasted into PowerShell:
#   irm https://raw.githubusercontent.com/marypaulin/heinrich-tool/main/scripts/setup.ps1 | iex
# Every later run: update.bat in the project root.
#
# Written for Windows PowerShell 5.1, which every Windows machine has. Saved as
# UTF-8 with BOM: without it, 5.1 reads the file as ANSI and garbles the umlauts.

# Everything runs inside a function because `irm | iex` executes in Max's own
# session: `exit` would close his window, and script-level variables and
# preferences would leak into it.
function Install-HeinrichTool {
    $ErrorActionPreference = 'Stop'

    $repoUrl = 'https://github.com/marypaulin/heinrich-tool.git'
    $folderName = 'heinrich-tool'

    # — Helpers ————————————————————————————————————————————————

    function Write-Step([string]$Text) {
        Write-Host ''
        Write-Host "==> $Text" -ForegroundColor Cyan
    }

    # Native programs report failure only through the exit code; PowerShell does
    # not turn that into an error by itself.
    function Invoke-Native([string]$Failure, [scriptblock]$Command) {
        & $Command
        if ($LASTEXITCODE -ne 0) { throw $Failure }
    }

    # A freshly installed program is on the stored PATH, but this window still
    # holds the copy it started with.
    function Update-SessionPath {
        $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' +
                    [Environment]::GetEnvironmentVariable('Path', 'User')
    }

    function Test-Command([string]$Name) {
        [bool](Get-Command $Name -ErrorAction SilentlyContinue)
    }

    function Install-WithWinget([string]$Command, [string]$PackageId, [string]$Label) {
        if (Test-Command $Command) { return }
        Write-Step "$Label wird installiert"
        if (-not (Test-Command 'winget')) {
            throw "winget fehlt. Bitte im Microsoft Store den 'App-Installer' installieren und das Skript erneut starten."
        }
        Invoke-Native "$Label konnte nicht installiert werden." {
            winget install --id $PackageId --exact --source winget `
                --accept-package-agreements --accept-source-agreements
        }
        Update-SessionPath
        if (-not (Test-Command $Command)) {
            throw "$Label wurde installiert, wird aber nicht gefunden. Bitte das Fenster schließen und das Skript erneut starten."
        }
    }

    # .venv and .git break when OneDrive syncs them between machines. The data
    # (data folder, config, template) stays in OneDrive; only the program is local.
    function Test-InOneDrive([string]$Path) {
        $full = [IO.Path]::GetFullPath($Path).TrimEnd('\') + '\'
        foreach ($root in @($env:OneDrive, $env:OneDriveCommercial, $env:OneDriveConsumer)) {
            if (-not $root) { continue }
            $rootFull = [IO.Path]::GetFullPath($root).TrimEnd('\') + '\'
            if ($full.StartsWith($rootFull, [StringComparison]::OrdinalIgnoreCase)) { return $true }
        }
        return $false
    }

    function Select-ParentFolder {
        Add-Type -AssemblyName System.Windows.Forms
        $dialog = New-Object System.Windows.Forms.FolderBrowserDialog
        $dialog.Description = "Ordner wählen, in dem Heinrich Tool installiert wird. Darin wird der Unterordner '$folderName' angelegt."
        $dialog.SelectedPath = $env:USERPROFILE
        # A topmost owner window, otherwise the dialog tends to open behind the
        # PowerShell window and the script seems to hang.
        $owner = New-Object System.Windows.Forms.Form -Property @{ TopMost = $true }
        try {
            if ($dialog.ShowDialog($owner) -ne [System.Windows.Forms.DialogResult]::OK) { return $null }
            return $dialog.SelectedPath
        }
        finally {
            $owner.Dispose()
            $dialog.Dispose()
        }
    }

    # On later runs the script sits in <project>\scripts; via `irm | iex` it has
    # no location at all.
    function Get-InstalledRoot {
        if (-not $PSScriptRoot) { return $null }
        $root = Split-Path $PSScriptRoot -Parent
        if (Test-Path (Join-Path $root '.git')) { return $root }
        return $null
    }

    function New-Shortcut([string]$Path, [string]$Target, [string]$Arguments, [string]$WorkingDirectory, [string]$Icon) {
        $shell = New-Object -ComObject WScript.Shell
        $link = $shell.CreateShortcut($Path)
        $link.TargetPath = $Target
        $link.Arguments = $Arguments
        $link.WorkingDirectory = $WorkingDirectory
        $link.IconLocation = $Icon
        $link.Save()
    }

    # — Steps ——————————————————————————————————————————————————

    function Get-ProjectRoot {
        $root = Get-InstalledRoot
        if ($root) { return $root }

        Write-Step 'Installationsort wählen'
        $parent = Select-ParentFolder
        if (-not $parent) { throw 'Kein Ordner gewählt. Es wurde nichts installiert.' }
        if (Test-InOneDrive $parent) {
            throw "Der Ordner liegt in OneDrive: $parent`nDas Programm muss lokal liegen, z. B. unter $env:USERPROFILE. Es wurde nichts installiert."
        }
        return Join-Path $parent $folderName
    }

    function Sync-Repository([string]$Root) {
        if (Test-Path (Join-Path $Root '.git')) {
            Write-Step 'Neueste Version wird geholt'
            # --ff-only and no reset: a local change must never be discarded
            # silently, so the update stops and leaves everything as it is.
            $changes = git -C $Root status --porcelain --untracked-files=no
            if ($changes) {
                throw "Im Programmordner wurden Dateien geändert:`n$($changes -join "`n")`nDas Update wurde abgebrochen, es wurde nichts verändert. Bitte bei Pau melden."
            }
            Invoke-Native 'Das Update konnte nicht geholt werden. Besteht eine Internetverbindung? Es wurde nichts verändert.' {
                git -C $Root pull --ff-only
            }
            return
        }
        if (Test-Path $Root) {
            throw "Der Ordner $Root existiert schon, ist aber keine Installation von Heinrich Tool. Bitte einen anderen Ort wählen oder den Ordner entfernen."
        }
        Write-Step "Heinrich Tool wird nach $Root geladen"
        Invoke-Native 'Heinrich Tool konnte nicht heruntergeladen werden. Besteht eine Internetverbindung?' {
            git clone $repoUrl $Root
        }
    }

    function Sync-Environment([string]$Root) {
        Write-Step 'Python und Bibliotheken werden eingerichtet'
        Invoke-Native 'Python und Bibliotheken konnten nicht eingerichtet werden.' {
            uv --directory $Root sync
        }
    }

    # Rewritten on every run so that changed paths or icons arrive with an update.
    function Write-Shortcuts([string]$Root) {
        Write-Step 'Verknüpfungen werden angelegt'
        $icon = Join-Path $Root 'src\heinrich_tool\assets\icon.ico'
        $wscript = Join-Path $env:WINDIR 'System32\wscript.exe'
        $launcher = '"' + (Join-Path $Root 'scripts\app_windows.vbs') + '"'
        $update = Join-Path $Root 'update.bat'
        # Folder lookups instead of fixed paths: OneDrive often redirects the desktop.
        $desktop = [Environment]::GetFolderPath('Desktop')
        $programs = [Environment]::GetFolderPath('Programs')

        New-Shortcut (Join-Path $desktop 'Heinrich Tool.lnk') $wscript $launcher $Root $icon
        New-Shortcut (Join-Path $programs 'Heinrich Tool.lnk') $wscript $launcher $Root $icon
        New-Shortcut (Join-Path $programs 'Heinrich Tool aktualisieren.lnk') $update '' $Root $icon
    }

    # — Main ———————————————————————————————————————————————————

    try {
        Install-WithWinget 'git' 'Git.Git' 'Git'
        Install-WithWinget 'uv' 'astral-sh.uv' 'uv'
        $root = Get-ProjectRoot
        Sync-Repository $root
        Sync-Environment $root
        Write-Shortcuts $root
        Write-Host ''
        Write-Host 'Fertig. Heinrich Tool startet über die Verknüpfung auf dem Desktop.' -ForegroundColor Green
    }
    catch {
        Write-Host ''
        # Only this script uses `throw`, and its messages are written for Max.
        # Anything else is a raw PowerShell error he cannot act on.
        if (-not $_.Exception.WasThrownFromThrowStatement) {
            Write-Host 'Unerwarteter Fehler, bitte bei Pau melden:' -ForegroundColor Red
        }
        Write-Host $_.Exception.Message -ForegroundColor Red
    }
}

Install-HeinrichTool
