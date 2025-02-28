from PIL import Image, ImageFont, ImageDraw
from scripts.images_templates.template_utils import center_text


def template_v5(data, colors, sizes, fonts):
    try:
        PRICE_FONT = ImageFont.truetype(fonts['price'], sizes['price'])
        AREA_FONT = ImageFont.truetype(fonts['area'], sizes['area'])
        LOCATION_FONT = ImageFont.truetype(fonts['location'], sizes['location'])
    except Exception as e:
        print(f'Fonts not found! {e}')
        return False
    
    top_padding = 40
    y_position = top_padding
    line_spacing = 15

    image = Image.new('RGBA', sizes['image'], colors['background'])

    full_price_text = f'{data["price-text"]} {data["price"]}'
    image, y_position = center_text(image, full_price_text, PRICE_FONT, colors['price'], y_position)
    y_position += line_spacing
    
    full_area_text = f'{data["rentorbuy"]} / {data["flatorhouse"]} / {data["squarefeets"]}'
    image, y_position = center_text(image, full_area_text, AREA_FONT, colors['area'], y_position)
    y_position += line_spacing

    image, y_position = center_text(image, data['location'], LOCATION_FONT, colors['location'], y_position)

    return image

