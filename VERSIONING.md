# Skill Versioning Workflow

This repository is the source of truth for Codex skills.

## Daily update flow

1. Edit the skill under `skills/su-fenjingskill-zh`.
2. Increment the version in `skills/su-fenjingskill-zh/VERSION` and in the `version` field / version section of `SKILL.md`.
3. Validate or test the skill.
4. Run `tools\publish-skill-update.cmd -Version <new-version> -Message "<summary>"`.

The publish command stages the skill files, commits the update, creates a version tag, syncs the installed Codex skill, and pushes both the commit and tag to GitHub.

## Save a stable version

Current version:

```powershell
2.1
```

Stable versions are preserved as Git tags named:

```text
su-fenjingskill-zh-v<version>
```

For example, version `2.0` is preserved as `su-fenjingskill-zh-v2.0`.

## Restore an old version

To restore a tagged version into the working tree:

```powershell
git checkout su-fenjingskill-zh-v1.0.0 -- skills/su-fenjingskill-zh
.\tools\sync-skill.cmd
```

Then run `tools\publish-skill-update.cmd -Version <new-version> -Message "Restore from <old-version>"` if you want it to become the current version again.

## Sync behavior

`tools/sync-skill.cmd` replaces the installed Codex skill at:

```text
C:\Users\苏苏\.codex\skills\su-fenjingskill-zh
```

Before replacement, it copies the existing installed version to:

```text
C:\Users\苏苏\.codex\skill-backups
```

Git tags remain the long-term version history. The backup folder is only a short-term safety copy.

## Automatic GitHub push

Use `tools\publish-skill-update.cmd` for every skill update. Do not use the older tag-only command as the normal release path. The publish command pushes to `origin` automatically after a successful commit and tag.
