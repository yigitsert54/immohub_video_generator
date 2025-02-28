from PIL import Image, ImageFont, ImageDraw
from scripts.images_templates.template_utils import draw_text, get_text_height


def template_v4(data, colors, sizes, fonts):
    try:
        price_font = ImageFont.truetype(fonts['price'], sizes['price'])
        area_font = ImageFont.truetype(fonts['area'], sizes['area'])
        location_font = ImageFont.truetype(fonts['location'], sizes['location'])
    except Exception as e:
        print(f'Fonts not found! {e}')
        return False


    # Create text elements to render
    full_price_text = f'{data["price-text"]} {data["price"]}'
    full_area_text = f'{data["rentorbuy"]} / {data["flatorhouse"]} / {data["squarefeets"]}'
    location_text = data['location']

    # Calculate text height of these text elements
    price_height = get_text_height(full_price_text, price_font)
    area_height = get_text_height(full_area_text, price_font)
    location_height = get_text_height(full_price_text, price_font)

    # Calculate text heiht and free height
    total_text_height = price_height + area_height + location_height
    total_free_height = 193 - total_text_height

    # Get line height
    line_height = int(total_free_height/8) if total_free_height/8 <= 8 else 8

    # Set other values
    top_padding = int((total_free_height - 2*line_height)/2)
    left_padding = 80
    y_position = top_padding
    line_spacing = line_height

    image = Image.new('RGBA', sizes['image'], colors['background'])
    draw = ImageDraw.Draw(image)


    y_position = draw_text(draw, (left_padding, y_position), full_price_text, colors['price'], price_font)
    y_position += line_spacing
    

    y_position = draw_text(draw, (left_padding, y_position), full_area_text, colors['area'], area_font)
    y_position += line_spacing

    y_position = draw_text(draw, (left_padding, y_position), location_text, colors['location'], location_font)

    return image

