from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt
from PIL import ImageQt


class PreviewWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.label = QLabel("预览区")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # 不再用 setScaledContents(True)，避免 QLabel 跟随图片放大缩小
        self.layout.addWidget(self.label)

        self._pixmap = None  # 缓存原始 pixmap

    def show_image(self, pil_image):
        """显示一张 PIL 图片到预览区"""
        qt_image = ImageQt.ImageQt(pil_image)
        pixmap = QPixmap.fromImage(QImage(qt_image))
        self._pixmap = pixmap
        # 按控件大小缩放一次
        self._update_scaled_pixmap()

    def resizeEvent(self, event):
        """当窗口大小变化时，自动缩放预览图"""
        self._update_scaled_pixmap()
        super().resizeEvent(event)

    def _update_scaled_pixmap(self):
        """根据 label 大小缩放 pixmap"""
        if self._pixmap:
            scaled = self._pixmap.scaled(
                self.label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.label.setPixmap(scaled)
