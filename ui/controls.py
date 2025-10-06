from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QSlider, QPushButton, QColorDialog, QFileDialog,
    QComboBox, QSpinBox
)
from PyQt6.QtCore import Qt


class Controls(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # 文本水印
        self.layout.addWidget(QLabel("文本水印"))
        self.text_input = QLineEdit()
        self.layout.addWidget(self.text_input)

        # 透明度
        self.layout.addWidget(QLabel("透明度"))
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 255)
        self.opacity_slider.setValue(180)
        self.layout.addWidget(self.opacity_slider)

        # 颜色选择
        self.color_button = QPushButton("选择颜色")
        self.color_button.clicked.connect(self.choose_color)
        self.selected_color = (255, 255, 255)
        self.layout.addWidget(self.color_button)

        # 图片水印
        self.image_button = QPushButton("选择图片水印")
        self.image_button.clicked.connect(self.choose_image)
        self.image_path = None
        self.layout.addWidget(self.image_button)

        # 命名规则
        self.layout.addWidget(QLabel("导出命名规则"))
        self.name_rule_combo = QComboBox()
        self.name_rule_combo.addItems(["original", "prefix", "suffix"])
        self.layout.addWidget(self.name_rule_combo)
        self.layout.addWidget(QLabel("前/后缀文本"))
        self.custom_str_input = QLineEdit("_watermarked")
        self.layout.addWidget(self.custom_str_input)

        # 导出格式选择
        self.layout.addWidget(QLabel("导出格式"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PNG", "JPEG"])
        self.layout.addWidget(self.format_combo)

        # JPEG 压缩质量
        self.layout.addWidget(QLabel("JPEG 压缩质量"))
        self.jpeg_quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.jpeg_quality_slider.setRange(1, 100)
        self.jpeg_quality_slider.setValue(90)
        self.layout.addWidget(self.jpeg_quality_slider)

        # 输出缩放比例
        self.layout.addWidget(QLabel("输出图片缩放比例 (%)"))
        self.scale_spinbox = QSpinBox()
        self.scale_spinbox.setRange(10, 500)
        self.scale_spinbox.setValue(100)
        self.layout.addWidget(self.scale_spinbox)

        # 导入/导出按钮
        self.import_btn = QPushButton("导入图片")
        self.export_btn = QPushButton("批量导出")
        self.layout.addWidget(self.import_btn)
        self.layout.addWidget(self.export_btn)

        self.layout.addStretch()

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.selected_color = (color.red(), color.green(), color.blue())

    def choose_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择水印图片", "", "Images (*.png *.jpg *.bmp *.tiff)"
        )
        if path:
            self.image_path = path
