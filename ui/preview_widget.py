from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPixmap, QImage, QMouseEvent
from PIL import ImageQt


class PreviewWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.label = QLabel("预览区")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.label)

        self._pixmap = None
        self._dragging = False
        self._wm_offset = QPoint(0, 0)
        self._wm_pos = QPoint(0, 0)
        self.drag_callback = None  # 拖拽更新回调

    def show_image(self, pil_image, wm_pos=None):
        qt_image = ImageQt.ImageQt(pil_image)
        pixmap = QPixmap.fromImage(QImage(qt_image))
        self._pixmap = pixmap
        if wm_pos:
            self._wm_pos = QPoint(*wm_pos)
        self._update_scaled_pixmap()

    def resizeEvent(self, event):
        self._update_scaled_pixmap()
        super().resizeEvent(event)

    def _update_scaled_pixmap(self):
        if self._pixmap:
            scaled = self._pixmap.scaled(
                self.label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.label.setPixmap(scaled)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._wm_offset = event.pos() - self._wm_pos

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._dragging:
            self._wm_pos = event.pos() - self._wm_offset
            if self.drag_callback:
                self.drag_callback((self._wm_pos.x(), self._wm_pos.y()))

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
