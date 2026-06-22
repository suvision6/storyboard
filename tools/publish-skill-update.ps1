[CmdletBinding()]
param(
    [string]$SkillName = "su-fenjingskill-zh",
    [Parameter(Mandatory = $true)]
    [string]$Version,
    [string]$Message,
    [string]$Remote = "origin",
    [switch]$NoPush,
    [switch]$NoSync
)

$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$SkillRoot = Join-Path $RepoRoot ("skills\" + $SkillName)
$SnapshotRoot = Join-Path $RepoRoot ("skill-versions\" + $SkillName)
$SnapshotPath = Join-Path $SnapshotRoot ("v" + $Version)
$VersionFile = Join-Path $SkillRoot "VERSION"
$SkillFile = Join-Path $SkillRoot "SKILL.md"

Push-Location $RepoRoot
try {
    if (-not (Test-Path -LiteralPath $SkillRoot -PathType Container)) {
        throw "Skill source not found: $SkillRoot"
    }
    if (-not (Test-Path -LiteralPath $VersionFile -PathType Leaf)) {
        throw "Missing version file: $VersionFile"
    }
    if (-not (Test-Path -LiteralPath $SkillFile -PathType Leaf)) {
        throw "Missing skill file: $SkillFile"
    }

    $VersionText = (Get-Content -LiteralPath $VersionFile -Raw -Encoding UTF8).Trim()
    if ($VersionText -ne $Version) {
        throw "VERSION file says '$VersionText', but publish requested '$Version'."
    }

    $SkillText = Get-Content -LiteralPath $SkillFile -Raw -Encoding UTF8
    if ($SkillText -notmatch "skill-version:\s*$([regex]::Escape($Version))") {
        throw "SKILL.md version marker does not contain skill-version: $Version."
    }

    $TagName = "$SkillName-v$Version"
    $ExistingLocalTag = git tag --list $TagName
    if ($ExistingLocalTag) {
        throw "Local tag already exists: $TagName"
    }
    $ExistingRemoteTag = git ls-remote --tags $Remote "refs/tags/$TagName"
    if ($ExistingRemoteTag) {
        throw "Remote tag already exists: $TagName"
    }

    if (-not $Message) {
        $Message = "Update $SkillName to v$Version"
    }

    if (Test-Path -LiteralPath $SnapshotPath) {
        throw "Version snapshot already exists and must not be overwritten: $SnapshotPath"
    }
    New-Item -ItemType Directory -Force -Path $SnapshotRoot | Out-Null
    Copy-Item -LiteralPath $SkillRoot -Destination $SnapshotPath -Recurse
    Write-Host "Version snapshot created: $SnapshotPath"

    $PathsToStage = @(
        ".gitignore",
        "VERSIONING.md",
        "tools",
        "skills/$SkillName",
        "skill-versions/$SkillName/v$Version"
    )
    git add -- $PathsToStage

    $Staged = git diff --cached --name-only
    if (-not $Staged) {
        throw "No staged changes to publish."
    }

    git commit -m $Message
    git tag -a $TagName -m "Release $TagName"

    if (-not $NoSync) {
        & (Join-Path $PSScriptRoot "sync-skill.ps1") -SkillName $SkillName
    }

    if (-not $NoPush) {
        $Branch = git branch --show-current
        if (-not $Branch) {
            throw "Cannot determine current branch for push."
        }
        git push $Remote $Branch
        git push $Remote $TagName
    }

    Write-Host "Published $SkillName version $Version as $TagName"
}
finally {
    Pop-Location
}
