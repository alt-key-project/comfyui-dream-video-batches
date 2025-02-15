# -*- coding: utf-8 -*-

import math

from PIL.Image import Resampling

from .categories import *
from .core import *



class BatchCameraMotion:
    def __init__(self, frames: FrameSet, output_width, output_height, motion_function, frame_function):
        assert isinstance(frames, FrameSet)
        self._proc = DVB_ImageBatchProcessor(frames.tensor)
        self._frames = frames
        self._output_width = output_width
        self._output_height = output_height
        self._motion_function = motion_function
        self._frame_function = frame_function
        self._indices = frames.indices
        self._first_index = frames.first_index
        self._last_index = frames.last_index
        self._frame_dims = frames.image_dimensions

    def execute(self):
        gc_comfyui()

        def do_recalc(n: int, total: int, image: DVB_Image):
            index = self._indices[n]
            if self._last_index == self._first_index:
                factor = 0.5
            else:
                factor = float(index - self._first_index) / (self._last_index - self._first_index)
            factor = max(0.0, min(1.0, self._motion_function(factor)))
            return self._frame_function(image, factor, self._output_width, self._output_height)

        return (FrameSet(self._proc.process(do_recalc), self._frames.framerate, self._frames.indices),)


def zoom_frame(image: DVB_Image, f, o_width, o_height):
    w = (image.width - o_width) * f + o_width
    h = (image.height - o_height) * f + o_height
    c = image.quad.center
    return image.crop(c.x - w * 0.5, c.y - h * 0.5, c.x + w * 0.5, c.y + h * 0.5).resize(o_width,
                                                                                         o_height,
                                                                                         Resampling.BILINEAR)


def make_pan_function(direction_x: float, direction_y: float):
    move_dir = Vector2d(direction_x, direction_y).normalized()

    def _pan_func(image: DVB_Image, f, o_width, o_height):
        input_width = image.width
        input_height = image.height
        if input_height < o_height or input_width < o_width:
            print("WARNING: Cannot pan - output larger than input!")
            return (image,)
        if direction_x == 0.0 and direction_y == 0.0:
            print("WARNING: Cannot pan - no direction!")
            return (image,)
        space = Quad2d(o_width * 0.5, o_height * 0.5, input_width - o_width * 0.5,
                       input_height - o_height * 0.5)
        a, b = space.calculate_intersections(space.center, move_dir)
        move_vector = b.sub(a).align(move_dir)

        start_move = space.center.sub(move_vector.multiply(0.5))

        start_quad = Quad2d(start_move.x - o_width * 0.5, start_move.y - o_height * 0.5,
                            start_move.x + o_width * 0.5, start_move.y + o_height * 0.5)
        subimage_quad = start_quad.add(move_vector.multiply(f))
        return image.crop(round(subimage_quad.mincorner.x), round(subimage_quad.mincorner.y),
                          round(subimage_quad.mincorner.x) + o_width,
                          round(subimage_quad.mincorner.y) + o_height)

    return _pan_func


def _recalc_motion_factor_to_loopable(f, total_frames):
    return f * (total_frames) / (total_frames + 1.0)

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

    def result(self, frames: FrameSet, output_width: int, output_height: int, direction):
        def motion(f):
            if direction == "in":
                return 1.0 - f
            else:
                return f

        return BatchCameraMotion(frames, output_width, output_height, motion, zoom_frame).execute()


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

    def result(self, frames: FrameSet, output_width: int, output_height: int, direction_x: float,
               direction_y: float, pan_mode: str):
        def motion(f):
            if pan_mode == "center to edge":
                return (f - 1.0) * 0.5
            elif pan_mode == "edge to center":
                return f * 0.5
            else:
                return f

        frame_func = make_pan_function(direction_x, direction_y)
        return BatchCameraMotion(frames, output_width, output_height, motion, frame_func).execute()


class DVB_LinearCameraRoll:
    NODE_NAME = "Linear Camera Roll"
    ICON = "↻"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "frames": (FrameSet.TYPE_NAME,),
                "output_width": ("INT", {"default": 512, "min": 1}),
                "output_height": ("INT", {"default": 512, "min": 1}),
                "degrees": ("FLOAT", {"default": 45.0})
            },
        }

    CATEGORY = NodeCategories.CAMERA
    RETURN_TYPES = (FrameSet.TYPE_NAME,)
    RETURN_NAMES = ("frames",)
    FUNCTION = "result"


    def result(self, frames: FrameSet, output_width: int, output_height: int, degrees: float):
        def motion(f):
            return f

        def frame_func(image: DVB_Image, f, o_width, o_height):
            w = image.width
            h = image.height
            c_x = round(w * 0.5)
            c_y = round(h * 0.5)
            a = c_x - o_width // 2
            b = c_y - o_height // 2
            return image.rotate(f * degrees).crop(a, b, a + o_width, b + o_height)

        return BatchCameraMotion(frames, output_width, output_height, motion, frame_func).execute()


class DVB_ZoomSine:
    NODE_NAME = "Sine Camera Zoom"
    ICON = "🔭"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "frames": (FrameSet.TYPE_NAME,),
                "output_width": ("INT", {"default": 512, "min": 1}),
                "output_height": ("INT", {"default": 512, "min": 1}),
                "period_seconds": ("FLOAT", {"default": 1.0, "min": 0.1, "step": 0.1}),
                "phase_seconds": ("FLOAT", {"default": 0.0})
            },
        }

    CATEGORY = NodeCategories.CAMERA
    RETURN_TYPES = (FrameSet.TYPE_NAME,)
    RETURN_NAMES = ("frames",)
    FUNCTION = "result"

    def result(self, frames: FrameSet, output_width: int, output_height: int, period_seconds, phase_seconds):
        def motion(f):
            f = _recalc_motion_factor_to_loopable(f, frames.indexed_length)
            length_in_seconds = frames.indexed_length / frames.framerate.as_float()
            t = length_in_seconds * f
            x = (t + phase_seconds) * math.pi * 2.0 / period_seconds
            return math.sin(x) * 0.5 + 0.5

        return BatchCameraMotion(frames, output_width, output_height, motion, zoom_frame).execute()


class DVB_SineCameraPan:
    NODE_NAME = "Sine Camera Pan"
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
                "period_seconds": ("FLOAT", {"default": 1.0, "min": 0.1, "step": 0.1}),
                "phase_seconds": ("FLOAT", {"default": 0.0}),
                "pan_mode": (["edge to edge", "edge to center"],)
            },
        }

    CATEGORY = NodeCategories.CAMERA
    RETURN_TYPES = (FrameSet.TYPE_NAME,)
    RETURN_NAMES = ("frames",)
    FUNCTION = "result"


    def result(self, frames: FrameSet, output_width: int, output_height: int, direction_x: float,
               direction_y: float, pan_mode: str, period_seconds, phase_seconds):
        def motion(f):
            f = _recalc_motion_factor_to_loopable(f, frames.indexed_length)
            if pan_mode == "edge to center":
                f = f * 0.5
            length_in_seconds = frames.indexed_length / frames.framerate.as_float()
            t = length_in_seconds * f
            x = (t + phase_seconds) * math.pi * 2.0 / period_seconds
            return math.sin(x) * 0.5 + 0.5

        frame_func = make_pan_function(direction_x, direction_y)
        return BatchCameraMotion(frames, output_width, output_height, motion, frame_func).execute()


class DVB_SineCameraRoll:
    NODE_NAME = "Sine Camera Roll"
    ICON = "↻"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "frames": (FrameSet.TYPE_NAME,),
                "output_width": ("INT", {"default": 512, "min": 1}),
                "output_height": ("INT", {"default": 512, "min": 1}),
                "period_seconds": ("FLOAT", {"default": 1.0, "min": 0.1, "step": 0.1}),
                "phase_seconds": ("FLOAT", {"default": 0.0}),
                "degrees": ("FLOAT", {"default": 45.0})
            },
        }

    CATEGORY = NodeCategories.CAMERA
    RETURN_TYPES = (FrameSet.TYPE_NAME,)
    RETURN_NAMES = ("frames",)
    FUNCTION = "result"

    def result(self, frames: FrameSet, output_width: int, output_height: int, degrees: float, period_seconds,
               phase_seconds):
        def motion(f):
            f = _recalc_motion_factor_to_loopable(f, frames.indexed_length)
            length_in_seconds = frames.indexed_length / frames.framerate.as_float()
            t = length_in_seconds * f
            x = (t + phase_seconds) * math.pi * 2.0 / period_seconds
            return math.sin(x) * 0.5 + 0.5

        def frame_func(image: DVB_Image, f, o_width, o_height):
            w = image.width
            h = image.height
            c_x = round(w * 0.5)
            c_y = round(h * 0.5)
            a = c_x - o_width // 2
            b = c_y - o_height // 2
            return image.rotate(f * degrees).crop(a, b, a + o_width, b + o_height)

        return BatchCameraMotion(frames, output_width, output_height, motion, frame_func).execute()
