from PIL import Image, ImageDraw, ImageFont

# 创建图像
width, height = 200, 100
image = Image.new('RGBA', (width, height), (0, 0, 0, 0))  # 透明背景

# 创建绘图对象
draw = ImageDraw.Draw(image)

try:
    # 尝试使用系统字体
    font = ImageFont.truetype("arial.ttf", 40)
except:
    try:
        # 如果arial不可用，尝试其他字体
        font = ImageFont.truetype("DejaVuSans.ttf", 40)
    except:
        # 如果都不可用，使用默认字体
        font = ImageFont.load_default()

# 计算文字位置使其居中
text = "LOGO"
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
x = (width - text_width) // 2
y = (height - text_height) // 2

# 绘制黑色文字
draw.text((x, y), text, fill=(0, 0, 0, 255), font=font)

# 保存为PNG文件
image.save("logo.png", "PNG")

print("LOGO图片已生成：logo.png")