# watermark/preview.py

from typing import Optional, Tuple
from PIL import Image
from .watermark_text import TextWatermark
from .watermark_image import ImageWatermark


class PreviewManager:
    def __init__(self):
        self.base_image: Optional[Image.Image] = None
        # 修改：将属性名改为 *_info，清晰地表明它包含对象和位置信息
        self.text_wm_info: Optional[Tuple[TextWatermark, Tuple[int, int]]] = None
        self.img_wm_info: Optional[Tuple[ImageWatermark, Tuple[int, int]]] = None

    def set_base_image(self, img: Image.Image):
        """设置当前预览的基础图片"""
        self.base_image = img

    # 修改：方法名不变，但内部逻辑改变
    def set_text_watermark(self, text_wm_info: Optional[Tuple[TextWatermark, Tuple[int, int]]]):
        """设置文本水印及其位置"""
        self.text_wm_info = text_wm_info

    # 修改：方法名不变，但内部逻辑改变
    def set_image_watermark(self, img_wm_info: Optional[Tuple[ImageWatermark, Tuple[int, int]]]):
        """设置图片水印及其位置"""
        self.img_wm_info = img_wm_info

    def generate_preview(self) -> Image.Image:
        """生成带水印的预览图"""
        if self.base_image is None:
            # 返回一个提示图，避免在没有选择图片时程序崩溃
            return Image.new("RGBA", (400, 300), (220, 220, 220, 255))

        preview_img = self.base_image.copy()

        # 修正：应用文本水印
        if self.text_wm_info:
            # 1. 从元组中解包出水印对象和位置
            wm_obj, wm_pos = self.text_wm_info
            # 2. 调用 apply 方法，并传入位置参数
            preview_img = wm_obj.apply(preview_img, position=wm_pos)

        # 修正：应用图片水印
        if self.img_wm_info:
            # 1. 解包
            wm_obj, wm_pos = self.img_wm_info
            # 2. 调用 apply
            preview_img = wm_obj.apply(preview_img, position=wm_pos)

        return preview_img