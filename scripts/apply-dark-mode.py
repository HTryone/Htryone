#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键注入：深色模式切换 + 图片点击放大
批量为所有 HTML 文件添加 dark-mode-toggle.js 和 image-zoom.js

用法：
    python apply-dark-mode.py

说明：
    1. 扫描工作区内所有 .html / .htm 文件
    2. 根据每个文件的位置，自动计算相对路径
    3. 在 </body> 标签前插入注入标记 + <script> 标签
    4. 已注入过的文件会跳过，不会重复插入
    5. 若文件已有 script 但缺标记，会自动补标记并去重
"""

import os
import re

# 配置
WORKSPACE   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXCLUDE     = {"dark-mode-demo.html", "smart-dark-mode-demo.html"}

# 两项注入的独立配置
INJECTIONS = [
    {
        "tag":  "<!-- __DARK_MODE_INJECTED__ -->",
        "file": "scripts/dark-mode-toggle.js",
    },
    {
        "tag":  "<!-- __IMAGE_ZOOM_INJECTED__ -->",
        "file": "scripts/image-zoom.js",
    },
]


def rel_script(filepath, script_rel):
    """计算 filepath 到 scripts/xxx.js 的相对路径"""
    d      = os.path.dirname(filepath)
    target = os.path.join(WORKSPACE, script_rel.replace("/", os.sep))
    return os.path.relpath(target, d).replace("\\", "/")


def _script_pattern(basename):
    """匹配任意路径引用的同名 js 文件的 <script> 标签"""
    return re.compile(
        r'\s*<script[^>]+src=["\'][^"\']*?'
        + re.escape(basename)
        + r'["\'][^>]*></script>\s*\n?',
        re.IGNORECASE,
    )


def inject_file(filepath):
    """
    对单个 HTML 文件执行所有注入。
    返回 True 表示文件被修改了，False 表示跳过。
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"  [读取失败] {filepath}: {e}")
        return False

    changed = False
    for inj in INJECTIONS:
        if inj["tag"] in content:
            continue   # 已有标记，跳过

        basename = os.path.basename(inj["file"])
        pattern  = _script_pattern(basename)

        # 移除所有重复的 script 标签（无论路径如何）
        new_content = pattern.sub("", content)
        if new_content != content:
            content = new_content
            changed = True

        # 注入：标记 + script
        src    = rel_script(filepath, inj["file"])
        insert = f"\n{inj['tag']}\n<script src=\"{src}\"></script>\n"

        pos = content.rfind("</body>")
        if pos != -1:
            content = content[:pos] + insert + content[pos:]
        else:
            content = content.rstrip() + insert

        changed = True

    if not changed:
        return False

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    rel = os.path.relpath(filepath, WORKSPACE)
    print(f"  [注入/修复] {rel}")
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
    print(f"\n  扫描完成：注入/修复 {count} 个文件\n")


def main():
    print("=" * 60)
    print("  一键注入工具（深色模式 + 图片缩放）")
    print("=" * 60)
    print(f"\n工作目录 : {WORKSPACE}")
    for inj in INJECTIONS:
        sf = os.path.join(WORKSPACE, inj["file"].replace("/", os.sep))
        ok = "✓" if os.path.exists(sf) else "✗ 缺失!"
        print(f"  {ok}  {inj['file']}")
    print()

    # 检查依赖脚本是否存在
    for inj in INJECTIONS:
        sf = os.path.join(WORKSPACE, inj["file"].replace("/", os.sep))
        if not os.path.exists(sf):
            print(f"错误: 脚本文件不存在: {sf}")
            return

    print("-" * 60)
    scan_all()

    print("现在打开任意 HTML 文件：")
    print("  🌞→🌙→⚡ 右上角主题切换按钮")
    print("  🔍 点击图片放大悬浮查看")


if __name__ == "__main__":
    main()
