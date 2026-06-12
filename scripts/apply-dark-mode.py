#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量为所有 HTML 文件添加深色模式切换脚本

用法：
    python apply-dark-mode.py

说明：
    1. 扫描工作区内所有 .html / .htm 文件（排除 dark-mode-demo.html）
    2. 根据每个文件的位置，自动计算到 dark-mode-toggle.js 的相对路径
    3. 在 </body> 标签前插入注入标记 + <script> 标签
    4. 已注入过的文件会跳过，不会重复插入
"""

import os

# 配置
WORKSPACE   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT_FILE = "scripts/dark-mode-toggle.js"
INJECT_TAG  = "<!-- __DARK_MODE_INJECTED__ -->"   # 唯一注入标记
EXCLUDE     = {"dark-mode-demo.html", "smart-dark-mode-demo.html"}


def has_inject_tag(content):
    """检查是否已包含注入标记（只认标记，不解析 <script> 标签）"""
    return INJECT_TAG in content


def rel_script(filepath):
    """计算 filepath 到 scripts/dark-mode-toggle.js 的相对路径"""
    d      = os.path.dirname(filepath)
    target = os.path.join(WORKSPACE, "scripts", "dark-mode-toggle.js")
    return os.path.relpath(target, d).replace("\\", "/")


def inject_file(filepath):
    """
    对单个 HTML 文件执行注入。
    返回 True 表示文件被修改了，False 表示跳过（已注入或出错）。
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"  [读取失败] {filepath}: {e}")
        return False

    if has_inject_tag(content):
        return False   # 已有标记，跳过

    src = rel_script(filepath)
    insert = f"\n{INJECT_TAG}\n<script src=\"{src}\"></script>\n"

    # 在 </body> 前插入，没有 </body> 就追加末尾
    pos = content.rfind("</body>")
    if pos != -1:
        new_content = content[:pos] + insert + content[pos:]
    else:
        new_content = content.rstrip() + insert

    # 只有内容真的变了才写文件
    if new_content == content:
        return False

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)

    rel = os.path.relpath(filepath, WORKSPACE)
    print(f"  [注入] {rel}  →  {src}")
    return True


def scan_all():
    """全量扫描并注入"""
    count = 0
    for root, dirs, files in os.walk(WORKSPACE):
        dirs[:] = [d for d in dirs if d not in {".git", ".workbuddy", "node_modules"}]
        for fname in files:
            if fname.lower().endswith((".html", ".htm")) and fname not in EXCLUDE:
                fp = os.path.join(root, fname)
                if inject_file(fp):
                    count += 1
    print(f"\n  扫描完成：注入 {count} 个文件\n")


def main():
    print("=" * 60)
    print("  深色模式脚本批量注入工具")
    print("=" * 60)
    print(f"\n工作目录 : {WORKSPACE}")
    print(f"脚本文件 : {SCRIPT_FILE}")
    print(f"注入标记 : {INJECT_TAG}\n")
    print("-" * 60)

    script_path = os.path.join(WORKSPACE, SCRIPT_FILE)
    if not os.path.exists(script_path):
        print(f"错误: 脚本文件不存在: {script_path}")
        return

    scan_all()

    print("现在打开任意 HTML 文件，右上角会出现主题切换按钮。")
    print("点击按钮循环切换: 🌞 原色 → 🌙 固定深色 → ⚡ 智能深色")


if __name__ == "__main__":
    main()
