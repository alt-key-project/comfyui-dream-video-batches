# -*- coding: utf-8 -*-
from typing import List

from PIL.Image import Resampling

from .categories import *
from .core import *


class DVB_Zoom:
    NODE_NAME = "Linear Camera Zoom"
    ICON = "🔭"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "frames": (FrameSet.TYPE_NAME,),
                "output_width": ("INT", {"default": 512, "min": 1}),
                "output_height": ("INT", {"default": 512, "min": 1}),
                "direction": (["in", "out"],)
            },
        }

    CATEGORY = NodeCategories.CAMERA
    RETURN_TYPES = (FrameSet.TYPE_NAME,)
    RETURN_NAMES = ("frames",)
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def result(self, frames: FrameSet, output_width: int, output_height: int, direction):
        assert isinstance(frames, FrameSet)
        gc_comfyui()
        proc = DVB_ImageBatchProcessor(frames.tensor)
        output_width = min(frames.image_dimensions[0], output_width)
        output_height = min(frames.image_dimensions[1], output_height)

        def do_zoom(n: int, total: int, image: DVB_Image):
            factor = n / (total - 1.0)
            if direction == "in":
                factor = 1.0 - factor
            w = (image.width - output_width) * factor + output_width
            h = (image.height - output_height) * factor + output_height
            c = image.quad.center
            return image.crop(c.x - w * 0.5, c.y - h * 0.5, c.x + w * 0.5, c.y + h * 0.5).resize(output_width,
                                                                                                 output_height,
                                                                                                 Resampling.BICUBIC)

        return (FrameSet(proc.process(do_zoom), frames.framerate, frames.indices),)


class DVB_LinearCameraPan:
    NODE_NAME = "Linear Camera Pan"
    ICON = "👉"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "frames": (FrameSet.TYPE_NAME,),
                "output_width": ("INT", {"default": 512, "min": 1}),
                "output_height": ("INT", {"default": 512, "min": 1}),
                "direction_x": ("FLOAT", {"default": 1.0}),
                "direction_y": ("FLOAT", {"default": -1.0}),
                "pan_mode": (["edge to edge", "center to edge", "edge to center"],)
            },
        }

    CATEGORY = NodeCategories.CAMERA
    RETURN_TYPES = (FrameSet.TYPE_NAME,)
    RETURN_NAMES = ("frames",)
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def result(self, frames: FrameSet, output_width: int, output_height: int, direction_x: float,
               direction_y: float, pan_mode: str):
        assert isinstance(frames, FrameSet)
        gc_comfyui()

        input_width, input_height = frames.image_dimensions
        if input_height < output_height or input_width < output_width:
            print("WARNING: Cannot pan - output larger than input!")
            return (frames,)
        if direction_x == 0.0 and direction_y == 0.0:
            print("WARNING: Cannot pan - no direction!")
            return (frames,)

        move_dir = Vector2d(direction_x, direction_y).normalized()
        space = Quad2d(output_width * 0.5, output_height * 0.5, input_width - output_width * 0.5,
                       input_height - output_height * 0.5)
        a, b = space.calculate_intersections(space.center, move_dir)


        move_vector = b.sub(a).align(move_dir)

        if pan_mode == "center to edge":
            start_move = space.center
            move_vector = move_vector.multiply(0.5)
        elif pan_mode == "edge to center":
            move_vector = move_vector.multiply(0.5)
            start_move = space.center.sub(move_vector)
        else:
            start_move = space.center.sub(move_vector.multiply(0.5))

        start_quad = Quad2d(start_move.x - output_width * 0.5, start_move.y - output_height * 0.5,
                            start_move.x + output_width * 0.5, start_move.y + output_height * 0.5)

        move_delta_vector = move_vector.multiply(1.0 / frames.indexed_length)

        proc = DVB_ImageBatchProcessor(frames.tensor, indices=frames.indices, first = frames.first_index)

        def do_pan(n: int, total: int, image: DVB_Image, indices : List[int], first: int):
            subimage_quad = start_quad.add(move_delta_vector.multiply(indices[n]-first))
            return image.crop(round(subimage_quad.mincorner.x), round(subimage_quad.mincorner.y),
                              round(subimage_quad.mincorner.x) + output_width,
                              round(subimage_quad.mincorner.y) + output_height)

        return (FrameSet(proc.process(do_pan), frames.framerate, frames.indices),)

