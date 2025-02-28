from scripts.create_slideshow import slide_show
from scripts.images_templates.template_v1 import template_v1
from moviepy import ImageClip, CompositeVideoClip
from scripts.video_template_utils import *
import numpy as np
import os
import random


# SlideShow setting
AUDIO_CODEC = 'aac'
IMAGES_DIR = 'data/images'
SLIDE_TRANSITION_DURATION_IN_SECONDS = 2.5
STATIC_SLIDE_DURATION = 0.1
VIDEO_SIZE = (1080, 1920)
SLIDE_SHOW_SIZE = (VIDEO_SIZE[0], 1120)
ZOOM_SCALE = 1.5
ZOOM_IN_ACCELERATION = 2 
ZOOM_OUT_ACCELERATION = 0.35 
FPS = 30
TRANSITION_VARIATION = 1
TRANSITION_DURATION = 0.5


# Template Setting
LOGO_WIDTH = 250
LOGO_POSITION = ((VIDEO_SIZE[0] / 2) - (LOGO_WIDTH / 2), 200)
TEMPLATE_SIZE = (VIDEO_SIZE[0], VIDEO_SIZE[1] - SLIDE_SHOW_SIZE[1])

TITLE_BACKGROUND_COLOR = (0, 57, 149)
TITLE_COLOR = (255, 255, 255)
TEMPLEATE_BACKGROUND_COLOR = (255, 255, 255)
PRICE_COLOR = (194, 18, 0)
LOCATION_COLOR = (0, 0, 0)
AREA_COLOR = (0, 57, 149)

TITLE_CHARACTER_LIMIT = 110
TITLE_FONT_SIZE = 38
PRICE_FONT_SIZE = 55
LOCATION_FONT_SIZE = 45
AREA_FONT_SIZE = 40

TITLE_FONT_PATH = 'data/fonts/Inter.ttf'
PRICE_FONT_PATH = 'data/fonts/InterBold.ttf'
AREA_FONT_PATH = 'data/fonts/Inter.ttf'
LOCATION_FONT_PATH = 'data/fonts/InterBold.ttf'



def main():

    files = os.listdir(IMAGES_DIR)
    files = [f'{IMAGES_DIR}/{file}' for file in organize_file_list(files)]

    slide_show_video = slide_show(
        files,
        SLIDE_TRANSITION_DURATION_IN_SECONDS,
        STATIC_SLIDE_DURATION,
        SLIDE_SHOW_SIZE,
        ZOOM_SCALE,
        ZOOM_IN_ACCELERATION,
        ZOOM_OUT_ACCELERATION,
        FPS,
        TRANSITION_VARIATION,
        TRANSITION_DURATION
    )

    if TRANSITION_VARIATION == 1:
        video_duration = slide_show_video[0].duration
    else:
        video_duration = (len(files) * SLIDE_TRANSITION_DURATION_IN_SECONDS)  + TRANSITION_DURATION

    data = get_data('data/data.txt')

    fonts = {
        'title': TITLE_FONT_PATH,
        'price': PRICE_FONT_PATH,
        'area': AREA_FONT_PATH,
        'location': LOCATION_FONT_PATH
    }

    colors = {
        'background': TEMPLEATE_BACKGROUND_COLOR,
        'title': TITLE_COLOR,
        'title_background': TITLE_BACKGROUND_COLOR,
        'price': PRICE_COLOR,
        'location': LOCATION_COLOR,
        'area': AREA_COLOR
    }

    sizes = {
        'image': TEMPLATE_SIZE,
        'price': PRICE_FONT_SIZE,
        'area': AREA_FONT_SIZE,
        'title': TITLE_FONT_SIZE,
        'location': LOCATION_FONT_SIZE,
        'title_limit': TITLE_CHARACTER_LIMIT
    }

    audio = select_music('data/songs', video_duration)

    if audio != False:
        logo_image = ImageClip('data/logo.png').with_duration(video_duration).resized(width=LOGO_WIDTH)
        logo_image = logo_image.with_position(LOGO_POSITION)

        image_template = template_v1(data, colors, sizes, fonts)

        image_clip = ImageClip(np.array(image_template)).with_position((0, SLIDE_SHOW_SIZE[1])).with_duration(video_duration)

        final_video = CompositeVideoClip([image_clip]+ slide_show_video + [logo_image], size=VIDEO_SIZE)
        final_video = final_video.with_audio(audio)
        final_video.write_videofile(f'final_video_{random.randint(11111,99999)}_var_{TRANSITION_VARIATION}.mp4', audio_codec=AUDIO_CODEC)

        if isinstance(audio, AudioFileClip):
            audio.close()

if __name__ == '__main__':
    main()
