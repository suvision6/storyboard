# Skill Versioning Workflow

This repository is the source of truth for Codex skills.

## Daily update flow

1. Before changing a released skill, confirm the previous version has a file snapshot under `skill-versions/<skill-name>/v<version>/`.
2. Edit the skill under `skills/<skill-name>`.
3. Increment the version in `skills/<skill-name>/VERSION` and in the `version` field / version section of `SKILL.md`.
4. Validate or test the skill.
5. Run `tools\publish-skill-update.cmd -SkillName <skill-name> -Version <new-version> -Message "<summary>"`.

The publish command creates an immutable file snapshot, stages the skill files and snapshot, commits the update, creates a version tag, syncs the installed Codex skill, and pushes both the commit and tag to GitHub.

## Mandatory file snapshots

Every released skill version must be preserved as files. Do not delete old version folders.

Snapshot location:

```text
skill-versions/su-fenjingskill-zh/v<version>/
```

Rules:

- Never overwrite an existing `skill-versions/su-fenjingskill-zh/v<version>/` directory.
- Never delete old version snapshot directories.
- Git tags are still required, but tags are not a substitute for the file snapshot.
- If a version was installed outside this repo, copy that installed skill folder into the matching snapshot directory before replacing it.

## Save a stable version

Current version:

```powershell
2.1
```

Stable versions are preserved both as file snapshots and as Git tags named:

```text
<skill-name>-v<version>
```

For example, `su-fenjingskill-zh` version `2.0` is preserved as `skill-versions/su-fenjingskill-zh/v2.0/` and `su-fenjingskill-zh-v2.0`; `su-image2-storyboard-grid-zh` version `1.0.0` is preserved as `skill-versions/su-image2-storyboard-grid-zh/v1.0.0/` and `su-image2-storyboard-grid-zh-v1.0.0`.

## Restore an old version

To restore a tagged version into the working tree:

```powershell
git checkout <skill-name>-v<version> -- skills/<skill-name>
.\tools\sync-skill.cmd -SkillName <skill-name>
```

Then run `tools\publish-skill-update.cmd -SkillName <skill-name> -Version <new-version> -Message "Restore from <old-version>"` if you want it to become the current version again.

## Sync behavior

`tools/sync-skill.cmd -SkillName <skill-name>` replaces the installed Codex skill at:

```text
$HOME\.codex\skills\<skill-name>
```

Before replacement, it copies the existing installed version to:

```text
$HOME\.codex\skill-backups
```

Git tags and `skill-versions/` snapshots are the long-term version history. The backup folder is only an additional safety copy and must not be treated as the only retained version.

## Automatic GitHub push

Use `tools\publish-skill-update.cmd -SkillName <skill-name>` for every skill update. Do not use the older tag-only command as the normal release path. The publish command pushes to `origin` automatically after a successful commit and tag.
