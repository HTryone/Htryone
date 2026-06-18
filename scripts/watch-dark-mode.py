#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键监控注入（watchdog 事件驱动版）
监听工作区新增/修改的 HTML 文件，自动注入 dark-mode-toggle.js + image-zoom.js

用法：python watch-dark-mode.py
"""

import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ── 配置 ────────────────────────────────────────────────
SCRIPTS_DIR   = os.path.dirname(os.path.abspath(__file__))
WORKSPACE     = os.path.dirname(SCRIPTS_DIR)
EXCLUDE_FILES = {"dark-mode-demo.html", "smart-dark-mode-demo.html"}

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
# ──────────────────────────────────────────────────────────


def rel_path(script_abs, html_file):
    """计算 html_file 到 script_abs 的相对路径"""
    d = os.path.dirname(html_file)
    return os.path.relpath(script_abs, d).replace("\\", "/")


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
            continue

        script_filename = os.path.basename(inj["file"])
        if script_filename in content:
            continue   # 已有引用但缺标记，静默跳过

        script_abs = os.path.join(WORKSPACE, inj["file"].replace("/", os.sep))
        src = rel_path(script_abs, filepath)
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
    """启动时全量扫描一次"""
    count = 0
    for root, dirs, files in os.walk(WORKSPACE):
        dirs[:] = [d for d in dirs if d not in {".git", ".workbuddy", "node_modules"}]
        for fname in files:
            if fname.lower().endswith((".html", ".htm")) and fname not in EXCLUDE_FILES:
                fp = os.path.join(root, fname)
                if inject_file(fp):
                    count += 1
    print(f"  启动扫描完成：注入 {count} 个文件\n")


# ── watchdog 事件处理 ──────────────────────────────────

class Handler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self._last = {}   # 防抖：filepath -> 最后处理时间戳

    def _debounce(self, fp):
        now = time.time()
        if now - self._last.get(fp, 0) < 5:
            return False
        self._last[fp] = now
        return True

    def _is_target(self, fp):
        f = os.path.basename(fp).lower()
        return f.endswith((".html", ".htm")) and f not in EXCLUDE_FILES

    def on_any_event(self, event):
        if event.is_directory:
            return
        fp = getattr(event, "dest_path", None) or event.src_path
        fp = os.path.normpath(fp)
        if not self._is_target(fp) or not self._debounce(fp):
            return
        # 等文件写完再读
        time.sleep(0.8)
        if os.path.exists(fp):
            inject_file(fp)


def main():
    print("=" * 60)
    print("  一键监控注入（深色模式 + 图片缩放）")
    print("=" * 60)
    print(f"\n工作目录   : {WORKSPACE}")
    print(f"防抖间隔   : 5 秒")
    for inj in INJECTIONS:
        sf = os.path.join(WORKSPACE, inj["file"].replace("/", os.sep))
        ok = "✓" if os.path.exists(sf) else "✗ 缺失!"
        print(f"  {ok}  {inj['file']}")
    print()
    print("-" * 60)

    scan_all()

    observer = Observer()
    observer.schedule(Handler(), WORKSPACE, recursive=True)
    observer.start()
    print("监控已启动，按 Ctrl+C 停止...\n")
    print("-" * 60)

    try:
        while observer.is_alive():
            observer.join(1)
    except KeyboardInterrupt:
        print("\n正在停止...")
    finally:
        observer.stop()
        observer.join()
        print("监控已停止。")


if __name__ == "__main__":
    main()
