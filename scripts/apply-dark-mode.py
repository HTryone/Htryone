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
"""

import os

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

        # 兼容旧版无标记的手动注入：检查 script 标签是否已存在
        # 如果内容中已经引用了该 js 文件但没有标记，补上标记后跳过注入
        script_filename = os.path.basename(inj["file"])
        if script_filename in content:
            # 已有引用但缺标记 → 不重复注入，只静默跳过
            # （如果你希望给旧文件自动补标记，可改为下面注释的代码）
            continue

        src = rel_script(filepath, inj["file"])
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
    print(f"  [注入] {rel}")
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
