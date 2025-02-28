from scripts.create_slideshow import slide_show
from scripts.images_templates.template_v4 import template_v4
from moviepy import ImageClip, CompositeVideoClip
from scripts.video_template_utils import *
from random import shuffle, randint
import numpy as np
import os
import re


# SlideShow setting
AUDIO_CODEC = 'aac'
IMAGES_DIR = 'data/images'
IMAGE_DURATION = 4
VIDEO_SIZE = (1080, 1920)
SLIDE_TRANSITION_DURATION_IN_SECONDS = 2.5
ZOOM_OUT_ACCELERATION = 0.35 
STATIC_SLIDE_DURATION = 0.1
SLIDE_SHOW_1_SIZE = (1080,731)
SLIDE_SHOW_2_SIZE = (463,796)
SLIDE_SHOW_3_SIZE = (619,1024)
BACKGROUND_SLIDE_SHOW_SIZE = VIDEO_SIZE
SLIDE_SHOW_1_POSITION = (0, 0)
SLIDE_SHOW_2_POSITION = (616, 731)
SLIDE_SHOW_3_POSITION = (0, 924)
ZOOM_SCALE = 1.2
ZOOM_IN_ACCELERATION = 1
FPS = 30

TRANS_VAR = 1
TRANSITION_VARIATION_1 = TRANS_VAR
TRANSITION_VARIATION_2 = TRANS_VAR
TRANSITION_VARIATION_3 = TRANS_VAR

TRANSITION_DURATION = 0.8


# Template Setting
LOGO_WIDTH = 290
LOGO_POSITION = (700, 1619)
TEMPLATE_SIZE = (616, 175)
TEMPLATE_POSITION = (0, 731)
GRADIENT_SIZE = (2356, 2356)
GRADIENT_POSITION = (-638, -218)

TEMPLEATE_BACKGROUND_COLOR = (255, 255, 255)
PRICE_COLOR = (194, 18, 0)
LOCATION_COLOR = (0, 0, 0)
AREA_COLOR = (0, 57, 149)
GRADIENT_COLOR = (255, 255, 255)
GRADIENT_INTENSITY = 0.43

PRICE_FONT_SIZE = 47
LOCATION_FONT_SIZE = 30
AREA_FONT_SIZE = 35

PRICE_FONT_PATH = 'data/fonts/InterBold.ttf'
AREA_FONT_PATH = 'data/fonts/Inter.ttf'
LOCATION_FONT_PATH = 'data/fonts/InterBold.ttf'


def extract_number(filename):
    """ Extrahiert die erste Zahl aus einem Dateinamen für die Sortierung. """
    match = re.search(r'\d+', filename)  # Sucht nach der ersten Zahl im Dateinamen
    return int(match.group()) if match else float('inf')  # Falls keine Zahl vorhanden, ans Ende sortieren

def organize_file_list(file_list):
    """ Sortiert die Dateien basierend auf den extrahierten Nummern. """
    return sorted(file_list, key=extract_number)


def main():

    files = os.listdir(IMAGES_DIR)
    files = [f'{IMAGES_DIR}/{file}' for file in organize_file_list(files)]

    slide_show_1 = slide_show(
        files,
        SLIDE_TRANSITION_DURATION_IN_SECONDS,
        STATIC_SLIDE_DURATION,
        SLIDE_SHOW_1_SIZE,
        ZOOM_SCALE,
        ZOOM_IN_ACCELERATION,
        ZOOM_OUT_ACCELERATION,
        FPS,
        TRANSITION_VARIATION_1,
        TRANSITION_DURATION
    )

    files = circular_shift(files, 1)

    slide_show_2 = slide_show(
        files,
        SLIDE_TRANSITION_DURATION_IN_SECONDS,
        STATIC_SLIDE_DURATION,
        SLIDE_SHOW_2_SIZE,
        ZOOM_SCALE,
        ZOOM_IN_ACCELERATION,
        ZOOM_OUT_ACCELERATION,
        FPS,
        TRANSITION_VARIATION_2,
        TRANSITION_DURATION
    )

    files = circular_shift(files, 1)

    slide_show_3 = slide_show(
        files,
        SLIDE_TRANSITION_DURATION_IN_SECONDS,
        STATIC_SLIDE_DURATION,
        SLIDE_SHOW_3_SIZE,
        ZOOM_SCALE,
        ZOOM_IN_ACCELERATION,
        ZOOM_OUT_ACCELERATION,
        FPS,
        TRANSITION_VARIATION_3,
        TRANSITION_DURATION
    )
    
    for index in range(len(slide_show_1)):
        slide_show_1[index] = slide_show_1[index].with_position(SLIDE_SHOW_1_POSITION)
        slide_show_2[index] = slide_show_2[index].with_position(SLIDE_SHOW_2_POSITION)
        slide_show_3[index] = slide_show_3[index].with_position(SLIDE_SHOW_3_POSITION)
            

    if TRANSITION_VARIATION_1 == 1:
        video_duration = slide_show_1[0].duration
    else:
        video_duration = (len(files) * SLIDE_TRANSITION_DURATION_IN_SECONDS)  + TRANSITION_DURATION

    data = get_data('data/data.txt')

    fonts = {
        'price': PRICE_FONT_PATH,
        'area': AREA_FONT_PATH,
        'location': LOCATION_FONT_PATH
    }

    colors = {
        'background': TEMPLEATE_BACKGROUND_COLOR,
        'price': PRICE_COLOR,
        'location': LOCATION_COLOR,
        'area': AREA_COLOR
    }

    sizes = {
        'image': TEMPLATE_SIZE,
        'price': PRICE_FONT_SIZE,
        'area': AREA_FONT_SIZE,
        'location': LOCATION_FONT_SIZE,
    }

    audio = select_music('data/songs', video_duration)

    if audio != False:
        logo_image = ImageClip('data/logo.png').with_duration(video_duration).resized(width=LOGO_WIDTH)
        logo_image = logo_image.with_position(LOGO_POSITION)

        image_template = template_v4(data, colors, sizes, fonts)
        image_clip = ImageClip(np.array(image_template)).with_position(TEMPLATE_POSITION).with_duration(video_duration)

        final_video = CompositeVideoClip([logo_image] + slide_show_1 + [image_clip] + slide_show_3 +  slide_show_2, size=VIDEO_SIZE, bg_color=(255, 255, 255))

        final_video = final_video.with_audio(audio)
        final_video.write_videofile(f'template_4_var_{TRANS_VAR}.mp4', audio_codec=AUDIO_CODEC)

        if isinstance(audio, AudioFileClip):
            audio.close()


if __name__ == '__main__':
    for i in range(3):
        TRANS_VAR = i+2
        TRANSITION_VARIATION_1 = TRANS_VAR
        TRANSITION_VARIATION_2 = TRANS_VAR
        TRANSITION_VARIATION_3 = TRANS_VAR
        print(TRANS_VAR, TRANSITION_VARIATION_1, TRANSITION_VARIATION_2, TRANSITION_VARIATION_3)
        main()
    
