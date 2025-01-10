import os
import argparse
import torch
import re
from omegaconf import OmegaConf

def generate(args):
    file_name = os.path.basename(args.model)
    pattern = r"epoch=(\d+)-val_loss=(-?[\d\.]+)\.ckpt"
    match = re.match(pattern, file_name)
    if match:
        epoch = match.group(1)
        val_loss = match.group(2)
        model_file_name = f"model_apollo_ep_{epoch}_val_loss_{val_loss}.ckpt"
        config_file_name = f"config_apollo_ep_{epoch}_val_loss_{val_loss}.yaml"
    else:
        model_file_name = "model_apollo.ckpt"
        config_file_name = "config_apollo.yaml"

    cfg = OmegaConf.load(args.config)
    msst_cfg = {
        'audio': {'chunk_size': 441000, 'min_mean_abs': 0.0, 'num_channels': 2, 'sample_rate': cfg.model.sr},
        'augmentations': {'enable': False},
        'inference': {'batch_size': 1, 'num_overlap': 4},
        'model': {
            'feature_dim': cfg.model.feature_dim,
            'layer': cfg.model.layer,
            'sr': cfg.model.sr,
            'win': cfg.model.win
        },
        'training': {
            'batch_size': 1, 'coarse_loss_clip': True, 'grad_clip': 0, 'instruments': ['restored', 'addition'], 
            'lr': 1.0, 'num_epochs': 1000, 'num_steps': 1000, 'optimizer': 'prodigy', 'patience': 2, 'q': 0.95, 
            'reduce_factor': 0.95, 'target_instrument': 'restored', 'use_amp': True
        }
    }
    with open(os.path.join(args.output, config_file_name), 'w') as f:
        OmegaConf.save(msst_cfg, f)

    checkpoint = torch.load(args.model, map_location='cpu', weights_only=False)
    state_dict = checkpoint['state_dict']
    for k in list(state_dict.keys()):
        if "audio_model" in k:
            new_k = k.replace("audio_model.", "")
            state_dict[new_k] = state_dict[k]
        del state_dict[k]
    checkpoint['state_dict'] = state_dict
    torch.save(checkpoint, os.path.join(args.output, model_file_name))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", type=str, default="configs/apollo.yaml")
    parser.add_argument("-m", "--model", type=str, default=None)
    parser.add_argument("-o", "--output", type=str, default="output")
    args = parser.parse_args()

    assert args.model is not None, "Please provide a model checkpoint"
    os.makedirs(args.output, exist_ok=True)
    generate(args)
    print(f"Generated MSST model and config file at {args.output}")