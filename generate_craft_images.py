import os
from PIL import Image, ImageDraw, ImageFont

img_dir = os.path.join(os.path.dirname(__file__), 'static', 'images')
os.makedirs(img_dir, exist_ok=True)

crafts = [
    ('terracotta_horse.jpg', (184, 80, 66), (231, 232, 209), "Terracotta Horse", "Bankura GI Craft"),
    ('chikankari_kurti.jpg', (255, 255, 255), (95, 122, 110), "Lucknow Chikankari", "Hand Embroidered"),
    ('dokra_art.jpg', (160, 120, 40), (74, 35, 24), "Bastar Dokra Metal", "Lost Wax Art"),
    ('madhubani_art.jpg', (230, 180, 80), (184, 80, 66), "Mithila Madhubani", "Natural Colors"),
    ('blue_pottery.jpg', (30, 100, 180), (251, 249, 243), "Jaipur Blue Pottery", "Quartz Clay Free")
]

for filename, bg_color, text_color, title, subtitle in crafts:
    filepath = os.path.join(img_dir, filename)
    img = Image.new('RGB', (600, 400), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Draw decorative border
    draw.rectangle([20, 20, 580, 380], outline=text_color, width=6)
    
    # Draw simple emblem circle
    draw.ellipse([250, 110, 350, 210], fill=text_color)
    
    # Draw title text fallback
    draw.text((300, 260), title, fill=text_color, anchor="mm")
    draw.text((300, 300), subtitle, fill=text_color, anchor="mm")
    
    img.save(filepath, "JPEG")
    print(f"Generated craft image asset: {filename}")
