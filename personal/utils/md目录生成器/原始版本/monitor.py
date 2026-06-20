"""
文件监控器：当文件被修改、新建或删除时，自动刷新 _Index.md
支持格式：.md, .doc, .docx, .ppt, .pptx, .html, .htm, .xls, .xlsx, .csv, .pdf
需要先安装 watchdog：pip install watchdog
"""
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from update_index import generate_md_index, SCAN_EXTENSIONS  # 引用上面的脚本

class IndexHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        # 只关心支持的文件格式
        if event.is_directory:
            return
        
        # 检查文件扩展名
        ext = Path(event.src_path).suffix.lower()
        if ext not in SCAN_EXTENSIONS:
            return
        
        # 避免重复触发
        if event.event_type in ['modified', 'created', 'deleted', 'moved']:
            print(f"🔄 检测到变化 [{event.event_type}]: {Path(event.src_path).name}")
            generate_md_index(".")

if __name__ == "__main__":
    path = "."  # 监控当前目录（及所有子目录）
    observer = Observer()
    observer.schedule(IndexHandler(), path, recursive=True)
    observer.start()
    print("👀 监控已启动，正在监视笔记目录...")
    print("💡 提示：支持格式文件的增删改都会自动刷新索引。")
    print(f"   支持格式：{', '.join(SCAN_EXTENSIONS)}")
    print("  按 Ctrl+C 可停止监控。\n")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n🛑 监控已停止。")
    observer.join()
