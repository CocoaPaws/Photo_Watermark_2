# watermark/watermark_image.py
from typing import Tuple, Optional
from pathlib import Path
from PIL import Image


class ImageWatermark:
    def __init__(
        self,
        watermark_path: str,
        opacity: int = 128,
        scale: float = 1.0,
    ):
        """
        :param watermark_path: 水印图片路径（支持 PNG 透明）
        :param opacity: 透明度 0-255
        :param scale: 缩放比例（相对原始大小）
        """
        self.watermark_path = Path(watermark_path)
        self.opacity = opacity
        self.scale = scale

        if not self.watermark_path.exists():
            raise FileNotFoundError(f"水印文件不存在: {watermark_path}")

        self.watermark = Image.open(self.watermark_path).convert("RGBA")

    def apply(
        self,
        img: Image.Image,
        position: Tuple[int, int] = (0, 0),
        resize: Optional[Tuple[int, int]] = None,
    ) -> Image.Image:
        """
        在图片上添加图片水印
        :param img: 输入 PIL.Image
        :param position: 左上角坐标 (x, y)
        :param resize: 可选，水印新尺寸 (width, height)
        :return: 带水印的新图像
        """
        if img.mode != "RGBA":
            base = img.convert("RGBA")
        else:
            base = img.copy()

        # 复制水印
        wm = self.watermark.copy()

        # 缩放
        if resize:
            wm = wm.resize(resize, Image.Resampling.LANCZOS)
        elif self.scale != 1.0:
            new_size = (
                int(wm.width * self.scale),
                int(wm.height * self.scale),
            )
            wm = wm.resize(new_size, Image.Resampling.LANCZOS)

        # 调整透明度
        if self.opacity < 255:
            alpha = wm.split()[3]
            alpha = alpha.point(lambda p: p * (self.opacity / 255.0))
            wm.putalpha(alpha)

        # 叠加
        base.alpha_composite(wm, position)
        return base
