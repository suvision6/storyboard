# su-image9 Canon Locks（唯一权威源）

<!-- canon-version: 1.7.1 -->
<!-- 锁文本与 1.7.0 完全相同（sha 不变，已开 batch 不受影响）；本次仅修订 R-CANON 规则。 -->

## 权威性声明

- **R-CANON-1**：本文件是四类锁文本、T1/T2/T3 词表、占位句黑名单的唯一权威源；其他文件中的锁文本一律为引用示意。
- **R-CANON-2（1.7.1 修订）**：`final_image_prompts.md` 中锁块**推荐写 `@CANON(NAME)` 标记**，由 validator 编译展开；手写全文被容忍——validator 比对后不一致即替换为 canon 原文并记 `canon_autofixed=true`（warn 备注）。生图只允许使用编译产物。
- **R-CANON-3**：修改任何 canon 块必须升 canon-version 并记 changelog；batch 一致性以锁文本 sha 为准。
- **R-CANON-4**：任务侧只能经 `forbidden_prompt_tokens_extra` 追加禁词，不得覆盖删减。
- **R-CANON-5**：四个 canon 块以 hash 校验，不参与词汇扫描。
- **R-CANON-6**：词汇扫描只作用于 `CONTINUITY_LOCK` 与 `PANEL_TASKS`。
- **R-CANON-7**：final prompt 正文为英文（专有名词除外）；中文禁词为防呆兜底。
- **R-CANON-8（新）**：validator 内置本文件各锁块的出厂 sha256 快照。锁文本变更而 canon-version 未升级 → validator 直接 fail；已升级 → 须 `--accept-canon-change` 显式确认。canon 变更从此必须是显式动作。

## 锁文本

### canon:STYLE_LOCK

```text
STYLE_LOCK:
Unified black-and-white director blocking sketch. Same clean pencil line width, same light gray density, low-detail faces, simple costume silhouettes, sparse structural environment. Prioritize composition, camera viewpoint, character placement, floor plane, object positions, action phase, and continuity over beauty, texture, atmosphere, or face matching. Not a polished illustration, not manga, not photoreal.
```

### canon:CANVAS_LOCK

```text
CANVAS_LOCK:
One wide horizontal 16:9 canvas. Exact clean 3x3 storyboard grid, nine equal horizontal 16:9 panels, straight borders and gutters. No text or labels inside the image. PANEL-1 establishes the master space; PANEL-2 to PANEL-9 inherit it unless a source shot changes state.
```

### canon:REFERENCE_LOCK

```text
REFERENCE_LOCK:
Reference images only lock identity silhouette, hairstyle silhouette, costume silhouette, prop shape, and prop ownership. Draw all characters as simplified director blocking sketch figures, not portrait renderings. Do not copy photo texture, skin detail, lighting, color, refinement level, or face matching.
```

### canon:REFERENCE_LOCK_TEXT_ONLY

```text
REFERENCE_LOCK:
No reference images are bound. Character identity, hairstyle, costume silhouette, and prop ownership are text-defined only, as stated in panel tasks. Draw all characters as simplified director blocking sketch figures. Do not invent photographic likeness, skin detail, lighting style, or color for any character.
```

### canon:NEGATIVE_LOCK

```text
NEGATIVE_LOCK:
No text, labels, captions, panel numbers, shot numbers, subtitles, arrows, UI, monitor graphics, logos, watermarks, Chinese or English writing. No photorealism, realistic skin, portrait rendering, cinematic lighting, color, CGI, 3D render, painting, polished illustration, manga/comic layout, collage, poster, heavy texture, dense environment rendering, mixed panel sizes.
```

## T1 图像内容禁令（仅扫内容字段：ACTION / COMPOSITION、PROP STATE、CONTINUITY_LOCK）

```text
countdown, numeric countdown, bpm, HR, ECG, monitor, screen text,
readable, digits, numerals, timer, clock face with numbers,
倒计时, 监护仪, 心跳仪, 读数, 屏幕文字
```

预处理：先整体剔除合法复合词 `non-readable` 再扫 `readable`。结构性数字（16:9、3x3、镜号、PANEL-n、字段名）豁免。

## T2 词汇禁令（封闭黑名单；英文词界+词形展开，中文子串+例外剔除）

色彩词形表：

| 基词 | 展开 |
|---|---|
| red | red, reddish, crimson, scarlet, ruby, blood-red |
| gold | gold, golden, gilded |
| blue | blue, azure, cyan, navy |
| green | green, emerald, jade-green |
| yellow | yellow, amber |
| purple | purple, violet |
| pink | pink, magenta |
| orange | orange |
| brown | brown |
| 泛色 | colorful, multicolored, vivid colors, saturated colors |
| 中文 | 红, 赤, 朱红, 金色, 金黑, 蓝, 绿, 黄, 紫, 粉, 橙, 棕, 彩色, 七彩 |

中文例外复合词（扫描前剔除）：`金属`。
允许色（唯一豁免）：gray, grey, black, white, pale, dark, light, monochrome, 黑, 白, 灰。
转换表：红光/赤光=light gray pulse；金黑雾=dark mist mass；金色纹路=pale line glow；其余色相按明度映射 light/mid/dark gray。

精修压力词（直接 fail）：

```text
portrait likeness, exact face, photoreal, photorealistic, hyperrealistic,
ultra detailed, highly detailed, intricate, 8k, 4k, masterpiece,
cinematic, studio lighting, skin texture, film grain,
精修, 精修脸, 真人相似, 照片质感, 照片级
```

## T3 风格词白名单（探测词库命中但不在白名单 → warn → HC-2）

```text
sketch, sketchy, blocking, storyboard, simplified, structural, sparse,
clean, rough, loose, minimal, flat, schematic, pencil, line, linework,
outline, silhouette, low-detail, black-and-white, monochrome,
gray, grey, pale, dark, light, wide, tight, shallow, deep
```

探测词库随回归案例持续增补（版本随 canon-version）。

## 占位句黑名单（命中即 fail）

```text
page A/B
foreground/background/shoulder locked
as applicable
allowed positions
fixed objects
source action phase
source camera tag
TBD
same as above
as needed
见前格
同上
```

## Changelog

- 1.7.1：锁文本无变化；R-CANON-2 改编译注入制；新增 R-CANON-8 出厂快照守卫。
- 1.7.0：初版。
