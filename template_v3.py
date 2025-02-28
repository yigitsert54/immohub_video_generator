from scripts.create_slideshow import slide_show
from scripts.images_templates.template_v3 import template_v3
from moviepy import ImageClip, CompositeVideoClip
from scripts.video_template_utils import *
import numpy as np
import os


# SlideShow setting
AUDIO_CODEC = 'aac'
IMAGES_DIR = 'data/images'
SLIDE_TRANSITION_DURATION_IN_SECONDS = 2.5
STATIC_SLIDE_DURATION = 0.1
VIDEO_SIZE = (1080, 1920)
SLIDE_SHOW_SIZE = VIDEO_SIZE
ZOOM_SCALE = 1.5
ZOOM_IN_ACCELERATION = 2 
ZOOM_OUT_ACCELERATION = 0.35 
FPS = 30
TRANSITION_VARIATION = 4
TRANSITION_DURATION = 0.5


# Template Setting
LOGO_WIDTH = 200
LOGO_POSITION = ((VIDEO_SIZE[0] / 2) - (LOGO_WIDTH / 2), 200)
TEMPLATE_SIZE = (735, 450)

TITLE_BACKGROUND_COLOR = (0, 57, 149)
TITLE_COLOR = (0, 0, 0)
TEMPLEATE_BACKGROUND_COLOR = (255, 255, 255, 150) # THE LAST VALUE IS THE ALPHA VALUE (0, 255)
PRICE_COLOR = (194, 18, 0)
AREA_COLOR = (0, 0, 0)
LOCATION_COLOR = (0, 0, 0)

TITLE_CHARACTER_LIMIT = 100
AREA_CHARACTER_LIMIT = 28
TITLE_FONT_SIZE = 38
PRICE_FONT_SIZE = 50
LOCATION_FONT_SIZE = 40
AREA_FONT_SIZE = 40

TITLE_FONT_PATH = 'data/fonts/Inter.ttf'
PRICE_FONT_PATH = 'data/fonts/InterBold.ttf'
AREA_FONT_PATH = 'data/fonts/InterBold.ttf'
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
        'title_limit': TITLE_CHARACTER_LIMIT,
        'area_limit': AREA_CHARACTER_LIMIT
    }


    audio = select_music('data/songs', video_duration)
    if audio != False:

        logo_image = ImageClip('data/logo.png').with_duration(video_duration).resized(width=LOGO_WIDTH)
        logo_image = logo_image.with_position(LOGO_POSITION)

        image_template = template_v3(data, colors, sizes, fonts)
        image_clip = ImageClip(np.array(image_template)).with_position((0, 1044)).with_duration(video_duration)

        final_video = CompositeVideoClip(slide_show_video + [image_clip, logo_image], size=VIDEO_SIZE)
        final_video = final_video.with_audio(audio)
        final_video.write_videofile(f'template_3_var_{TRANSITION_VARIATION}.mp4', audio_codec=AUDIO_CODEC)

        if isinstance(audio, AudioFileClip):
            audio.close()


if __name__ == '__main__':

    for i in range(4):
        TRANSITION_VARIATION = i+1
        main()
