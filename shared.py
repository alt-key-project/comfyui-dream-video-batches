# -*- coding: utf-8 -*-

import hashlib
import json
import os
import random
from typing import Dict, Tuple, List

import folder_paths as comfy_paths
import glob
import numpy
import torch
from PIL import Image, ImageFilter, ImageEnhance



NODE_FILE = os.path.abspath(__file__)
DREAM_NODES_SOURCE_ROOT = os.path.dirname(NODE_FILE)
TEMP_PATH = os.path.join(os.path.abspath(comfy_paths.temp_directory), "Dream_Anim")




_config_data = None




def pick_random_by_weight(data: List[Tuple[float, object]], rng: random.Random):
    total_weight = sum(map(lambda item: item[0], data))
    r = rng.random()
    for (weight, obj) in data:
        r -= weight / total_weight
        if r <= 0:
            return obj
    return data[0][1]




class DreamMask:
    def __init__(self, tensor_image=None, pil_image=None):
        if pil_image:
            self.pil_image = pil_image
        else:
            self.pil_image = convertTensorImageToPIL(tensor_image)
        if self.pil_image.mode != "L":
            self.pil_image = self.pil_image.convert("L")

    def create_tensor_image(self):
        return torch.from_numpy(numpy.array(self.pil_image).astype(numpy.float32) / 255.0)


def list_files_in_directory(directory_path: str, pattern: str, alphabetic_index: bool,
                             endings=('.jpeg', '.jpg', '.png', '.tiff', '.gif', '.bmp', '.webp')) -> Dict[int, List[str]]:
    if not os.path.isdir(directory_path):
        return {}
    dirs_to_search = [directory_path]
    if os.path.isdir(os.path.join(directory_path, "batch_0001")):
        dirs_to_search = list()
        for i in range(10000):
            dirpath = os.path.join(directory_path, "batch_" + (str(i).zfill(4)))
            if not os.path.isdir(dirpath):
                break
            else:
                dirs_to_search.append(dirpath)

    def _num_from_filename(fn):
        (text, _) = os.path.splitext(fn)
        token = text.split("_")[-1]
        if token.isdigit():
            return int(token)
        else:
            return -1

    result = dict()
    for search_path in dirs_to_search:
        files = []
        for file_name in glob.glob(os.path.join(search_path, pattern), recursive=False):
            if (endings is None) or file_name.lower().endswith(endings):
                files.append(os.path.abspath(file_name))

        if alphabetic_index:
            files.sort()
            for idx, item in enumerate(files):
                lst = result.get(idx, [])
                lst.append(item)
                result[idx] = lst
        else:
            for filepath in files:
                idx = _num_from_filename(os.path.basename(filepath))
                lst = result.get(idx, [])
                lst.append(filepath)
                result[idx] = lst
    return result

def list_images_in_directory(directory_path: str, pattern: str, alphabetic_index: bool) -> Dict[int, List[str]]:
    return list_files_in_directory(directory_path, pattern, alphabetic_index,
                                   ('.jpeg', '.jpg', '.png', '.tiff', '.gif', '.bmp', '.webp'))



class DreamStateStore:
    def __init__(self, name, read_fun, write_fun):
        self._read = read_fun
        self._write = write_fun
        self._name = name

    def _as_key(self, k):
        return self._name + "_" + k

    def get(self, key, default):
        v = self[key]
        if v is None:
            return default
        else:
            return v

    def update(self, key, default, f):
        prev = self.get(key, default)
        v = f(prev)
        self[key] = v
        return v

    def __getitem__(self, item):
        return self._read(self._as_key(item))

    def __setitem__(self, key, value):
        return self._write(self._as_key(key), value)


class DreamStateFile:
    def __init__(self, state_collection_name="state"):
        self._filepath = os.path.join(TEMP_PATH, state_collection_name + ".json")
        self._dirname = os.path.dirname(self._filepath)
        if not os.path.isdir(self._dirname):
            os.makedirs(self._dirname)
        if not os.path.isfile(self._filepath):
            self._data = {}
        else:
            with open(self._filepath, encoding="utf-8") as f:
                self._data = json.load(f)

    def get_section(self, name: str) -> DreamStateStore:
        return DreamStateStore(name, self._read, self._write)

    def _read(self, key):
        return self._data.get(key, None)

    def _write(self, key, value):
        previous = self._data.get(key, None)
        if value is None:
            if key in self._data:
                del self._data[key]
        else:
            self._data[key] = value
        with open(self._filepath, "w", encoding="utf-8") as f:
            json.dump(self._data, f)
        return previous



#
#
# class MpegEncoderUtility:
#     def __init__(self, video_path: str, bit_rate_factor: float, width: int, height: int, files: List[str],
#                  fps: float, encoding_threads: int, codec_name, max_b_frame):
#         import mpegCoder
#         self._files = files
#         self._logger = get_logger()
#         self._enc = mpegCoder.MpegEncoder()
#         bit_rate = self._calculate_bit_rate(width, height, fps, bit_rate_factor)
#         self._logger.info("Bitrate " + str(bit_rate))
#         self._enc.setParameter(
#             videoPath=video_path, codecName=codec_name,
#             nthread=encoding_threads, bitRate=bit_rate, width=width, height=height, widthSrc=width,
#             heightSrc=height,
#             GOPSize=len(files), maxBframe=max_b_frame, frameRate=self._fps_to_tuple(fps))
#
#     def _calculate_bit_rate(self, width: int, height: int, fps: float, bit_rate_factor: float):
#         bits_per_pixel_base = 0.5
#         return round(max(10, float(width * height * fps * bits_per_pixel_base * bit_rate_factor * 0.001)))
#
#     def encode(self):
#         if not self._enc.FFmpegSetup():
#             raise Exception("Failed to setup MPEG Encoder - check parameters!")
#         try:
#             t = time.time()
#
#             for filepath in self._files:
#                 self._logger.debug("Encoding frame {}", filepath)
#                 image = DreamImage.from_file(filepath).convert("RGB")
#                 self._enc.EncodeFrame(image.numpy_array())
#             self._enc.FFmpegClose()
#             self._logger.info("Completed video encoding of {n} frames in {t} seconds", n=len(self._files),
#                               t=round(time.time() - t))
#         finally:
#             self._enc.clear()
#
#     def _fps_to_tuple(self, fps: float):
#         def _is_almost_int(f: float):
#             return abs(f - int(f)) < 0.001
#
#         a = fps
#         b = 1
#         while not _is_almost_int(a) and b < 100:
#             a /= 10
#             b *= 10
#         a = round(a)
#         b = round(b)
#         self._logger.info("Video specified as {fps} fps - encoder framerate {a}/{b}", fps=fps, a=a, b=b)
#         return (a, b)
