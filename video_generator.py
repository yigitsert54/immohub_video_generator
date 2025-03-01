# import from own files
from urls import ROOT_DOMAIN
from scripts.create_slideshow import slide_show
from keys import OPEN_AI_KEY

# import video template utils
from scripts.video_template_utils import (
select_music,
create_gradient,
create_gradient_v2,
set_gradient,
circular_shift
)

# import image templates
from scripts.images_templates.template_v1 import template_v1
from scripts.images_templates.template_v2 import template_v2
from scripts.images_templates.template_v3 import template_v3
from scripts.images_templates.template_v4 import template_v4
from scripts.images_templates.template_v5 import template_v5

# import modules
from moviepy import ImageClip, CompositeVideoClip, AudioFileClip
from PIL import ImageColor, ImageFont
import numpy as np
import traceback
import requests
import random
import shutil
import uuid
import os


class VideoGenerator:
    def __init__(self, client):

        # Open AI client
        self.client = client

        # General settings
        self.audio_codec = 'aac'  # AUDIO_CODEC
        self.image_dir = 'data/images/'  # IMAGES_DIR
        self.video_size = (1080, 1920)  # VIDEO_SIZE
        self.fps = 30  # FPS

    def delete_directories(self):

        # Extract root images directory
        root_image_dir = self.image_dir

        # Loop through each entry in root_image_dir
        for entry in os.listdir(root_image_dir):

            # Get entry path
            entry_path = os.path.join(root_image_dir, entry)

            # Check if the entry is a sub_directory
            if os.path.isdir(entry_path):
                shutil.rmtree(entry_path)

    def download_images(self, property_id, image_urls, logo_url,  max_image_count=10, random_image_order=False):

        # Extract root images directory
        root_image_dir = self.image_dir

        # target folder path
        target_folder_path = root_image_dir + property_id

        # Create new directory with property id
        os.makedirs(target_folder_path, exist_ok=True)

        # Create copy of image_urls_list
        image_urls_copy = image_urls.copy()

        # shuffle list
        if random_image_order:
            random.shuffle(image_urls_copy)

        # Loop through each image_url to download them
        for i, url in enumerate(image_urls_copy):

            # break loop if max number of images is reached
            if i + 1 > max_image_count:
                break

            try:  # execute request to image url
                r = requests.get(url)
                r.raise_for_status()
            except requests.RequestException as e:
                print(f"Error in {__file__}: {e}")
                traceback.print_exc()
                continue
            else:
                image_type = url.split(".")[-1]

                # Create path for image
                file_path = os.path.join(target_folder_path, f"image_{property_id}_{i}.{image_type}")

                # Save image
                with open(file_path, "wb") as f:
                    f.write(r.content)

        # Download logo image
        if logo_url:

            # Create new logo directory
            os.makedirs(target_folder_path + "/logo", exist_ok=True)

            try:  # execute request to logo url
                r = requests.get(ROOT_DOMAIN+logo_url)
                r.raise_for_status()
            except requests.RequestException as e:
                print(f"Error while downloading logo image in {__file__}: {e}")
                traceback.print_exc()
            else:

                logo_image_type = logo_url.split(".")[-1]

                # Create path for image
                file_path_logo = os.path.join(target_folder_path + "/logo", f"logo.{logo_image_type}")

                # Save image
                with open(file_path_logo, "wb") as f:
                    f.write(r.content)

        # return target_folder_path for further use in rendering script
        return target_folder_path

    def generate_video_text(self, description_text):

        if description_text is not None and len(description_text) >= 5:

            # Set immo_description
            immo_description = description_text

        else:
            immo_description = ("Leider keine Beschreibung verfügbar. Erstelle deshalb einen allgemein gültigen "
                                "Exposé-Teaser/Immobilien-Spotlight. Verzichte dabei auf explizite Werte und Daten. "
                                "Mach es so dass es immer passt und halte dich an meine Vorgaben!")

        final_prompt = ("Fasse mir die folgende Immobilien Beschreibung als Exposé-Teaser/Immobilien-Spotlight "
                        "auf 25 Wörter zusammen. Fasse den Inhalt auf das nötigste zusammen, aber erreiche dennoch "
                        "einen maximalen Werbeeffekt (Social Media geeignet).\n"
                        "Benutze mindestens 20 aber maximal 25 Wörter. Keine Hashtags, Sonderzeichen, "
                        "Anführungszeichen oder Satzeichen am Ende. - Wichtig alles auf deutsch!\n"
                        f'Hier die Beschreibung: "{immo_description}"')

        print("  - Generating ai video text...\n")

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": final_prompt}]
        )

        video_text = response.choices[0].message.content

        return video_text

    @staticmethod
    def convert_to_rgba(color: str):
        if color.startswith("rgba"):  # if color is already rgba
            rgba_splitted = color.replace(")", "").split("rgba(")[1].split(", ")
            alpha_small = rgba_splitted[3]
            alpha_large = round(float(rgba_splitted[3]) * 255)

            modified_rgba_color = color.replace(alpha_small, str(alpha_large))
            rgba = ImageColor.getcolor(modified_rgba_color, "RGBA")

        else:
            rgba = ImageColor.getcolor(color, "RGBA")

        return rgba

    def get_dynamic_font_size(self, text: str, font_path: str, max_width_ratio: float, static_font_size: int) -> int:
        """
        Calculates the ideal font size so that the text does not exceed the maximum width.

        :param text: The text to be displayed
        :param font_path: Path to the font file (e.g. “arial.ttf”)
        :param max_width_ratio: The maximum ratio of text width to video width
        :param static_font_size: The static font size set in the template
        :return: The adjusted font size (int)
        """

        # Set up final font size (start with 'static_font_size')
        final_font_size = static_font_size

        # Create font
        font = ImageFont.truetype(font_path, final_font_size)

        # Calculate text width in pixels
        text_width = font.getlength(text)

        # Calculate current_width_ratio
        current_width_ratio = text_width/self.video_size[0]

        # Check if current_width_ratio is wider than allowed
        if current_width_ratio > max_width_ratio:

            # Start while loop until the font size is correct
            while current_width_ratio > max_width_ratio:

                # Reduce the font size
                final_font_size -= 1

                # Create font
                font = ImageFont.truetype(font_path, final_font_size)

                # Calculate text width in pixels
                text_width = font.getlength(text)

                # Calculate current_width_ratio
                current_width_ratio = text_width / self.video_size[0]

        return final_font_size

    def render_template_v1(self, property_id, immo_data, color_data, further_settings):

        # TEMPLATE VARS
        slide_transition_duration_in_seconds = 2.5  # SLIDE_TRANSITION_DURATION_IN_SECONDS
        static_slide_duration = 0.1  # STATIC_SLIDE_DURATION
        slide_show_size = (self.video_size[0], 1120)  # SLIDE_SHOW_SIZE
        zoom_scale = 1.5  # ZOOM_SCALE
        zoom_in_acceleration = 2  # ZOOM_IN_ACCELERATION
        zoom_out_acceleration = 0.35  # ZOOM_OUT_ACCELERATION
        logo_width = 250  # LOGO_WIDTH
        logo_position = ((self.video_size[0] / 2) - (logo_width / 2), 200)  # LOGO_POSITION
        transition_type = further_settings["transition_type"]
        transition_duration = 0.5  # TRANSITION_DURATION

        title_font_path = 'data/fonts/Inter.ttf'  # TITLE_FONT_PATH
        price_font_path = 'data/fonts/InterBold.ttf'  # PRICE_FONT_PATH
        area_font_path = 'data/fonts/Inter.ttf'  # AREA_FONT_PATH
        location_font_path = 'data/fonts/InterBold.ttf'  # LOCATION_FONT_PATH

        template_size = (self.video_size[0], self.video_size[1] - slide_show_size[1])
        price_font_size = 55
        area_font_size = 40
        title_font_size = 38
        location_font_size = 45
        title_character_limit = 110
        # / TEMPLATE VARS

        # Create video name with uuid
        video_name = str(uuid.uuid4())

        # Extract image_urls
        image_urls = immo_data["images"]

        # Extract logo url
        logo_url = immo_data["logo_url"]

        # Download images and save path
        images_path = self.download_images(
            property_id=property_id,
            image_urls=image_urls,
            logo_url=logo_url,
            max_image_count=further_settings["max_image_count"],
            random_image_order=further_settings["random_image_order"]
        )

        # List and organize image files
        files = [f for f in os.listdir(images_path) if os.path.isfile(os.path.join(images_path, f))]
        files = [f'{images_path}/{file}' for file in files]

        slide_show_video = slide_show(
            files,
            slide_transition_duration_in_seconds,
            static_slide_duration,
            slide_show_size,
            zoom_scale,
            zoom_in_acceleration,
            zoom_out_acceleration,
            self.fps,
            transition_type,
            transition_duration
        )

        if transition_type == 1:
            video_duration = slide_show_video[0].duration
        else:
            video_duration = (len(files) * slide_transition_duration_in_seconds) + transition_duration

        data = immo_data

        # Create formated ai video text
        video_text = self.generate_video_text(immo_data["description_text"])

        # Add created text to data
        data["title"] = video_text.replace("-", "-\u200b")

        fonts = {
            'title': title_font_path,
            'price': price_font_path,
            'area': area_font_path,
            'location': location_font_path
        }

        colors = {
            'background': self.convert_to_rgba(color_data["color_1"]),  # Large Background
            'price': self.convert_to_rgba(color_data["color_2"]),  # Text 1: Price
            'area': self.convert_to_rgba(color_data["color_3"]),  # Text 2: rentorbuy + area
            'location': self.convert_to_rgba(color_data["color_4"]),  # Text 3: location
            'title_background': self.convert_to_rgba(color_data["color_5"]),  # Small box (video text background)
            'title': self.convert_to_rgba(color_data["color_6"]),  # Long Video Text
        }

        # Get dynamic font size: price
        dynamic_size_price = self.get_dynamic_font_size(
            text=f'{data["price-text"]} {immo_data["price"]}',
            font_path=price_font_path,
            max_width_ratio=0.45,
            static_font_size=price_font_size
        )

        # Get dynamic font size: area
        dynamic_size_area = self.get_dynamic_font_size(
            text=f'{data["rentorbuy"]} / {data["flatorhouse"]} / {data["squarefeets"]}',
            font_path=area_font_path,
            max_width_ratio=0.6,
            static_font_size=area_font_size
        )

        # Get dynamic font size: location
        dynamic_size_location = self.get_dynamic_font_size(
            text=data["location"],
            font_path=location_font_path,
            max_width_ratio=0.85,
            static_font_size=location_font_size
        )

        sizes = {
            'image': template_size,
            'price': dynamic_size_price,
            'area': dynamic_size_area,
            'title': title_font_size,
            'location': dynamic_size_location,
            'title_limit': title_character_limit
        }

        audio = select_music('data/songs', video_duration)

        if audio:

            # Add logo if available
            if logo_url:
                logo_image_type = logo_url.split(".")[-1]
                logo_path = f'{images_path}/logo/logo.{logo_image_type}'
            else:
                logo_path = 'data/transparent.png'

            logo_image = ImageClip(logo_path).with_duration(
                video_duration).resized(width=logo_width)
            logo_image = logo_image.with_position(logo_position)

            image_template = template_v1(data, colors, sizes, fonts)

            image_clip = ImageClip(np.array(image_template)).with_position(
                (0, slide_show_size[1])).with_duration(video_duration)

            final_video = CompositeVideoClip(
                [image_clip] + slide_show_video + [logo_image],
                size=self.video_size
            )

            final_video = final_video.with_audio(audio)
            final_video.write_videofile(
                f'data/videos/{video_name}.mp4',
                audio_codec=self.audio_codec
            )

            if isinstance(audio, AudioFileClip):
                audio.close()
                return video_name

        return None

    def render_template_v2(self, property_id, immo_data, color_data, further_settings):

        # TEMPLATE VARS
        slide_transition_duration_in_seconds = 2.5  # SLIDE_TRANSITION_DURATION_IN_SECONDS
        static_slide_duration = 0.1  # STATIC_SLIDE_DURATION
        slide_show_size = (self.video_size[0], 1290)  # SLIDE_SHOW_SIZE
        zoom_scale = 1.5  # ZOOM_SCALE
        zoom_in_acceleration = 2  # ZOOM_IN_ACCELERATION
        zoom_out_acceleration = 0.35  # ZOOM_OUT_ACCELERATION
        logo_width = 200  # LOGO_WIDTH
        logo_position = ((self.video_size[0] / 2) - (logo_width / 2), 480 )  # LOGO_POSITION
        transition_type = further_settings["transition_type"]
        transition_duration = 0.5  # TRANSITION_DURATION

        title_font_path = 'data/fonts/Inter.ttf'  # TITLE_FONT_PATH
        price_font_path = 'data/fonts/InterBold.ttf'  # PRICE_FONT_PATH
        area_font_path = 'data/fonts/InterBold.ttf'  # AREA_FONT_PATH
        location_font_path = 'data/fonts/InterBold.ttf'  # LOCATION_FONT_PATH

        template_size = (self.video_size[0], 800)
        price_font_size = 55
        area_font_size = 45
        title_font_size = 40
        location_font_size = 45
        title_character_limit = 250

        gradient_height = 630
        gradient_pos = (0, slide_show_size[1] - gradient_height)  # GRADIENT_POS
        # / TEMPLATE VARS

        # Create video name with uuid
        video_name = str(uuid.uuid4())

        # Extract image_urls
        image_urls = immo_data["images"]

        # Extract logo url
        logo_url = immo_data["logo_url"]

        # Download images and save path
        images_path = self.download_images(
            property_id=property_id,
            image_urls=image_urls,
            logo_url=logo_url,
            max_image_count=further_settings["max_image_count"],
            random_image_order=further_settings["random_image_order"]
        )

        # List and organize image files
        files = [f for f in os.listdir(images_path) if os.path.isfile(os.path.join(images_path, f))]
        files = [f'{images_path}/{file}' for file in files]


        slide_show_video = slide_show(
            files,
            slide_transition_duration_in_seconds,
            static_slide_duration,
            slide_show_size,
            zoom_scale,
            zoom_in_acceleration,
            zoom_out_acceleration,
            self.fps,
            transition_type,
            transition_duration
        )

        if transition_type == 1:
            video_duration = slide_show_video[0].duration
        else:
            video_duration = (len(files) * slide_transition_duration_in_seconds) + transition_duration

        data = immo_data

        # Create formated ai video text
        video_text = self.generate_video_text(immo_data["description_text"])

        # Add created text to data
        data["title"] = video_text.replace("-", "-\u200b")

        fonts = {
            'title': title_font_path,
            'price': price_font_path,
            'area': area_font_path,
            'location': location_font_path
        }

        colors = {
            'background': self.convert_to_rgba(color_data["color_1"]),  # Background box
            'location': self.convert_to_rgba(color_data["color_2"]),  # Text 1: location
            'price_background': self.convert_to_rgba(color_data["color_3"]),  # Price background
            'price': self.convert_to_rgba(color_data["color_4"]),  # Text 2: price
            'area': self.convert_to_rgba(color_data["color_5"]),  # Text 3: area
            'title': self.convert_to_rgba(color_data["color_6"]),  # video text
        }

        # Get dynamic font size: price
        dynamic_size_price = self.get_dynamic_font_size(
            text=f'{data["price-text"]} {immo_data["price"]}',
            font_path=price_font_path,
            max_width_ratio=0.6,
            static_font_size=price_font_size
        )

        # Get dynamic font size: area
        dynamic_size_area = self.get_dynamic_font_size(
            text=f'{data["rentorbuy"]} / {data["flatorhouse"]} / {data["squarefeets"]}',
            font_path=area_font_path,
            max_width_ratio=0.63,
            static_font_size=area_font_size
        )

        # Get dynamic font size: location
        dynamic_size_location = self.get_dynamic_font_size(
            text=data["location"],
            font_path=location_font_path,
            max_width_ratio=0.8,
            static_font_size=location_font_size
        )

        sizes = {
            'image': template_size,
            'price': dynamic_size_price,
            'area': dynamic_size_area,
            'title': title_font_size,
            'location': dynamic_size_location,
            'title_limit': title_character_limit
        }

        audio = select_music('data/songs', video_duration)

        if audio:

            gradient = create_gradient_v2(self.video_size[0], gradient_height, colors["background"])
            gradient = ImageClip(np.array(gradient)).with_position(gradient_pos).with_duration(video_duration)

            # Add logo if available
            if logo_url:
                logo_image_type = logo_url.split(".")[-1]
                logo_path = f'{images_path}/logo/logo.{logo_image_type}'
            else:
                logo_path = 'data/transparent.png'

            logo_image = ImageClip(logo_path).with_duration(
                video_duration).resized(width=logo_width)
            logo_image = logo_image.with_position(logo_position)

            image_template, height_limit = template_v2(data, colors, sizes, fonts)

            image_clip = ImageClip(np.array(image_template)).with_position(
                (0, slide_show_size[1] - height_limit)).with_duration(video_duration)

            final_video = CompositeVideoClip(
                slide_show_video + [gradient, image_clip, logo_image],
                size=self.video_size
            )

            final_video = final_video.with_audio(audio)

            final_video.write_videofile(
                f'data/videos/{video_name}.mp4',
                audio_codec=self.audio_codec
            )

            if isinstance(audio, AudioFileClip):
                audio.close()
                return video_name

        return None

    def render_template_v2_test(self, property_id, immo_data, color_data, further_settings):

        # TEMPLATE VARS
        slide_transition_duration_in_seconds = 2.5  # SLIDE_TRANSITION_DURATION_IN_SECONDS
        static_slide_duration = 0.1  # STATIC_SLIDE_DURATION
        slide_show_size = (self.video_size[0], 1290)  # SLIDE_SHOW_SIZE
        zoom_scale = 1.5  # ZOOM_SCALE
        zoom_in_acceleration = 2  # ZOOM_IN_ACCELERATION
        zoom_out_acceleration = 0.35  # ZOOM_OUT_ACCELERATION
        logo_width = 200  # LOGO_WIDTH
        logo_position = ((self.video_size[0] / 2) - (logo_width / 2), 480 )  # LOGO_POSITION
        transition_type = further_settings["transition_type"]
        transition_duration = 0.5  # TRANSITION_DURATION

        title_font_path = 'data/fonts/Inter.ttf'  # TITLE_FONT_PATH
        price_font_path = 'data/fonts/InterBold.ttf'  # PRICE_FONT_PATH
        area_font_path = 'data/fonts/InterBold.ttf'  # AREA_FONT_PATH
        location_font_path = 'data/fonts/InterBold.ttf'  # LOCATION_FONT_PATH

        template_size = (self.video_size[0], 800)
        price_font_size = 55
        area_font_size = 45
        title_font_size = 40
        location_font_size = 45
        title_character_limit = 250

        gradient_height = 630
        gradient_pos = (0, slide_show_size[1]-gradient_height)  # GRADIENT_POS
        # / TEMPLATE VARS

        # Create video name with uuid
        video_name = str(uuid.uuid4())

        # Extract image_urls
        image_urls = immo_data["images"]

        # Extract logo url
        logo_url = immo_data["logo_url"]

        # Download images and save path
        # Download images and save path
        # images_path = self.download_images(
        #     property_id=property_id,
        #     image_urls=image_urls,
        #     logo_url=logo_url,
        #     max_image_count=further_settings["max_image_count"],
        #     random_image_order=further_settings["random_image_order"]
        # )

        # List and organize image files
        # files = [f for f in os.listdir(images_path) if os.path.isfile(os.path.join(images_path, f))]
        # files = [f'{images_path}/{file}' for file in files]
        files = os.listdir('data/images')
        files = [f'data/images/{file}' for file in files]

        slide_show_video = slide_show(
            files,
            slide_transition_duration_in_seconds,
            static_slide_duration,
            slide_show_size,
            zoom_scale,
            zoom_in_acceleration,
            zoom_out_acceleration,
            self.fps,
            transition_type,
            transition_duration
        )

        if transition_type == 1:
            video_duration = slide_show_video[0].duration
        else:
            video_duration = (len(files) * slide_transition_duration_in_seconds) + transition_duration

        data = immo_data

        # Create formated ai video text
        video_text = self.generate_video_text(immo_data["description_text"])

        # Add created text to data
        data["title"] = video_text.replace("-", "-\u200b")

        fonts = {
            'title': title_font_path,
            'price': price_font_path,
            'area': area_font_path,
            'location': location_font_path
        }

        colors = {
            'background': self.convert_to_rgba(color_data["color_1"]),
            'title': self.convert_to_rgba(color_data["color_6"]),
            'price_background': self.convert_to_rgba(color_data["color_3"]),
            'price': self.convert_to_rgba(color_data["color_4"]),
            'location': self.convert_to_rgba(color_data["color_2"]),
            'area': self.convert_to_rgba(color_data["color_5"]),
        }

        # Get dynamic font size: price
        dynamic_size_price = self.get_dynamic_font_size(
            text=f'{data["price-text"]} {immo_data["price"]}',
            font_path=price_font_path,
            max_width_ratio=0.6,
            static_font_size=price_font_size
        )

        # Get dynamic font size: area
        dynamic_size_area = self.get_dynamic_font_size(
            text=f'{data["rentorbuy"]} / {data["flatorhouse"]} / {data["squarefeets"]}',
            font_path=area_font_path,
            max_width_ratio=0.63,
            static_font_size=area_font_size
        )

        # Get dynamic font size: location
        dynamic_size_location = self.get_dynamic_font_size(
            text=data["location"],
            font_path=location_font_path,
            max_width_ratio=0.8,
            static_font_size=location_font_size
        )

        sizes = {
            'image': template_size,
            'price': dynamic_size_price,
            'area': dynamic_size_area,
            'title': title_font_size,
            'location': dynamic_size_location,
            'title_limit': title_character_limit
        }

        audio = select_music('data/songs', video_duration)

        if audio:

            gradient = create_gradient_v2(self.video_size[0], gradient_height, colors["price_background"])
            gradient = ImageClip(np.array(gradient)).with_position(gradient_pos).with_duration(video_duration)

            logo_path = 'data/transparent.png'

            logo_image = ImageClip(logo_path).with_duration(
                video_duration).resized(width=logo_width)
            logo_image = logo_image.with_position(logo_position)

            image_template, height_limit = template_v2(data, colors, sizes, fonts)

            image_clip = ImageClip(np.array(image_template)).with_position(
                (0, slide_show_size[1] - height_limit)).with_duration(video_duration)

            final_video = CompositeVideoClip(
                slide_show_video + [gradient, image_clip, logo_image],
                size=self.video_size
            )

            final_video = final_video.with_audio(audio)

            final_video.write_videofile(
                f'data/videos/{video_name}.mp4',
                audio_codec=self.audio_codec
            )

            if isinstance(audio, AudioFileClip):
                audio.close()
                return video_name

        return None

    def render_template_v3(self, property_id, immo_data, color_data, further_settings):

        # TEMPLATE VARS
        slide_transition_duration_in_seconds = 2.5  # SLIDE_TRANSITION_DURATION_IN_SECONDS
        static_slide_duration = 0.1  # STATIC_SLIDE_DURATION
        slide_show_size = self.video_size  # SLIDE_SHOW_SIZE
        zoom_scale = 1.5  # ZOOM_SCALE
        zoom_in_acceleration = 2  # ZOOM_IN_ACCELERATION
        zoom_out_acceleration = 0.35  # ZOOM_OUT_ACCELERATION
        logo_width = 200  # LOGO_WIDTH
        logo_position = ((self.video_size[0] / 2) - (logo_width / 2), 200)  # LOGO_POSITION
        transition_type = further_settings["transition_type"]
        transition_duration = 0.5  # TRANSITION_DURATION

        title_font_path = 'data/fonts/Inter.ttf'  # TITLE_FONT_PATH
        price_font_path = 'data/fonts/InterBold.ttf'  # PRICE_FONT_PATH
        area_font_path = 'data/fonts/InterBold.ttf'  # AREA_FONT_PATH
        location_font_path = 'data/fonts/InterBold.ttf'  # LOCATION_FONT_PATH

        template_size = (735, 450)
        price_font_size = 50
        area_font_size = 40
        title_font_size = 38
        location_font_size = 40
        title_character_limit = 100
        area_character_limit = 32
        # / TEMPLATE VARS

        # Create video name with uuid
        video_name = str(uuid.uuid4())

        # Extract image_urls
        image_urls = immo_data["images"]

        # Extract logo url
        logo_url = immo_data["logo_url"]

        # Download images and save path
        images_path = self.download_images(
            property_id=property_id,
            image_urls=image_urls,
            logo_url=logo_url,
            max_image_count=further_settings["max_image_count"],
            random_image_order=further_settings["random_image_order"]
        )

        # List and organize image files
        files = [f for f in os.listdir(images_path) if os.path.isfile(os.path.join(images_path, f))]
        files = [f'{images_path}/{file}' for file in files]

        slide_show_video = slide_show(
            files,
            slide_transition_duration_in_seconds,
            static_slide_duration,
            slide_show_size,
            zoom_scale,
            zoom_in_acceleration,
            zoom_out_acceleration,
            self.fps,
            transition_type,
            transition_duration
        )

        if transition_type == 1:
            video_duration = slide_show_video[0].duration
        else:
            video_duration = (len(files) * slide_transition_duration_in_seconds) + transition_duration

        data = immo_data

        # Create formated ai video text
        video_text = self.generate_video_text(immo_data["description_text"])

        # Add created text to data
        data["title"] = video_text.replace("-", "-\u200b")

        fonts = {
            'title': title_font_path,
            'price': price_font_path,
            'area': area_font_path,
            'location': location_font_path
        }

        colors = {
            'background': self.convert_to_rgba(color_data["color_1"]),  # Background box
            'location': self.convert_to_rgba(color_data["color_2"]), # Text 1: Location
            'price': self.convert_to_rgba(color_data["color_3"]),  # Text 2: Price
            'area': self.convert_to_rgba(color_data["color_4"]),  # Text 3: Area
            'title': self.convert_to_rgba(color_data["color_5"]),  # Video Text
        }

        # Get dynamic font size: price
        dynamic_size_price = self.get_dynamic_font_size(
            text=f'{data["price-text"]} {immo_data["price"]}',
            font_path=price_font_path,
            max_width_ratio=0.53,
            static_font_size=price_font_size
        )

        # Get dynamic font size: area
        dynamic_size_area = self.get_dynamic_font_size(
            text=f'{data["rentorbuy"]} / {data["flatorhouse"]} / {data["squarefeets"]}',
            font_path=area_font_path,
            max_width_ratio=0.53,
            static_font_size=area_font_size
        )

        # Get dynamic font size: location
        dynamic_size_location = self.get_dynamic_font_size(
            text=data["location"],
            font_path=location_font_path,
            max_width_ratio=0.55,
            static_font_size=location_font_size
        )

        sizes = {
            'image': template_size,
            'price': dynamic_size_price,
            'area': dynamic_size_area,
            'title': title_font_size,
            'location': dynamic_size_location,
            'title_limit': title_character_limit,
            'area_limit': area_character_limit
        }

        audio = select_music('data/songs', video_duration)

        if audio:

            # Add logo if available
            if logo_url:
                logo_image_type = logo_url.split(".")[-1]
                logo_path = f'{images_path}/logo/logo.{logo_image_type}'
            else:
                logo_path = 'data/transparent.png'

            logo_image = ImageClip(logo_path).with_duration(video_duration).resized(width=logo_width)

            logo_image = logo_image.with_position(logo_position)

            image_template = template_v3(data, colors, sizes, fonts)

            image_clip = ImageClip(np.array(image_template)).with_position((0, 1044)).with_duration(video_duration)

            final_video = CompositeVideoClip(
                slide_show_video + [image_clip, logo_image],
                size=self.video_size
            )

            final_video = final_video.with_audio(audio)

            final_video.write_videofile(
                f'data/videos/{video_name}.mp4',
                audio_codec=self.audio_codec
            )

            if isinstance(audio, AudioFileClip):
                audio.close()
                return video_name

        return None

    def render_template_v4(self, property_id, immo_data, color_data, further_settings):

        # TEMPLATE VARS
        slide_transition_duration_in_seconds = 2.5  # SLIDE_TRANSITION_DURATION_IN_SECONDS
        static_slide_duration = 0.1  # STATIC_SLIDE_DURATION
        slide_show_size_1 = (1080, 731)  # SLIDE_SHOW_1_SIZE
        slide_show_size_2 = (463, 796)  # SLIDE_SHOW_2_SIZE
        slide_show_size_3 = (619, 1024)  # SLIDE_SHOW_3_SIZE
        background_slide_show_size = self.video_size  # BACKGROUND_SLIDE_SHOW_SIZE
        slide_show_position_1 = (0, 0)  # SLIDE_SHOW_1_POSITION
        slide_show_position_2 = (616, 731)  # SLIDE_SHOW_2_POSITION
        slide_show_position_3 = (0, 924)  # SLIDE_SHOW_3_POSITION
        zoom_scale = 1.2  # ZOOM_SCALE
        zoom_in_acceleration = 1  # ZOOM_IN_ACCELERATION
        zoom_out_acceleration = 0.35  # ZOOM_OUT_ACCELERATION
        logo_width = 290  # LOGO_WIDTH
        logo_position = (700, 1619)  # LOGO_POSITION
        transition_type = further_settings["transition_type"]
        transition_duration = 0.8  # TRANSITION_DURATION

        price_font_path = 'data/fonts/InterBold.ttf'  # PRICE_FONT_PATH
        area_font_path = 'data/fonts/Inter.ttf'  # AREA_FONT_PATH
        location_font_path = 'data/fonts/InterBold.ttf'  # LOCATION_FONT_PATH

        # template_size = (616, 175)
        template_size = (616, 193)
        template_position = (0, 731)
        price_font_size = 47
        area_font_size = 35
        location_font_size = 30

        # / TEMPLATE VARS

        # Create video name with uuid
        video_name = str(uuid.uuid4())

        # Extract image_urls
        image_urls = immo_data["images"]

        # Extract logo url
        logo_url = immo_data["logo_url"]

        # Download images and save path
        images_path = self.download_images(
            property_id=property_id,
            image_urls=image_urls,
            logo_url=logo_url,
            max_image_count=further_settings["max_image_count"],
            random_image_order=further_settings["random_image_order"]
        )

        # List and organize image files
        files = [f for f in os.listdir(images_path) if os.path.isfile(os.path.join(images_path, f))]
        files = [f'{images_path}/{file}' for file in files]

        slide_show_1 = slide_show(
            files,
            slide_transition_duration_in_seconds,
            static_slide_duration,
            slide_show_size_1,
            zoom_scale,
            zoom_in_acceleration,
            zoom_out_acceleration,
            self.fps,
            transition_type,
            transition_duration
        )

        # Shift files list
        files = circular_shift(files, 1)

        slide_show_2 = slide_show(
            files,
            slide_transition_duration_in_seconds,
            static_slide_duration,
            slide_show_size_2,
            zoom_scale,
            zoom_in_acceleration,
            zoom_out_acceleration,
            self.fps,
            transition_type,
            transition_duration
        )

        # Shift files list
        files = circular_shift(files, 1)

        slide_show_3 = slide_show(
            files,
            slide_transition_duration_in_seconds,
            static_slide_duration,
            slide_show_size_3,
            zoom_scale,
            zoom_in_acceleration,
            zoom_out_acceleration,
            self.fps,
            transition_type,
            transition_duration
        )

        for index in range(len(slide_show_1)):
            slide_show_1[index] = slide_show_1[index].with_position(slide_show_position_1)
            slide_show_2[index] = slide_show_2[index].with_position(slide_show_position_2)
            slide_show_3[index] = slide_show_3[index].with_position(slide_show_position_3)

        if transition_type == 1:
            video_duration = slide_show_1[0].duration
        else:
            video_duration = (len(files) * slide_transition_duration_in_seconds) + transition_duration

        data = immo_data

        # Create formated ai video text
        video_text = self.generate_video_text(immo_data["description_text"])

        # Add created text to data
        data["title"] = video_text.replace("-", "-\u200b")

        fonts = {
            'price': price_font_path,
            'area': area_font_path,
            'location': location_font_path
        }

        colors = {
            'background': self.convert_to_rgba(color_data["color_1"]),  # Background box
            'price': self.convert_to_rgba(color_data["color_2"]),  # Text 1: Price
            'area': self.convert_to_rgba(color_data["color_3"]),  # Text 2: Area
            'location': self.convert_to_rgba(color_data["color_4"]),  # Text 3: location
        }

        # Get dynamic font size: price
        dynamic_size_price = self.get_dynamic_font_size(
            text=f'{data["price-text"]} {immo_data["price"]}',
            font_path=price_font_path,
            max_width_ratio=0.45,
            static_font_size=price_font_size
        )

        # Get dynamic font size: area
        dynamic_size_area = self.get_dynamic_font_size(
            text=f'{data["rentorbuy"]} / {data["flatorhouse"]} / {data["squarefeets"]}',
            font_path=area_font_path,
            max_width_ratio=0.45,
            static_font_size=area_font_size
        )

        # Get dynamic font size: location
        dynamic_size_location = self.get_dynamic_font_size(
            text=data["location"],
            font_path=location_font_path,
            max_width_ratio=0.45,
            static_font_size=location_font_size
        )

        sizes = {
            'image': template_size,
            'price': dynamic_size_price,
            'area': dynamic_size_area,
            'location': dynamic_size_location,
        }

        audio = select_music('data/songs', video_duration)

        if audio:

            # Add logo if available
            if logo_url:
                logo_image_type = logo_url.split(".")[-1]
                logo_path = f'{images_path}/logo/logo.{logo_image_type}'
            else:
                logo_path = 'data/transparent.png'

            logo_image = ImageClip(logo_path).with_duration(video_duration).resized(width=logo_width)

            logo_image = logo_image.with_position(logo_position)

            image_template = template_v4(data, colors, sizes, fonts)

            image_clip = ImageClip(np.array(image_template)).with_position(template_position).with_duration(
                video_duration)

            final_video = CompositeVideoClip(
                [logo_image] + slide_show_1 + [image_clip] + slide_show_3 + slide_show_2,
                size=self.video_size,
                bg_color=(255, 255, 255)
            )

            final_video = final_video.with_audio(audio)

            final_video.write_videofile(
                f'data/videos/{video_name}.mp4',
                audio_codec=self.audio_codec
            )

            if isinstance(audio, AudioFileClip):
                audio.close()
                return video_name

        return None

    def render_template_v5(self, property_id, immo_data, color_data, further_settings):

        # TEMPLATE VARS
        slide_transition_duration_in_seconds = 2.5  # SLIDE_TRANSITION_DURATION_IN_SECONDS
        static_slide_duration = 0.1  # STATIC_SLIDE_DURATION
        main_slide_show_size = (926, 676)  # MAIN_SLIDE_SHOW_SIZE
        background_slide_show_size = self.video_size  # BACKGROUND_SLIDE_SHOW_SIZE
        main_slide_show_position = (76, 512)  # MAIN_SLIDE_SHOW_POSITION
        zoom_scale = 1.3  # ZOOM_SCALE
        zoom_in_acceleration = 2  # ZOOM_IN_ACCELERATION
        zoom_out_acceleration = 0.35  # ZOOM_OUT_ACCELERATION
        logo_width = 180  # LOGO_WIDTH
        logo_position = ((self.video_size[0] / 2) - (logo_width / 2), 214)  # LOGO_POSITION
        transition_type = further_settings["transition_type"]
        transition_duration = 0.8  # TRANSITION_DURATION

        price_font_path = 'data/fonts/InterBold.ttf'  # PRICE_FONT_PATH
        area_font_path = 'data/fonts/InterBold.ttf'  # AREA_FONT_PATH
        location_font_path = 'data/fonts/InterBold.ttf'  # LOCATION_FONT_PATH

        template_size = (926, 275)
        template_position = (main_slide_show_position[0], main_slide_show_size[1] + main_slide_show_position[1])
        price_font_size = 55
        area_font_size = 45
        location_font_size = 40

        gradient_position = (-638, -218)  # GRADIENT_POSITION
        gradient_size = (2356, 2356)  # GRADIENT_SIZE
        gradient_color = (255, 255, 255)  # GRADIENT_COLOR
        gradient_intensity = 0.43  # GRADIENT_INTENSITY
        # / TEMPLATE VARS

        # Create video name with uuid
        video_name = str(uuid.uuid4())

        # Extract image_urls
        image_urls = immo_data["images"]

        # Extract logo url
        logo_url = immo_data["logo_url"]

        # Download images and save path
        images_path = self.download_images(
            property_id=property_id,
            image_urls=image_urls,
            logo_url=logo_url,
            max_image_count=further_settings["max_image_count"],
            random_image_order=further_settings["random_image_order"]
        )

        # List and organize image files
        files = [f for f in os.listdir(images_path) if os.path.isfile(os.path.join(images_path, f))]
        files = [f'{images_path}/{file}' for file in files]

        main_slide_show = slide_show(
            files,
            slide_transition_duration_in_seconds,
            static_slide_duration,
            main_slide_show_size,
            zoom_scale,
            zoom_in_acceleration,
            zoom_out_acceleration,
            self.fps,
            transition_type,
            transition_duration
        )

        background_slide_show = slide_show(
            files,
            slide_transition_duration_in_seconds,
            static_slide_duration,
            background_slide_show_size,
            zoom_scale,
            zoom_in_acceleration,
            zoom_out_acceleration,
            self.fps,
            transition_type,
            transition_duration
        )

        if transition_type == 1:
            video_duration = main_slide_show[0].duration
        else:
            video_duration = (len(files) * slide_transition_duration_in_seconds) + transition_duration

        data = immo_data

        # Create formated ai video text
        video_text = self.generate_video_text(immo_data["description_text"])

        # Add created text to data
        data["title"] = video_text.replace("-", "-\u200b")

        fonts = {
            'price': price_font_path,
            'area': area_font_path,
            'location': location_font_path
        }

        colors = {
            'background': self.convert_to_rgba(color_data["color_1"]),  # Background box
            'price': self.convert_to_rgba(color_data["color_2"]),  # Text 1: Price
            'area': self.convert_to_rgba(color_data["color_3"]),  # Text 2: Area
            'location': self.convert_to_rgba(color_data["color_4"]),  # Text 3: location
        }

        # Get dynamic font size: price
        dynamic_size_price = self.get_dynamic_font_size(
            text=f'{data["price-text"]} {immo_data["price"]}',
            font_path=price_font_path,
            max_width_ratio=0.75,
            static_font_size=price_font_size
        )

        # Get dynamic font size: area
        dynamic_size_area = self.get_dynamic_font_size(
            text=f'{data["rentorbuy"]} / {data["flatorhouse"]} / {data["squarefeets"]}',
            font_path=area_font_path,
            max_width_ratio=0.75,
            static_font_size=area_font_size
        )

        # Get dynamic font size: location
        dynamic_size_location = self.get_dynamic_font_size(
            text=data["location"],
            font_path=location_font_path,
            max_width_ratio=0.75,
            static_font_size=location_font_size
        )

        sizes = {
            'image': template_size,
            'price': dynamic_size_price,
            'area': dynamic_size_area,
            'location': dynamic_size_location,
        }

        audio = select_music('data/songs', video_duration)

        if audio:

            # Add logo if available
            if logo_url:
                logo_image_type = logo_url.split(".")[-1]
                logo_path = f'{images_path}/logo/logo.{logo_image_type}'
            else:
                logo_path = 'data/transparent.png'

            logo_image = ImageClip(logo_path).with_duration(video_duration).resized(width=logo_width)

            logo_image = logo_image.with_position(logo_position)

            image_template = template_v5(data, colors, sizes, fonts)
            image_clip = ImageClip(np.array(image_template)).with_position(template_position).with_duration(
                video_duration)

            gradient_image = set_gradient(
                self.video_size,
                gradient_position,
                gradient_size,
                gradient_color,
                gradient_intensity
            )
            gradient_image_clip = ImageClip(np.array(gradient_image)).with_duration(video_duration)

            if transition_type == 1:
                main_slide_show[0] = main_slide_show[0].with_position(main_slide_show_position)
            else:
                for index_ in range(len(main_slide_show)):
                    main_slide_show[index_] = main_slide_show[index_].with_position(main_slide_show_position)

            final_video = CompositeVideoClip(
                background_slide_show + [gradient_image_clip, image_clip] + main_slide_show + [logo_image],
                size=self.video_size
            )

            final_video = final_video.with_audio(audio)

            final_video.write_videofile(
                f'data/videos/{video_name}.mp4',
                audio_codec=self.audio_codec
            )

            if isinstance(audio, AudioFileClip):
                audio.close()
                return video_name

        return None


if __name__ == '__main__':
    from openai import OpenAI

    def test_template(template_name: str, transition_type_test_number: int):

        def extract_immo_data(data):
            return {
                'description_text': data["description_text"],
                'price-text': data["price_text"],
                'price': data["price"],
                'location': data["location"],
                'rentorbuy': data["rentorbuy"],
                'flatorhouse': data["flatorhouse"],
                'squarefeets': data["squarefeets"],
                'images': data["images"],
                'logo_url': data["logo_url"]
            }

        def generate_video(generator, selected_template, prop_id, prop_data, colors, settings):

            video = None

            if selected_template == "template_1":
                video = generator.render_template_v1(prop_id, prop_data, colors, settings)
            elif selected_template == "template_2":
                video = generator.render_template_v2(prop_id, prop_data, colors, settings)
            elif selected_template == "template_3":
                video = generator.render_template_v3(prop_id, prop_data, colors, settings)
            elif selected_template == "template_4":
                video = generator.render_template_v4(prop_id, prop_data, colors, settings)
            elif selected_template == "template_5":
                video = generator.render_template_v5(prop_id, prop_data, colors, settings)

            return video

        # initialize Open AI Client
        client = OpenAI(api_key=OPEN_AI_KEY)

        # initialize Video Generator
        video_generator = VideoGenerator(client=client)

        # Delete image directories
        video_generator.delete_directories()

        # Get video data for new or updated properties
        video_data_list = [
            {
                "immohub_account_id": "d254bb92-19b0-4b9c-bba7-5095504f2657",
                "immohub_user_data": "Yigit Sert - yigit@email.com",
                "property_id": "2b1dc0f0-4c47-45bd-9cbf-1eb358bb04ad",
                "selected_template": template_name,
                "immo_data": {
                    "description_text": "Titel: Ferienwohnung mit Zweitwohnsitzeignung für den Winter &amp; Sommertourismus nähe Präbichl |2 Zimmer|TOP 14\nBeschreibung: NUR NOCH ZWEI 2-Zimmer-WOHNUNGEN VERFÜGBAR !!! Die Eigentumswohnung ist für eine Nutzung als Zeitwohnsitz oder auch als Ferienwohnung für den Winter & Sommertourismus perfekt geeignet, da sich das Projekt in der Nähe des Skigebiets Präbichl befindet, das außer Skifahren verschiedene sportliche Aktivitäten (wie z. B. Wandern, Paragliding, Tauchen uvw.) ganzjährig bietet.\n\n\nAm Fuß des Präbichl in den Eisenerzer Alpen ist die idylische steiermarkische Marktgemeinde Vordernberg gelegen.\n\nHier handelt es sich um 2-Zimmer-Eigentumswohnung mit ca. 53m² Wohnfläche.\nEin Geschoss darüber steht die zweite 2-Zimmerwohnung zum Verkauf mit einer Wohnfläche von 52,45 m²\n\n<b>Die Raumaufteilung:</b>\n– Wohnzimmer\n– Schlafzimmer\n– große Küche\n– Bad mit WC\n– Vorraum\n\n<b>Objektbeschreibung & Ausstattung:</b>\n– Ziegelmaßive Bauweise\n– Erstbezug\n– Schlüsselfertig\n– Parkett\n– Fliesen\n– Heizung: Pellets Zentralheizung\n– Ausreichend Kfz-Abstellplätze vorhanden\n\nEine detailierte Bau- und Ausstattungsbeschreibung erhalten Sie gerne auf Anfrage.\n\n<b>Infrastruktur und Umgebung:</b>\n– Präbichl, Eisenerzer Alpen & Der Wilde Berg Mautern in der Nähe\nEntfernungen:\n– 15 km bis nach Leoben- ca. 15 Minuten Autofahrt\n– 67 km bis nach Graz – ca. 45 Minuten Autofahrt\n– 170 km bis nach Wien – ca. 1,5 Stunden Autofahrt\n– 200 km bis nach Salzburg – ca. 1,5 Stunden Stunden Autofahrt\n– 350 km bis nach München – ca. 3,5 Stunden Autofahrt\n\nKaufpreis: <b>€ 128.000,-</b>\nPKW-Stellplatz Kaufpreis: € 4.900,- exkl. MwSt.\nBetriebskosten: ca. € 182,-  inkl. Heizung, Warmwasser, Internet und Steuer\n\nKaufnebenkosten:\n3,5% Grunderwerbsteuer\n1,1% Grundbucheintragungsgebühr\n1,5% Vertragserrichtungskosten + 20 % MwSt.\n\n\n<b>Finanzierung?</b>\nWir kümmern uns um die Finanzierung Ihres Apartments in den Alpen. Fragen Sie noch heute bei uns an und Sie bekommen Ihr unverbindliches individuelles Finanzierungsangebot.\n\nFür nähere Auskünfte stehen wir Ihnen unter +43 1 720 129 211 oder unter +43 664 524 95 15 gerne zur Verfügung.\n\nCatchYourHome Immobilien GmbH\n<i>Because home is not a place, it´s a feeling.</i>\nwww.catchyourhome.at\nMünichreiterstraße 29/6, A-1130 Wien\nTelefon: +43 1 720 129 211\nFax:      +43 1 720 129 211 DW 89\n\n---------------------------------------------------------------------------------------------------------------------------------------------------------\n\n\nONLY TWO 2-ROOM APARTMENTS LEFT !!! The condominium is perfectly suited for use as a temporary home or as a holiday home for winter and summer tourism, as the project is located near the Präbichl ski area, which, in addition to skiing, offers various sporting activities (such as hiking, paragliding, diving, etc .) offers all year round.\n\n\nThe idyllic Styrian market town of Vordernberg is located at the foot of the Präbichl in the Eisenerz Alps.\n\n\n\nThis is a 2-room condominium with approx. 53m² of living space.\nThere is another Flat with 2 rooms available, one stage above with 52,45m²\n\n<b>The room layout:</b>\n- Living room\n- Bedroom\n- big kitchen\n– bathroom with toilet\n– anteroom\n\n<b>Property description & equipment:</b>\n– Solid brick construction\n– first time occupancy\n– Turnkey\n– parquet\n– tiles\n– Heating: pellets central heating\n- Sufficient car parking spaces available\n\nA detailed description of the construction and equipment is available on request.\n\n<b>Infrastructure and environment:</b>\n– Präbichl, Eisenerz Alps & The Wild Mountain Mautern nearby\n\nDistances:\n– 15 km till Leoben- ca. 15 min. of drive\n– 67 km till Graz – ca. 45 min. of drive\n– 170 km till Vienna – ca. 1,5h of drive\n– 200 km till Salzburg – ca. 1,5 h of drive\n– 350 km till Munich – ca. 3,5h of drive\n\nPurchase price: <b>€ 128.000.-</b>\nParking space purchase price: € 5,400.00\nOperating costs: approx. € 1.85 / m² (incl. VAT € 2.10 / m²)\n\nAdditional purchase costs:\n3.5% real estate transfer tax\n1.1% land registration fee\n1.5% contract establishment costs + 20% VAT\n3 % Commission + 20% VAT\n\n<b>Financing?</b>\nWe take care of financing your apartment in the Alps. Ask us today and you will receive your non-binding individual financing offer.\n\nWe are at your disposal for more information on +43 1 720 129 211.\n\nCatchYourHome Immobilien GmbH\n<i>Because home is not a place, it´s a feeling.</i>\nwww.catchyourhome.at\nMünichreiterstraße 29/6, A-1130 Wien\nTelefon: +43 1 720 129 211\nFax:      +43 1 720 129 211 DW 89<table><tr><td colspan=\"4\">Angaben gemäß gesetzlichem Erfordernis:\n</td></tr><tr><td>Heizwärmebedarf:</td><td>132.0 kWh/(m&sup2;a)</td><td></td><td></td></tr><tr><td>Klasse Heizwärmebedarf:</td><td>D</td><td></td><td></td></tr><tr><td>Faktor Gesamtenergieeffizienz:</td><td>1.8</td><td></td><td></td></tr><tr><td>Klasse Faktor Gesamtenergieeffizienz:</td><td>C</td><td></td><td></td></tr></table>",
                    "price_text": "KAUFPREIS",
                    "price": "123.456.789,00 €",
                    "location": "Mühlbach am Manhartsberg, Niederösterreich, Österreich",
                    "rentorbuy": "Kauf",
                    "flatorhouse": "Wohnung",
                    "squarefeets": "123.456.789 m²",
                    "images": [
                        "https://media.edireal.com/media/image/-30000723/orig/1003057237_0.jpg",
                        "https://media.edireal.com/media/image/-30000723/orig/1003057237_1.jpg",
                        "https://media.edireal.com/media/image/-30000723/orig/1003057237_2.jpg",
                        "https://media.edireal.com/media/image/-30000723/orig/1003057237_3.jpg",
                        "https://media.edireal.com/media/image/-30000723/orig/1003057237_4.jpg",
                        "https://media.edireal.com/media/image/-30000723/orig/1003057237_5.jpg",
                        "https://media.edireal.com/media/image/-30000723/orig/1003057237_6.jpg",
                        "https://media.edireal.com/media/image/-30000723/orig/1003057237_7.jpg",
                        "https://media.edireal.com/media/image/-30000723/orig/1003057237_8.jpg",
                        "https://media.edireal.com/media/image/-30000723/orig/1003057237_9.jpg",
                        "https://media.edireal.com/media/image/-30000723/orig/1003057237_10.jpg",
                        "https://media.edireal.com/media/image/-30000723/orig/1003057237_11.jpg",
                        "https://media.edireal.com/media/image/-30000723/orig/1003057237_12.jpg",
                        "https://media.edireal.com/media/image/-30000723/orig/1003057237_13.jpg",
                        "https://media.edireal.com/media/image/-30000723/orig/1003057237_14.jpg",
                        "https://media.edireal.com/media/image/-30000723/orig/1003057237_15.jpg",
                        "https://media.edireal.com/media/image/-30000723/orig/1003057237_16.jpg",
                        "https://media.edireal.com/media/image/-30000723/orig/1003057237_17.jpg"
                    ],
                    #"logo_url": "media/immohub/logo/63625d853d2ecc2c15d5e253_Logo_neu.png"
                    "logo_url": None
                },
                "color_data": {
                    "color_1": "#ff6767",
                    "color_2": "#000000",
                    "color_3": "#c72626",
                    "color_4": "#ffffff",
                    "color_5": "#000000",
                    "color_6": "#000000"
                },
                "further_settings": {
                    "max_image_count": 2,
                    "random_image_order": True,
                    "number_of_videos": 1,
                    "transition_type": transition_type_test_number
                }
            }
        ]

        print("\n#####################################################################################")
        print("STARTING VIDEO GENERATION")
        print("#####################################################################################\n")

        # Loop though each property to extract necessary data
        for i, video_data in enumerate(video_data_list):

            print(f" - Generating video {i + 1} of {len(video_data_list)} entries in video_data_list...\n")

            # Extract account id in immohub server
            immohub_account_id = video_data["immohub_account_id"]

            # Extract property id
            property_id = video_data["property_id"]

            # Extract immo data
            immo_data = extract_immo_data(video_data["immo_data"])

            # Extract color_data
            color_data = video_data["color_data"]

            # Extra further settings
            further_settings = video_data["further_settings"]

            # Loop through missing video count
            for counter in range(further_settings["number_of_videos"]):

                # Generate video
                try:
                    video_name = generate_video(
                        generator=video_generator,
                        selected_template=video_data["selected_template"],
                        prop_id=property_id,
                        prop_data=immo_data,
                        colors=color_data,
                        settings=further_settings
                    )
                except Exception as e:
                    print(f"Error Generating video in {__file__}: {e}")
                    traceback.print_exc()
                else:
                    if video_name is not None:
                        print("Video Creation Successful")

                print("\n-------------------------------------------------------------------------------\n")

        # Delete image directories
        video_generator.delete_directories()


    templates_to_test = [
        #1,
        2,
        #3,
        #4,
        #5
    ]
    for template_counter in templates_to_test:
        for i in range(2, 3):
            test_template(f"template_{template_counter}",i+1)