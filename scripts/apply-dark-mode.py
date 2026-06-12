#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量为所有 HTML 文件添加深色模式切换脚本

用法：
    python apply-dark-mode.py

说明：
    1. 扫描工作区内所有 .html / .htm 文件（排除 dark-mode-demo.html）
    2. 根据每个文件的位置，自动计算到 dark-mode.js 的相对路径
    3. 在 </body> 标签前插入 <script src="相对路径/dark-mode.js"></script>
    4. 已添加过的文件会跳过，不会重复插入
"""

import os
import re

# 配置
# apply-dark-mode.py 在 scripts/ 目录下，工作区是它的父目录
WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT_FILE = "scripts/dark-mode-toggle.js"
MARKER = "scripts/dark-mode-toggle.js"  # 用于判断是否已添加
EXCLUDE_FILES = {"dark-mode-demo.html", "smart-dark-mode-demo.html"}  # 排除的文件


def get_relative_path(from_file, to_file):
    """
    计算从 from_file 到 to_file 的相对路径
    """
    from_dir = os.path.dirname(from_file)
    rel = os.path.relpath(to_file, from_dir)
    # 统一用正斜杠
    return rel.replace("\\", "/")


def has_dark_mode_script(content):
    """
    检查 HTML 内容中是否已包含深色模式脚本引用
    """
    return MARKER in content


def insert_script(content, script_src):
    """
    在 </body> 标签之前插入脚本引用
    """
    # 在 </body> 之前插入，处理可能有空格/换行的情况
    # 也处理 </body></html> 连在一起的情况
    pattern = re.compile(r'(<script>.*?</script>)(</body>)', re.DOTALL)
    match = pattern.search(content)

    if match:
        # 在最后一个 </script></body> 的 </body> 前插入
        # 找到最后一个 </body>
        last_body_pos = content.rfind('</body>')
        if last_body_pos != -1:
            insert = f'\n<script src="{script_src}"></script>\n'
            return content[:last_body_pos] + insert + content[last_body_pos:]

    # 兜底：直接找最后的 </body>
    last_body_pos = content.rfind('</body>')
    if last_body_pos != -1:
        insert = f'\n<script src="{script_src}"></script>\n'
        return content[:last_body_pos] + insert + content[last_body_pos:]

    # 如果连 </body> 都没有，在末尾追加
    if content.strip().endswith('</html>'):
        insert = f'\n<script src="{script_src}"></script>\n'
        return content.rstrip()[:-7] + insert + '</html>\n'

    return content + f'\n<script src="{script_src}"></script>\n'


def remove_old_script(content):
    """
    移除旧的深色模式脚本引用（包括旧路径的 dark-mode.js 和 dark-mode-toggle.js）
    """
    # 匹配旧的 dark-mode.js 引用（根目录下）
    content = re.sub(r'\s*<script\s+src="[^"]*dark-mode\.js"[^>]*></script>\s*', '\n', content)
    # 匹配旧的 dark-mode-toggle.js 引用（根目录下）
    content = re.sub(r'\s*<script\s+src="[^"]*dark-mode-toggle\.js"[^>]*></script>\s*', '\n', content)
    return content


def process_file(filepath, script_path):
    """
    处理单个 HTML 文件
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 先移除旧的 dark-mode.js 引用
    content = remove_old_script(content)

    if has_dark_mode_script(content):
        print(f"  [跳过] 已包含深色模式脚本: {filepath}")
        # 即使跳过，也要保存移除旧引用后的内容
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return False

    rel_path = get_relative_path(filepath, script_path)
    new_content = insert_script(content, rel_path)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"  [已添加] {filepath}  →  <script src=\"{rel_path}\"></script>")
    return True


def main():
    print("=" * 60)
    print("  深色模式脚本批量添加工具")
    print("=" * 60)
    print(f"\n工作目录: {WORKSPACE}")
    print(f"脚本文件: {SCRIPT_FILE}")
    print()

    script_path = os.path.join(WORKSPACE, SCRIPT_FILE)

    if not os.path.exists(script_path):
        print(f"错误: 脚本文件不存在: {script_path}")
        return

    # 收集所有 HTML 文件
    html_files = []
    for root, dirs, files in os.walk(WORKSPACE):
        # 排除 .git 和 .workbuddy 目录
        dirs[:] = [d for d in dirs if d not in {'.git', '.workbuddy', 'node_modules'}]

        for fname in files:
            if fname.lower().endswith(('.html', '.htm')) and fname not in EXCLUDE_FILES:
                full_path = os.path.join(root, fname)
                html_files.append(full_path)

    # 按路径排序，方便查看
    html_files.sort()

    print(f"找到 {len(html_files)} 个 HTML 文件:")
    for fp in html_files:
        rel = os.path.relpath(fp, WORKSPACE)
        print(f"  - {rel}")

    print()
    print("开始处理...")
    print("-" * 60)

    added = 0
    skipped = 0

    for fp in html_files:
        if process_file(fp, script_path):
            added += 1
        else:
            skipped += 1

    print("-" * 60)
    print(f"\n处理完成: 新增 {added} 个, 跳过 {skipped} 个")
    print("\n现在打开任意 HTML 文件，右上角会出现主题切换按钮。")
    print("点击按钮循环切换: 🌞 原色 → 🌙 固定深色 → ⚡ 智能深色")


if __name__ == "__main__":
    main()
