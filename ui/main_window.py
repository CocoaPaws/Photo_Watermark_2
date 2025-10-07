import sys
import os
from pathlib import Path
from PIL import Image
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QApplication, QFileDialog, QPushButton, QVBoxLayout
from PyQt6.QtCore import Qt, QPoint

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.image_list import ImageList
from ui.preview_widget import PreviewWidget
from ui.controls import Controls
from watermark.preview import PreviewManager
from watermark.watermark_text import TextWatermark
from watermark.watermark_image import ImageWatermark
from watermark.file_manager import FileManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Photo Watermark App")
        self.resize(1200, 800)
        self.setMinimumSize(1000, 600)

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

        # 当前水印位置
        self.current_wm_pos = (0, 0)
        self.dragging = False
        self.drag_offset = QPoint(0, 0)

        # 新增：用于缓存当前正在编辑的图片
        self.current_original_image: Image.Image = None
        self.current_preview_image: Image.Image = None
        self.current_image_path: str = ""
        self.preview_scale_ratio: float = 1.0 # 预览图相对于原图的缩放比例

        # -------------------------------
        # 绑定信号
        # -------------------------------
        self.controls.settingsChanged.connect(self.update_preview)
        self.image_list.currentItemChanged.connect(self.update_preview)
        self.controls.import_btn.clicked.connect(self.import_images)
        self.controls.export_btn.clicked.connect(self.export_images)
        
        # 九宫格按钮
        for pos_name, btn in self.controls.position_buttons.items():
            btn.clicked.connect(lambda checked, name=pos_name: self.set_watermark_position(name))

        # 拖拽导入绑定
        self.image_list.setFileDroppedCallback(self.handle_import_files)

        # 预览鼠标事件
        self.preview_widget.label.mousePressEvent = self.preview_mouse_press
        self.preview_widget.label.mouseMoveEvent = self.preview_mouse_move
        self.preview_widget.label.mouseReleaseEvent = self.preview_mouse_release

    # -------------------------------
    # 九宫格点击设置水印位置
    # -------------------------------
    def set_watermark_position(self, pos_name: str):
        # 修正第一处：直接访问 .base_image 属性
        img = self.preview_manager.base_image
        if not img:
            return

        w, h = img.width, img.height
        
        # 获取水印的大致尺寸以便居中/右对齐时计算偏移
        # 这是一个简化的估算，对于精确定位，这个逻辑应该在水印模块内部完成
        # 但对于当前结构，这是一个有效的修复
        wm_w, wm_h = 100, 50 # 假设一个默认的水印宽高
        if self.controls.text_input.text():
            font_size = self.controls.font_size_spin.value()
            wm_w = len(self.controls.text_input.text()) * font_size
            wm_h = font_size
        
        # 修正第二处：使用与按钮名称一致的中文键
        positions = {
            "左上": (0, 0),
            "上中": (w // 2 - wm_w // 2, 0),
            "右上": (w - wm_w, 0),
            "左中": (0, h // 2 - wm_h // 2),
            "中心": (w // 2 - wm_w // 2, h // 2 - wm_h // 2),
            "右中": (w - wm_w, h // 2 - wm_h // 2),
            "左下": (0, h - wm_h),
            "下中": (w // 2 - wm_w // 2, h - wm_h),
            "右下": (w - wm_w, h - wm_h),
        }
        
        # 更新控件状态并设置当前位置
        self.controls.set_position(pos_name)
        self.current_wm_pos = positions.get(pos_name, (0, 0))
        self.update_preview()

    # -------------------------------
    # 拖拽事件
    # -------------------------------
    def preview_mouse_press(self, event):
        pos = event.position().toPoint()
        self.dragging = True
        self.drag_offset = pos
        event.accept()

    def preview_mouse_move(self, event):
        if self.dragging:
            pos = event.position().toPoint()
            dx = pos.x() - self.drag_offset.x()
            dy = pos.y() - self.drag_offset.y()
            x, y = self.current_wm_pos
            self.current_wm_pos = (x + dx, y + dy)
            self.drag_offset = pos
            self.update_preview()
            event.accept()

    def preview_mouse_release(self, event):
        self.dragging = False
        event.accept()

    # -------------------------------
    # 更新预览
    # -------------------------------

    def update_preview(self, *_): # 使用 *_ 接收所有信号，避免不必要的参数
        selected_path = self.image_list.get_selected_image()
        
        # 如果没有选中任何图片，则不进行任何操作
        if not selected_path:
            # 你可以在这里清空预览区 self.preview_widget.label.clear()
            return

        try:
            # 关键：检查是否是新选择的图片
            if self.current_image_path != selected_path:
                self.current_image_path = selected_path
                self.current_original_image = Image.open(selected_path).convert("RGBA")

                # --- 生成预览小图 ---
                max_preview_size = (1280, 1280) # 预览图最大尺寸
                
                # 计算缩放比例
                original_w, original_h = self.current_original_image.size
                
                if original_w > max_preview_size[0] or original_h > max_preview_size[1]:
                    self.current_preview_image = self.current_original_image.copy()
                    self.current_preview_image.thumbnail(max_preview_size, Image.Resampling.LANCZOS)
                    preview_w, _ = self.current_preview_image.size
                    self.preview_scale_ratio = preview_w / original_w
                else:
                    self.current_preview_image = self.current_original_image
                    self.preview_scale_ratio = 1.0
            
            # --- 所有后续操作都在 preview_image 上进行 ---
            if self.current_preview_image is None:
                return

            # 复制小图进行操作，速度极快
            preview_with_wm = self.current_preview_image.copy()
            self.preview_manager.set_base_image(preview_with_wm)

            # --- 水印参数等比例缩放 ---
            scaled_font_size = int(self.controls.font_size_spin.value() * self.preview_scale_ratio)
            # 保证缩放后的字号至少为1
            scaled_font_size = max(1, scaled_font_size) 
            
            # 文本水印
            text = self.controls.text_input.text().strip()
            if text:
                tw = TextWatermark(
                    text=text,
                    font_size=scaled_font_size, # 使用缩放后的字号
                    color=self.controls.selected_color,
                    opacity=self.controls.opacity_slider.value(),
                    bold=self.controls.bold_checkbox.isChecked(),
                    italic=self.controls.italic_checkbox.isChecked(),
                )
                # 位置也需要缩放
                scaled_pos = (int(self.current_wm_pos[0] * self.preview_scale_ratio), 
                              int(self.current_wm_pos[1] * self.preview_scale_ratio))
                self.preview_manager.set_text_watermark((tw, scaled_pos))
            else:
                self.preview_manager.set_text_watermark(None)

            # 图片水印
            if self.controls.image_path:
                iw = ImageWatermark(
                    watermark_path=self.controls.image_path,
                    opacity=self.controls.opacity_slider.value(),
                    # 注意：图片水印的 scale 是相对于水印自身大小，所以不需要额外缩放
                    # 但如果想让它相对于主图大小，则需要调整
                    scale=0.3 
                )
                scaled_pos = (int(self.current_wm_pos[0] * self.preview_scale_ratio), 
                              int(self.current_wm_pos[1] * self.preview_scale_ratio))
                self.preview_manager.set_image_watermark((iw, scaled_pos))
            else:
                self.preview_manager.set_image_watermark(None)

            final_preview_img = self.preview_manager.generate_preview()
            self.preview_widget.show_image(final_preview_img)
            
        except Exception as e:
            print(f"[ERROR] 生成预览失败: {e}")
            import traceback
            traceback.print_exc() # 打印详细的错误堆栈
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
                    font_size=self.controls.font_size_spin.value(),
                    color=self.controls.selected_color,
                    opacity=self.controls.opacity_slider.value(),
                    bold=self.controls.bold_checkbox.isChecked(),
                    italic=self.controls.italic_checkbox.isChecked(),
                )
                self.preview_manager.set_text_watermark((tw, self.current_wm_pos))
            else:
                self.preview_manager.set_text_watermark(None)

            # 图片水印
            if self.controls.image_path:
                iw = ImageWatermark(
                    watermark_path=self.controls.image_path,
                    opacity=self.controls.opacity_slider.value(),
                    scale=0.3
                )
                self.preview_manager.set_image_watermark((iw, self.current_wm_pos))
            else:
                self.preview_manager.set_image_watermark(None)

            preview_img = self.preview_manager.generate_preview()
            self.preview_widget.show_image(preview_img)
        except Exception as e:
            print(f"[ERROR] 生成预览失败: {e}")

    # -------------------------------
    # 导入图片
    # -------------------------------
    def import_images(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择图片", "", "Images (*.png *.jpg *.bmp *.tiff)"
        )
        if not files:
            return
        self.handle_import_files(files)

    # -------------------------------
    # 拖拽导入
    # -------------------------------
    def handle_import_files(self, file_paths):
        imported_files = self.file_manager.import_files(file_paths)
        for f in imported_files:
            self.image_list.add_image(f)
        if imported_files and not self.image_list.currentItem():
            self.image_list.setCurrentRow(0)

    # -------------------------------
    # 批量导出
    # -------------------------------
    def export_images(self):
        output_dir = QFileDialog.getExistingDirectory(
            self,
            "选择导出文件夹",
            "",  # 这是一个可选参数，用于指定起始目录，留空即可
            QFileDialog.Option.DontUseNativeDialog  # <-- 关键就在这里！
        )
        if not output_dir:
            return

        if self.image_list.count() > 0:
            first_item = self.image_list.item(0)
            first_image_path = Path(first_item.data(256))
            if Path(output_dir).resolve() == first_image_path.parent.resolve():
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(
                    self,
                    "警告",
                    "当前选择的导出文件夹与原图片文件夹相同。\n为避免覆盖原图，已取消导出操作。",
                    QMessageBox.StandardButton.Ok
                )
                return

        images_to_export = []
        scale_percent = self.controls.scale_spinbox.value() / 100.0

        for i in range(self.image_list.count()):
            item = self.image_list.item(i)
            img_path = Path(item.data(256))
            img = Image.open(img_path)

            if scale_percent != 1.0:
                new_size = (int(img.width * scale_percent), int(img.height * scale_percent))
                img = img.resize(new_size, Image.Resampling.LANCZOS)

            # 文本水印
            text = self.controls.text_input.text()
            if text:
                tw = TextWatermark(
                    text=text,
                    font_size=self.controls.font_size_spin.value(),
                    color=self.controls.selected_color,
                    opacity=self.controls.opacity_slider.value(),
                    bold=self.controls.bold_checkbox.isChecked(),
                    italic=self.controls.italic_checkbox.isChecked(),
                )
                img = tw.apply(img, position=self.current_wm_pos)

            # 图片水印
            if self.controls.image_path:
                iw = ImageWatermark(
                    watermark_path=self.controls.image_path,
                    opacity=self.controls.opacity_slider.value(),
                    scale=0.3
                )
                img = iw.apply(img, position=self.current_wm_pos)

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
