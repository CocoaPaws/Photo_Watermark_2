import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QApplication, QFileDialog
from ui.image_list import ImageList
from ui.preview_widget import PreviewWidget
from ui.controls import Controls
from watermark.preview import PreviewManager
from watermark.watermark_text import TextWatermark
from watermark.watermark_image import ImageWatermark
from watermark.file_manager import FileManager
from PIL import Image
from pathlib import Path


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Photo Watermark App")
        self.resize(1200, 800)            # 初始大小
        self.setMinimumSize(1000, 600)    # 最小窗口大小


        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.layout = QHBoxLayout()
        self.central.setLayout(self.layout)

        # 左侧图片列表
        self.image_list = ImageList()
        self.layout.addWidget(self.image_list, 1)

        # 中间预览
        self.preview_widget = PreviewWidget()
        self.layout.addWidget(self.preview_widget, 3)

        # 右侧控制区
        self.controls = Controls()
        self.layout.addWidget(self.controls, 1)

        # PreviewManager
        self.preview_manager = PreviewManager()

        # FileManager
        self.file_manager = FileManager()

        # 信号绑定
        self.image_list.currentItemChanged.connect(self.update_preview)
        self.controls.text_input.textChanged.connect(self.update_preview)
        self.controls.opacity_slider.valueChanged.connect(self.update_preview)
        self.controls.color_button.clicked.connect(self.update_preview)
        self.controls.image_button.clicked.connect(self.update_preview)
        self.controls.import_btn.clicked.connect(self.import_images)
        self.controls.export_btn.clicked.connect(self.export_images)

        # 拖拽导入绑定
        self.image_list.setFileDroppedCallback(self.handle_import_files)

    # ----------------------
    # 更新预览
    # ----------------------
    def update_preview(self):
        image_path = self.image_list.get_selected_image()
        if not image_path or not Path(image_path).exists():
            return
        try:
            img = Image.open(image_path).convert("RGBA")
        except Exception as e:
            print(f"[ERROR] 打开图片失败: {image_path}, {e}")
            return

        try:
            self.preview_manager.set_base_image(img)

            # 文本水印
            text = self.controls.text_input.text().strip()
            if text:
                tw = TextWatermark(
                    text=text,
                    font_size=32,
                    color=self.controls.selected_color,
                    opacity=self.controls.opacity_slider.value()
                )
                self.preview_manager.set_text_watermark(tw)
            else:
                self.preview_manager.set_text_watermark(None)

            # 图片水印
            if self.controls.image_path:
                iw = ImageWatermark(
                    watermark_path=self.controls.image_path,
                    opacity=self.controls.opacity_slider.value(),
                    scale=0.3
                )
                self.preview_manager.set_image_watermark(iw)
            else:
                self.preview_manager.set_image_watermark(None)

            preview_img = self.preview_manager.generate_preview()
            self.preview_widget.show_image(preview_img)
        except Exception as e:
            print(f"[ERROR] 生成预览失败: {e}")

    # ----------------------
    # 导入图片（按钮方式）
    # ----------------------
    def import_images(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择图片", "", "Images (*.png *.jpg *.bmp *.tiff)"
        )
        if not files:
            return
        self.handle_import_files(files)

    # ----------------------
    # 导入图片（拖拽方式统一处理）
    # ----------------------
    def handle_import_files(self, file_paths):
        imported_files = self.file_manager.import_files(file_paths)
        for f in imported_files:
            self.image_list.add_image(f)
        # 默认选中第一张，刷新预览
        if imported_files and not self.image_list.currentItem():
            self.image_list.setCurrentRow(0)

    # ----------------------
    # 批量导出
    # ----------------------
    def export_images(self):
        output_dir = QFileDialog.getExistingDirectory(self, "选择导出文件夹")
        if not output_dir:
            return

        images_to_export = []
        scale_percent = self.controls.scale_spinbox.value() / 100.0

        for i in range(self.image_list.count()):
            item = self.image_list.item(i)
            img_path = Path(item.data(256))
            img = Image.open(img_path)

            # 缩放
            if scale_percent != 1.0:
                new_size = (int(img.width * scale_percent), int(img.height * scale_percent))
                img = img.resize(new_size, Image.Resampling.LANCZOS)

            # 文本水印
            text = self.controls.text_input.text()
            if text:
                tw = TextWatermark(
                    text=text,
                    font_size=32,
                    color=self.controls.selected_color,
                    opacity=self.controls.opacity_slider.value()
                )
                img = tw.apply(img)

            # 图片水印
            if self.controls.image_path:
                iw = ImageWatermark(
                    watermark_path=self.controls.image_path,
                    opacity=self.controls.opacity_slider.value(),
                    scale=0.3
                )
                img = iw.apply(img)

            images_to_export.append((img, img_path))

        # 导出参数
        output_format = self.controls.format_combo.currentText()
        name_rule = self.controls.name_rule_combo.currentText()
        custom_str = self.controls.custom_str_input.text()
        jpeg_quality = self.controls.jpeg_quality_slider.value() if output_format == "JPEG" else None

        exported_files = self.file_manager.batch_export(
            images=images_to_export,
            output_dir=output_dir,
            output_format=output_format,
            name_rule=name_rule,
            custom_str=custom_str,
            jpeg_quality=jpeg_quality
        )
        print(f"[OK] 批量导出完成，共 {len(exported_files)} 张图片")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
