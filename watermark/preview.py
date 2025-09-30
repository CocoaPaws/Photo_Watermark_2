# watermark/preview.py
from typing import Optional
from PIL import Image
from watermark.watermark_text import TextWatermark
from watermark.watermark_image import ImageWatermark


class PreviewManager:
    def __init__(self):
        self.base_image: Optional[Image.Image] = None
        self.text_wm: Optional[TextWatermark] = None
        self.img_wm: Optional[ImageWatermark] = None

    def set_base_image(self, img: Image.Image):
        """设置当前预览的基础图片"""
        self.base_image = img

    def set_text_watermark(self, text_wm: TextWatermark):
        """设置文本水印"""
        self.text_wm = text_wm

    def set_image_watermark(self, img_wm: ImageWatermark):
        """设置图片水印"""
        self.img_wm = img_wm

    def generate_preview(self) -> Image.Image:
        """生成带水印的预览图"""
        if self.base_image is None:
            raise ValueError("请先设置 base_image")

        preview_img = self.base_image.copy()

        # 应用文本水印
        if self.text_wm:
            preview_img = self.text_wm.apply(preview_img)

        # 应用图片水印
        if self.img_wm:
            preview_img = self.img_wm.apply(preview_img)

        return preview_img
