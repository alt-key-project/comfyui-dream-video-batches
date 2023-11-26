import comfy.model_management
import torch

def gc_comfyui():
    comfy.model_management.cleanup_models()
    torch.cuda.empty_cache()
    torch.cuda.ipc_collect()