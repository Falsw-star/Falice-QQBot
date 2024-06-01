from PIL import Image, ImageDraw, ImageFont
img = Image.new('RGB', (400, 200), (255, 255, 255))
font = ImageFont.truetype("C:/Windows/fonts/STXINWEI.TTF", 60)
text_bbox = font.getbbox("content")
text_position = (10, 10)
draw = ImageDraw.Draw(img)
draw.text(text_position, "content", fill=(0, 0, 0), font=font)
img.show()