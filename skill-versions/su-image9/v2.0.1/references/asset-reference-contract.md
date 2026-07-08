# su-image9 Asset Reference Contract

<!-- ref-version: 2.0.1 -->

## Reference Purpose

参考图是内容锚点，不是风格目标。

可继承：

- 角色身份轮廓、发型轮廓、服装剪影。
- 道具形状、尺度、归属。
- 空间结构、门窗家具、车辆位置、机位关系。

不可继承：

- 色彩、照片质感、电影光效、CG 渲染、厚涂笔触、漫画线稿、AI 精修质感。
- 精修脸、照片级皮肤、肖像相似度和参考图风格。

## Conflict Handling

图片用途不清、资产编号无法匹配、俯视图与透视图冲突、用户文字与参考图在门窗家具/站位/机位/道具归属上冲突时，输出 `任务失败：参考资产冲突（F-ASSET）` 并停止。

若参考图风格与 `SYSTEM_STYLE_LAYER` 冲突且无法剥离，输出 `任务失败：参考风格冲突（F-ASSET）` 或请求用户确认是否改变技能目标。

## Binding Matrix

- `bound`：全流程可用。
- `prompt_only`：仅 prompt 交付。
- `not_bound`：可 raw_generation，但须在规划确认时声明并标记 `reference_risk: unbound`。
- `formal_reference_image`：必须 bound。
- 矩阵外组合为 F-GATE。
