# watermark/watermark_text.py
from typing import Tuple, Optional
from PIL import Image, ImageDraw, ImageFont


class TextWatermark:
    def __init__(
        self,
        text: str,
        font_path: Optional[str] = None,
        font_size: int = 24,
        color: Tuple[int, int, int] = (255, 255, 255),
        opacity: int = 128,
        bold: bool = False,
        italic: bool = False,
    ):
        """
        :param text: 水印文本
        :param font_path: 字体路径（None 使用 Pillow 默认字体）
        :param font_size: 字号
        :param color: 颜色 (R, G, B)
        :param opacity: 透明度 0-255
        :param bold: 是否加粗（简易方式：绘制两次）
        :param italic: 是否倾斜（暂不处理，留作扩展）
        """
        self.text = text
        self.font_path = font_path
        self.font_size = font_size
        self.color = color
        self.opacity = opacity
        self.bold = bold
        self.italic = italic

    def apply(
        self,
        img: Image.Image,
        position: Tuple[int, int] = (0, 0),
    ) -> Image.Image:
        """
        在图片上添加文本水印
        :param img: 输入 PIL.Image
        :param position: 左上角坐标 (x, y)
        :return: 带水印的新图像
        """
        # 确保是 RGBA 模式
        if img.mode != "RGBA":
            base = img.convert("RGBA")
        else:
            base = img.copy()

        # 创建透明图层
        txt_layer = Image.new("RGBA", base.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)

        # 加载字体
        if self.font_path:
            font = ImageFont.truetype(self.font_path, self.font_size)
        else:
            font = ImageFont.load_default()

        # RGBA 颜色
        fill_color = (*self.color, self.opacity)

        # 绘制文字
        if self.bold:
            offsets = [(0, 0), (1, 0), (0, 1), (1, 1)]
        else:
            offsets = [(0, 0)]

        for dx, dy in offsets:
            draw.text(
                (position[0] + dx, position[1] + dy),
                self.text,
                font=font,
                fill=fill_color,
            )

        # 合并
        combined = Image.alpha_composite(base, txt_layer)
        return combined.convert("RGB")
