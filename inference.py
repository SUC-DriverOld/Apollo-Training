import os
import torch
import torchaudio
import argparse
import look2hear.models

def load_audio(file_path):
    audio, _ = torchaudio.load(file_path)
    return audio.unsqueeze(0).cuda()  # [1, 1, samples]

def save_audio(file_path, audio, samplerate=44100):
    audio = audio.squeeze(0).cpu()
    torchaudio.save(file_path, audio, samplerate)

def main(input_wav, output_wav, model_path):
    os.environ['CUDA_VISIBLE_DEVICES'] = "0"

    model = look2hear.models.BaseModel.from_pretrain(model_path).cuda()
    test_data = load_audio(input_wav)
    with torch.no_grad():
        out = model(test_data)
    save_audio(output_wav, out)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audio Inference Script")
    parser.add_argument("-m", "--model", type=str, required=True, help="Path to model checkpoint")
    parser.add_argument("-i", "--in_wav", type=str, required=True, help="Path to input wav file")
    parser.add_argument("-o", "--out_wav", type=str, required=True, help="Path to output wav file")
    args = parser.parse_args()

    main(args.in_wav, args.out_wav, args.model)
