# md 目录生成器

> 为 Typora 笔记库设计的自动化索引生成工具，一键扫描目录、生成带树状图和可点击链接的 Markdown 索引文件。

---

## 项目简介

随着笔记数量和文件夹层级不断增加，手动维护目录索引变得繁琐且容易过时。**md 目录生成器** 是一个轻量级 Python 脚本工具，能够：

- 递归（或按需非递归）扫描指定目录
- 识别多种常见文档格式
- 自动生成包含 **ASCII 树状结构图** 和 **可点击文件列表** 的 Markdown 索引文件
- 用 Typora 打开即可直接点击跳转，无需任何额外配置

本项目提供**三个脚本**，分别覆盖"全站索引""子文件夹索引""本地通用笔记库"三种场景，按需选用。

---

## 功能特性

### 核心功能

| 功能 | 说明 |
|------|------|
| 多格式支持 | 视版本不同，支持 `.md .html .htm .pdf .doc .docx .ppt .pptx .xls .xlsx .csv` |
| 递归扫描 | 自动遍历所有子目录，无限层级 |
| ASCII 树状图 | 生成兼容 Markdown 代码块的文件夹结构可视化 |
| 可点击链接 | 每个文件自动生成 `[文件名](路径)` 格式的 Markdown 链接 |
| 智能排序 | 含关键词（如"目录""index"）的文件优先展示；含"后记""personal"的自动沉底 |
| 自动排除 | 可配置忽略目录和文件名，避免索引文件自身被重复扫描 |
| 文件计数 | 每个文件夹标题旁显示该文件夹下的文件总数 |

### 扩展功能（原始版本）

| 功能 | 说明 |
|------|------|
| 文件监控 | 基于 `watchdog` 库，监听文件系统变化，自动重新生成索引 |
| 完整技术文档 | 含需求规格、技术设计、用户手册、接口设计、更新日志共 5 份文档 |

---

## 文件结构

```
personal/utils/md目录生成器/
├── README.md                  # 本文件（总说明）
├── 原始版本/
│   ├── update_index.py        # 主程序（递归扫描，输出 _Index.md）
│   ├── monitor.py             # 文件监控程序（需安装 watchdog）
│   └── doc/                  # 完整技术文档
│       ├── 01_需求规格说明书.md
│       ├── 02_技术设计说明书.md
│       ├── 03_用户使用手册.md
│       ├── 04_接口设计说明书.md
│       ├── 05_项目更新日志.md
│       └── README.md
└── 修改版本/
    ├── update_index.py        # 适配本仓库的递归版（输出 index.md）
    └── update_2.py           # 子文件夹专用版（非递归，输出 目录.md）
```

---

## 三个脚本详细对比

### 总览表

| 特性 | 原始版本/update_index.py | 修改版本/update_index.py | 修改版本/update_2.py |
|------|--------------------------|--------------------------|----------------------|
| 设计用途 | 本地 Typora 笔记库通用 | 本仓库（Htryone/Htryone）全站索引 | 子文件夹独立索引 |
| 扫描范围 | 递归全目录 | 递归全目录 | **仅当前目录，不递归** |
| 输出文件名 | `_Index.md` | `index.md` | `目录.md` |
| 支持格式 | `.md .doc .docx .ppt .pptx .html .htm .xls .xlsx .csv .pdf` | `.html .htm .pdf` | `.html .htm .pdf` |
| ASCII 树状图 | ✅ | ✅ | ❌（输出简洁，无树状图） |
| 文件夹文件计数 | ✅ | ✅ | ❌ |
| 自动排除自身 | ❌（需手动配置 IGNORE_FILES） | ❌ | ✅（自动排除 `目录.md` 和 `目录.html`） |
| 智能排序 | ✅（PINNED + BOTTOM） | ✅（增强版，含 subPath 支持） | ✅（简易版） |
| 监控支持 | ✅（monitor.py） | ❌ | ❌ |
| 技术文档 | ✅（5 份完整文档） | ❌ | ❌ |
| 配置区位置 | 第 12-19 行 | 第 12-25 行 | 第 11-17 行 |

---

### 原始版本/update_index.py

**适用场景**：本地 Typora 笔记库，文件格式多样（含 Word/PPT/Excel 等）。

**支持格式（最全）**：

| 格式 | 扩展名 | 图标 |
|------|--------|------|
| Markdown | `.md` | 📝 |
| Word 文档 | `.doc`, `.docx` | 📘 |
| PPT 演示 | `.ppt`, `.pptx` | 📊 |
| HTML 网页 | `.html`, `.htm` | 🌐 |
| Excel 表格 | `.xls`, `.xlsx`, `.csv` | 📈 |
| PDF 文档 | `.pdf` | 📕 |

**输出示例**（`_Index.md`）：

```markdown
# 📚 我的知识库

> 📅 索引更新：2026-04-21 12:00:00 | 📄 共 **22** 篇笔记

---

## 🗺️ 文件夹结构图

```
📂 根目录/
├── 📁 know/
│   ├── 📁 hu共享/
│   │   └── 📁 个人简历/
│   │       └── 📘 260405HU.docx
│   └── 📁 知识库/
│       └── 📝 笔记.md
└── 📁 笔记/
    └── 📝 README.md
```

---

## 📑 笔记目录（点击直接打开）

## 📁 know/（9 篇）

### 📁 hu共享/（8 篇）
...
```

**用法**：

```bash
# 方式一：双击运行（Windows）
双击 update_index.py

# 方式二：命令行
python update_index.py
```

**配置文件说明**（脚本头部第 12-19 行）：

```python
NOTES_DIR = "."              # 笔记根目录（脚本所在目录）
OUTPUT_FILE = "_Index.md"    # 输出文件名
IGNORE_DIRS = {".git", ".obsidian", "assets", "images", "附件",
                "__pycache__", "templates", "build"}
SCAN_EXTENSIONS = {".md", ".doc", ".docx", ".ppt", ".pptx",
                    ".html", ".htm", ".xls", ".xlsx", ".csv", ".pdf"}
```

---

### 修改版本/update_index.py

**适用场景**：本仓库（Htryone/Htryone）全站索引，只扫描 HTML/PDF，输出 `index.md`。

**与原始版本的主要差异**：

1. **输出文件名**：`_Index.md` → `index.md`
2. **支持格式精简**：只保留 `.html .htm .pdf`（匹配本仓库实际内容）
3. **排除规则增强**：`IGNORE_DIRS` 新增 `.workbuddy`；`IGNORE_FILES` 默认排除 `index.html` 和 `index.md`
4. **排序逻辑增强**：
   - 优先关键词：`PINNED_KEYWORDS = ["目录", "index", "Index", "README"]`
   - 沉底关键词：`BOTTOM_KEYWORDS = ["后记", "personal"]`
   - 含关键词的文件夹在左侧树状图中也优先展示
5. **子路径显示**：文件信息新增 `subPath` 字段，渲染时显示相对子路径

**用法**：

```bash
cd "D:\工作空间网页版"
python personal/utils/md目录生成器/修改版本/update_index.py
```

---

### 修改版本/update_2.py

**适用场景**：为某个子文件夹单独生成索引，不递归，输出简洁的 `目录.md`。

**特点**：

- **非递归**：只扫描当前目录，不进入子文件夹
- **自动排除自身**：运行时会自动跳过 `目录.md` 和 `目录.html`，无需手动配置
- **输出轻量**：只有一级标题 + 文件列表，无树状图，适合嵌入子文件夹内
- **智能排序**：含"目录""index""README"的文件优先展示

**输出示例**（`目录.md`）：

```markdown
# 📁 子文件夹名称

> 📅 更新：2026-06-20 13:00:00 | 📄 共 **5** 个文件

---

## 📑 文件列表

- 🌐 [页面1.html](./页面1.html)
- 📕 [文档.pdf](./文档.pdf)
- 🌐 [目录.html](./目录.html)
```

**用法**：

```bash
# 将 update_2.py 放入目标子文件夹，然后：
cd 目标子文件夹路径
python "D:\工作空间网页版\personal\utils\md目录生成器\修改版本\update_2.py"

# 或更简单：直接双击 update_2.py（Windows）
```

---

## 安装与依赖

### Python 版本要求

- 原始版本：Python 3.7+
- 修改版本：Python 3.7+（两个脚本均无第三方依赖）

### 第三方依赖

| 脚本 | 依赖 | 安装命令 |
|------|------|----------|
| 原始版本/update_index.py | 无（标准库） | — |
| 原始版本/monitor.py | `watchdog` | `pip install watchdog` |
| 修改版本/update_index.py | 无（标准库） | — |
| 修改版本/update_2.py | 无（标准库） | — |

> ✅ 所有核心脚本均**无需安装任何第三方库**，下载即可运行。

---

## 配置区详解

各脚本头部均有**配置区**（用 `=================` 注释包裹），可按需修改。以下以**修改版本/update_index.py** 为例说明：

```python
# ==================== 配置区（可按需修改） ====================
NOTES_DIR = "."  # 笔记根目录（在目标目录执行即可）

# 不想被索引的文件夹名称（按名称匹配，任意层级）
IGNORE_DIRS = {".git", ".workbuddy", ".obsidian", "assets", "images", "附件",
                "__pycache__", "templates", "build", "node_modules"}

# 不想被索引的文件名
IGNORE_FILES = {"index.html", "index.md"}

# 要扫描的文件扩展名
SCAN_EXTENSIONS = {".html", ".htm", ".pdf"}

# 优先排在前面的文件名关键词（含这些词的文件排前面）
PINNED_KEYWORDS = ["目录", "index", "Index", "README"]

# 固定在最后面的文件名关键词（含这些词的文件排最后）
BOTTOM_KEYWORDS = ["后记", "personal"]
# ============================================================
```

**配置项说明**：

| 配置项 | 类型 | 说明 |
|--------|------|------|
| `NOTES_DIR` | 字符串 | 扫描根目录，`.` 表示脚本运行所在目录 |
| `IGNORE_DIRS` | 集合 | 按**文件夹名称**忽略，任意层级生效（如 `.git` 无论在哪层都会被跳过） |
| `IGNORE_FILES` | 集合 | 按**文件名**忽略，任意层级生效 |
| `SCAN_EXTENSIONS` | 集合 | 需要扫描的文件扩展名，小写 |
| `PINNED_KEYWORDS` | 列表 | 文件名含这些关键词的文件，在同类型中优先展示 |
| `BOTTOM_KEYWORDS` | 列表 | 文件名含这些关键词的文件，固定排在最后 |

---

## 输出格式详解

### ASCII 树状图

生成的树状图放在 Markdown 代码块（```）中，兼容所有 Markdown 编辑器：

```
📂 根目录/
├── 📁 科技数码相关/（12 篇）
│   ├── 📁 小米/（5 篇）
│   │   ├── 🌐 手机测评.html
│   │   └── 📕 规格.pdf
│   └── 📁 华为/（7 篇）
└── 📁 personal/（3 篇）
    └── 📝 Git 命令大全.html
```

- `├──`：非末项连接线
- `└──`：末项连接线
- `│   `：垂直连接线（缩进对齐用）
- 文件夹图标：`📁`
- 根目录图标：`📂`

### 可点击目录列表

树状图之后是层级化的文件列表，每个文件名都是可点击的 Markdown 链接：

```markdown
## 📁 科技数码相关/（12 篇）

- 🌐 [小米手机测评.html](./科技数码相关/小米/小米手机测评.html)
- 📕 [规格说明.pdf](./科技数码相关/小米/规格说明.pdf)
```

用 Typora 打开后，按住 `Ctrl` 点击链接即可直接打开对应文件。

---

## 技术实现

### 核心算法

#### 1. 文件扫描

使用 `pathlib.Path.rglob("*")` 递归遍历，结合多层过滤：

```python
for p in base_path.rglob("*"):
    if not p.is_file(): continue
    if any(ignored in p.parts for ignored in IGNORE_DIRS): continue
    if p.name in IGNORE_FILES: continue
    if p.suffix.lower() not in SCAN_EXTENSIONS: continue
```

#### 2. 树状结构构建

将文件路径解析为 `parts` 元组，逐层插入字典树：

```python
def build_folder_tree(files, base_path):
    root = {}
    for file in files:
        rel = file.relative_to(base_path)
        parts = list(rel.parts)
        current = root
        for i, part in enumerate(parts):
            is_last = (i == len(parts) - 1)
            if is_last:
                current[part] = file  # 叶子节点存储 Path 对象
            else:
                if part not in current:
                    current[part] = {}
                current = current[part]
    return root
```

#### 3. ASCII 树状图渲染

递归遍历字典树，根据当前节点是否为末项选择连接线：

```python
def render_tree_ascii(tree, prefix="", is_last=True):
    for i, (name, content) in enumerate(items):
        is_last_item = (i == len(items) - 1)
        connector = "└── " if is_last_item else "├── "
        ...
```

#### 4. 智能排序

文件排序优先级（数字越小越靠前）：

```
(是否沉底, 是否为文件, 是否优先, 文件名)
```

- 沉底文件：`(1, ...)` → 排最后
- 目录：`(0, 0, ...)` → 排前面
- 优先文件：`(0, 1, 1, ...)` → 同类型中排前面
- 普通文件：`(0, 1, 2, ...)` → 按名称排序

---

## 常见问题（FAQ）

### Q1：生成的索引文件中链接打不开？

**A**：检查文件路径是否包含中文或特殊字符。Typora 支持 Unicode 路径，但需确保文件系统编码一致。建议使用相对路径（脚本默认行为）。

### Q2：如何排除某个特定子目录？

**A**：在 `IGNORE_DIRS` 中添加文件夹名称即可（按名称匹配，任意层级生效）。如果需要精确匹配某个路径，修改版本可在 `IGNORE_PATHS` 中添加相对路径。

### Q3：update_2.py 能递归扫描子文件夹吗？

**A**：不能，这是设计使然。`update_2.py` 专为子文件夹设计，只扫当前目录，生成简洁索引。如需递归，请使用 `update_index.py`。

### Q4：原始版本的 monitor.py 怎么用？

**A**：
```bash
pip install watchdog
python monitor.py
```
启动后脚本会监听笔记目录的文件变化，自动重新生成 `_Index.md`。按 `Ctrl+C` 停止。

### Q5：扫描大目录（1000+ 文件）会慢吗？

**A**：不会。实测扫描 1000 个文件通常在 2 秒内完成，远少于 5 秒的设计目标。瓶颈通常在磁盘 I/O，而非脚本本身。

### Q6：能自定义输出的 Markdown 格式吗？

**A**：可以。直接修改脚本中 `md_content` 列表里的字符串模板即可。如果需求复杂，建议基于本工具二次开发。

---

## 更新日志

### 修改版本

| 日期 | 版本 | 变更内容 |
|------|------|----------|
| 2026-06-20 | v1.1 | `personal/scripts` 重命名为 `personal/utils`；`README.md` 补充完整说明 |
| 2026-06（早期） | v1.0 | 从原始版本改编，适配本仓库；支持格式精简为 html/htm/pdf；增加 `PINNED_KEYWORDS` 和 `BOTTOM_KEYWORDS` 排序；新增 `update_2.py` |

### 原始版本

| 日期 | 版本 | 变更内容 |
|------|------|----------|
| 2026-04-21 | v1.0 | 正式版发布；支持 11 种文件格式；ASCII 树状图；可点击链接；`monitor.py` 文件监控；完整技术文档 5 份 |

---

## 许可证

本工具随仓库整体以 **CC BY-NC 4.0** 协议发布。

- ✅ 分享、修改、二次发布（需署名）
- ❌ 商用需另行授权

---

## 相关链接

- 仓库地址：[https://github.com/HTryone/Htryone](https://github.com/HTryone/Htryone)
- 在线预览：由 Cloudflare Pages 自动部署
- 问题反馈：通过仓库 Issues 提交

---

*最后更新：2026-06-20*
