# ui/image_list.py

import sys
import os
from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QMenu
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon
from pathlib import Path

# 动态添加项目根目录到Python路径，以便能导入watermark模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --- 新增：从 FileManager 导入格式列表 ---
from watermark.file_manager import FileManager
# --- 新增结束 ---


class ImageList(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAcceptDrops(True)
        self.setDragEnabled(False)
        self.setDropIndicatorShown(True)
        self.fileDroppedCallback = None

    def setFileDroppedCallback(self, callback):
        """设置文件拖拽后的回调"""
        self.fileDroppedCallback = callback

    def dragEnterEvent(self, event):
        """拖拽进入时触发"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """拖拽移动时触发"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        """拖拽释放时触发"""
        if event.mimeData().hasUrls():
            files = []
            for url in event.mimeData().urls():
                f = Path(url.toLocalFile())
                
                # --- 修改：使用导入的格式列表进行判断 ---
                if f.is_file() and f.suffix.lower() in FileManager.SUPPORTED_INPUT_FORMATS:
                    files.append(str(f))
                elif f.is_dir():
                    for img in f.iterdir():
                        if img.suffix.lower() in FileManager.SUPPORTED_INPUT_FORMATS:
                            files.append(str(img))
                # --- 修改结束 ---

            if self.fileDroppedCallback and files:
                self.fileDroppedCallback(files)
            event.acceptProposedAction()
        else:
            event.ignore()

    def add_image(self, path: str):
        path_str = str(path)
        if not Path(path_str).exists():
            print(f"[WARN] 文件不存在: {path_str}")
            return
        try:
            pixmap = QPixmap(path_str)
            if pixmap.isNull():
                print(f"[WARN] 无法加载图片: {path_str}")
                return
            pixmap = pixmap.scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatio)
            item = QListWidgetItem(Path(path_str).name)
            item.setIcon(QIcon(pixmap))
            item.setData(Qt.ItemDataRole.UserRole, path_str)
            self.addItem(item)
        except Exception as e:
            print(f"[ERROR] 添加图片失败 {path_str}: {e}")

    def get_selected_image(self) -> str:
        """返回当前选中的图片路径"""
        item = self.currentItem()
        if item:
            return item.data(Qt.ItemDataRole.UserRole)
        return None

    def contextMenuEvent(self, event):
        """重写此方法以响应右键点击"""
        clicked_item = self.itemAt(event.pos())
        if clicked_item:
            menu = QMenu(self)
            delete_action = menu.addAction("删除")
            chosen_action = menu.exec(event.globalPos())
            if chosen_action == delete_action:
                self.delete_item(clicked_item)

    def delete_item(self, item_to_delete: QListWidgetItem):
        """从列表中删除指定的项"""
        row = self.row(item_to_delete)
        self.takeItem(row)