# Skill Versioning Workflow

This repository is the source of truth for Codex skills.

## Daily update flow

1. Edit the skill under `skills/su-fenjingskill-zh`.
2. Validate or test the skill.
3. Commit the change with Git.
4. Run `tools/sync-skill.cmd` to install the repository version into Codex.

## Save a stable version

After committing a stable version, create a tag:

```powershell
.\tools\tag-skill-release.cmd -Version 1.0.0
```

This creates a tag named `su-fenjingskill-zh-v1.0.0`.

## Restore an old version

To restore a tagged version into the working tree:

```powershell
git checkout su-fenjingskill-zh-v1.0.0 -- skills/su-fenjingskill-zh
.\tools\sync-skill.cmd
```

Then commit the restored state if you want it to become the current version again.

## Sync behavior

`tools/sync-skill.cmd` replaces the installed Codex skill at:

```text
C:\Users\苏苏\.codex\skills\su-fenjingskill-zh
```

Before replacement, it copies the existing installed version to:

```text
C:\Users\苏苏\.codex\skills\_backups
```

Git tags remain the long-term version history. The backup folder is only a short-term safety copy.
