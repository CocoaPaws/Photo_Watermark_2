from typing import Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


class TextWatermark:
    def __init__(
        self,
        text: str,
        font_name: Optional[str] = None,
        font_size: int = 24,
        color: Tuple[int, int, int] = (255, 255, 255),
        opacity: int = 128,
        bold: bool = False,
        italic: bool = False,
    ):
        self.text = text
        self.font_name = font_name or "SimHei"  # 默认黑体
        self.font_size = font_size
        self.color = color
        self.opacity = opacity
        self.bold = bold
        self.italic = italic

    def apply(self, img: Image.Image, position: Tuple[int, int] = (0, 0)) -> Image.Image:
        if img.mode != "RGBA":
            base = img.convert("RGBA")
        else:
            base = img.copy()

        txt_layer = Image.new("RGBA", base.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)
        font = self._load_font()
        fill_color = (*self.color, self.opacity)

        offsets = [(0, 0)]
        if self.bold:
            offsets = [(0, 0), (1, 0), (0, 1), (1, 1)]

        if self.italic:
            temp_layer = Image.new("RGBA", base.size, (255, 255, 255, 0))
            temp_draw = ImageDraw.Draw(temp_layer)
            for dx, dy in offsets:
                temp_draw.text((position[0] + dx, position[1] + dy), self.text, font=font, fill=fill_color)
            txt_layer = self._apply_italic(temp_layer)
        else:
            for dx, dy in offsets:
                draw.text((position[0] + dx, position[1] + dy), self.text, font=font, fill=fill_color)

        combined = Image.alpha_composite(base, txt_layer)
        return combined.convert("RGB")

    def _load_font(self) -> ImageFont.FreeTypeFont:
        font_path = None
        search_dirs = [Path("C:/Windows/Fonts"), Path("/usr/share/fonts"), Path("/Library/Fonts")]

        # 系统字体查找
        for folder in search_dirs:
            if folder.exists():
                for f in folder.glob("*"):
                    if self.font_name.lower() in f.stem.lower():
                        font_path = f
                        break
            if font_path:
                break

        # fallback 中文字体
        if not font_path:
            fallback_fonts = ["msyh.ttc", "simhei.ttf", "simsun.ttc"]
            for fb in fallback_fonts:
                for folder in search_dirs:
                    fb_path = folder / fb
                    if fb_path.exists():
                        font_path = fb_path
                        break
                if font_path:
                    break

        if not font_path:
            print("[警告] 未找到可用字体，使用默认字体（不支持中文）")
            return ImageFont.load_default()

        try:
            return ImageFont.truetype(str(font_path), self.font_size)
        except Exception as e:
            print(f"[警告] 字体加载失败: {e}")
            return ImageFont.load_default()

    def _apply_italic(self, txt_layer: Image.Image) -> Image.Image:
        w, h = txt_layer.size
        shear_factor = 0.2
        xshift = abs(shear_factor) * h
        new_w = w
        return txt_layer.transform(
            (new_w, h),
            Image.AFFINE,
            (1, shear_factor, -xshift if shear_factor > 0 else 0, 0, 1, 0),
            Image.BICUBIC,
        )
