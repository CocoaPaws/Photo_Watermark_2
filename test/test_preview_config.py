import sys
from pathlib import Path
from PIL import Image, ImageDraw

# 添加项目根目录到 sys.path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from watermark.watermark_text import TextWatermark
from watermark.watermark_image import ImageWatermark
from watermark.preview import PreviewManager
from watermark.config_manager import ConfigManager


def create_sample_image(path: Path):
    """生成一张基础测试图片"""
    img = Image.new("RGB", (500, 300), color=(200, 220, 255))
    draw = ImageDraw.Draw(img)
    draw.text((50, 130), "Base Image", fill=(0, 0, 0))
    img.save(path, "PNG")
    return path


def main():
    # 准备目录
    input_dir = Path("test_inputs")
    output_dir = Path("test_outputs")
    assets_dir = Path("assets")
    input_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)

    # Step 1: 生成基础图片
    base_img_path = create_sample_image(input_dir / "base.png")
    base_img = Image.open(base_img_path)

    # Step 2: 初始化预览管理器
    preview = PreviewManager()

    # 文本水印
    tw = TextWatermark(
        text="Demo WM",
        font_size=32,
        color=(255, 0, 0),
        opacity=180,
        bold=True,
    )
    preview.set_text_watermark(tw)

    # 图片水印（logo.png）
    logo_path = assets_dir / "logo.png"
    if logo_path.exists():
        iw = ImageWatermark(
            watermark_path=str(logo_path),
            opacity=200,
            scale=0.3,
        )
        preview.set_image_watermark(iw)
    else:
        print(f"[WARN] 未找到 logo.png，跳过图片水印")

    # 设置基础图片
    preview.set_base_image(base_img)

    # Step 3: 生成预览图
    preview_img = preview.generate_preview()
    preview_out = output_dir / "preview_combined.png"
    preview_img.save(preview_out)
    print(f"[OK] 预览图已保存: {preview_out}")

    # Step 4: 模板管理测试
    cm = ConfigManager()
    template_config = {
        "text": "Demo WM",
        "font_size": 32,
        "color": [255, 0, 0],
        "opacity": 180,
        "bold": True,
        "watermark_image": str(logo_path),
        "image_opacity": 200,
        "scale": 0.3
    }
    cm.save_template("preview_template", template_config)

    # 加载模板
    loaded_config = cm.load_template("preview_template")
    print(f"[OK] 模板加载成功: {loaded_config}")

    # 列出模板
    print("当前模板列表:", cm.list_templates())

    # 删除模板
    cm.delete_template("preview_template")


if __name__ == "__main__":
    main()
