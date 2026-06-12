#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深色模式自动监控（watchdog 事件驱动版）
用法：python watch-dark-mode.py
"""

import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ── 配置 ────────────────────────────────────────────────
SCRIPTS_DIR   = os.path.dirname(os.path.abspath(__file__))
WORKSPACE     = os.path.dirname(SCRIPTS_DIR)
INJECT_TAG    = "<!-- __DARK_MODE_INJECTED__ -->"   # 唯一注入标记
EXCLUDE_FILES = {"dark-mode-demo.html", "smart-dark-mode-demo.html"}
# ──────────────────────────────────────────────────────────


def is_injected(content):
    """判断是否已注入，只认唯一标记注释"""
    return INJECT_TAG in content


def rel_path(script_abs, html_file):
    """计算 html_file 到 script_abs 的相对路径"""
    d = os.path.dirname(html_file)
    return os.path.relpath(script_abs, d).replace("\\", "/")


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

    if is_injected(content):
        return False   # 已有标记，跳过

    script_abs = os.path.join(WORKSPACE, "scripts", "dark-mode-toggle.js")
    src = rel_path(script_abs, filepath)

    # 构造要插入的片段：标记 + script 标签
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
        # 兼容 moved 事件（src_path + dest_path）
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
    print("  深色模式脚本自动监控（watchdog 事件驱动）")
    print("=" * 60)
    print(f"\n工作目录 : {WORKSPACE}")
    print(f"注入标记   : {INJECT_TAG}")
    print(f"防抖间隔   : 5 秒\n")
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
