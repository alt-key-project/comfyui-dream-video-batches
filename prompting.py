from .categories import NodeCategories
from .dreamtypes import PartialPrompt
from .shared import hashed_as_strings


class RandomPromptScheduleGenerator:
    NODE_NAME = "Random Prompt Schedule Generator"
    ICON = "🖺"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "partial_prompt": (PartialPrompt.ID,),
                "fixed_partial_prompt": (PartialPrompt.ID,),
                "total_frames": ("INT", {"default": 100, "min": 1, "max": 0xffffffffffffffff}),
                "prompt_interval": ("INT", {"default": 10, "min": 1, "max": 0xffffffffffffffff}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "num_positive": ("INT", {"default": 3, "min": 1, "max": 100}),
                "num_negative": ("INT", {"default": 0, "min": 0, "max": 100}),
                "adjustment": (["raw", "by_abs_max", "by_abs_sum"],),
                "clamp": ("FLOAT", {"default": 2.0, "min": 0.1, "step": 0.1}),
                "adjustment_reference": ("FLOAT", {"default": 1.0, "min": 0.1}),
            },
        }

    CATEGORY = NodeCategories.CONDITIONING
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("prompt_schedule", "positive_prompt_schedule", "negative_prompt_schedule")
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return hashed_as_strings(*values)

    def result(self, partial_prompt: PartialPrompt, fixed_partial_prompt, total_frames, prompt_interval, seed,
               num_positive, num_negative, adjustment, adjustment_reference, clamp):
        text = list()
        text_pos = list()
        text_neg = list()
        prompt_interval = max(1, prompt_interval)
        i = 0
        while i < total_frames:
            step_prompt = partial_prompt.random_subset(num_positive, num_negative, seed + i)
            step_prompt = step_prompt.merge(fixed_partial_prompt)

            f = 1.0
            if adjustment == "by_abs_sum":
                f = adjustment_reference / step_prompt.abs_sum()
            elif adjustment == "by_abs_max":
                f = adjustment_reference / step_prompt.abs_max()
            step_prompt = step_prompt.scaled_by(f)

            pos, neg = step_prompt.finalize(clamp)
            signed_prompt = step_prompt.finalize_signed(clamp)

            text.append('"{}": "{}"'.format(i, signed_prompt))
            text_pos.append('"{}": "{}"'.format(i, pos))
            text_neg.append('"{}": "{}"'.format(i, neg))
            i += prompt_interval

        return (",\n".join(text) + "\n", ",\n".join(text_pos) + "\n", ",\n".join(text_neg) + "\n")


class DreamWeightedPromptBuilder:
    NODE_NAME = "Build Prompt"
    ICON = "⚖"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "optional": {
                "partial_prompt": (PartialPrompt.ID,)
            },
            "required": {
                "added_prompt": ("STRING", {"default": "", "multiline": True}),
                "weight": ("FLOAT", {"default": 1.0}),
            },
        }

    CATEGORY = NodeCategories.CONDITIONING
    RETURN_TYPES = (PartialPrompt.ID,)
    RETURN_NAMES = ("partial_prompt",)
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return hashed_as_strings(*values)

    def result(self, added_prompt, weight, **args):
        input = args.get("partial_prompt", PartialPrompt())
        p = input.add(added_prompt, weight)
        return (p,)


class DreamPromptFinalizer:
    NODE_NAME = "Finalize Prompt"
    ICON = "🗫"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "partial_prompt": (PartialPrompt.ID,),
                "adjustment": (["raw", "by_abs_max", "by_abs_sum"],),
                "clamp": ("FLOAT", {"default": 2.0, "min": 0.1, "step": 0.1}),
                "adjustment_reference": ("FLOAT", {"default": 1.0, "min": 0.1}),
            },
        }

    CATEGORY = NodeCategories.CONDITIONING
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("positive", "negative")
    FUNCTION = "result"

    @classmethod
    def IS_CHANGED(cls, *values):
        return hashed_as_strings(*values)

    def result(self, partial_prompt: PartialPrompt, adjustment, adjustment_reference, clamp):
        if adjustment == "raw" or partial_prompt.is_empty():
            return partial_prompt.finalize(clamp)
        elif adjustment == "by_abs_sum":
            f = adjustment_reference / partial_prompt.abs_sum()
            return partial_prompt.scaled_by(f).finalize(clamp)
        else:
            f = adjustment_reference / partial_prompt.abs_max()
            return partial_prompt.scaled_by(f).finalize(clamp)
