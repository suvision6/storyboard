# 项目层词表与偏好

<!-- for skill-version: 2.4.4 / rule-revision: 2.4.4-emotion-performance-guard-2026-07-16 -->

本文件可选，位阶低于 `SKILL.md` 与四份通用 reference。它只保存当前项目的字面词和偏好，不得新增、覆盖或删除通用拆镜规则。文件存在不代表自动启用；需要使用词表时，人工确认后将所需词显式复制到 `metadata.project_lexicon`，并随 Gate 0/A/B hash 冻结。

## 当前项目字面词

- `prop_terms`：`手环`、`短棍`、`长棍`、`磁卡`、`魂钉`、`裂痕`、`项链`、`绿灯`、`铜镯`。
- `space_terms`：`东侧`、`西侧`、`南侧`、`高台`、`祭池边`、`裂缝`、`地底`、`神殿`、`人间`。
- `vfx_terms`：`阵眼`、`破阵`、`续阵`、`阵破`、`符文`、`祭池`、`锁魂柱`、`柱身`、`黑纹`、`黑雾`、`龙卷`、`漩涡`、`回收`、`光柱`、`封印`、`赤光`、`蓝光`。
- `reality_terms`：`灵魂`、`亡魂`、`残魂`。
- `sound_terms`：`画外声`、`VO`。

这些值均为普通字面子串，不是正则表达式；不得放入空字符串、首尾空白、重复词或 Unicode 控制/格式/代理字符。允许出现 `.*`、`+` 等正则元字符，但 validator 会统一转义并按字面匹配，不得期待它们扩大命中范围。通用词继续由 validator 的通用规则负责，不要为了“更容易命中”把整个剧本词汇批量复制进来。

## metadata 复制示例

```json
{
  "metadata": {
    "project_lexicon": {
      "prop_terms": ["魂钉", "铜镯"],
      "space_terms": ["祭池边", "神殿"],
      "vfx_terms": ["锁魂柱", "黑雾", "赤光"],
      "reality_terms": ["灵魂", "亡魂"],
      "sound_terms": ["VO"]
    }
  }
}
```

只允许 `prop_terms | space_terms | vfx_terms | reality_terms | sound_terms` 五个 key；无词项的 key 可省略，每个已出现的数组必须非空。完全不启用项目词时省略整个 `metadata.project_lexicon`。复制后不得在 Gate 0/A/B 之间静默增删词；需调整时按对应 Gate 回流并重新计算审核 hash。
