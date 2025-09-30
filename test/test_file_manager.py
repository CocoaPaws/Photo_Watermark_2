import os
import sys
from pathlib import Path
# 添加项目根目录到 sys.path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from PIL import Image, ImageDraw, ImageFont

from watermark.file_manager import FileManager

def create_sample_image(path: Path):
    """创建一张简单的测试图片"""
    img = Image.new("RGB", (400, 200), color=(200, 200, 255))
    draw = ImageDraw.Draw(img)
    draw.text((50, 80), "Test Image", fill=(0, 0, 0))
    img.save(path, "PNG")
    return path


def add_dummy_watermark(img: Image.Image) -> Image.Image:
    """在图片上加一个简单的文字水印（模拟水印逻辑）"""
    watermarked = img.copy()
    draw = ImageDraw.Draw(watermarked)

    # 使用默认字体（避免依赖系统字体）
    text = "WATERMARK"
    text_size = draw.textlength(text)
    position = (img.width - text_size - 20, img.height - 30)

    draw.text(position, text, fill=(255, 0, 0, 128))  # 半透明红色
    return watermarked


def main():
    fm = FileManager()

    # Step 1: 创建测试图片
    input_dir = Path("test_inputs")
    output_dir = Path("test_outputs")
    input_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)

    test_img_path = create_sample_image(input_dir / "sample.png")
    print(f"已生成测试图片: {test_img_path}")

    # Step 2: 导入文件
    imported = fm.import_files([str(test_img_path)])
    print(f"导入的文件: {imported}")

    # Step 3: 打开并加水印
    img = Image.open(imported[0])
    watermarked_img = add_dummy_watermark(img)

    # Step 4: 导出文件
    exported = fm.export_image(
        img=watermarked_img,
        original_path=imported[0],
        output_dir=str(output_dir),
        output_format="PNG",
        name_rule="suffix",
        custom_str="_wm",
    )

    print(f"导出成功: {exported}")


if __name__ == "__main__":
    main()
