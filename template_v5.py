from scripts.create_slideshow import slide_show
from scripts.images_templates.template_v5 import template_v5
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
MAIN_SLIDE_SHOW_SIZE = (926, 676)
BACKGROUND_SLIDE_SHOW_SIZE = VIDEO_SIZE
MAIN_SLIDE_SHOW_POSITION = (76, 512)
ZOOM_SCALE = 1.3
ZOOM_IN_ACCELERATION = 2 
ZOOM_OUT_ACCELERATION = 0.35 
FPS = 30
TRANSITION_VARIATION = 4
TRANSITION_DURATION = 0.8



# Template Setting
LOGO_WIDTH = 180
LOGO_POSITION = ((VIDEO_SIZE[0] / 2) - (LOGO_WIDTH / 2), 214)
TEMPLATE_SIZE = (926, 275)
TEMPLATE_POSITION = (MAIN_SLIDE_SHOW_POSITION[0], MAIN_SLIDE_SHOW_SIZE[1] + MAIN_SLIDE_SHOW_POSITION[1])
GRADIENT_SIZE = (2356, 2356)
GRADIENT_POSITION = (-638, -218)

TEMPLEATE_BACKGROUND_COLOR = (255, 255, 255)
PRICE_COLOR = (194, 18, 0)
LOCATION_COLOR = (0, 0, 0)
AREA_COLOR = (0, 57, 149)
GRADIENT_COLOR = (255, 255, 255)
GRADIENT_INTENSITY = 0.43

PRICE_FONT_SIZE = 55
LOCATION_FONT_SIZE = 40
AREA_FONT_SIZE = 45

PRICE_FONT_PATH = 'data/fonts/InterBold.ttf'
AREA_FONT_PATH = 'data/fonts/InterBold.ttf'
LOCATION_FONT_PATH = 'data/fonts/InterBold.ttf'



def main():

    files = os.listdir(IMAGES_DIR)
    files = [f'{IMAGES_DIR}/{file}' for file in organize_file_list(files)]

    main_slide_show = slide_show(
        files,
        SLIDE_TRANSITION_DURATION_IN_SECONDS,
        STATIC_SLIDE_DURATION,
        MAIN_SLIDE_SHOW_SIZE,
        ZOOM_SCALE,
        ZOOM_IN_ACCELERATION,
        ZOOM_OUT_ACCELERATION,
        FPS,
        TRANSITION_VARIATION,
        TRANSITION_DURATION
    )

    background_slide_show = slide_show(
        files,
        SLIDE_TRANSITION_DURATION_IN_SECONDS,
        STATIC_SLIDE_DURATION,
        VIDEO_SIZE,
        ZOOM_SCALE,
        ZOOM_IN_ACCELERATION,
        ZOOM_OUT_ACCELERATION,
        FPS,
        TRANSITION_VARIATION,
        TRANSITION_DURATION
    )

    if TRANSITION_VARIATION == 1:
        video_duration = main_slide_show[0].duration
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

        image_template = template_v5(data, colors, sizes, fonts)
        image_clip = ImageClip(np.array(image_template)).with_position(TEMPLATE_POSITION).with_duration(video_duration)

        gradient_image = set_gradient(VIDEO_SIZE, GRADIENT_POSITION, GRADIENT_SIZE, GRADIENT_COLOR, GRADIENT_INTENSITY)
        gradient_image_clip = ImageClip(np.array(gradient_image)).with_duration(video_duration)


        if TRANSITION_VARIATION == 1:
            main_slide_show[0] = main_slide_show[0].with_position(MAIN_SLIDE_SHOW_POSITION)
        else:
            for index in range(len(main_slide_show)):
                main_slide_show[index] = main_slide_show[index].with_position(MAIN_SLIDE_SHOW_POSITION)


        final_video = CompositeVideoClip(background_slide_show + [gradient_image_clip, image_clip] + main_slide_show + [logo_image], size=VIDEO_SIZE)
        final_video = final_video.with_audio(audio)
        final_video.write_videofile(f'template_5_var_{TRANSITION_VARIATION}.mp4', audio_codec=AUDIO_CODEC)


        if isinstance(audio, AudioFileClip):
            audio.close()



if __name__ == '__main__':
    for i in range(4):
        TRANSITION_VARIATION = i+1
        main()
    