import sys
from pathlib import Path
from PIL import Image, ImageDraw

# 添加项目根目录到 sys.path，确保能找到 watermark 包
sys.path.append(str(Path(__file__).resolve().parents[1]))

from watermark.watermark_text import TextWatermark
from watermark.watermark_image import ImageWatermark


def create_sample_image(path: Path):
    """生成一张基础测试图片"""
    img = Image.new("RGB", (500, 300), color=(180, 220, 250))
    draw = ImageDraw.Draw(img)
    draw.text((50, 130), "Base Image", fill=(0, 0, 0))
    img.save(path, "PNG")
    return path


def test_text_watermark(input_img: Path, output_dir: Path):
    """测试文本水印"""
    img = Image.open(input_img)

    tw = TextWatermark(
        text="Hello WM",
        font_size=32,
        color=(255, 0, 0),
        opacity=180,
        bold=True,
    )
    watermarked = tw.apply(img, position=(50, 50))

    out_path = output_dir / "text_watermark.png"
    watermarked.save(out_path)
    print(f"[OK] 文本水印已保存: {out_path}")


def test_image_watermark(input_img: Path, output_dir: Path, logo_path: Path):
    """测试图片水印"""
    if not logo_path.exists():
        print(f"[WARN] 未找到 logo 文件: {logo_path}, 跳过图片水印测试")
        return

    img = Image.open(input_img)

    iw = ImageWatermark(
        watermark_path=str(logo_path),
        opacity=200,
        scale=0.3,
    )
    watermarked = iw.apply(img, position=(200, 100))

    out_path = output_dir / "image_watermark.png"
    watermarked.save(out_path)
    print(f"[OK] 图片水印已保存: {out_path}")


def main():
    input_dir = Path("test_inputs")
    output_dir = Path("test_outputs")
    assets_dir = Path("assets")

    input_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)

    # Step 1: 生成基础图片
    base_img = create_sample_image(input_dir / "base.png")

    # Step 2: 测试文本水印
    test_text_watermark(base_img, output_dir)

    # Step 3: 测试图片水印（需要 assets/logo.png）
    test_image_watermark(base_img, output_dir, assets_dir / "logo.png")


if __name__ == "__main__":
    main()
