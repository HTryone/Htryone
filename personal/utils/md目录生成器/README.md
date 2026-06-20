# md 目录生成器

Typora 笔记索引自动生成工具，扫描指定目录的 HTML/PDF 文件，生成带树状图和可点击链接的 Markdown 索引文件。

---

## 目录结构

```
md目录生成器/
├── 原始版本/
│   ├── update_index.py    # 主程序：递归扫描全目录，生成带树状图的 _Index.md
│   ├── monitor.py         # 文件监控：检测到变化后自动重新生成
│   └── doc/              # 完整技术文档（需求/设计/使用手册/接口/日志）
│
└── 修改版本/
    ├── update_index.py    # 适配本仓库路径配置的递归版，输出 index.md
    └── update_2.py       # 子文件夹专用，只扫当前目录，输出 目录.md
```

---

## 原始版本 — `原始版本/`

最初为本地 Typora 笔记库设计的完整工具，含自动监控和技术文档。

### 特点
- 支持格式最广：`.md .doc .docx .ppt .pptx .html .htm .xls .xlsx .csv .pdf`
- 递归扫描整个目录树
- 生成文件：`_Index.md`（含 ASCII 树状图 + 按文件夹分组的可点击链接列表）
- 附带 `monitor.py`：实时监听文件变化，自动重新生成索引
- 附带 `doc/` 目录：含需求规格、技术设计、用户手册、接口设计、更新日志 5 份完整文档

### 用法
```bash
cd 原始版本路径
python update_index.py
```

---

## 修改版本 — `修改版本/`

在原始版本基础上精简，适配本仓库（Htryone/Htryone）的实际目录结构。

### `update_index.py`
递归扫描全目录，适配本仓库的 `IGNORE_DIRS` 配置（新增 `.workbuddy` 等排除项），输出 `index.md`。

**与原始版本的主要差异：**
- 输出文件名：`_Index.md` → `index.md`
- 支持格式：只保留 `.html .htm .pdf`（匹配本仓库实际内容）
- 排除规则：新增 `.workbuddy`、调整 `IGNORE_FILES`
- 排序逻辑：增强，支持 `PINNED_KEYWORDS`（优先排前）和 `BOTTOM_KEYWORDS`（固定排后）

**用法：**
```bash
cd "D:\工作空间网页版"
python personal/utils/md目录生成器/修改版本/update_index.py
```

### `update_2.py`
专为子文件夹设计，**不递归**，只扫描当前目录下的文件，输出简洁的 `目录.md`。

**特点：**
- 非递归：只处理当前目录，不进入子文件夹
- 自动排除自身：运行时会自动跳过 `目录.md` 和 `目录.html`，无需手动配置
- 输出轻量：只有标题 + 文件列表，无树状图，适合子文件夹独立索引

**用法：**
```bash
cd 目标子文件夹
python "D:\工作空间网页版\personal\utils\md目录生成器\修改版本\update_2.py"
```

---

## 三个脚本对比

| | 原始版本/update_index.py | 修改版本/update_index.py | 修改版本/update_2.py |
|---|---|---|---|
| 扫描范围 | 递归全目录 | 递归全目录 | 仅当前目录 |
| 输出文件 | `_Index.md` | `index.md` | `目录.md` |
| 支持格式 | md/doc/ppt/xls/html/pdf 等 | html/htm/pdf | html/htm/pdf |
| 树状图 | ✅ | ✅ | ❌ |
| 自动排除自身 | ❌（需手动配置） | ❌ | ✅ |
| 适用场景 | 本地 Typora 笔记库 | 本仓库全站索引 | 子文件夹独立索引 |

---

## 注意事项

- 脚本均使用相对路径（`NOTES_DIR = "."`），需在目标目录或正确指定路径运行
- 生成的 `.md` 文件用 Typora 打开效果最佳（树状图、链接均可正常渲染）
- `修改版本/update_index.py` 的 `IGNORE_DIRS` 和 `IGNORE_FILES` 可按需修改，配置区集中在脚本头部（第 12-25 行）
