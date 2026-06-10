"""
二级目录索引生成器（用于子文件夹）
功能：扫描当前目录的 HTML/PDF 文件，生成简洁的文件列表

支持格式：.html, .htm, .pdf
用法：放在任意子文件夹中运行即可生成该文件夹的索引
"""
from pathlib import Path
from datetime import datetime

# ==================== 配置区 ====================
NOTES_DIR = "."           # 当前目录
OUTPUT_FILE = "目录.md"   # 输出文件名（自动排除自身 + 对应的 html 版本）
IGNORE_FILES = {"index.html", "index.md"}  # 固定排除的文件名
SCAN_EXTENSIONS = {".html", ".htm", ".pdf"}
PINNED_KEYWORDS = ["目录", "index", "Index", "README"]  # 含这些关键词的文件排前面
FILE_ICONS = {".html": "🌐", ".htm": "🌐", ".pdf": "📕"}
# ================================================


def generate_index(base_dir):
    base_path = Path(base_dir).resolve()
    folder_name = base_path.name or "root"
    print(f"[INFO] 正在扫描：{base_path}")

    # 自动排除输出文件自身（md + html 版本）
    self_exclude = {OUTPUT_FILE, Path(OUTPUT_FILE).stem + ".html"}

    # 收集当前目录下的文件（不递归子目录）
    files = [
        p for p in base_path.iterdir()
        if p.is_file()
        and p.name not in IGNORE_FILES | self_exclude
        and p.suffix.lower() in SCAN_EXTENSIONS
    ]

    if not files:
        print("[WARN] 未找到任何支持的文件。")
        return

    # 排序：含关键词优先 → 其余按名称字母序
    files.sort(key=lambda f: (
        0 if any(kw in f.name for kw in PINNED_KEYWORDS) else 1,
        f.name
    ))

    # 生成内容
    lines = [
        f"# 📁 {folder_name}",
        "",
        f"> 📅 更新：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 📄 共 **{len(files)}** 个文件",
        "",
        "---",
        "",
        "## 📑 文件列表",
        "",
    ] + [f"- {FILE_ICONS.get(f.suffix.lower(), '📄')} [{f.name}]({f.name})" for f in files]
    lines.append("")

    # 写入文件
    output_path = base_path / OUTPUT_FILE
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[OK] 索引生成成功！")
    print(f"[OK] 文件位置：{output_path}")


if __name__ == "__main__":
    generate_index(NOTES_DIR)
