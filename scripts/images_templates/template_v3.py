from PIL import Image, ImageFont, ImageDraw
from scripts.images_templates.template_utils import truncate_text, separate_text_in_lines_by_length, separate_text_in_lines_by_width

def template_v3(data, colors, sizes, fonts):
    try:
        TITLE_FONT = ImageFont.truetype(fonts['title'], sizes['title'])
        PRICE_FONT = ImageFont.truetype(fonts['price'], sizes['price'])
        AREA_FONT = ImageFont.truetype(fonts['area'], sizes['area'])
        LOCATION_FONT = ImageFont.truetype(fonts['location'], sizes['location'])
    except Exception as e:
        print(f'Fonts not found! {e}')

    data['title'] = truncate_text(data['title'], sizes['title_limit'])
    
    image = Image.new('RGBA', sizes['image'], colors['background'])
    draw = ImageDraw.Draw(image)

    top_bottom_padding = 50
    left_right_padding = 80
    y_position = top_bottom_padding

    draw.text((left_right_padding, y_position), data['location'], colors['location'], LOCATION_FONT)
    y_position += draw.textbbox((0, 0), 'temp_text', LOCATION_FONT)[3]

    full_price_text = f'{data["price-text"]} {data["price"]}'
    draw.text((left_right_padding, y_position), full_price_text, colors['price'], PRICE_FONT)
    y_position += draw.textbbox((0, 0), 'temp_text', PRICE_FONT)[3]

    full_area_text = f'{data["rentorbuy"]} / {data["flatorhouse"]} / {data["squarefeets"]}'
    area_line_height = draw.textbbox((0, 0), 'temp_text', AREA_FONT)[3]
    area_lines = separate_text_in_lines_by_length(full_area_text, sizes['area_limit'])

    for line in area_lines:
        draw.text((left_right_padding, y_position), line, colors['area'], AREA_FONT)
        y_position += area_line_height

    y_position += 20

    title_line_width = sizes['image'][0] - (2 * left_right_padding)
    title_line_height = draw.textbbox((0, 0), 'temp_text', TITLE_FONT)[3]
    title_lines = separate_text_in_lines_by_width(draw, data['title'], TITLE_FONT, title_line_width)

    for line in title_lines:
        draw.text((left_right_padding,  y_position), line, fill=colors['title'], font=TITLE_FONT)
        y_position += title_line_height



    return image
