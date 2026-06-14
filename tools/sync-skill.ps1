[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$SkillName = "su-fenjingskill-zh",
    [string]$TargetRoot = (Join-Path $HOME ".codex\skills"),
    [switch]$NoBackup
)

$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$Source = Join-Path $RepoRoot ("skills\" + $SkillName)
$Target = Join-Path $TargetRoot $SkillName

if (-not (Test-Path -LiteralPath $Source -PathType Container)) {
    throw "Skill source not found: $Source"
}

if (-not (Test-Path -LiteralPath $TargetRoot -PathType Container)) {
    New-Item -ItemType Directory -Force -Path $TargetRoot | Out-Null
}

if ($PSCmdlet.ShouldProcess($Target, "Replace installed skill from $Source")) {
    if ((Test-Path -LiteralPath $Target -PathType Container) -and -not $NoBackup) {
        $Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
        $BackupRoot = Join-Path $TargetRoot "_backups"
        $BackupPath = Join-Path $BackupRoot "$SkillName-$Timestamp"
        New-Item -ItemType Directory -Force -Path $BackupRoot | Out-Null
        Copy-Item -LiteralPath $Target -Destination $BackupPath -Recurse -Force
        Write-Host "Backup created: $BackupPath"
    }

    if (Test-Path -LiteralPath $Target -PathType Container) {
        Remove-Item -LiteralPath $Target -Recurse -Force
    }

    Copy-Item -LiteralPath $Source -Destination $Target -Recurse -Force
    Write-Host "Synced $SkillName to $Target"
}
