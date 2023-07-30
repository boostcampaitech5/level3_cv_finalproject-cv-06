# AI 사진관
"**AI 사진관**" is a service that can generate identification photos highly resembling the user anytime and anywhere.

[Project Presentation Video](https://www.youtube.com/watch?v=u7cyPepuSsQ)

## 얼GAN이들

임지윤|정현진|오서영|이현구|김가영|
:-:|:-:|:-:|:-:|:-:
<img src='https://avatars.githubusercontent.com/u/65935803?v=4' height=80 width=80px></img>|<img src='https://avatars.githubusercontent.com/u/67624124?v=4' height=80 width=80px></img>|<img src='https://avatars.githubusercontent.com/u/91474981?v=4' height=80 width=80px></img>|<img src='https://avatars.githubusercontent.com/u/101376814?v=4' height=80 width=80px></img>|<img src='https://avatars.githubusercontent.com/u/102473690?v=4g' height=80 width=80px></img>
[Github](https://github.com/JiyunIm00)|[Github](https://github.com/Hyunjin-Jung)|[Github](https://github.com/ohsy0512)|[Github](https://github.com/gurigoo)|[Github](https://github.com/GGrite)

## Introduction
#### Project Background
- Absence of a natural AI-based passport photo generation service
- Occurrence of temporal, spatial, and cost-related issues when visiting a photo studio

#### Project Objective
- Creating AI-generated passport photos that preserve the individual's facial features as much as possible
- Liberating users from temporal, spatial, and cost constraints by enabling them to generate passport photos freely

#### Key Features
-   Stable diffusion is used to generate style photos for usage
-   ArcFace is employed to select style photos that closely resemble the user's face
-   Watermarking is applied to prevent indiscriminate usage and provide proper attribution

## Dataset
The dataset is located in the "serving/data/" directory. The images in this dataset are used as style photos for the SimSwap model, and the style categories are as follows:
|Style Domain| Gender| Bangs | Hair Style | Style Categories|
:-:|:-:|:-:|:-:|:-:
|Profile|female|||profile/female|
||male|||profile/male|
|Identity|female|O|long|id/female/bangs_long|
||||short|id/female/bangs_short|
|||X|long|id/female/noBangs_long|
||||short|id/female/noBangs_short|
||||tie|id/female/noBangs_tie|
||male|O||id/male/bangs|
|||X||id/male/noBangs|


## Getting Started
#### Installation
```
git clone https://github.com/boostcampaitech5/level3_cv_finalproject-cv-06.git
```
[SimSwap preperation ](https://github.com/neuralchen/SimSwap/blob/main/docs/guidance/preparation.md)

#### Environment
```
wget https://developer.download.nvidia.com/compute/cuda/11.0.3/local_installers/cuda_11.0.3_450.51.06_linux.run
sh cuda_11.0.3_450.51.06_linux.run
apt-get update
apt-get install g++
conda create -n ai-photo-studio
conda activate ai-photo-studio
conda install --file requirements.txt
```	

#### Run
```
streamlit run serving/code/main.py
```

## Results
![results](https://github.com/boostcampaitech5/level3_cv_finalproject-cv-06/assets/67624124/1af0afbc-0564-4364-8a61-0011b17ccc8c)

## License
For academic and non-commercial use only.The whole project is under the CC-BY-NC 4.0 license. See [LICENSE](https://github.com/neuralchen/SimSwap/blob/main/LICENSE) for additional details.

## Acknowledgments
* [SimSwap](https://github.com/neuralchen/SimSwap/tree/main)
* [Insightface](https://github.com/deepinsight/insightface)
* [fast-stable-diffusion](https://github.com/TheLastBen/fast-stable-diffusion)
* [GFPGAN](https://github.com/TencentARC/GFPGAN)
* [invisible-watermark](https://github.com/ShieldMnt/invisible-watermark)
