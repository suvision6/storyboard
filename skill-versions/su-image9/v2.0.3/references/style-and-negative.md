# su-image9 Style And Negative Reference

<!-- ref-version: 2.0.3 -->

## v2.0.3 Rule

`SYSTEM_STYLE_LAYER`、几何蓝图、硬词清单和 `NEGATIVE_CONSTRAINTS` 是生成层合同，不得被预算、词表、人工确认或 references 文件削弱。

正式提示词可写 canon 标记：

```text
SYSTEM_STYLE_LAYER:
@CANON(SYSTEM_STYLE_LAYER)

DELIVERABLE:
@CANON(HARD_PHRASES)
@CANON(GEOMETRY_BLUEPRINT)

NEGATIVE_CONSTRAINTS:
@CANON(NEGATIVE_CONSTRAINTS)
```

validator 在场时必须编译展开，并严格比对 canon 文件、SKILL 内联副本和 validator 快照。禁止 `canon_autofixed`。validator 或 canon 缺失时只能从 `SKILL.md` 内联副本生成诊断草稿，并设置 `release_ready=false`、返回 `REVIEW_REQUIRED`；不得正式生图。

## Forbidden In Final Image Text

- 最终 compiled 文本不得出现 `@CANON(`。
- `PANEL_LAYER` 不得写新的风格定义词，例如 `cinematic lighting`、`anime rendering`、`digital painting`、`photorealistic`、`concept art`、`watercolor`、`oil painting`、`CGI render`。
- `PANEL_LAYER` 只写内容、构图、动作、空间继承、坐标、轴线、道具状态和可见情绪表达。
- 原始生图永远无字；页眉、镜号、C 序号和三要素只允许后处理脚本写在图外标签区。
