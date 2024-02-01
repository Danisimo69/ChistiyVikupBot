import random
from PIL import Image, ImageDraw, ImageFont


def add_watermark(path, name):
    img = Image.open(f"{path}/{name}").convert("RGBA")
    txt = Image.new('RGBA', img.size, (255,255,255,0))

    #Creating Text
    text = "Smile025"
    font = ImageFont.truetype("OtherFiles/Rare_Groove.ttf", 60)

    #Creating Draw Object
    d = ImageDraw.Draw(txt)

    #Positioning Text
    width, height = img.size

    x=width/2-60
    y=height/2-50

    #Applying Text
    d.text((x,y), text, fill=(255,255,255, 83), font=font)

    #Combining Original Image with Text and Saving
    watermarked = Image.alpha_composite(img, txt)
    watermarked.save(f'{path}/new_{name.replace(".jpg",".png")}')