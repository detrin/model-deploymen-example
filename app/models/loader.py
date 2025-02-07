import torch
from transformers import AlignProcessor, AlignModel

def load_model():
    processor = AlignProcessor.from_pretrained("kakaobrain/align-base")
    model = AlignModel.from_pretrained("kakaobrain/align-base")
    
    # Optimize for CPU
    # model = torch.jit.script(model)
    # model.eval()
    # model = torch.jit.optimize_for_inference(model)
    
    return model, processor