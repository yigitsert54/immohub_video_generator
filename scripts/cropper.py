from moviepy import ImageClip
import os

def crop_and_resize_image(image_clip: ImageClip, size):
    original_width, original_height = image_clip.size
    original_ratio = original_width / original_height
    target_width, target_height = size
    target_ratio = target_width / target_height

    if original_ratio == target_ratio:
        return image_clip.resized(size)
    else:
        if original_ratio > target_ratio:
            new_width = round(original_height * target_ratio)
            x1 = (original_width - new_width) // 2
            x2 = x1 + new_width
            y1, y2 = 0, original_height
        else:
            new_height = round(original_width / target_ratio)
            y1 = (original_height - new_height) // 2
            y2 = y1 + new_height
            x1, x2 = 0, original_width

        cropped_image = image_clip.cropped(x1=x1, y1=y1, x2=x2, y2=y2)

        return cropped_image.resized([target_width, target_height])


def crop_all_images(files, images_size):
    try:
        cropped_images = []

        for file in files:
            if file.lower().endswith((".png", ".jpg", ".jpeg")):

                try:
                    image_clip = ImageClip(file)
                    processed_image = crop_and_resize_image(image_clip, images_size)
                    cropped_images.append(processed_image)
                except Exception as e:
                    print(f"Error{file}: {e}")

        return cropped_images

    except Exception as e:
        print(f"Error: {e}")
        return []
