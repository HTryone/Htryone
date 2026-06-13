"""
网页索引 HTML 生成器（博客风格）
功能：扫描目录的 HTML/PDF 文件，生成博客风格首页 home.html
模板：home_template.html（与脚本同级）

核心逻辑参考 update_index.py 的 build_folder_tree，递归构建嵌套目录树，
左侧导航栏可折叠展开，文件可点击打开。

用法：python generate_index_html.py
"""

from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ==================== 配置区（可按需修改） ====================
NOTES_DIR = "."              # 笔记根目录（在目标目录执行即可）
OUTPUT_FILE = "home.html"     # 生成的索引文件名
TEMPLATE_FILE = "home_template.html"  # 模板文件名

# 不想被索引的文件夹名称
IGNORE_DIRS = {".git", ".workbuddy", ".obsidian", "assets", "images", "附件",
                "__pycache__", "templates", "build", "node_modules"}
# 不想被索引的文件名（在根目录或子目录都会被忽略）
IGNORE_FILES = {"index.html", "home.html", "home_template.html"}
# 优先排在前面的文件名关键词（包含这些词的文件排前面）
PINNED_KEYWORDS = ["目录", "index", "Index", "README"]
# 固定在最后面的文件名关键词（包含这些词的文件排最后）
BOTTOM_KEYWORDS = ["后记", "personal"]
# 要扫描的文件扩展名
SCAN_EXTENSIONS = {".html", ".htm", ".pdf"}
# =====================================================================

# 图标映射
FILE_ICONS = {".html": "🌐", ".htm": "🌐", ".pdf": "📕"}
FILE_TYPE_LABEL = {".html": "HTML", ".htm": "HTML", ".pdf": "PDF"}


# ─────────────── 文件收集 ───────────────

def collect_files(base_path):
    """收集所有支持的文件，返回 Path 列表"""
    files = []
    for p in base_path.rglob("*"):
        if not p.is_file():
            continue
        if any(ignored in p.parts for ignored in IGNORE_DIRS):
            continue
        if p.name in IGNORE_FILES:
            continue
        if p.suffix.lower() not in SCAN_EXTENSIONS:
            continue
        files.append(p)
    return files


# ─────────────── 树构建（与 update_index.py 一致的嵌套逻辑） ───────────────

def build_folder_tree(files, base_path):
    """
    构建文件夹树状结构（与 update_index.py 的 build_folder_tree 逻辑一致）。
    返回嵌套字典：{ 文件夹名: { 子文件夹名: { ... }, 文件名: Path对象 } }
    """
    root = {}
    for file in files:
        rel = file.relative_to(base_path)
        parts = list(rel.parts)
        current = root
        for i, part in enumerate(parts):
            is_last = (i == len(parts) - 1)
            if is_last:
                current[part] = file  # 叶子节点存 Path
            else:
                if part not in current:
                    current[part] = {}
                current = current[part]
    return root


def count_files_in_tree(node):
    """递归统计树中文件数量"""
    if isinstance(node, Path):
        return 1
    return sum(count_files_in_tree(v) for v in node.values())


# ─────────────── 排序 ───────────────

def folder_sort_key(name):
    """文件夹排序：普通(0) > __root__(1) > personal(2)"""
    if name == "__root__":
        return (1, "")
    if name == "personal":
        return (2, name)
    return (0, name)


def tree_sort_key(item):
    """
    树节点排序（与 update_index.py 的 sort_key 一致）。
    目录排前，文件排后；PINNED 排前，BOTTOM 排后。
    """
    name, content = item
    is_file = isinstance(content, Path)
    is_pinned = 1 if any(kw in name for kw in PINNED_KEYWORDS) else 2
    is_bottom = 1 if any(kw in name for kw in BOTTOM_KEYWORDS) else 0
    return (is_bottom, is_file, is_pinned, name)


def file_sort_key(f):
    """文件排序：PINNED > 普通 > BOTTOM"""
    stem = f.stem
    is_pinned = any(kw in stem for kw in PINNED_KEYWORDS)
    is_bottom = any(kw in stem for kw in BOTTOM_KEYWORDS)
    return (is_bottom, not is_pinned, stem.lower())


# ─────────────── HTML 渲染 ───────────────

def render_tree_html(tree, base_path):
    """
    生成左侧文件夹树的 HTML。
    递归渲染：文件夹节点（可折叠）+ 文件叶子节点（可点击打开）。
    """
    tree_id = [0]

    def next_id():
        tree_id[0] += 1
        return str(tree_id[0])

    def get_icon(name, is_dir):
        """获取节点图标"""
        if is_dir:
            return "📁"
        ext = Path(name).suffix.lower()
        return FILE_ICONS.get(ext, "📄")

    def render_node(name, content, depth, parent_path=""):
        """
        递归渲染一个树节点。
        - 如果 content 是 Path → 文件叶子
        - 如果 content 是 dict → 文件夹（可能有子文件夹和文件）
        - parent_path: 父级路径，用于拼接 data-folder
        """
        # 当前节点的完整路径（用于 data-folder 过滤）
        current_path = f"{parent_path}/{name}" if parent_path else name

        if isinstance(content, Path):
            # 文件叶子节点
            f = content
            rel = "./" + f.relative_to(base_path).as_posix()
            stem = f.stem.replace("_", " ").replace("-", " ")
            ext = f.suffix.lower()
            icon = FILE_ICONS.get(ext, "📄")
            type_label = FILE_TYPE_LABEL.get(ext, "")
            nid = next_id()
            html = f'<div class="tree-leaf" data-folder="{parent_path}" '
            html += f'data-tree-id="{nid}" '
            html += f'onclick="event.stopPropagation(); window.open(\'{rel}\', \'_blank\')" '
            html += f'title="{f.name}">\n'
            html += f'  <span class="tree-arrow empty"></span>\n'
            html += f'  <span class="tree-icon">{icon}</span>\n'
            html += f'  <span class="tree-name">{stem}</span>\n'
            html += f'  <span class="tree-type">{type_label}</span>\n'
            html += f'</div>\n'
            return html

        # 文件夹节点
        children = content
        file_count = count_files_in_tree(children)
        has_content = len(children) > 0
        nid = next_id()

        arrow_class = "tree-arrow" + (" open" if has_content else " empty")
        icon = "📁"

        # 当前文件夹的 data-folder 路径（用于过滤）
        onclick_filter = f"filterByFolder('{current_path}')"
        onclick_toggle = f"event.stopPropagation(); toggleTree('{nid}')"

        html = f'<div class="tree-item" data-folder="{current_path}" data-tree-id="{nid}" '
        html += f'onclick="{onclick_filter}" title="{current_path}">\n'

        if has_content:
            html += f'  <span class="{arrow_class}" id="tree-arrow-{nid}" '
            html += f'onclick="{onclick_toggle}">&#9654;</span>\n'
        else:
            html += f'  <span class="tree-arrow empty"></span>\n'

        html += f'  <span class="tree-icon">{icon}</span>\n'
        html += f'  <span class="tree-name">{name}</span>\n'
        html += f'  <span class="tree-count">({file_count})</span>\n'
        html += f'</div>\n'

        # 子节点容器
        if has_content:
            html += f'<div class="tree-children" id="tree-children-{nid}">\n'
            items = sorted(children.items(), key=tree_sort_key)
            for child_name, child_content in items:
                html += render_node(child_name, child_content, depth + 1, current_path)
            html += f'</div>\n'

        return html

    # "全部文件" 入口
    total = count_files_in_tree(tree)
    all_html = f'<div class="tree-item active" data-folder="all" onclick="filterByFolder(\'all\')">\n'
    all_html += f'  <span class="tree-arrow empty">&#9654;</span>\n'
    all_html += f'  <span class="tree-icon">📂</span>\n'
    all_html += f'  <span class="tree-name">全部文件</span>\n'
    all_html += f'  <span class="tree-count">({total})</span>\n'
    all_html += f'</div>\n'

    # 只渲染顶级文件夹（不展开子文件夹）
    items_html = ""
    for name, content in sorted(tree.items(), key=tree_sort_key):
        if isinstance(content, Path):
            continue  # 根目录文件不在左侧栏显示
        file_count = count_files_in_tree(content)
        items_html += f'<div class="tree-item" data-folder="{name}" '
        items_html += f'onclick="filterByFolder(\'{name}\')" title="{name}">\n'
        items_html += f'  <span class="tree-arrow empty">&#9654;</span>\n'
        items_html += f'  <span class="tree-icon">📁</span>\n'
        items_html += f'  <span class="tree-name">{name}</span>\n'
        items_html += f'  <span class="tree-count">({file_count})</span>\n'
        items_html += f'</div>\n'

    return all_html + items_html


def collect_all_files(node):
    """递归收集树中所有文件 Path"""
    files = []
    for content in node.values():
        if isinstance(content, Path):
            files.append(content)
        else:
            files.extend(collect_all_files(content))
    return files


def render_file_sections(tree, base_path, depth=0):
    """
    按顶级文件夹分组渲染文件卡片区域（右侧主内容区）。
    每个顶级文件夹显示其下所有文件（含子文件夹内的），按子文件夹分区。
    """
    sections = []

    for name, content in sorted(tree.items(), key=tree_sort_key):
        if isinstance(content, Path):
            continue  # 根目录文件跳过

        # 收集该顶级文件夹下所有文件（含子文件夹内的）
        all_files = collect_all_files(content)
        if not all_files:
            continue

        sorted_files = sorted(all_files, key=file_sort_key)

        section = f'<div class="file-section" data-folder="{name}">\n'
        section += f'  <div class="section-title">{name}</div>\n'
        section += f'  <div class="file-list">\n'

        for f in sorted_files:
            rel = "./" + f.relative_to(base_path).as_posix()
            ext = f.suffix.lower()
            icon = FILE_ICONS.get(ext, "📄")
            type_label = FILE_TYPE_LABEL.get(ext, "")
            show_name = f.stem.replace("_", " ").replace("-", " ")

            # 显示相对路径中的子文件夹名
            rel_to_folder = f.relative_to(base_path)
            if len(rel_to_folder.parts) > 2:
                sub_path = "/".join(rel_to_folder.parts[1:-1])
                show_name = f"{sub_path} / {show_name}"

            section += (
                f'    <a class="file-card" data-name="{f.stem.lower()}" '
                f'href="{rel}" target="_blank">\n'
                f'      <span class="file-icon">{icon}</span>\n'
                f'      <div class="file-info">\n'
                f'        <div class="file-name">{show_name}</div>\n'
                f'        <div class="file-meta">{type_label}</div>\n'
                f'      </div>\n'
                f'    </a>\n'
            )

        section += f'  </div>\n'
        section += f'</div>\n'
        sections.append(section)

    return "\n".join(sections)


# ─────────────── 主函数 ───────────────

def generate_html(base_dir):
    base_path = Path(base_dir).resolve()
    print(f"[INFO] 扫描目录：{base_path}")

    files = collect_files(base_path)
    if not files:
        print("[WARN] 未找到任何支持的文件。")
        return

    print(f"[INFO] 共找到 {len(files)} 个文件")

    # 读取模板
    template_path = base_path / TEMPLATE_FILE
    if not template_path.exists():
        print(f"[ERROR] 模板文件不存在：{template_path}")
        return
    template = template_path.read_text(encoding="utf-8")

    # 构建嵌套目录树（与 update_index.py 一致）
    folder_tree = build_folder_tree(files, base_path)

    # 统计文件夹数
    folder_count = 0
    def count_folders(node):
        nonlocal folder_count
        for name, content in node.items():
            if not isinstance(content, Path):
                folder_count += 1
                count_folders(content)
    count_folders(folder_tree)

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 替换占位符
    html = template
    html = html.replace("{{UPDATE_TIME}}", now_str)
    html = html.replace("{{TOTAL}}", str(len(files)))
    html = html.replace("{{FOLDER_COUNT}}", str(folder_count))
    html = html.replace("{{TREE_HTML}}", render_tree_html(folder_tree, base_path))
    html = html.replace("{{FILE_SECTIONS}}", render_file_sections(folder_tree, base_path))

    # 写入
    output_path = base_path / OUTPUT_FILE
    output_path.write_text(html, encoding="utf-8")
    print(f"[OK] 生成成功：{output_path}")
    print(f"[OK] 共 {len(files)} 个文件 / {folder_count} 个文件夹")


if __name__ == "__main__":
    generate_html(NOTES_DIR)
