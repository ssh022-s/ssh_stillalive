from PIL import Image, ImageDraw, ImageFont

# Create a new image with a transparent background
size = (256, 256)
image = Image.new('RGBA', size, (0, 0, 0, 0))
draw = ImageDraw.Draw(image)

# Draw a rounded rectangle for CPU
margin = 40
rect_bounds = [margin, margin, size[0]-margin, size[1]-margin]
draw.rounded_rectangle(rect_bounds, fill='#2196F3', radius=30)

# Draw some "pins" at the bottom to make it look like a CPU
pin_width = 20
pin_height = 30
pin_spacing = 40
pin_y = size[1] - margin + 10
for x in range(margin + 20, size[0] - margin, pin_spacing):
    draw.rectangle([x, pin_y, x + pin_width, pin_y + pin_height], fill='#1976D2')

# Draw some "circuit lines"
line_color = '#64B5F6'
line_width = 6
# Horizontal lines
for y in range(margin + 40, size[1] - margin - 40, 40):
    draw.line([(margin + 30, y), (size[0] - margin - 30, y)], fill=line_color, width=line_width)
# Vertical lines
for x in range(margin + 40, size[0] - margin - 40, 40):
    draw.line([(x, margin + 30), (x, size[1] - margin - 30)], fill=line_color, width=line_width)

# Add "CPU" text
try:
    font = ImageFont.truetype("arial.ttf", 60)
except:
    font = ImageFont.load_default()
    
text_position = (size[0]//2, size[1]//2 - 10)
draw.text(text_position, "CPU", fill="white", font=font, anchor="mm")

# Save as ICO file
image.save('app_icon.ico', format='ICO', sizes=[(256, 256)]) 