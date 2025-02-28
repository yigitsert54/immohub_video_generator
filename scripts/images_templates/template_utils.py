from PIL import Image, ImageDraw


def create_half_white_half_transparent(width, height, color, height_limit) -> Image:
    image = Image.new("RGBA", (width, height), color=(255, 255, 255, 0))  

    for y in range(height):
        for x in range(width):
            if y >= height_limit:
                image.putpixel((x, y), color)
            else:

                image.putpixel((x, y), (255, 255, 255, 0))
    
    return image


def separate_text_in_lines_by_widthx(draw, text, font, max_width):
    lines = []
    line = []
    
    for word in text.split(' '):
        temp_text = ' '.join(line + [word])
        width = draw.textbbox((0, 0), temp_text, font)[2]
        
        if width <= max_width:
            line.append(word)  
        else:
            lines.append(' '.join(line))

            line = [word]

    if line:
        lines.append(' '.join(line))
    
    return lines


def separate_text_in_lines_by_width(draw, text, font, max_width):

    lines = []
    line = []

    for word in text.split(' '):
        # Prüfe, ob das Wort einen Bindestrich enthält und lang genug ist
        if '-' in word and len(word) > 3:
            # Teile das Wort an den Bindestrichen
            parts = word.split('-')

            for i, part in enumerate(parts):
                # Füge den Bindestrich wieder hinzu, außer beim letzten Teil
                if i < len(parts) - 1:
                    part = part + '-'

                # Prüfe, ob dieser Teil in die aktuelle Zeile passt
                temp_text = ' '.join(line + [part])
                width = draw.textbbox((0, 0), temp_text, font)[2]

                if width <= max_width:
                    line.append(part)
                else:
                    lines.append(' '.join(line))
                    line = [part]
        else:
            # Normales Wort ohne Bindestrich, wie in der ursprünglichen Funktion
            temp_text = ' '.join(line + [word])
            width = draw.textbbox((0, 0), temp_text, font)[2]

            if width <= max_width:
                line.append(word)
            else:
                lines.append(' '.join(line))
                line = [word]

    # Füge die letzte Zeile hinzu
    if line:
        lines.append(' '.join(line))

    return lines


def separate_text_in_lines_by_length(text, max_length):
    line = []
    lines = []

    for word in text.split(' '):
        temp_text = ' '.join(line + [word])

        
        if len(temp_text) <= max_length:
            line.append(word)  
        else:
            lines.append(' '.join(line))

            line = [word]

    if line:
        
        lines.append(' '.join(line))
    
    return lines


def truncate_text(text, character_limit):
    if len(text) > character_limit:
        return text[:character_limit - 3] + "..."
    return text


def center_text(image, text, font, color, y):
    draw = ImageDraw.Draw(image)

    img_width, _ = image.size

    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]

    x = (img_width - text_width) // 2
    draw.text((x, y), text, font=font, fill=color)

    return image, y + text_bbox[3]


def draw_text(draw, pos, text, color, font):
    draw.text(pos, text, color, font)
    return pos[1] + draw.textbbox((0, 0), 'temp_text', font)[3]


def get_text_height(text, image_font):
    """
    Berechnet die Höhe eines Textes beim Rendern mit der angegebenen Schriftart und -größe.

    :param text: Der zu messende Text.
    :param image_font: ImageFont.truetype(font_path, font_size)
    :return: die Höhe des gerenderten Textes in Pixel oder None, falls ein Fehler auftritt.
    """

    font = image_font

    # Dummy-Image erstellen, um ein ImageDraw-Objekt zu erhalten
    dummy_image = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(dummy_image)

    # Bounding Box des Textes ermitteln
    bbox = draw.textbbox((0, 0), text, font=font)
    text_height = bbox[3] - bbox[1]  # Höhe berechnen (y_max - y_min)

    return text_height
