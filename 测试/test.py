from PIL import Image, ImageDraw, ImageFont
img = Image.new('RGB', (80, 80), (255, 255, 255))
font = ImageFont.truetype("C:/Windows/fonts/STXINWEI.TTF", 60)
text_bbox = font.getbbox("无")
text_position = (10, 10)
draw = ImageDraw.Draw(img)
draw.text(text_position, "c", fill=(0, 0, 0), font=font)
img.show()