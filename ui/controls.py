# ui/controls.py

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QSlider, QPushButton, QSpinBox,
    QHBoxLayout, QCheckBox, QComboBox, QSizePolicy, QGridLayout, QColorDialog,
    QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal # <--- 1. 导入 pyqtSignal
from PyQt6.QtGui import QColor


class Controls(QWidget):
    # 2. 定义一个自定义信号，当任何控件的值改变时，就发射这个信号
    settingsChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # --- 创建控件 (这部分不变) ---
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

        self.layout.addWidget(QLabel("字号"))
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 200)
        self.font_size_spin.setValue(32)
        self.layout.addWidget(self.font_size_spin)

        self.bold_checkbox = QCheckBox("粗体")
        self.italic_checkbox = QCheckBox("斜体")
        font_style_layout = QHBoxLayout()
        font_style_layout.addWidget(self.bold_checkbox)
        font_style_layout.addWidget(self.italic_checkbox)
        self.layout.addLayout(font_style_layout)

        self.image_button = QPushButton("选择图片水印")
        self.image_path = None
        self.layout.addWidget(self.image_button)
        
        self.layout.addWidget(QLabel("水印位置"))
        self.position_buttons = {}
        self.current_position = "左上"
        grid = QGridLayout()
        positions = [
            ("左上", 0, 0), ("上中", 0, 1), ("右上", 0, 2),
            ("左中", 1, 0), ("中心", 1, 1), ("右中", 1, 2),
            ("左下", 2, 0), ("下中", 2, 1), ("右下", 2, 2),
        ]
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

        self.import_btn = QPushButton("导入图片")
        self.export_btn = QPushButton("批量导出")
        self.layout.addWidget(self.import_btn)
        self.layout.addWidget(self.export_btn)
        self.layout.addStretch()

        # --- 绑定内部信号 ---
        # 3. 将所有会改变设置的控件信号，连接到自定义信号的 emit() 方法
        self.text_input.textChanged.connect(self.settingsChanged.emit)
        self.opacity_slider.valueChanged.connect(self.settingsChanged.emit)
        self.font_size_spin.valueChanged.connect(self.settingsChanged.emit)
        self.bold_checkbox.stateChanged.connect(self.settingsChanged.emit)
        self.italic_checkbox.stateChanged.connect(self.settingsChanged.emit)
        
        # 对于需要打开对话框的按钮，我们在其自定义方法内发射信号
        self.color_button.clicked.connect(self.choose_color)
        self.image_button.clicked.connect(self.choose_image)
        for btn in self.position_buttons.values():
            btn.clicked.connect(self.settingsChanged.emit)

    def choose_color(self):
        color = QColorDialog.getColor(QColor(*self.selected_color))
        if color.isValid():
            self.selected_color = (color.red(), color.green(), color.blue())
            self.settingsChanged.emit() # 4. 只有在成功选择颜色后才发射信号

    def choose_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择水印图片", "", "Images (*.png *.jpg *.bmp *.tiff)"
        )
        if path:
            self.image_path = path
            self.settingsChanged.emit() # 5. 只有在成功选择图片后才发射信号

    def set_position(self, pos_name: str):
        if self.current_position == pos_name:
            return
        self.current_position = pos_name
        for name, btn in self.position_buttons.items():
            btn.setChecked(name == pos_name)
        # set_position 本身不发射信号，因为它是由 MainWindow 调用的
        # MainWindow 调用后会自己更新预览