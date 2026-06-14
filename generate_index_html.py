"""
网页索引 HTML 生成器（博客风格）
功能：扫描目录的 HTML/PDF 文件，输出 JSON 数据到模板，生成 index.html
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

# 不想被索引的文件夹名称（按名称匹配，任意层级）
IGNORE_DIRS = {".git", ".workbuddy", ".obsidian", "assets", "images", "附件",
                "__pycache__", "templates", "build", "node_modules"}
# 不想被索引的子目录路径（相对于根目录，精确匹配）
# 例如："personal/旧文档" 或 "科技数码相关/草稿"
IGNORE_PATHS = set()
# 不想被索引的文件名
IGNORE_FILES = {"home.html", "home_template.html"}  # 自身输出和模板不退化
# 是否排除根目录下的文件（True = 排除，False = 包含）
EXCLUDE_ROOT_FILES = True
# 要扫描的文件扩展名
SCAN_EXTENSIONS = {".html", ".htm", ".pdf"}
# 门户子文件夹：主区域展示文件夹卡片，文件收纳在卡片内（点击展开）
# 格式：相对于根目录的路径，如 "科技数码相关/华为"
# 未被指定的子文件夹内文件照常平铺展示
PORTAL_FOLDERS = {"科技数码相关/小米"}
# =====================================================================


def collect_files(base_path):
    """收集所有支持的文件，返回 Path 列表"""
    base_path = Path(base_path).resolve()
    files = []
    for p in base_path.rglob("*"):
        if not p.is_file():
            continue
        if EXCLUDE_ROOT_FILES and p.parent.resolve() == base_path:
            continue  # 排除根目录文件
        if any(ignored in p.parts for ignored in IGNORE_DIRS):
            continue
        # 检查 IGNORE_PATHS：文件的相对路径是否以某个忽略路径开头
        rel = p.relative_to(base_path)
        rel_str = rel.as_posix()
        if any(rel_str.startswith(ignore_path) for ignore_path in IGNORE_PATHS):
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
    返回 dict: { "folders": [ { "name", "count", "files": [...], "portals": [...] } ], "total": N }
    """
    # groups[folder] = {"files": [...], "portals": {"portal_name": {...}}}
    groups = {}
    for f in files:
        rel = f.relative_to(base_path)
        parts = rel.parts
        folder = parts[0] if len(parts) > 1 else "__root__"
        rel_path = rel.as_posix()

        stem = f.stem.replace("_", " ").replace("-", " ")
        ext = f.suffix.lower()

        # 子路径（不含顶级文件夹和文件名）
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

        # 检查是否属于门户子文件夹
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

    # 排序关键词
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

    # 构建文件夹列表（含 portal）
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
            "count": len(ffiles) + len(portals),  # 文件 + 门户入口
            "files": ffiles,
            "portals": portals,
        })

    return {
        "total": len(files),
        "updateTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "folders": folders,
    }


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

    # 构建 JSON 数据
    data = build_file_data(files, base_path)

    # 替换占位符：只把 JSON 数据注入模板
    html = template.replace("{{SITE_DATA}}", json.dumps(data, ensure_ascii=False))

    # 写入
    output_path = base_path / OUTPUT_FILE
    output_path.write_text(html, encoding="utf-8")
    print(f"[OK] 生成成功：{output_path}")
    print(f"[OK] 共 {data['total']} 个文件 / {len(data['folders'])} 个文件夹")


if __name__ == "__main__":
    generate_html(NOTES_DIR)
