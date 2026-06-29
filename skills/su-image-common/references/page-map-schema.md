# Page Map Schema

`annotate_storyboard_pages.py` 使用独立 `page-map.json` 作为面板映射输入，避免脚本猜测每个宫格对应哪些镜头。

## 最小结构

```json
{
  "pages": [
    {
      "page_no": 1,
      "layout": "7",
      "source": "page-001.png",
      "panels": [
        { "panel_no": 1, "shot_nos": [1] },
        { "panel_no": 2, "shot_nos": [2, 3] },
        { "panel_no": 3, "shot_nos": [4] },
        { "panel_no": 4, "shot_nos": [5] },
        { "panel_no": 5, "shot_nos": [6] },
        { "panel_no": 6, "shot_nos": [7] },
        { "panel_no": 7, "shot_nos": [8] }
      ]
    }
  ]
}
```

## 字段说明

- `page_no`
  - 页序号。
- `layout`
  - `7` / `9` / `su-image7` / `su-image9`。
- `source`
  - 原始无字 PNG 文件名，默认相对 `pages/` 目录解析。
- `header`
  - 可选。显式覆盖页眉文本。
- `panels`
  - 必填。每页所有宫格映射。
- `panel_no`
  - 宫格序号。7 格必须完整覆盖 `1..7`，9 格必须完整覆盖 `1..9`。
- `shot_nos`
  - 宫格对应的镜头号数组。标签默认取首镜头三要素。
- `box`
  - 可选。显式给出宫格矩形。

## box 格式

对象格式：

```json
{ "x": 80, "y": 120, "width": 620, "height": 349 }
```

数组格式：

```json
[80, 120, 620, 349]
```

说明：

- `x`, `y` 为左上角坐标
- `width`, `height` 为矩形尺寸
- 坐标基于原始无字 PNG

如果省略 `box`，脚本会按 `su-image7` / `su-image9` 规则使用默认几何推导。
