from typing import Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


class TextWatermark:
    def __init__(
        self,
        text: str,
        font_name: Optional[str] = None,
        # --- 修改点 1: 参数重命名并改变含义 ---
        relative_font_size: float = 5.0, # 现在是相对于图片高度的百分比
        color: Tuple[int, int, int] = (255, 255, 255),
        opacity: int = 128,
        bold: bool = False,
        italic: bool = False,
    ):
        self.text = text
        self.font_name = font_name or "SimHei"
        self.relative_font_size = relative_font_size
        self.color = color
        self.opacity = opacity
        self.bold = bold
        self.italic = italic

    def apply(self, img: Image.Image, position: Tuple[int, int] = (0, 0)) -> Image.Image:
        if img.mode != "RGBA":
            base = img.convert("RGBA")
        else:
            base = img.copy()

        # --- 修改点 2: 动态计算像素字号 ---
        # 以图片的短边作为参考基准，防止在极端宽高比的图片上变形
        reference_dimension = min(img.width, img.height)
        pixel_font_size = int(reference_dimension * (self.relative_font_size / 100.0))
        # 保证最小字号为1像素
        pixel_font_size = max(1, pixel_font_size)

        txt_layer = Image.new("RGBA", base.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)
        
        # 使用计算出的像素字号加载字体
        font = self._load_font(pixel_font_size)
        fill_color = (*self.color, self.opacity)

        # 粗体和斜体的逻辑不变
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
        # 导出时再统一转RGB，这里保持RGBA以支持透明度
        return combined

    # --- 修改点 3: _load_font 方法现在需要接收字号参数 ---
    def _load_font(self, font_size: int) -> ImageFont.FreeTypeFont:
        font_path = None
        search_dirs = [Path("C:/Windows/Fonts"), Path("/usr/share/fonts"), Path("/Library/Fonts")]

        for folder in search_dirs:
            if folder.exists():
                for f in folder.glob("*"):
                    if self.font_name.lower() in f.stem.lower():
                        font_path = f
                        break
            if font_path:
                break
        
        if not font_path:
            fallback_fonts = ["msyh.ttc", "simhei.ttf", "simsun.ttc"]
            for fb in fallback_fonts:
                for folder in search_dirs:
                    if (fb_path := folder / fb).exists():
                        font_path = fb_path
                        break
                if font_path:
                    break

        if not font_path:
            print("[警告] 未找到可用字体，使用默认字体")
            return ImageFont.load_default()

        try:
            # 使用传入的 font_size
            return ImageFont.truetype(str(font_path), font_size)
        except Exception as e:
            print(f"[警告] 字体加载失败: {e}")
            return ImageFont.load_default()

    def _apply_italic(self, txt_layer: Image.Image) -> Image.Image:
        # 斜体逻辑不变
        w, h = txt_layer.size
        shear_factor = 0.2
        xshift = abs(shear_factor) * h
        new_w = w
        return txt_layer.transform(
            (new_w, h), Image.AFFINE,
            (1, shear_factor, -xshift if shear_factor > 0 else 0, 0, 1, 0),
            Image.BICUBIC,
        )