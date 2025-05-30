<div align="center">

# Apollo Training

在[原始Apollo代码](https://github.com/JusperLee/Apollo)基础上改进了训练集格式以及训练过程<br>
Improve the training set production process and the training process

</div>

## 1. 环境配置

经测试，python310可以运行，其他版本未测试。此外，建议手动安装PyTorch。

```shell
conda create -n apollo python=3.10 -y
conda activate apollo
pip install -r requirements.txt
```

## 2. 数据集构建

### 2.1 训练集格式

支持采用多个训练集进行训练，但所有训练集的格式（type1或者type2）必须一致。训练集文件夹结构如下：

- **Type 1 (MUSDB)**

  每个音频放在单独文件夹内。每个文件夹包含该歌曲的原始音频（original.wav）以及压缩后的音频（codec.wav），格式与MUSDBHQ18数据集相同。原始音频和压缩后的音频格式可以不一致，例如（original.wav，codec.mp3）。但不同文件夹中所有的原始音频和所有的压缩后的音频格式必须一致（例如所有的原始音频全部是wav，全部的压缩后的音频全部是mp3）。音频格式需要在配置文件中指定。
  ```
  train
    ├─ song_1
    │    codec.mp3
    │    original.wav
    ├─ song_2
    │    codec.mp3
    │    original.wav
    └─ song_3
        ...
  ```

- **Type 2 (stems)**

  所有的原始音频放在同一个文件夹内（original文件夹），所有的压缩后的音频放在另一个文件夹内（codec文件夹）。同一个文件夹中的所有音频格式需要一致（例如original文件夹中所有音频格式为wav，codec文件夹中所有音频格式为mp3）。音频格式需要在配置文件中指定。此外，original文件夹中的音频文件和codec文件夹中的音频文件，除后缀名以外的其余名称一一对应。
  ```
  train
    ├─codec
    │    my_song.wav
    │    test_song.wav
    │    vocals.wav
    │    114514.wav
    │    ...
    └─original
        my_song.mp3
        test_song.mp3
        vocals.mp3
        114514.mp3
        ...
  ```

### 2.2 验证集格式

支持多个验证集进行验证，无论训练集选择何种方式，都需要按照**Type 1 (MUSDB)**的结构构建验证集文件夹。

每个音频放在单独文件夹内。每个文件夹包含该歌曲的原始音频（original.wav）以及压缩后的音频（codec.wav），格式与MUSDBHQ18数据集相同。原始音频和压缩后的音频格式可以不一致，例如（original.wav，codec.mp3）。但不同文件夹中所有的原始音频和所有的压缩后的音频格式必须一致（例如所有的原始音频全部是wav，全部的压缩后的音频全部是mp3）。音频格式需要在配置文件中指定。
```
valid
  ├─ song_1
  │    codec.mp3
  │    original.wav
  ├─ song_2
  │    codec.mp3
  │    original.wav
  └─ song_3
       ...
```

### 2.3 自动构建压缩音频

你可以手动构建压缩后的音频，然后根据上面的“数据集格式”，构建数据集文件夹。也可以使用提供的脚本自动构建压缩音频，脚本位于`scripts/generate_datasets.py`。使用该脚本时，请确保已经安装了FFmpeg。具体使用方法可以通过 `python scripts/generate_datasets.py -h` 查看。

**参数说明：**

- `-i`, `--input_folder`：输入文件夹，包含原始音频。
- `-o`, `--output_folder`：输出文件夹，输出压缩后的音频。
- `-t`, `--dataset_type`：数据集类型，1表示MUSDB格式，2表示stems格式。默认为1。
- `-gt`, `--generate_train`：构建训练集。
- `-gv`, `--generate_valid`：构建验证集。
- `-th`, `--threads`：处理线程数量，默认为CPU核心数。
- `--save_logs`：保存处理过程的详细信息至输出文件夹。
- `--bitrates`：构建验证集时，指定比特率，默认为所有随机比特率。["64k", "96k", "128k", "192k", "256k", "320k"]
- `--enable_quality`：启用质量参数。
  - `--quality_possibility`：启用质量参数的概率，默认为1。
  - `--quality_min`：随机质量参数的最小值，最小为0，默认为0。**注意，此处的quality数值越小，音频质量越高。**
  - `--quality_max`：随机质量参数的最大值，最大为9，默认为9。**注意，此处的quality数值越大，音频质量越低。**
- `--enable_lowpass`：启用低通滤波。
  - `--lowpass_possibility`：启用低通滤波的概率，默认为1。
  - `--lowpass_min_freq`：随机低通滤波的最小频率，默认为12000。
  - `--lowpass_max_freq`：随机低通滤波的最大频率，默认为16000。

**一些示例：**

- 输入文件夹input，输出文件夹output，使用dataset type1，构建训练集。默认采用所有随机比特率，不启用其余参数。
  ```bash
  python scripts/generate_datasets.py -i input -o output --dataset_type 1 --generate_train
  ```

- 输入文件夹input，输出文件夹output，构建验证集。采用随机比特率["192k", "256k", "320k"]，不启用其余参数。
  ```bash
  python scripts/generate_datasets.py -i input -o output --generate_valid --bitrate 192k 256k 320k

- 输入文件夹input，输出文件夹output，使用dataset type2，构建训练集。启用质量参数，启用概率为0.5，质量范围为0-9。启用低通，启用概率为0.5，低通频率范围为12k-16k。
  ```bash
  python scripts/generate_datasets.py -i input -o output --dataset_type 2 --generate_train --enable_quality --quality_possibility 0.5 --quality_min 0 --quality_max 9 --enable_lowpass --lowpass_possibility 0.5 --lowpass_min_freq 12000 --lowpass_max_freq 16000
  ```

- 输入文件夹input，输出文件夹output，构建验证集。限制处理线程数量为2，默认采用所有随机比特率，不启用其余参数。保存处理过程的详细信息。
  ```bash
  python scripts/generate_datasets.py -i input -o output --generate_valid --threads 2 --save_logs
  ```

### 2.4 修改配置文件

配置文件模板位于`configs/apollo.yaml`，下面仅介绍一些关键参数。其余参数请前往配置文件根据注释介绍自行修改。

```yaml
exp: 
  dir: ./exps # 训练结果存放路径
  name: apollo # 实验名称
  # 上面两行加起来，即会在./exps/apollo中存放此次训练的结果和日志

datas:
  _target_: look2hear.datas.DataModule
  dataset_type: 1 # 数据集类型，1为MUSDB格式，2为stem格式，参考上面的数据集制作部分
  sr: 44100 # 采样率
  segments: 4 # 训练时随机裁剪的音频长度（单位：秒）
  num_steps: 1000 # 一个epoch中的迭代次数，也可理解为一个epoch中随机抽取的音频数量
  batch_size: 1
  num_workers: 0
  pin_memory: true

  stems:
    original: original # 不要修改
    codec: codec # 不要修改

  train:
    dir: # 训练集文件夹路径，支持输入多个文件夹
    - train_dir_1
    - train_dir_2
    - train_dir_3
    original_format: wav # 训练集文件夹中原始音频的格式
    codec_format: mp3 # 训练集文件夹中压缩音频的格式

  valid:
    dir: # 验证集文件夹路径，支持输入多个文件夹
    - valid_dir_1
    - valid_dir_2
    - valid_dir_3
    original_format: wav # 验证集文件夹中原始音频的格式
    codec_format: mp3 # 验证集文件夹中压缩音频的格式

model:
  _target_: look2hear.models.apollo.Apollo
  sr: 44100 # 采样率
  win: 20 # 窗口长度
  feature_dim: 256 # 特征维度
  layer: 6 # 网络层数
  # feature_dim和layer决定网络大小，例如256x6

metrics:
  _target_: look2hear.losses.MultiSrcNegSDR
  sdr_type: sisdr # 验证时使用的metric，可选[snr, sisdr, sdsdr]

# 如果你不希望early_stopping，可以注释掉或者删除掉下面的内容
early_stopping:
  _target_: pytorch_lightning.callbacks.EarlyStopping
  monitor: val_loss # 监控的指标
  patience: 50 # 连续多少个epoch没有改进，训练就会提前结束
  mode: min
  verbose: true

trainer:
  _target_: pytorch_lightning.Trainer
  devices: [0] # 训练使用的GPU ID
  max_epochs: 1000 # 最大训练轮数
  sync_batchnorm: true
  default_root_dir: ${exp.dir}/${exp.name}/
  accelerator: cuda
  limit_train_batches: 1.0
  fast_dev_run: false
  precision: bf16 # 可选项：[16, bf16, 32, 64]，建议采用bf16
  enable_model_summary: true
```

## 3. 训练

训练代码已在Windows及Linux系统下单卡/多卡测试通过。使用下面的代码开始训练。若需要wandb在线可视化，请先执行`wandb login`，并根据指示，完成登陆。

配置文件中默认启用了early stopping机制，并且设置了patience。这意味着如果验证集的损失在连续patience个epoch内没有改进，训练就会提前结束。如果不希望提前结束而是训练到最大epoch，你可以删除配置文件中的early_stopping相关的配置。

- 从头开始训练apollo模型
  ```bash
  python train.py -c CONFIG_FILE
  # 例如：python train.py -c ./configs/apollo.yaml
  ```

- 继续训练apollo模型
  ```bash
  python train.py -c CONFIG_FILE -m MODEL_FILE
  # 例如：python train.py -c ./configs/apollo.yaml -m ./exps/apollo/last.ckpt
  ```

## 4. 推理

更推荐使用[ZFTurbo](https://github.com/ZFTurbo)的[Music-Source-Separation-Training](https://github.com/ZFTurbo/Music-Source-Separation-Training)进行模型推理和验证。

也可以使用本仓库中的`inference.py`进行推理。代码修改自[Music-Source-Separation-Training](https://github.com/ZFTurbo/Music-Source-Separation-Training)，并进行了简化。具体使用方法可以通过 `python inference.py -h` 查看。

- `-m`, `--model`: 模型路径
- `-c`, `--config`: 配置文件路径
- `-i`, `--input`: 输入音频路径或者输入文件夹路径
- `-o`, `--output`: 输出结果文件夹路径
- `--segments`: 切片长度，单位为秒，默认为10秒
- `--overlap`: 切片重叠长度，默认为4
- `--batch_size`: 批量大小，默认为1
- `--save_addition`: 同时保存addition音频，addition=input-output

```bash
python inference.py -m MODEL_FILE -c CONFIG_FILE -i INPUT -o OUTPUT_DIR [OPTIONS]
# 例如：python inference.py -m model.ckpt -c ./configs/apollo.yaml -i input -o output
```

## 5. 验证

使用本仓库中的`validate.py`进行验证。需要输入验证集文件夹路径。验证集制作方法参考上面的2.2。

脚本可以根据验证集，计算模型的['sdr', 'si_sdr', 'l1_freq', 'log_wmse', 'aura_stft', 'aura_mrstft', 'bleedless', 'fullness']数值。具体使用方法可以通过 `python validate.py -h` 查看。

- `-m`, `--model`: 模型路径
- `-c`, `--config`: 配置文件路径
- `-i`, `--input`: 输入验证集文件夹路径
- `--metrics`: 需要计算的指标，默认为['sdr']，可选值：['sdr', 'si_sdr', 'l1_freq', 'log_wmse', 'aura_stft', 'aura_mrstft', 'bleedless', 'fullness']
- `--segments`: 切片长度，单位为秒，默认为10秒
- `--overlap`: 切片重叠长度，默认为4
- `--batch_size`: 批量大小，默认为1
- `--save_results`: 同时保存验证结果和验证日志文件
- `--output`: 验证结果的保存文件夹路径

```bash
python validate.py -m MODEL_FILE -c CONFIG_FILE -i INPUT_DIR --metrics METRICS1 METRICS2 ... [OPTIONS]
# 例如：python validate.py -m model.ckpt -c ./configs/apollo.yaml -i VALID --metrics sdr si_sdr bleedless fullness
```

## 5. 导出[MSST](https://github.com/ZFTurbo/Music-Source-Separation-Training)模型和配置文件

由此仓库训练出来的Apollo模型无法直接在MSST中使用，需要进行一些转换。使用 `scripts/generate_msst_model.py`。该脚本可以删除模型中的无用参数（模型大小大约缩减至一半），并且转换成[MSST](https://github.com/ZFTurbo/Music-Source-Separation-Training)支持的模型。具体使用方法可以通过 `python scripts/generate_msst_model.py -h` 查看。

- `-c`, `--config`: Apollo配置文件路径
- `-m`, `--model`: Apollo模型路径
- `-o`, `--output`: 输出文件夹路径，默认为output
- `-d`, `--discription`: 嵌入到模型文件中的描述信息，默认为空

```bash
python scripts/generate_msst_model.py -c CONFIG_FILE -m MODEL_FILE -o OUTPUT_DIR [OPTIONS]
# 例如：python scripts/generate_msst_model.py -c ./configs/apollo.yaml -m ./exps/apollo/last.ckpt
```

----

<div align="center">

# Apollo: Band-sequence Modeling for High-Quality Audio Restoration

  <strong>Kai Li<sup>1,2</sup>, Yi Luo<sup>2</sup></strong><br>
    <strong><sup>1</sup>Tsinghua University, Beijing, China</strong><br>
    <strong><sup>2</sup>Tencent AI Lab, Shenzhen, China</strong><br>
  <a href="https://arxiv.org/abs/2409.08514">ArXiv</a> | <a href="https://cslikai.cn/Apollo/">Demo</a>
</div>

## 📖 Abstract

Audio restoration has become increasingly significant in modern society, not only due to the demand for high-quality auditory experiences enabled by advanced playback devices, but also because the growing capabilities of generative audio models necessitate high-fidelity audio. Typically, audio restoration is defined as a task of predicting undistorted audio from damaged input, often trained using a GAN framework to balance perception and distortion. Since audio degradation is primarily concentrated in mid- and high-frequency ranges, especially due to codecs, a key challenge lies in designing a generator capable of preserving low-frequency information while accurately reconstructing high-quality mid- and high-frequency content. Inspired by recent advancements in high-sample-rate music separation, speech enhancement, and audio codec models, we propose Apollo, a generative model designed for high-sample-rate audio restoration. Apollo employs an explicit **frequency band split module** to model the relationships between different frequency bands, allowing for **more coherent and higher-quality** restored audio. Evaluated on the MUSDB18-HQ and MoisesDB datasets, Apollo consistently outperforms existing SR-GAN models across various bit rates and music genres, particularly excelling in complex scenarios involving mixtures of multiple instruments and vocals. Apollo significantly improves music restoration quality while maintaining computational efficiency.

## 📊 Results

*Here, you can include a brief overview of the performance metrics or results that Apollo achieves using different bitrates*

*Different methods' SDR/SI-SNR/VISQOL scores for various types of music, as well as the number of model parameters and GPU inference time. For the GPU inference time test, a music signal with a sampling rate of 44.1 kHz and a length of 1 second was used.*

## License

<a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License</a>.

## Third Party

[Apollo-Colab-Inference](https://github.com/jarredou/Apollo-Colab-Inference)

## Acknowledgements

Apollo is developed by the **Look2Hear** at Tsinghua University.

## Citation

If you use Apollo in your research or project, please cite the following paper:

```bibtex
@inproceedings{li2025apollo,
  title={Apollo: Band-sequence Modeling for High-Quality Music Restoration in Compressed Audio},
  author={Li, Kai and Luo, Yi},
  booktitle={IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)},
  year={2025},
  organization={IEEE}
}
```

## Contact

For any questions or feedback regarding Apollo, feel free to reach out to us via email: `tsinghua.kaili@gmail.com`
