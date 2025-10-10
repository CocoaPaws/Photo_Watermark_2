# ui/controls.py

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QSlider, QPushButton, QSpinBox,
    QHBoxLayout, QCheckBox, QComboBox, QSizePolicy, QGridLayout, QColorDialog,
    QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

# 动态添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from watermark.watermark_image import ImageWatermark


class Controls(QWidget):
    # 定义一个自定义信号，当任何控件的值改变时，就发射这个信号
    settingsChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # --- 创建控件 ---
        self.layout.addWidget(QLabel("文本水印"))
        self.text_input = QLineEdit()
        self.layout.addWidget(self.text_input)

        self.layout.addWidget(QLabel("透明度"))
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 255)
        self.opacity_slider.setValue(180)
        self.layout.addWidget(self.opacity_slider)

        self.color_button = QPushButton("选择颜色")
        self.selected_color = (255, 255, 255)
        self.layout.addWidget(self.color_button)

        self.layout.addWidget(QLabel("相对字号 (%)"))
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(1, 50)
        self.font_size_spin.setValue(5)
        self.layout.addWidget(self.font_size_spin)

        self.bold_checkbox = QCheckBox("粗体")
        self.italic_checkbox = QCheckBox("斜体")
        font_style_layout = QHBoxLayout()
        font_style_layout.addWidget(self.bold_checkbox)
        font_style_layout.addWidget(self.italic_checkbox)
        self.layout.addLayout(font_style_layout)

        # --- 图片水印UI ---
        self.image_button = QPushButton("选择图片水印")
        self.image_watermark_obj: ImageWatermark | None = None
        self.layout.addWidget(self.image_button)

        self.image_wm_display_widget = QWidget()
        self.image_wm_layout = QHBoxLayout()
        self.image_wm_layout.setContentsMargins(0, 5, 0, 0)
        self.image_wm_display_widget.setLayout(self.image_wm_layout)
        self.image_wm_label = QLabel()
        self.image_wm_label.setStyleSheet("color: #666;")
        self.clear_image_wm_btn = QPushButton("移除")
        self.image_wm_layout.addWidget(self.image_wm_label)
        self.image_wm_layout.addStretch()
        self.image_wm_layout.addWidget(self.clear_image_wm_btn)
        self.layout.addWidget(self.image_wm_display_widget)
        self.image_wm_display_widget.hide()

        # --- 新增：图片水印缩放UI ---
        self.image_scale_widget = QWidget()
        self.image_scale_layout = QVBoxLayout()
        self.image_scale_layout.setContentsMargins(0, 5, 0, 0)
        self.image_scale_widget.setLayout(self.image_scale_layout)
        self.image_scale_label_title = QLabel("图片水印缩放")
        self.image_scale_layout.addWidget(self.image_scale_label_title)
        scale_slider_layout = QHBoxLayout()
        self.image_scale_slider = QSlider(Qt.Orientation.Horizontal)
        self.image_scale_slider.setRange(1, 200)
        self.image_scale_slider.setValue(15)
        self.image_scale_value_label = QLabel("15 %")
        scale_slider_layout.addWidget(self.image_scale_slider)
        scale_slider_layout.addWidget(self.image_scale_value_label)
        self.image_scale_layout.addLayout(scale_slider_layout)
        self.layout.addWidget(self.image_scale_widget)
        self.image_scale_widget.hide()
        # --- 新增结束 ---

        self.layout.addWidget(QLabel("水印模板"))
        self.template_combo = QComboBox()
        self.layout.addWidget(self.template_combo)

        template_btn_layout = QHBoxLayout()
        self.save_template_btn = QPushButton("保存为模板")
        self.delete_template_btn = QPushButton("删除此模板")
        template_btn_layout.addWidget(self.save_template_btn)
        template_btn_layout.addWidget(self.delete_template_btn)
        self.layout.addLayout(template_btn_layout)

        self.layout.addWidget(QLabel("水印位置"))
        self.position_buttons = {}
        self.current_position = "左上"
        grid = QGridLayout()
        positions = [("左上", 0, 0), ("上中", 0, 1), ("右上", 0, 2), ("左中", 1, 0), ("中心", 1, 1), ("右中", 1, 2), ("左下", 2, 0), ("下中", 2, 1), ("右下", 2, 2)]
        for name, r, c in positions:
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            grid.addWidget(btn, r, c)
            self.position_buttons[name] = btn
        self.layout.addLayout(grid)
        self.position_buttons[self.current_position].setChecked(True)

        self.layout.addWidget(QLabel("导出命名规则"))
        self.name_rule_combo = QComboBox()
        self.name_rule_combo.addItems(["original", "prefix", "suffix"])
        self.layout.addWidget(self.name_rule_combo)
        self.layout.addWidget(QLabel("前/后缀文本"))
        self.custom_str_input = QLineEdit("_watermarked")
        self.layout.addWidget(self.custom_str_input)
        self.layout.addWidget(QLabel("导出格式"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PNG", "JPEG"])
        self.layout.addWidget(self.format_combo)
        self.layout.addWidget(QLabel("JPEG 压缩质量"))
        self.jpeg_quality_slider = QSlider(Qt.Orientation.Horizontal)
        self.jpeg_quality_slider.setRange(1, 100)
        self.jpeg_quality_slider.setValue(90)
        self.layout.addWidget(self.jpeg_quality_slider)
        self.layout.addWidget(QLabel("输出图片缩放比例 (%)"))
        self.scale_spinbox = QSpinBox()
        self.scale_spinbox.setRange(10, 500)
        self.scale_spinbox.setValue(100)
        self.layout.addWidget(self.scale_spinbox)
        self.export_btn = QPushButton("批量导出")

        import_layout = QHBoxLayout()
        self.import_btn = QPushButton("导入图片")
        self.import_folder_btn = QPushButton("导入文件夹") # 新增按钮
        import_layout.addWidget(self.import_btn)
        import_layout.addWidget(self.import_folder_btn)
        self.layout.addLayout(import_layout)
        
        self.layout.addWidget(self.export_btn)
        self.layout.addStretch()

        # --- 绑定内部信号 ---
        self.text_input.textChanged.connect(self.settingsChanged.emit)
        self.opacity_slider.valueChanged.connect(self.settingsChanged.emit)
        self.font_size_spin.valueChanged.connect(self.settingsChanged.emit)
        self.bold_checkbox.stateChanged.connect(self.settingsChanged.emit)
        self.italic_checkbox.stateChanged.connect(self.settingsChanged.emit)
        self.color_button.clicked.connect(self.choose_color)
        self.image_button.clicked.connect(self.choose_image)
        self.clear_image_wm_btn.clicked.connect(self.clear_image_watermark)
        self.image_scale_slider.valueChanged.connect(self._on_image_scale_changed)
        for btn in self.position_buttons.values():
            btn.clicked.connect(self.settingsChanged.emit)

    def choose_color(self):
        color = QColorDialog.getColor(QColor(*self.selected_color))
        if color.isValid():
            self.selected_color = (color.red(), color.green(), color.blue())
            self.settingsChanged.emit()

    def choose_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择水印图片", "", "Images (*.png *.jpg *.jpeg *.bmp *.tiff)")
        if path:
            try:
                self.image_watermark_obj = ImageWatermark(watermark_path=path)
                self.update_image_watermark_display(path)
                self.settingsChanged.emit()
            except Exception as e:
                print(f"[ERROR] 加载水印图片失败: {e}")
                self.image_watermark_obj = None
                self.update_image_watermark_display(None)

    def clear_image_watermark(self):
        self.image_watermark_obj = None
        self.update_image_watermark_display(None)
        self.settingsChanged.emit()

    def update_image_watermark_display(self, path: str | None):
        if path:
            filename = Path(path).name
            self.image_wm_label.setText(filename)
            self.image_wm_label.setToolTip(path)
            self.image_wm_display_widget.show()
            self.image_scale_widget.show()
        else:
            self.image_wm_display_widget.hide()
            self.image_scale_widget.hide()

    def _on_image_scale_changed(self, value):
        self.image_scale_value_label.setText(f"{value} %")
        self.settingsChanged.emit()

    def set_position(self, pos_name: str):
        if self.current_position == pos_name: return
        self.current_position = pos_name
        for name, btn in self.position_buttons.items():
            btn.setChecked(name == pos_name)

    def update_template_list(self, templates: list[str]):
        current_selection = self.template_combo.currentText()
        self.template_combo.blockSignals(True)
        self.template_combo.clear()
        self.template_combo.addItems(["- 选择模板 -"] + sorted(templates))
        index = self.template_combo.findText(current_selection)
        if index != -1:
            self.template_combo.setCurrentIndex(index)
        self.template_combo.blockSignals(False)