from PIL import Image, ImageFont, ImageDraw
from scripts.images_templates.template_utils import truncate_text, separate_text_in_lines_by_width

def template_v1(data, colors, sizes, fonts):
    try:
        TITLE_FONT = ImageFont.truetype(fonts['title'], sizes['title'])
        PRICE_FONT = ImageFont.truetype(fonts['price'], sizes['price'])
        AREA_FONT = ImageFont.truetype(fonts['area'], sizes['area'])
        LOCATION_FONT = ImageFont.truetype(fonts['location'], sizes['location'])
    except Exception as e:
        print(f'Fonts not found! {e}')
        return False
    
    data['title'] = truncate_text(data['title'], sizes['title_limit'])
    
    left_right_padding = 80
    top_bottom_padding_box = 38
    top_bottom_padding_title = 22

    image = Image.new('RGBA', sizes['image'], colors['background'])
    draw = ImageDraw.Draw(image)

    y_position = top_bottom_padding_title

    full_price_text = f'{data["price-text"]} {data["price"]}'
    draw.text((left_right_padding, y_position), full_price_text, colors['price'], PRICE_FONT)
    y_position += draw.textbbox((0, 0), 'temp_text', PRICE_FONT)[3]

    full_area_text = f'{data["rentorbuy"]} / {data["flatorhouse"]} / {data["squarefeets"]}'
    draw.text((left_right_padding, y_position), full_area_text, colors['area'], AREA_FONT)
    y_position += draw.textbbox((0, 0), 'temp_text', AREA_FONT)[3]

    draw.text((left_right_padding, y_position), data['location'], colors['location'], LOCATION_FONT)
    y_position += draw.textbbox((0, 0), 'temp_text', LOCATION_FONT)[3]

    line_width = 760
    line_height = draw.textbbox((0, 0), 'temp_text', TITLE_FONT)[3]
    lines = separate_text_in_lines_by_width(draw, data['title'], TITLE_FONT, line_width)

    rect_height = (len(lines) * line_height) + 2 * (top_bottom_padding_box)
    draw.rectangle(
        [(0, y_position + top_bottom_padding_title), (sizes['image'][0], rect_height + y_position + top_bottom_padding_box)], fill=colors['title_background']
    )
    y_position += top_bottom_padding_title + top_bottom_padding_box

    for line in lines:
        draw.text((left_right_padding,  y_position), line, fill=colors['title'], font=TITLE_FONT)
        y_position += line_height

    return image
