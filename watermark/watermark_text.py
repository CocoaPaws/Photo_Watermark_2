# watermark/watermark_text.py

from typing import Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


class TextWatermark:
    def __init__(
        self,
        text: str,
        font_name: Optional[str] = None,
        relative_font_size: float = 5.0,
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
        if not self.text:
            return img

        if img.mode != "RGBA":
            base = img.convert("RGBA")
        else:
            base = img.copy()

        # 动态计算像素字号
        reference_dimension = min(img.width, img.height)
        pixel_font_size = max(1, int(reference_dimension * (self.relative_font_size / 100.0)))

        font = self._load_font(pixel_font_size)
        fill_color = (*self.color, self.opacity)
        
        # 创建最终用于合成的、与底图一样大的透明图层
        txt_layer = Image.new("RGBA", base.size, (255, 255, 255, 0))

        if self.italic:
            # --- 斜体处理逻辑 ---
            # 1. 使用临时绘图对象精确测量文字边界
            temp_draw = ImageDraw.Draw(Image.new("RGBA", (0, 0)))
            bbox = temp_draw.textbbox((0, 0), self.text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # 2. 为斜体变形计算所需的额外空间
            shear_factor = 0.2
            x_shift = abs(shear_factor) * text_height
            
            # 3. 创建一个刚好包裹文字的小图层（带额外空间）
            small_surface_size = (int(text_width + x_shift), text_height)
            text_surface = Image.new("RGBA", small_surface_size, (255, 255, 255, 0))
            text_draw = ImageDraw.Draw(text_surface)

            # 4. 在小图层上绘制文字（支持粗体）
            draw_pos = (-bbox[0], -bbox[1])
            self._draw_text_with_bold(text_draw, draw_pos, font, fill_color)

            # 5. 只对这个小图层进行斜体变换
            italic_surface = self._apply_italic(text_surface)

            # 6. 将变形好的小图层粘贴到最终的大图层上
            txt_layer.paste(italic_surface, (int(position[0]), int(position[1])), italic_surface)

        else:
            # --- 非斜体处理逻辑 ---
            # 直接在最终的大图层上绘制（支持粗体）
            final_draw = ImageDraw.Draw(txt_layer)
            self._draw_text_with_bold(final_draw, (int(position[0]), int(position[1])), font, fill_color)

        # 最终合成
        return Image.alpha_composite(base, txt_layer)

    def _draw_text_with_bold(self, draw: ImageDraw.Draw, pos: Tuple[int, int], font, fill):
        """一个辅助方法，用于绘制带粗体效果的文本"""
        x, y = pos
        if self.bold:
            # 通过在周围偏移1像素绘制来模拟粗体
            draw.text((x + 1, y), self.text, font=font, fill=fill)
            draw.text((x, y + 1), self.text, font=font, fill=fill)
            draw.text((x + 1, y + 1), self.text, font=font, fill=fill)
        draw.text(pos, self.text, font=font, fill=fill)

    def _load_font(self, font_size: int) -> ImageFont.FreeTypeFont:
        """根据名称和字号加载字体"""
        font_path = None
        # (这部分可以缓存以提高性能，但为保持简单暂不实现)
        search_dirs = [Path("C:/Windows/Fonts"), Path("/usr/share/fonts"), Path("/System/Library/Fonts")]
        for folder in search_dirs:
            if folder.exists():
                for f in folder.glob(f"*{self.font_name}*.*"):
                    if f.suffix.lower() in ['.ttf', '.otf', '.ttc']:
                        font_path = f
                        break
            if font_path:
                break
        
        if not font_path:
            fallback_fonts = ["msyh.ttc", "simhei.ttf", "simsun.ttc", "Arial.ttf"]
            for fb in fallback_fonts:
                for folder in search_dirs:
                    if (fb_path := folder / fb).exists():
                        font_path = fb_path
                        break
                if font_path:
                    break

        if not font_path:
            print("[警告] 未找到可用字体，使用Pillow默认字体")
            try:
                # Pillow 9.2.0 之后 load_default 需要字号参数
                return ImageFont.load_default(font_size)
            except TypeError:
                return ImageFont.load_default()

        try:
            return ImageFont.truetype(str(font_path), font_size)
        except Exception as e:
            print(f"[警告] 字体加载失败 '{font_path}': {e}")
            try:
                return ImageFont.load_default(font_size)
            except TypeError:
                return ImageFont.load_default()

    def _apply_italic(self, surface: Image.Image) -> Image.Image:
        """对传入的图层进行错切变换以模拟斜体"""
        w, h = surface.size
        shear_factor = 0.2
        xshift = abs(shear_factor) * h
        return surface.transform(
            (int(w), h), # 保持宽度，让transform自己计算最终尺寸
            Image.AFFINE,
            (1, shear_factor, -xshift if shear_factor > 0 else 0, 0, 1, 0),
            Image.BICUBIC,
        )