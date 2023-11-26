# -*- coding: utf-8 -*-
import torch

from .dvb_image import DVB_Image


class DVB_ImageBatchProcessor:
    def __init__(self, inputs: torch.Tensor, **extra_args):
        self._size = len(inputs)
        self._tensor = inputs
        self._extra_args = extra_args

    def process(self, proc_fun) -> torch.Tensor:
        output = list()
        for i in range(self._size):
            r = proc_fun(i, self._size, DVB_Image(self._tensor[i]), **self._extra_args)
            if isinstance(r, DVB_Image):
                output.append(r)
        return DVB_Image.join_to_tensor_data(output)
