# ui/image_list.py

from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QMenu
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon
from pathlib import Path


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
                if f.is_file() and f.suffix.lower() in [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]:
                    files.append(str(f))
                elif f.is_dir():
                    for img in f.iterdir():
                        if img.suffix.lower() in [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]:
                            files.append(str(img))
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

    # --- 新增：处理右键菜单 ---
    def contextMenuEvent(self, event):
        """重写此方法以响应右键点击"""
        # 获取被右键点击的列表项
        clicked_item = self.itemAt(event.pos())
        
        # 如果确实点在了一个项目上
        if clicked_item:
            # 创建一个菜单
            menu = QMenu(self)
            
            # 添加一个名为“删除”的动作
            delete_action = menu.addAction("删除")
            
            # 在鼠标光标的全局位置显示菜单，并等待用户操作
            # exec() 会返回用户点击的那个动作
            chosen_action = menu.exec(event.globalPos())
            
            # 如果用户点击的是“删除”动作
            if chosen_action == delete_action:
                self.delete_item(clicked_item)

    def delete_item(self, item_to_delete: QListWidgetItem):
        """从列表中删除指定的项"""
        # 获取该项所在的行号
        row = self.row(item_to_delete)
        # 从该行移除这个项。这个操作会自动触发 currentItemChanged 信号
        self.takeItem(row)
    # --- 新增结束 ---