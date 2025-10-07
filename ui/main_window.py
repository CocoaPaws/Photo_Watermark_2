import sys
import os
import json
from pathlib import Path
from PIL import Image
from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QApplication, 
                             QFileDialog, QMessageBox, QInputDialog)
from PyQt6.QtCore import Qt, QPoint

# 动态添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.image_list import ImageList
from ui.preview_widget import PreviewWidget
from ui.controls import Controls
from watermark.preview import PreviewManager
from watermark.watermark_text import TextWatermark
from watermark.watermark_image import ImageWatermark
from watermark.file_manager import FileManager
from watermark.config_manager import ConfigManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Photo Watermark App")
        self.resize(1200, 800)
        self.setMinimumSize(1000, 800)

        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.layout = QHBoxLayout()
        self.central.setLayout(self.layout)

        # UI组件初始化
        self.image_list = ImageList()
        self.preview_widget = PreviewWidget()
        self.controls = Controls()
        
        self.image_list.setMinimumWidth(200)  # 左边栏至少保持200像素宽
        self.controls.setMinimumWidth(280)    # 右边栏至少保持280像素宽

        # 添加组件并设置拉伸因子
        # 1:3:1 的比例意味着中间区域会优先缩放
        self.layout.addWidget(self.image_list, 1)
        self.layout.addWidget(self.preview_widget, 3)
        self.layout.addWidget(self.controls, 1)

        # 后端管理器初始化
        self.preview_manager = PreviewManager()
        self.file_manager = FileManager()
        self.config_manager = ConfigManager()

        # --- 核心状态变量 ---
        self.wm_offset_relative = (0.0, 0.0) # 核心：拖拽产生的相对偏移百分比
        self.current_wm_pos = (0, 0)         # 临时的：每次update时计算的最终渲染位置
        self.dragging = False
        self.drag_offset = QPoint(0, 0)      # 临时的：拖拽时用于计算移动量的点

        # 图片缓存，用于优化性能
        self.current_original_image: Image.Image = None
        self.current_preview_image: Image.Image = None
        self.current_image_path: str = ""
        self.preview_scale_ratio: float = 1.0

        # -------------------------------
        # 绑定信号
        # -------------------------------
        self.image_list.currentItemChanged.connect(self.update_preview)
        self.controls.settingsChanged.connect(self.update_preview)
        
        self.controls.import_btn.clicked.connect(self.import_images)
        self.controls.export_btn.clicked.connect(self.export_images)
        
        self.controls.save_template_btn.clicked.connect(self.save_template)
        self.controls.delete_template_btn.clicked.connect(self.delete_template)
        self.controls.template_combo.currentIndexChanged.connect(self.on_template_selected)
        
        for pos_name, btn in self.controls.position_buttons.items():
            btn.clicked.connect(lambda checked, name=pos_name: self.set_watermark_position(name))

        self.image_list.setFileDroppedCallback(self.handle_import_files)

        self.preview_widget.label.mousePressEvent = self.preview_mouse_press
        self.preview_widget.label.mouseMoveEvent = self.preview_mouse_move
        self.preview_widget.label.mouseReleaseEvent = self.preview_mouse_release

        self.refresh_template_list()
        self.load_last_settings()

    # -------------------------------
    # 位置与拖拽
    # -------------------------------
    def set_watermark_position(self, pos_name: str):
        """当用户点击九宫格按钮时，更新意图并重置相对偏移"""
        self.controls.set_position(pos_name)
        self.wm_offset_relative = (0.0, 0.0)
        self.update_preview()

    def preview_mouse_press(self, event):
        pos = event.position().toPoint()
        self.dragging = True
        self.drag_offset = pos
        event.accept()

    def preview_mouse_move(self, event):
        """拖拽时，计算并更新核心的相对偏移量"""
        if self.dragging and self.current_original_image:
            pos = event.position().toPoint()
            w, h = self.current_original_image.size

            dx = (pos.x() - self.drag_offset.x()) / self.preview_scale_ratio
            dy = (pos.y() - self.drag_offset.y()) / self.preview_scale_ratio
            
            if w > 0 and h > 0:
                relative_dx = dx / w
                relative_dy = dy / h
                self.wm_offset_relative = (
                    self.wm_offset_relative[0] + relative_dx,
                    self.wm_offset_relative[1] + relative_dy
                )
            
            self.drag_offset = pos
            self.update_preview()
            event.accept()

    def preview_mouse_release(self, event):
        self.dragging = False
        event.accept()

    # -------------------------------
    # 核心：更新预览
    # -------------------------------
    def update_preview(self, *_):
        selected_path = self.image_list.get_selected_image()
        if not selected_path:
            self.preview_widget.label.clear()
            return

        try:
            if self.current_image_path != selected_path:
                self.current_image_path = selected_path
                self.current_original_image = Image.open(selected_path).convert("RGBA")

                max_preview_size = (1280, 1280)
                original_w, _ = self.current_original_image.size
                
                self.current_preview_image = self.current_original_image.copy()
                self.current_preview_image.thumbnail(max_preview_size, Image.Resampling.LANCZOS)
                
                preview_w, _ = self.current_preview_image.size
                self.preview_scale_ratio = preview_w / original_w if original_w > 0 else 1.0

            if not self.current_preview_image: return

            preview_with_wm = self.current_preview_image.copy()
            self.preview_manager.set_base_image(preview_with_wm)
            
            w, h = self.current_original_image.size
            pos_name = self.controls.current_position

            # --- 每次都动态计算最终位置 ---
            current_absolute_offset = (self.wm_offset_relative[0] * w, self.wm_offset_relative[1] * h)
            
            ref_dim = min(w, h)
            pixel_font_size = ref_dim * (self.controls.font_size_spin.value() / 100.0)
            wm_w = len(self.controls.text_input.text()) * pixel_font_size * 0.6
            wm_h = pixel_font_size

            base_positions = {
                "左上": (0, 0), "上中": (w/2-wm_w/2, 0), "右上": (w-wm_w, 0),
                "左中": (0, h/2-wm_h/2), "中心": (w/2-wm_w/2, h/2-wm_h/2), "右中": (w-wm_w, h/2-wm_h/2),
                "左下": (0, h-wm_h), "下中": (w/2-wm_w/2, h-wm_h), "右下": (w-wm_w, h-wm_h),
            }
            base_pos = base_positions.get(pos_name, (0, 0))
            self.current_wm_pos = (base_pos[0] + current_absolute_offset[0], base_pos[1] + current_absolute_offset[1])

            scaled_pos = (int(self.current_wm_pos[0] * self.preview_scale_ratio), 
                          int(self.current_wm_pos[1] * self.preview_scale_ratio))

            # --- 应用水印 ---
            text = self.controls.text_input.text().strip()
            if text:
                tw = TextWatermark(
                    text=text, relative_font_size=self.controls.font_size_spin.value(),
                    color=self.controls.selected_color, opacity=self.controls.opacity_slider.value(), 
                    bold=self.controls.bold_checkbox.isChecked(), italic=self.controls.italic_checkbox.isChecked(),
                )
                self.preview_manager.set_text_watermark((tw, scaled_pos))
            else:
                self.preview_manager.set_text_watermark(None)

            if self.controls.image_path:
                iw = ImageWatermark(
                    watermark_path=self.controls.image_path, opacity=self.controls.opacity_slider.value(), scale=0.3
                )
                self.preview_manager.set_image_watermark((iw, scaled_pos))
            else:
                self.preview_manager.set_image_watermark(None)

            final_preview_img = self.preview_manager.generate_preview()
            self.preview_widget.show_image(final_preview_img)

        except Exception as e:
            print(f"[ERROR] 生成预览失败: {e}")
            import traceback
            traceback.print_exc()

    # -------------------------------
    # 文件导入/导出
    # -------------------------------
    def import_images(self):
        files, _ = QFileDialog.getOpenFileNames(self, "选择图片", "", "Images (*.png *.jpg *.bmp *.tiff)")
        if files: self.handle_import_files(files)

    def handle_import_files(self, file_paths):
        imported_files = self.file_manager.import_files(file_paths)
        for f in imported_files:
            self.image_list.add_image(f)
        if imported_files and not self.image_list.currentItem():
            self.image_list.setCurrentRow(0)

    def export_images(self):
        if self.image_list.count() == 0:
            QMessageBox.warning(self, "提示", "请先导入至少一张图片。")
            return
            
        output_dir = QFileDialog.getExistingDirectory(self, "选择导出文件夹", "", QFileDialog.Option.DontUseNativeDialog)
        if not output_dir: return

        first_image_path = Path(self.image_list.item(0).data(Qt.ItemDataRole.UserRole))
        if Path(output_dir).resolve() == first_image_path.parent.resolve():
            QMessageBox.warning(self, "警告", "导出文件夹不能与原图文件夹相同，请重新选择。", QMessageBox.StandardButton.Ok)
            return

        images_to_export = []
        scale_percent = self.controls.scale_spinbox.value() / 100.0
        
        # 获取通用设置一次
        current_settings = self.get_current_settings()
        pos_name = current_settings["position_name"]
        relative_offset = current_settings["wm_offset_relative"]

        for i in range(self.image_list.count()):
            item = self.image_list.item(i)
            img_path = Path(item.data(Qt.ItemDataRole.UserRole))
            img = Image.open(img_path).convert("RGBA")

            if scale_percent != 1.0:
                new_size = (int(img.width * scale_percent), int(img.height * scale_percent))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # --- 为每张导出的图片动态计算精确位置 ---
            w, h = img.size
            absolute_offset = (relative_offset[0] * w, relative_offset[1] * h)
            ref_dim = min(w, h)
            pixel_font_size = ref_dim * (current_settings["relative_font_size"] / 100.0)
            wm_w = len(current_settings["text_content"]) * pixel_font_size * 0.6
            wm_h = pixel_font_size
            base_positions = { "左上": (0, 0), "上中": (w/2-wm_w/2, 0), "右上": (w-wm_w, 0), "左中": (0, h/2-wm_h/2), "中心": (w/2-wm_w/2, h/2-wm_h/2), "右中": (w-wm_w, h/2-wm_h/2), "左下": (0, h-wm_h), "下中": (w/2-wm_w/2, h-wm_h), "右下": (w-wm_w, h-wm_h) }
            base_pos = base_positions.get(pos_name, (0, 0))
            final_pos = (base_pos[0] + absolute_offset[0], base_pos[1] + absolute_offset[1])
            
            # --- 应用水印 ---
            if current_settings["text_content"]:
                tw = TextWatermark(
                    text=current_settings["text_content"], relative_font_size=current_settings["relative_font_size"],
                    color=current_settings["color"], opacity=current_settings["opacity"],
                    bold=current_settings["is_bold"], italic=current_settings["is_italic"]
                )
                img = tw.apply(img, position=final_pos)

            if current_settings["image_path"]:
                iw = ImageWatermark(
                    watermark_path=current_settings["image_path"], opacity=current_settings["opacity"], scale=0.3
                )
                img = iw.apply(img, position=final_pos)

            images_to_export.append((img, img_path))

        final_images_to_export = []
        for img, path in images_to_export:
            final_images_to_export.append((img.convert("RGB"), path))

        self.file_manager.batch_export(
            images=final_images_to_export, output_dir=output_dir, output_format=self.controls.format_combo.currentText(),
            name_rule=self.controls.name_rule_combo.currentText(), custom_str=self.controls.custom_str_input.text(),
            jpeg_quality=self.controls.jpeg_quality_slider.value()
        )
        
        QMessageBox.information(self, "成功", f"批量导出完成，共 {len(final_images_to_export)} 张图片。")

    # -------------------------------
    # 模板功能
    # -------------------------------
    def refresh_template_list(self):
        templates = self.config_manager.list_templates()
        visible_templates = [t for t in templates if t != "_last_session"]
        self.controls.update_template_list(visible_templates)

    def get_current_settings(self) -> dict:
        return {
            "text_content": self.controls.text_input.text(),
            "opacity": self.controls.opacity_slider.value(),
            "color": self.controls.selected_color,
            "relative_font_size": self.controls.font_size_spin.value(),
            "is_bold": self.controls.bold_checkbox.isChecked(),
            "is_italic": self.controls.italic_checkbox.isChecked(),
            "image_path": self.controls.image_path,
            "position_name": self.controls.current_position,
            "wm_offset_relative": self.wm_offset_relative,
            "name_rule": self.controls.name_rule_combo.currentText(),
            "custom_str": self.controls.custom_str_input.text(),
            "output_format": self.controls.format_combo.currentText(),
            "jpeg_quality": self.controls.jpeg_quality_slider.value(),
            "scale_percent": self.controls.scale_spinbox.value(),
        }

    def apply_settings(self, settings: dict):
        c = self.controls
        c.text_input.setText(settings.get("text_content", ""))
        c.opacity_slider.setValue(settings.get("opacity", 180))
        c.selected_color = settings.get("color", (255, 255, 255))
        c.font_size_spin.setValue(settings.get("relative_font_size", 5))
        c.bold_checkbox.setChecked(settings.get("is_bold", False))
        c.italic_checkbox.setChecked(settings.get("is_italic", False))
        c.image_path = settings.get("image_path", None)
        
        self.wm_offset_relative = settings.get("wm_offset_relative", (0.0, 0.0))
        
        pos_name = settings.get("position_name", "左上")
        self.controls.set_position(pos_name)
        
        c.name_rule_combo.setCurrentText(settings.get("name_rule", "suffix"))
        c.custom_str_input.setText(settings.get("custom_str", "_watermarked"))
        c.format_combo.setCurrentText(settings.get("output_format", "PNG"))
        c.jpeg_quality_slider.setValue(settings.get("jpeg_quality", 90))
        c.scale_spinbox.setValue(settings.get("scale_percent", 100))
        
        self.update_preview()
    
    def save_template(self):
        name, ok = QInputDialog.getText(self, "保存模板", "请输入模板名称:")
        if ok and name:
            settings = self.get_current_settings()
            self.config_manager.save_template(name, settings)
            self.refresh_template_list()
            self.controls.template_combo.blockSignals(True)
            self.controls.template_combo.setCurrentText(name)
            self.controls.template_combo.blockSignals(False)
            QMessageBox.information(self, "成功", f"模板 '{name}' 已保存。")

    def delete_template(self):
        name = self.controls.template_combo.currentText()
        if not name or name == "- 选择模板 -":
            QMessageBox.warning(self, "提示", "请先选择一个要删除的模板。")
            return
        reply = QMessageBox.question(self, "确认删除", f"确定要删除模板 '{name}' 吗？",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.config_manager.delete_template(name)
            self.refresh_template_list()
            QMessageBox.information(self, "成功", f"模板 '{name}' 已删除。")

    def on_template_selected(self, index):
        if index <= 0: return
        name = self.controls.template_combo.currentText()
        try:
            settings = self.config_manager.load_template(name)
            self.apply_settings(settings)
        except (FileNotFoundError, json.JSONDecodeError):
            QMessageBox.critical(self, "错误", f"加载模板 '{name}' 失败，文件不存在或已损坏。")

    def load_last_settings(self):
        try:
            settings = self.config_manager.load_template("_last_session")
            self.apply_settings(settings)
            print("[INFO] 已成功加载上一次的会话设置。")
        except (FileNotFoundError, json.JSONDecodeError):
            print("[INFO] 未找到或无法解析上一次的会话设置，使用默认值。")

    def closeEvent(self, event):
        settings = self.get_current_settings()
        self.config_manager.save_template("_last_session", settings)
        print("[INFO] 当前会话设置已保存。")
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())