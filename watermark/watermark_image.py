# watermark/watermark_image.py

from typing import Tuple, Optional
from pathlib import Path
from PIL import Image


class ImageWatermark:
    def __init__(
        self,
        watermark_path: str,
        opacity: int = 128,
        scale: float = 0.15, # 默认缩放比例 (15%)
    ):
        self.watermark_path = Path(watermark_path)
        self.opacity = opacity
        self.scale = scale

        if not self.watermark_path.exists():
            raise FileNotFoundError(f"水印文件不存在: {watermark_path}")

        # --- 核心修改 1: 保存原始水印和其尺寸 ---
        self.original_watermark = Image.open(self.watermark_path).convert("RGBA")
        self.original_width, self.original_height = self.original_watermark.size
        # --- 修改结束 ---

    def apply(
        self,
        img: Image.Image,
        position: Tuple[int, int] = (0, 0),
    ) -> Image.Image:
        """
        在图片上添加图片水印，并实现中心点固定缩放。
        """
        if img.mode != "RGBA":
            base = img.convert("RGBA")
        else:
            base = img.copy()

        # --- 核心重构 2: 实现中心点缩放逻辑 ---

        # 1. 计算缩放后的新尺寸
        new_width = int(self.original_width * self.scale)
        new_height = int(self.original_height * self.scale)
        
        # 保证最小尺寸为1x1像素
        new_width = max(1, new_width)
        new_height = max(1, new_height)
        
        # 2. 对原始水印进行高质量缩放
        # 注意：每次都从 self.original_watermark 开始缩放，避免连续缩放导致的质量下降
        resized_wm = self.original_watermark.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # 3. 调整透明度
        if self.opacity < 255:
            alpha = resized_wm.split()[3]
            # 创建一个修改函数，确保透明度不会超过原始值
            def modulate_alpha(p):
                return int(p * (self.opacity / 255.0))
            alpha = alpha.point(modulate_alpha)
            resized_wm.putalpha(alpha)

        # 4. 计算中心点偏移补偿
        # 注意：这里我们不需要计算偏移，因为我们将直接把缩放后图片的中心对齐到指定位置
        # paste 方法的 box 参数的左上角坐标，需要从中心点反推
        paste_x = int(position[0] - new_width / 2)
        paste_y = int(position[1] - new_height / 2)
        
        # 5. 使用补偿后的坐标进行粘贴
        # 使用 resized_wm 作为 mask，可以正确处理水印本身的透明区域
        base.paste(resized_wm, (paste_x, paste_y), resized_wm)
        
        # --- 重构结束 ---

        return base