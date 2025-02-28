from moviepy import AudioFileClip
from PIL import Image
from random import shuffle, randint
import os


def select_music(path, video_duration):
    files = os.listdir(path)
    audio_files = [audio for audio in files if audio.endswith(('.mp3', '.wav'))]
    shuffle(audio_files)
    for file in audio_files:
        audio = AudioFileClip(os.path.join(path, file))
        if audio.duration >= video_duration:
            audio_diference_duration = audio.duration - video_duration
            start = randint(0, int(audio_diference_duration))
            end = start + video_duration
            return audio.subclipped(start, end)
        
    print('You do not have any songs with the required duration for this video.')
    return False


def get_data(path):
    data = {}
    
    with open(path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()

            if not line:
                continue
            if '|' in line:
                key, value = line.split('|', 1)  
                data[key.strip()] = value.strip() 
    
    return data


def create_radial_gradient(width, height, color, intensity):
    gradient = Image.new("RGBA", (width, height), color=(255, 255, 255, 0))
    center_x, center_y = width // 2, height // 2
    max_distance = ((center_x ** 2 + center_y ** 2) ** 0.5)  

    for y in range(height):
        for x in range(width):
            distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** intensity
            alpha = int(255 * (1 - (distance / max_distance)))
            alpha = max(0, min(255, alpha))
            gradient.putpixel((x, y), (color[0], color[1], color[2], alpha))

    return gradient


def set_gradient(video_size, gradient_position, gradient_size, color, intesitivy):
    image = Image.new('RGBA', video_size, (255, 255, 255, 0))
    gradient_image = create_radial_gradient(gradient_size[0], gradient_size[1], color, intesitivy)
    image.paste(gradient_image, gradient_position, gradient_image)

    return image


def organize_file_list(file_list):
    def extract_number(file_name):
        name_without_extension = file_name.split(".")[0]
        return int(name_without_extension)  
    return sorted(file_list, key=extract_number)


def create_gradient1(width, height, color):
    gradient = Image.new("RGBA", (width, height), color=(255, 255, 255, 0))  
    for y in range(height):
        alpha = int(350 * (y / height))
        for x in range(width):
            gradient.putpixel((x, y), (color[0], color[1], color[2], alpha))
    
    return gradient


def create_gradient(width, height, color):
    gradient = Image.new("RGBA", (width, height), color=(255, 255, 255, 0))
    for y in range(height):
        alpha = 255
        for x in range(width):
            gradient.putpixel((x, y), (color[0], color[1], color[2], alpha))

    return gradient

def create_gradient_v2(width, height, color):
    gradient = Image.new("RGBA", (width, height), color=(255, 255, 255, 0))

    # y = mx + n
    m = 255/(height-1)
    n = 0
    for y in range(height):
        alpha = m * y + n

        for x in range(width):
            gradient.putpixel((x, y), (color[0], color[1], color[2], int(alpha)))

    return gradient



def circular_shift(lst, shift):
    shift = shift % len(lst)
    return lst[shift:] + lst[:shift]
