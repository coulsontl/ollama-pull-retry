from PIL import Image, ImageDraw
import os

def create_rounded_rectangle(size, radius):
    """创建一个带圆角的蒙版"""
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    
    # 画一个圆角矩形
    draw.rounded_rectangle([(0, 0), size], radius=radius, fill=255)
    
    return mask

def convert_png_to_ico(png_path, ico_path, corner_radius=200):
    # 打开原始图片
    img = Image.open(png_path)
    
    # 确保图片是正方形
    size = min(img.size)
    img = img.resize((size, size))
    
    # 创建一个新的RGBA图片
    rounded_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    
    # 创建圆角蒙版
    mask = create_rounded_rectangle((size, size), corner_radius)
    
    # 将原始图片和蒙版结合
    rounded_img.paste(img, (0, 0))
    rounded_img.putalpha(mask)
    
    # 保存为ICO文件
    rounded_img.save(ico_path, format='ICO')
    print(f"已将 {png_path} 转换为圆角图标，保存为 {ico_path}")

if __name__ == "__main__":
    convert_png_to_ico("icon.png", "icon.ico") 