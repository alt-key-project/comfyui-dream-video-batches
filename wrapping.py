from .categories import NodeCategories
from .core import *


class DVB_ImagesToFrameSet:
    NODE_NAME = "Create Frame Set"
    ICON = "📽"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "first_frame_index": ("INT", {"default": 0}),
                "step": ("INT", {"default": 1, "min": 1, "max": 256}),
                "framerate_base": ("INT", {"default": 24, "min": 1}),
                "framerate_divisor": ("INT", {"default": 1, "min": 1}),
            },
        }

    CATEGORY = NodeCategories.BATCH
    RETURN_TYPES = (FrameSet.TYPE_NAME,)
    RETURN_NAMES = ("frames",)
    FUNCTION = "work"

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def work(self, images, first_frame_index, step, framerate_base, framerate_divisor):
        fps = FrameRate(framerate_base, framerate_divisor)
        indices = []
        for i in range(len(images)):
            indices.append(first_frame_index + i * step)
        return (FrameSet(images, fps, indices),)


class DVB_UnwrapFrameSet:
    NODE_NAME = "Unwrap Frame Set"
    ICON = "📽"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "frames": (FrameSet.TYPE_NAME,),
                "gap_mode": (["BLEND", "FAIL", "REINDEX"],),
            },
        }

    CATEGORY = NodeCategories.BATCH
    RETURN_TYPES = ("IMAGE", "FLOAT", "INT", "INT", "INT", "INT", "INT", "INT")
    RETURN_NAMES = ("images", "framerate_float", "framerate_rounded", "framerate_base", "framerate_divisor",
                    "first_index", "indexed_length", "frame_count")
    FUNCTION = "work"

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def work(self, frames: FrameSet, gap_mode: str):
        images = frames.images
        if gap_mode == "FAIL" and frames.has_index_gaps():
            on_node_error(DVB_ImagesToFrameSet, "Frame set contains gaps!")
        if gap_mode == "BLEND":
            images = frames.get_blended_frame_images()
        return (DVB_Image.join_to_tensor_data(images), frames.framerate.as_float(), frames.framerate.rounded_int(),
                frames.framerate.base, frames.framerate.divisor, frames.first_index, frames.indexed_length, len(frames))
