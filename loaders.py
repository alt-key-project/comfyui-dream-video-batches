# -*- coding: utf-8 -*-
import os
import random

from .categories import NodeCategories
from .dreamtypes import SharedTypes, FrameCounter
from .shared import ALWAYS_CHANGED_FLAG, list_images_in_directory, DreamImage, list_files_in_directory


def _load_and_resize(image_path, resize_width, resize_height, mode) -> DreamImage:
    return DreamImage(file_path=image_path).resize(resize_width, resize_height).convert(mode)


class DreamRandomBatchLoader:
    CATEGORY = NodeCategories.BATCH
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "result"
    NODE_NAME = "Image Batch Random Loader"
    ICON = "⚅"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "directory_path": ("STRING", {"default": '', "multiline": False}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "pattern": ("STRING", {"default": '*', "multiline": False}),
                "mode": (["RGB", "RGBA", "GRAY"],),
                "load_count": ("INT", {"default": 2, "min": 1, "max": 100000})
            },
            "optional": {
                "resize_width": ("INT", {"default": 0, "min": 0, "max": 8192}),
                "resize_height": ("INT", {"default": 0, "min": 0, "max": 8192})
            }
        }

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def result(self, directory_path, pattern, load_count, seed, mode, **other):
        entries = list_images_in_directory(directory_path, pattern, True)
        keys_in_order = list(sorted(entries.keys()))
        random.Random(seed).shuffle(keys_in_order)

        if len(keys_in_order) > load_count:
            keys_in_order = list(keys_in_order[0:load_count])

        resize_width = other.get("resize_width", 0)
        resize_height = other.get("resize_height", 0)

        images = list()
        for k in keys_in_order:
            images.append(_load_and_resize(entries[k].pop(), resize_width, resize_height, mode))
        if len(images) == 0:
            images.append(DreamImage.empty(512, 512, "RGB").resize(resize_width, resize_height).convert(mode))
        return (DreamImage.join_to_tensor_data(images),)


class DreamImageBatchLoader:
    CATEGORY = NodeCategories.BATCH
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "result"
    NODE_NAME = "Image Big Batch Loader"
    ICON = "💾"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "directory_path": ("STRING", {"default": '', "multiline": False}),
                "pattern": ("STRING", {"default": '*', "multiline": False}),
                "max_loaded": ("INT", {"default": 100, "min": 1, "max": 100000}),
                "mode": (["RGB", "RGBA", "GRAY"],),
                "indexing": (["numeric", "alphabetic order"],)
            },
            "optional": {
                "resize_width": ("INT", {"default": 0, "min": 0, "max": 8192}),
                "resize_height": ("INT", {"default": 0, "min": 0, "max": 8192})
            }
        }

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def result(self, directory_path, pattern, indexing, max_loaded, mode, **other):
        entries = list_images_in_directory(directory_path, pattern, indexing == "alphabetic order")
        keys_in_order = list(sorted(entries.keys()))

        if len(keys_in_order) > max_loaded:
            keys_in_order = list(keys_in_order[0:max_loaded])

        resize_width = other.get("resize_width", 0)
        resize_height = other.get("resize_height", 0)

        images = list()
        i = 0
        for k in keys_in_order:
            images.append(_load_and_resize(entries[k].pop(), resize_width, resize_height, mode))
            i += 1
            if (i % 100) == 0:
                print("Loaded image {}/{}".format(i, len(entries)))
        if len(images) == 0:
            images.append(DreamImage.empty(512, 512, "RGB").resize(resize_width, resize_height).convert(mode))
        return (DreamImage.join_to_tensor_data(images),)


class DreamDirContents:
    NODE_NAME = "Directory Contents"
    ICON = "💾"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": SharedTypes.frame_counter | {
                "directory_path": ("STRING", {"default": '', "multiline": False}),
                "pattern": ("STRING", {"default": '*', "multiline": False}),
                "indexing": (["numeric", "alphabetic order"],)
            }
        }

    CATEGORY = NodeCategories.UTILS
    RETURN_TYPES = ("STRING","STRING")
    RETURN_NAMES = ("file_path", "name")
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def result(self, frame_counter: FrameCounter, directory_path, pattern, indexing, **other):
        entries = list_files_in_directory(directory_path, pattern, indexing == "alphabetic order",
                                          (".mpg", ".mp4", ".avi", ".xvid", ".wmv", ".flv", ".mkv", ".webm"))
        entry = entries.get(frame_counter.current_frame, None)
        if entry is None:
            raise Exception("No such entry!")
        p = os.path.normpath(os.path.abspath(entry[0]))
        nm, _ = os.path.splitext(os.path.basename(p))
        return (entry[0], nm)


class DreamImageSequenceInputWithDefaultFallback:
    NODE_NAME = "Image Sequence Loader"
    ICON = "💾"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": SharedTypes.frame_counter | {
                "directory_path": ("STRING", {"default": '', "multiline": False}),
                "pattern": ("STRING", {"default": '*', "multiline": False}),
                "indexing": (["numeric", "alphabetic order"],)
            },
            "optional": {
                "default_image": ("IMAGE", {"default": None})
            }
        }

    CATEGORY = NodeCategories.IMAGE_ANIMATION
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("image", "frame_name")
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return ALWAYS_CHANGED_FLAG

    def result(self, frame_counter: FrameCounter, directory_path, pattern, indexing, **other):
        default_image = other.get("default_image", None)
        entries = list_images_in_directory(directory_path, pattern, indexing == "alphabetic order")
        entry = entries.get(frame_counter.current_frame, None)
        if not entry:
            return (default_image, "")
        else:
            image_names = [os.path.basename(file_path) for file_path in entry]
            images = map(lambda f: DreamImage(file_path=f), entry)
            return (DreamImage.join_to_tensor_data(images), image_names[0])
