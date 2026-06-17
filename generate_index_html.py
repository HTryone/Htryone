"""
网页索引 HTML 生成器（博客风格）
功能：扫描目录的 HTML/PDF 文件，输出 JSON 数据到模板，生成 index.html
     同时为 PORTAL_FOLDERS 指定的子文件夹生成独立入口页面
模板：home_template.html（负责所有样式和渲染逻辑）

用法：python generate_index_html.py
"""

from pathlib import Path
from datetime import datetime
import json

# ==================== 配置区（可按需修改） ====================
NOTES_DIR = "."              # 笔记根目录（在目标目录执行即可）
OUTPUT_FILE = "index.html"    # 生成的索引文件名
TEMPLATE_FILE = "home_template.html"  # 模板文件名
DATA_DIR = "scripts/data"     # JSON 数据输出目录

# 不想被索引的文件夹名称（按名称匹配，任意层级）
IGNORE_DIRS = {".git", ".workbuddy", ".obsidian", "assets", "images", "附件",
                "__pycache__", "templates", "build", "node_modules"}
# 不想被索引的子目录路径（相对于根目录，精确匹配）
IGNORE_PATHS = set()
# 不想被索引的文件名
IGNORE_FILES = {"home.html", "home_template.html"}
# 是否排除根目录下的文件
EXCLUDE_ROOT_FILES = True
# 要扫描的文件扩展名
SCAN_EXTENSIONS = {".html", ".htm", ".pdf"}
# 门户子文件夹：主区域展示 📁 卡片，点击跳转独立页面
# 格式：相对于根目录的路径，如 "科技数码相关/华为"
PORTAL_FOLDERS = {"科技数码相关/小米"}
# =====================================================================


def collect_files(base_path, extra_ignore_paths=None):
    """收集所有支持的文件，返回 Path 列表
    extra_ignore_paths：额外要忽略的相对路径集合（如门户子页面的 index.html）
    """
    base_path = Path(base_path).resolve()
    ignore_paths = IGNORE_PATHS.copy()
    if extra_ignore_paths:
        ignore_paths.update(extra_ignore_paths)
    files = []
    for p in base_path.rglob("*"):
        if not p.is_file():
            continue
        if EXCLUDE_ROOT_FILES and p.parent.resolve() == base_path:
            continue
        if any(ignored in p.parts for ignored in IGNORE_DIRS):
            continue
        rel = p.relative_to(base_path)
        rel_str = rel.as_posix()
        if any(rel_str.startswith(ignore_path) for ignore_path in ignore_paths):
            continue
        if p.name in IGNORE_FILES:
            continue
        if p.suffix.lower() not in SCAN_EXTENSIONS:
            continue
        files.append(p)
    return files


def build_file_data(files, base_path):
    """
    扫描文件列表，构建 JSON 数据。
    PORTAL_FOLDERS 指定的子文件夹内的文件归入 portal，不在主文件列表中展示。
    返回 dict: { "folders": [ { "name", "count", "files": [...], "portals": [...] } ], "total": N, "updateTime": "..." }
    """
    groups = {}
    for f in files:
        rel = f.relative_to(base_path)
        parts = rel.parts
        folder = parts[0] if len(parts) > 1 else "__root__"
        rel_path = rel.as_posix()

        stem = f.stem.replace("_", " ").replace("-", " ")
        ext = f.suffix.lower()

        sub_path = "/".join(parts[1:-1]) if len(parts) > 2 else ""

        file_info = {
            "name": stem,
            "path": "./" + rel_path,
            "ext": ext,
            "type": {"html": "HTML", "htm": "HTML", "pdf": "PDF"}.get(ext.lstrip("."), ""),
            "subPath": sub_path,
        }

        if folder not in groups:
            groups[folder] = {"files": [], "portals": {}}

        portal_matched = None
        for portal in PORTAL_FOLDERS:
            if rel_path.startswith(portal + "/"):
                portal_matched = portal
                break

        if portal_matched:
            portal_name = portal_matched.rsplit("/", 1)[-1]
            if portal_name not in groups[folder]["portals"]:
                groups[folder]["portals"][portal_name] = {
                    "name": portal_name,
                    "path": portal_matched,
                    "count": 0,
                    "files": [],
                }
            groups[folder]["portals"][portal_name]["files"].append(file_info)
            groups[folder]["portals"][portal_name]["count"] += 1
        else:
            groups[folder]["files"].append(file_info)

    PINNED = ["目录", "index", "Index", "README"]
    BOTTOM = ["后记", "personal"]

    def file_sort_key(item):
        name = item["name"]
        is_pinned = any(kw in name for kw in PINNED)
        is_bottom = any(kw in name for kw in BOTTOM)
        return (is_bottom, not is_pinned, name.lower())

    def folder_sort_key(name):
        if name == "__root__":
            return (1, "")
        if name == "personal":
            return (2, name)
        return (0, name)

    folders = []
    for fname in sorted(groups.keys(), key=folder_sort_key):
        g = groups[fname]
        ffiles = sorted(g["files"], key=file_sort_key)

        portals = []
        for pname in sorted(g["portals"].keys()):
            pdata = g["portals"][pname]
            pdata["files"] = sorted(pdata["files"], key=file_sort_key)
            portals.append(pdata)

        folders.append({
            "name": fname if fname != "__root__" else "根目录",
            "count": len(ffiles) + len(portals),
            "files": ffiles,
            "portals": portals,
        })

    return {
        "total": len(files),
        "updateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "folders": folders,
    }


def generate_portal_pages(data, base_path):
    """为每个门户子文件夹生成独立的 index.html"""
    update_time = data["updateTime"]
    for folder in data["folders"]:
        for portal in folder["portals"]:
            depth = portal["path"].count("/") + 1
            up = "../" * depth

            files_html = ""
            for f in portal["files"]:
                icon = {"html": "🌐", "htm": "🌐", "pdf": "📕"}.get(f["ext"].lstrip("."), "📄")
                filename = f["path"].rsplit("/", 1)[-1]
                files_html += (
                    f'<a class="file-card" href="./{filename}" target="_blank">'
                    f'<span class="file-icon">{icon}</span>'
                    f'<div class="file-info">'
                    f'<div class="file-name">{f["name"]}</div>'
                    f'<div class="file-meta">{f["type"]}</div>'
                    f'</div></a>\n'
                )

            html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{portal["name"]} - 文件索引</title>
<link rel="stylesheet" href="{up}scripts/css/home.css">
<link rel="stylesheet" href="{up}scripts/css/home-dark.css">
</head>
<body>

<div class="header">
  <h1>📁 {portal["name"]}</h1>
  <p>共 <strong>{portal["count"]}</strong> 篇 · 索引更新：{update_time}</p>
</div>

<div class="main" style="padding: 24px 28px 32px; max-width: 960px; margin: 0 auto;">
  <div style="margin-bottom: 16px;">
    <a href="{up}index.html" style="color: #888; text-decoration: none; font-size: 0.85rem;">← 返回首页</a>
  </div>
  <div class="file-list">
    {files_html}
  </div>
</div>

<div class="footer" style="font-size: 0.76rem; color: #ccc; text-align: center; padding: 24px; border-top: 1px solid #e8e4df;">
  Powered by generate_index_html.py · {update_time}
</div>

<script src="{up}scripts/dark-mode-toggle.js"></script>
</body>
</html>'''

    output_path = base_path / portal["path"] / "page2.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    print(f"[OK] 门户页面：{output_path}")


def generate_html(base_dir):
    base_path = Path(base_dir).resolve()

    # 自动忽略门户子页面的 page2.html，防止二次扫描
    ignore_paths_local = set()
    for p in PORTAL_FOLDERS:
        ignore_paths_local.add(p + "/page2.html")

    print(f"[INFO] 扫描目录：{base_path}")

    files = collect_files(base_path, ignore_paths_local)
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

    # 构建 JSON 数据
    data = build_file_data(files, base_path)

    # 写入 JS 数据文件（供 <script> 加载）
    data_dir = base_path / DATA_DIR
    data_dir.mkdir(parents=True, exist_ok=True)
    js_path = data_dir / "site_data.js"
    js_content = "const SITE_DATA = " + json.dumps(data, ensure_ascii=False) + ";"
    js_path.write_text(js_content, encoding="utf-8")
    print(f"[OK] JS 数据：{js_path}")

    # 生成主页 HTML（模板不再内嵌 SITE_DATA，改为运行时 fetch JSON）
    html = template
    output_path = base_path / OUTPUT_FILE
    output_path.write_text(html, encoding="utf-8")
    print(f"[OK] 生成成功：{output_path}")
    print(f"[OK] 共 {data['total']} 个文件 / {len(data['folders'])} 个主文件夹")

    # 生成门户子页面
    if PORTAL_FOLDERS:
        generate_portal_pages(data, base_path)


if __name__ == "__main__":
    generate_html(NOTES_DIR)
