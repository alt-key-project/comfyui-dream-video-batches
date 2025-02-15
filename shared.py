# -*- coding: utf-8 -*-

import os
import random
from typing import Dict, Tuple, List
import glob

NODE_FILE = os.path.abspath(__file__)
DREAM_NODES_SOURCE_ROOT = os.path.dirname(NODE_FILE)

_config_data = None

def pick_random_by_weight(data: List[Tuple[float, object]], rng: random.Random):
    total_weight = sum(map(lambda item: item[0], data))
    r = rng.random()
    for (weight, obj) in data:
        r -= weight / total_weight
        if r <= 0:
            return obj
    return data[0][1]


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


