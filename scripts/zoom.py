from moviepy import ImageClip, VideoClip
import math, numpy
from PIL import Image


def zoom_in_effect(clip: ImageClip, start_scale, zoom_ratio, acceleration, zoom_pos, zoom_out=False):
    def effect(get_frame, t):
        img = Image.fromarray(get_frame(t))
        base_size = img.size

        if zoom_out:
            scale = (start_scale - zoom_ratio * (t ** acceleration))
        else:
            scale = (start_scale + zoom_ratio * (t ** acceleration))

        new_size = [
            math.ceil(img.size[0] * scale),
            math.ceil(img.size[1] * scale)
        ]
        new_size[0] += new_size[0] % 2  
        new_size[1] += new_size[1] % 2  

        img = img.resize(new_size, Image.LANCZOS)

        focus_x_original = zoom_pos[0] * base_size[0]
        focus_y_original = zoom_pos[1] * base_size[1]
        focus_x_new = zoom_pos[0] * new_size[0]
        focus_y_new = zoom_pos[1] * new_size[1]

        left = int(focus_x_new - focus_x_original)
        top = int(focus_y_new - focus_y_original)

        left = max(0, min(left, new_size[0] - base_size[0]))
        top = max(0, min(top, new_size[1] - base_size[1]))

        right = left + base_size[0]
        bottom = top + base_size[1]

        img = img.crop((left, top, right, bottom)).resize(base_size, Image.LANCZOS)

        result = numpy.array(img)
        img.close()

        return result
    return clip.transform(effect)


def apply_zoom_in(clip, duration, final_scale, acceleration, zoom_pos):
    zoom_ratio = (final_scale - 1) / (duration ** acceleration)
    return zoom_in_effect(clip, 1, zoom_ratio, acceleration, zoom_pos)


def apply_zoom_out(clip, duration, start_scale, acceleration, zoom_pos):
    zoom_ratio = (start_scale - 1) / (duration ** acceleration) 
    return zoom_in_effect(clip, start_scale, zoom_ratio, acceleration, zoom_pos, zoom_out=True)

