from PyQt6.QtWidgets import QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon
from pathlib import Path


class ImageList(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 关键：启用接收拖拽
        self.setAcceptDrops(True)
        self.setDragEnabled(False)  # 禁止内部拖动 item
        self.setDropIndicatorShown(True)

        # 拖拽完成后回调（由 MainWindow 设置）
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
        """拖拽移动时触发（必须有，否则 dropEvent 不执行）"""
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
                    # 如果拖进来的是文件夹，递归加载里面的图片
                    for img in f.iterdir():
                        if img.suffix.lower() in [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]:
                            files.append(str(img))
            if self.fileDroppedCallback and files:
                self.fileDroppedCallback(files)  # 交给 MainWindow 处理
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