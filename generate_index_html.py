"""
网页索引 HTML 生成器（博客风格）
功能：扫描目录的 HTML/PDF 文件，生成博客风格首页 home.html
模板：home_template.html（与脚本同级）

用法：python generate_index_html.py
"""

import os
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
# ===================================================================


FILE_ICONS = {".html": "&#127760;", ".htm": "&#127760;", ".pdf": "&#128217;"}
FILE_TYPE_LABEL = {".html": "HTML", ".htm": "HTML", ".pdf": "PDF"}


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


def build_dir_tree(base_path, files):
    """
    构建目录树（包含所有有文件的文件夹）。
    返回 (tree_dict, folder_file_map)
      tree_dict: { folder_path: [subfolder_names] }
      folder_file_map: { folder_path: [file_Path] }
    """
    # 收集所有包含文件的文件夹
    dirs_with_files = set()
    folder_file_map = defaultdict(list)
    for f in files:
        rel = f.relative_to(base_path)
        # 每个文件的所在文件夹（最后一个目录）
        if len(rel.parts) == 1:
            folder = "__root__"
        else:
            folder = rel.parts[0]
        dirs_with_files.add(folder)
        folder_file_map[folder].append(f)

    return folder_file_map


def folder_sort_key(name):
    """文件夹排序：普通(0) > __root__(1) > personal(2)"""
    if name == "__root__":
        return (1, "")
    if name == "personal":
        return (2, name)
    return (0, name)


def render_tree_html(folder_file_map, base_path):
    """
    生成左侧文件夹树的 HTML。
    一级文件夹可点击过滤；有子文件夹的显示箭头可折叠。
    """
    # 收集所有有文件的路径前缀（用于构建树）
    all_prefixes = set()
    for f in [f for flist in folder_file_map.values() for f in flist]:
        rel = f.relative_to(base_path)
        parts = list(rel.parts)
        # 收集每个前缀
        for i in range(1, len(parts)):
            prefix = "/".join(parts[:i])
            all_prefixes.add(prefix)

    # 构建树：{ name: { "count": int, "children": { ... } } }
    tree = {}
    for folder, flist in folder_file_map.items():
        if folder not in tree:
            tree[folder] = {"count": len(flist), "children": {}, "is_leaf": True}
        # 检查是否有子文件夹
        subdirs = set()
        for f in flist:
            rel = f.relative_to(base_path)
            if len(rel.parts) > 2:
                subdirs.add(rel.parts[1])
        for sd in subdirs:
            if "children" not in tree[folder]:
                tree[folder]["children"] = {}
            if sd not in tree[folder]["children"]:
                # 统计该子文件夹下的文件数
                cnt = sum(1 for f in flist
                          if len(f.relative_to(base_path).parts) > 1
                          and f.relative_to(base_path).parts[1] == sd)
                tree[folder]["children"][sd] = {"count": cnt, "children": {}}

    # 生成 HTML
    items = []
    tree_id = [0]

    def make_id():
        tree_id[0] += 1
        return str(tree_id[0])

    def render_node(name, info, depth, full_path=""):
        """递归渲染树节点"""
        is_root = (full_path == "")
        display_path = name if is_root else full_path
        has_children = len(info.get("children", {})) > 0
        arrow_class = "tree-arrow" + (" open" if has_children else " empty")
        icon = "📂" if has_children or depth == 0 else "📄"
        cnt = info.get("count", 0)

        # 点击文件夹名 → 过滤；点击箭头 → 折叠
        onclick_filter = f"filterByFolder('{display_path}')" if depth == 0 else "void(0)"
        item_id = make_id()

        html = f'<div class="tree-item" data-folder="{display_path}" data-tree-id="{item_id}" '
        html += f'onclick="{onclick_filter}" title="{display_path}">\n'
        html += f'  <span class="{arrow_class}" id="tree-arrow-{item_id}" '
        html += f'onclick="event.stopPropagation(); toggleTree(\'{item_id}\')">&#9654;</span>\n'
        html += f'  <span class="tree-icon">{icon}</span>\n'
        html += f'  <span>{name}</span>\n'
        html += f'  <span class="tree-count">({cnt})</span>\n'
        html += f'</div>\n'

        if has_children:
            html += f'<div class="tree-children" id="tree-children-{item_id}">\n'
            for child_name, child_info in sorted(info["children"].items()):
                child_path = f"{display_path}/{child_name}" if not is_root else child_name
                html += render_node(child_name, child_info, depth + 1, child_path)
            html += f'</div>\n'

        return html

    # 排序后渲染
    sorted_folders = sorted(folder_file_map.keys(), key=folder_sort_key)
    for name in sorted_folders:
        info = tree.get(name, {"count": len(folder_file_map[name]), "children": {}})
        items.append(render_node(name, info, 0))

    # "全部" 入口
    total = sum(len(v) for v in folder_file_map.values())
    all_html = f'<div class="tree-item active" data-folder="all" onclick="filterByFolder(\'all\')">\n'
    all_html += f'  <span class="tree-arrow empty">&#9654;</span>\n'
    all_html += f'  <span class="tree-icon">📂</span>\n'
    all_html += f'  <span>全部文件</span>\n'
    all_html += f'  <span class="tree-count">({total})</span>\n'
    all_html += f'</div>\n'

    return all_html + "\n".join(items)


def render_file_sections(folder_file_map, base_path):
    """
    按文件夹分组渲染文件卡片区域。
    """
    sections = []

    for name in sorted(folder_file_map.keys(), key=folder_sort_key):
        files = folder_file_map[name]

        # 文件排序：PINNED > 普通 > BOTTOM
        def file_sort_key(f):
            stem = f.stem
            is_pinned = any(kw in stem for kw in PINNED_KEYWORDS)
            is_bottom = any(kw in stem for kw in BOTTOM_KEYWORDS)
            return (is_bottom, not is_pinned, stem.lower())

        sorted_files = sorted(files, key=file_sort_key)
        display_name = "根目录" if name == "__root__" else name

        section = f'<div class="file-section" data-folder="{name}">\n'
        section += f'  <div class="section-title">{display_name}（{len(files)} 篇）</div>\n'
        section += f'  <div class="file-grid">\n'

        for f in sorted_files:
            rel = "./" + f.relative_to(base_path).as_posix()
            ext = f.suffix.lower()
            icon = FILE_ICONS.get(ext, "&#128196;")
            type_label = FILE_TYPE_LABEL.get(ext, "")
            show_name = f.stem.replace("_", " ").replace("-", " ")

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

    # 按文件夹分组
    folder_file_map = build_dir_tree(base_path, files)
    folder_count = len(folder_file_map)

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 替换占位符
    html = template
    html = html.replace("{{UPDATE_TIME}}", now_str)
    html = html.replace("{{TOTAL}}", str(len(files)))
    html = html.replace("{{FOLDER_COUNT}}", str(folder_count))
    html = html.replace("{{TREE_HTML}}", render_tree_html(folder_file_map, base_path))
    html = html.replace("{{FILE_SECTIONS}}", render_file_sections(folder_file_map, base_path))

    # 写入
    output_path = base_path / OUTPUT_FILE
    output_path.write_text(html, encoding="utf-8")
    print(f"[OK] 生成成功：{output_path}")
    print(f"[OK] 共 {len(files)} 个文件 / {folder_count} 个文件夹")


if __name__ == "__main__":
    generate_html(NOTES_DIR)
