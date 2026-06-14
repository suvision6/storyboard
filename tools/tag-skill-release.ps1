param(
    [string]$SkillName = "su-fenjingskill-zh",
    [Parameter(Mandatory = $true)]
    [string]$Version,
    [string]$Message
)

$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Push-Location $RepoRoot
try {
    $TagName = "$SkillName-v$Version"
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
}
finally {
    Pop-Location
}
