#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理注入残留：
  1. 移除 <!-- @#@ --> 等废弃标记
  2. 每个注入只保留标记后紧跟的一个 script 标签
用法：python scripts/cleanup-injections.py
"""

import os
import re

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INJECTIONS = [
    ("<!-- __DARK_MODE_INJECTED__ -->", "dark-mode-toggle.js"),
    ("<!-- __IMAGE_ZOOM_INJECTED__ -->", "image-zoom.js"),
]

# 需要移除的废弃标记
JUNK_MARKERS = ["<!-- @#@ -->"]


def _script_pattern(basename):
    return re.compile(
        r'\s*<script[^>]+src=["\'][^"\']*?'
        + re.escape(basename)
        + r'["\'][^>]*></script>\s*\n?',
        re.IGNORECASE,
    )


def cleanup_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return False

    original = content
    changed = False

    # 1. 移除废弃标记
    for junk in JUNK_MARKERS:
        if junk in content:
            content = content.replace(junk, "")
            changed = True

    # 2. 每个注入去重
    for tag, basename in INJECTIONS:
        pattern = _script_pattern(basename)
        matches = list(pattern.finditer(content))
        if len(matches) <= 1:
            continue

        # 优先保留标记后紧跟的那个
        keep = matches[0]
        if tag in content:
            tag_pos = content.index(tag)
            for m in matches:
                if m.start() > tag_pos:
                    keep = m
                    break

        for m in reversed(matches):
            if m is keep:
                continue
            content = content[:m.start()] + content[m.end():]
        changed = True

    if not changed:
        return False

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    rel = os.path.relpath(filepath, WORKSPACE)
    print(f"  [清理] {rel}")
    return True


def main():
    count = 0
    for root, dirs, files in os.walk(WORKSPACE):
        dirs[:] = [d for d in dirs if d not in {".git", ".workbuddy", "node_modules"}]
        for fname in files:
            if fname.lower().endswith((".html", ".htm")):
                fp = os.path.join(root, fname)
                if cleanup_file(fp):
                    count += 1
    print(f"\n  清理完成：处理了 {count} 个文件\n")


if __name__ == "__main__":
    main()
