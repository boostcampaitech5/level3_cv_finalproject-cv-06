import cv2
from PIL import Image
import numpy as np
# import  time
import torch
from torch.nn import functional as F
import torch.nn as nn

import os
from torchvision.transforms.functional import normalize
from torchvision.transforms import Resize, ToTensor, Normalize, Compose
from basicsr.utils import tensor2img

gfpgan_transform_upsample = Compose([
    Resize([int(512), int(512)]),
    # ToTensor(),
    Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
])  

def gfpgan_downsampler(crop_size): 
  return Compose([
    Resize([int(crop_size), int(crop_size)]),
    # ToTensor(),
    # Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
])  

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

os.chdir('/opt/ml/input/code/GFPGAN')
from gfpgan.archs.gfpganv1_clean_arch import GFPGANv1Clean

arch = 'clean'
channel_multiplier = 2
model_name = 'GFPGANv1.3'
model_path = os.path.join('/opt/ml/input/code/GFPGAN/experiments/pretrained_models', model_name + '.pth')

if arch == 'clean':
  gfpgan = GFPGANv1Clean(
      out_size=512,
      num_style_feat=512,
      channel_multiplier=channel_multiplier,
      decoder_load_path=None,
      fix_decoder=False,
      num_mlp=8,
      input_is_latent=True,
      different_w=True,
      narrow=1,
      sft_half=True)

loadnet = torch.load(model_path)
if 'params_ema' in loadnet:
    keyname = 'params_ema'
else:
    keyname = 'params'
gfpgan.load_state_dict(loadnet[keyname], strict=True)
gfpgan.eval()
gfpgan = gfpgan.to(device)


os.chdir('../SimSwap')


def encode_segmentation_rgb(segmentation, no_neck=True):
    parse = segmentation

    face_part_ids = [1, 2, 3, 4, 5, 6, 10, 12, 13] if no_neck else [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 13, 14]
    mouth_id = 11
    # hair_id = 17
    face_map = np.zeros([parse.shape[0], parse.shape[1]])
    mouth_map = np.zeros([parse.shape[0], parse.shape[1]])
    # hair_map = np.zeros([parse.shape[0], parse.shape[1]])

    for valid_id in face_part_ids:
        valid_index = np.where(parse==valid_id)
        face_map[valid_index] = 255
    valid_index = np.where(parse==mouth_id)
    mouth_map[valid_index] = 255
    # valid_index = np.where(parse==hair_id)
    # hair_map[valid_index] = 255
    #return np.stack([face_map, mouth_map,hair_map], axis=2)
    return np.stack([face_map, mouth_map], axis=2)


class SoftErosion(nn.Module):
    def __init__(self, kernel_size=15, threshold=0.6, iterations=1):
        super(SoftErosion, self).__init__()
        r = kernel_size // 2
        self.padding = r
        self.iterations = iterations
        self.threshold = threshold

        # Create kernel
        y_indices, x_indices = torch.meshgrid(torch.arange(0., kernel_size), torch.arange(0., kernel_size))
        dist = torch.sqrt((x_indices - r) ** 2 + (y_indices - r) ** 2)
        kernel = dist.max() - dist
        kernel /= kernel.sum()
        kernel = kernel.view(1, 1, *kernel.shape)
        self.register_buffer('weight', kernel)

    def forward(self, x):
        x = x.float()
        for i in range(self.iterations - 1):
            x = torch.min(x, F.conv2d(x, weight=self.weight, groups=x.shape[1], padding=self.padding))
        x = F.conv2d(x, weight=self.weight, groups=x.shape[1], padding=self.padding)

        mask = x >= self.threshold
        x[mask] = 1.0
        x[~mask] /= x[~mask].max()

        return x, mask


def postprocess(swapped_face, target, target_mask,smooth_mask):
    # target_mask = cv2.resize(target_mask, (self.size,  self.size))

    mask_tensor = torch.from_numpy(target_mask.copy().transpose((2, 0, 1))).float().mul_(1/255.0).cuda()
    face_mask_tensor = mask_tensor[0] + mask_tensor[1]
    
    soft_face_mask_tensor, _ = smooth_mask(face_mask_tensor.unsqueeze_(0).unsqueeze_(0))
    soft_face_mask_tensor.squeeze_()

    soft_face_mask = soft_face_mask_tensor.cpu().numpy()
    soft_face_mask = soft_face_mask[:, :, np.newaxis]

    result =  swapped_face * soft_face_mask + target * (1 - soft_face_mask)
    result = result[:,:,::-1]# .astype(np.uint8)
    return result

def reverse2wholeimage(b_align_crop_tenor_list,swaped_imgs, mats, crop_size, oriimg, logoclass, save_path = '', \
                    no_simswaplogo = False,pasring_model =None,norm = None, use_mask = False):

    def _totensor(array):
        tensor = torch.from_numpy(array)
        img = tensor.transpose(0, 1).transpose(0, 2).contiguous()
        return img.float().div(255)

    gfpgan_transform_downsample = gfpgan_downsampler(crop_size)

    def gfpgan_enhance(img_tensor): 
        # gfp_t = normalize(img_tensor, (0.5, 0.5, 0.5), (0.5, 0.5, 0.5), inplace=False)
        # gfp_t = gfp_t.unsqueeze(0).to(device)
        img_tensor = gfpgan_transform_upsample(img_tensor.unsqueeze(0))
        output = gfpgan(img_tensor,return_rgb=True, weight=0.5)[0]
        # restored_face = tensor2img(output.squeeze(0), rgb2bgr=False, min_max=(-1, 1))
        down_img = tensor2img(gfpgan_transform_downsample(output).squeeze(0), rgb2bgr=True, min_max=(-1, 1))[:,:,[2,1,0]]
        return _totensor(down_img)
    
    swaped_imgs = [gfpgan_enhance(img) for img in swaped_imgs]

    target_image_list = []
    img_mask_list = []
    if use_mask:
        smooth_mask = SoftErosion(kernel_size=17, threshold=0.9, iterations=7).cuda()
    else:
        pass

    # print(len(swaped_imgs))
    # print(mats)
    # print(len(b_align_crop_tenor_list))
    for swaped_img, mat ,source_img in zip(swaped_imgs, mats,b_align_crop_tenor_list):
        swaped_img = swaped_img.cpu().detach().numpy().transpose((1, 2, 0))
        img_white = np.full((crop_size,crop_size), 255, dtype=float)

        # inverse the Affine transformation matrix
        mat_rev = np.zeros([2,3])
        div1 = mat[0][0]*mat[1][1]-mat[0][1]*mat[1][0]
        mat_rev[0][0] = mat[1][1]/div1
        mat_rev[0][1] = -mat[0][1]/div1
        mat_rev[0][2] = -(mat[0][2]*mat[1][1]-mat[0][1]*mat[1][2])/div1
        div2 = mat[0][1]*mat[1][0]-mat[0][0]*mat[1][1]
        mat_rev[1][0] = mat[1][0]/div2
        mat_rev[1][1] = -mat[0][0]/div2
        mat_rev[1][2] = -(mat[0][2]*mat[1][0]-mat[0][0]*mat[1][2])/div2

        orisize = (oriimg.shape[1], oriimg.shape[0])
        if use_mask:
            source_img_norm = norm(source_img)
            source_img_512  = F.interpolate(source_img_norm,size=(512,512))
            out = pasring_model(source_img_512)[0]
            parsing = out.squeeze(0).detach().cpu().numpy().argmax(0)
            vis_parsing_anno = parsing.copy().astype(np.uint8)
            tgt_mask = encode_segmentation_rgb(vis_parsing_anno)
            if tgt_mask.sum() >= 5000:
                # face_mask_tensor = tgt_mask[...,0] + tgt_mask[...,1]
                target_mask = cv2.resize(tgt_mask, (crop_size,  crop_size))
                # print(source_img)
                target_image_parsing = postprocess(swaped_img, source_img[0].cpu().detach().numpy().transpose((1, 2, 0)), target_mask,smooth_mask)
                

                target_image = cv2.warpAffine(target_image_parsing, mat_rev, orisize)
                # target_image_parsing = cv2.warpAffine(swaped_img, mat_rev, orisize)
            else:
                target_image = cv2.warpAffine(swaped_img, mat_rev, orisize)[..., ::-1]
        else:
            target_image = cv2.warpAffine(swaped_img, mat_rev, orisize)
        # source_image   = cv2.warpAffine(source_img, mat_rev, orisize)

        img_white = cv2.warpAffine(img_white, mat_rev, orisize)


        img_white[img_white>20] =255

        img_mask = img_white

        # if use_mask:
        #     kernel = np.ones((40,40),np.uint8)
        #     img_mask = cv2.erode(img_mask,kernel,iterations = 1)
        # else:
        kernel = np.ones((40,40),np.uint8)
        img_mask = cv2.erode(img_mask,kernel,iterations = 1)
        kernel_size = (20, 20)
        blur_size = tuple(2*i+1 for i in kernel_size)
        img_mask = cv2.GaussianBlur(img_mask, blur_size, 0)

        # kernel = np.ones((10,10),np.uint8)
        # img_mask = cv2.erode(img_mask,kernel,iterations = 1)



        img_mask /= 255

        img_mask = np.reshape(img_mask, [img_mask.shape[0],img_mask.shape[1],1])

        # pasing mask

        # target_image_parsing = postprocess(target_image, source_image, tgt_mask)

        if use_mask:
            target_image = np.array(target_image, dtype=np.float64) * 255
        else:
            target_image = np.array(target_image, dtype=np.float64)[..., ::-1] * 255


        img_mask_list.append(img_mask)
        target_image_list.append(target_image)
        

    # target_image /= 255
    # target_image = 0
    img = np.array(oriimg, dtype=np.float64)
    for img_mask, target_image in zip(img_mask_list, target_image_list):
        img = img_mask * target_image + (1-img_mask) * img
        
    final_img = img.astype(np.uint8)
    if not no_simswaplogo:
        final_img = logoclass.apply_frames(final_img)
    final_img = cv2.cvtColor(final_img, cv2.COLOR_BGR2RGB)
    #final_img = np.array(final_img)
    final_img=Image.fromarray(final_img)
    return final_img