param(
    [string]$SkillName = "su-fenjingskill-zh",
    [Parameter(Mandatory = $true)]
    [string]$Version,
    [string]$Message,
    [string]$Remote = "origin",
    [switch]$NoPush
)

$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Push-Location $RepoRoot
try {
    $TagName = "$SkillName-v$Version"
    $SnapshotPath = Join-Path $RepoRoot ("skill-versions\" + $SkillName + "\v" + $Version)
    if (-not (Test-Path -LiteralPath $SnapshotPath -PathType Container)) {
        throw "Missing required version snapshot: $SnapshotPath"
    }

    $ExistingTag = git tag --list $TagName
    if ($ExistingTag) {
        throw "Tag already exists: $TagName"
    }

    $Dirty = git status --porcelain
    if ($Dirty) {
        throw "Working tree has uncommitted changes. Commit before tagging $TagName."
    }

    if (-not $Message) {
        $Message = "Release $TagName"
    }

    git tag -a $TagName -m $Message
    Write-Host "Created release tag: $TagName"

    if (-not $NoPush) {
        $Branch = git branch --show-current
        if (-not $Branch) {
            throw "Cannot determine current branch for push."
        }
        git push $Remote $Branch
        git push $Remote $TagName
        Write-Host "Pushed $Branch and $TagName to $Remote"
    }
}
finally {
    Pop-Location
}
