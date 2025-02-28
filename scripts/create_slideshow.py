from scripts.zoom import (
    apply_zoom_in,
    apply_zoom_out,
)
from scripts.cropper import crop_all_images
from moviepy import concatenate_videoclips, vfx, CompositeVideoClip, ImageClip

def slide_show(
    files,
    slide_transition_duration_in_seconds,
    static_slide_duraton,
    image_size,
    zoom_scale,
    zoom_in_acceleration,
    zoom_out_acceleration,
    fps,
    transition_variation,
    transition_duration=0.5,
):


    processed_images = crop_all_images(files, image_size)

    animated_images = []
    for index, image in enumerate(processed_images):

        if transition_variation == 1:
            in_image = apply_zoom_out(
                image, slide_transition_duration_in_seconds, zoom_scale, zoom_out_acceleration, [0.5, 0.5]
            )
            out_image = apply_zoom_in(
                image, slide_transition_duration_in_seconds, zoom_scale, zoom_in_acceleration, [0.5, 0.5]
            )

            animated_images.append(in_image.with_duration(slide_transition_duration_in_seconds).with_fps(fps))
            animated_images.append(image.with_duration(static_slide_duraton).with_fps(fps))
            animated_images.append(out_image.with_duration(slide_transition_duration_in_seconds).with_fps(fps))

        elif transition_variation == 2:

            image_duration = slide_transition_duration_in_seconds + transition_duration 
            image = image.with_duration(image_duration).with_fps(fps)

            image = apply_zoom_in(
                image, slide_transition_duration_in_seconds, 1.2, 1, [0.5, 0.5]
            )
            if index == 0:
                start = index
            else:
                start = (index * image_duration) - (transition_duration * index)
                image = image.with_effects([vfx.FadeIn(transition_duration, [255, 255, 255])])
            
                
            animated_images.append(image.with_start(start))

        elif transition_variation == 3:
            image_duration = slide_transition_duration_in_seconds + transition_duration 

            image = image.with_duration(image_duration).with_fps(fps)
            image = apply_zoom_in(
                image, slide_transition_duration_in_seconds, 1.2, 1, [0.5, 0.5]
            )
            if index == 0:
                start = index
            else:
                start = (index * image_duration) - (transition_duration * index)
                image = image.with_effects([vfx.CrossFadeIn(transition_duration)])

            animated_images.append(image.with_start(start))

        elif transition_variation == 4:
            image_duration = slide_transition_duration_in_seconds
            start = index * image_duration
            image = image.with_duration(image_duration).with_fps(fps)
            image = apply_zoom_in(
                image, image_duration, 1.2, 1, [0.5, 0.5]
            )
            image_transition_clip = ImageClip(image.get_frame(image_duration)).with_duration(transition_duration) 
            image_transition_clip = apply_zoom_in(
                image_transition_clip, transition_duration, 1.2, 1, [0.5, 0.5]
            )
            final_image_clip = concatenate_videoclips([image, image_transition_clip]).with_start(start)
            if index != 0:
                final_image_clip = final_image_clip.with_effects([vfx.CrossFadeIn(transition_duration)])
            animated_images.append(final_image_clip)


    if transition_variation == 1:
        final_video = [concatenate_videoclips(animated_images)]
    else:
        final_video = animated_images

    return final_video


if __name__ == '__main__':
    slide_show()

