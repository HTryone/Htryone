"""
网页索引 HTML 生成器（博客风格）
功能：扫描目录的 HTML/PDF 文件，输出 JSON 数据到模板，生成 home.html
模板：home_template.html（负责所有样式和渲染逻辑）

用法：python generate_index_html.py
"""

from pathlib import Path
from datetime import datetime
import json

# ==================== 配置区（可按需修改） ====================
NOTES_DIR = "."              # 笔记根目录（在目标目录执行即可）
OUTPUT_FILE = "home.html"    # 生成的索引文件名
TEMPLATE_FILE = "home_template.html"  # 模板文件名

# 不想被索引的文件夹名称
IGNORE_DIRS = {".git", ".workbuddy", ".obsidian", "assets", "images", "附件",
                "__pycache__", "templates", "build", "node_modules"}
# 不想被索引的文件名
IGNORE_FILES = {"index.html", "home.html", "home_template.html"}
# 要扫描的文件扩展名
SCAN_EXTENSIONS = {".html", ".htm", ".pdf"}
# =====================================================================


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


def build_file_data(files, base_path):
    """
    扫描文件列表，构建 JSON 数据。
    返回 dict: { "folders": [ { "name", "count", "files": [...] } ], "total": N }
    每个文件: { "name", "path", "ext", "type", "subPath" }
    """
    # 按顶级文件夹分组
    groups = {}
    for f in files:
        rel = f.relative_to(base_path)
        parts = rel.parts
        folder = parts[0] if len(parts) > 1 else "__root__"

        stem = f.stem.replace("_", " ").replace("-", " ")
        ext = f.suffix.lower()

        # 子路径（不含顶级文件夹和文件名）
        sub_path = "/".join(parts[1:-1]) if len(parts) > 2 else ""

        file_info = {
            "name": stem,
            "path": "./" + rel.as_posix(),
            "ext": ext,
            "type": {"html": "HTML", "htm": "HTML", "pdf": "PDF"}.get(ext.lstrip("."), ""),
            "subPath": sub_path,
        }

        if folder not in groups:
            groups[folder] = []
        groups[folder].append(file_info)

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

    # 构建文件夹列表
    folders = []
    for fname in sorted(groups.keys(), key=folder_sort_key):
        ffiles = sorted(groups[fname], key=file_sort_key)
        folders.append({
            "name": fname if fname != "__root__" else "根目录",
            "count": len(ffiles),
            "files": ffiles,
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
