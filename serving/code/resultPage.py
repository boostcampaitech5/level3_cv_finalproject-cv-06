import streamlit as st
from PIL import Image
import io
import os
import sys
#import insightface
import numpy as np

sys.path.append('/opt/ml/input/code/SimSwap')
import cv2
import torch
import fractions
import numpy as np
from PIL import Image
import torch.nn.functional as F
from torchvision import transforms
from models.models import create_model
from options.infer_options import TestOptions
from insightface_func.face_detect_crop_single import Face_detect_crop
from util.reverse2original_infer import reverse2wholeimage
import os
from util.add_watermark import watermark_image
from util.norm import SpecificNorm
from parsing_model.model import BiSeNet


opt = TestOptions().parse()

def image_to_bytes(image):
    img_byte_array = io.BytesIO()
    image.save(img_byte_array, format = "JPEG")
    return img_byte_array.getvalue()
'''
@st.cache_resource
def load_insight_model():
    model = insightface.app.FaceAnalysis()
    model.prepare(ctx_id=0)
    return model
'''

@st.cache_resource
def load_simswap_model():
    model = create_model(opt)
    model.eval()
    return model

@st.cache_resource
def load_app():
    app = Face_detect_crop(name='antelope', root='/opt/ml/input/code/SimSwap/insightface_func/models')
    app.prepare(ctx_id= 0, det_thresh=0.6, det_size=(640,640),mode='None')
    return app

@st.cache_data
def load_embedding_vectors(path):
    dir = os.path.join(path, "embedding_vectors.npz")
    ref_vectors = np.load(dir)['data']
    return ref_vectors

def get_reference_images(domain, gender, src):
    crop_size =opt.crop_size
    transformer_Arcface = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    # dataset path
    path = "/opt/ml/input/serving/data" # todo : domain + gender에 따라 path 설정
    files = os.listdir(path)
    files = [file for file in files if file.lower().endswith(('.jpg', '.jpeg', '.png'))]

    # ref 이미지 embedding vector 읽어오기
    ref_vectors = load_embedding_vectors(path)
    '''
    # src embedding vector 구하기
    model = load_insight_model()
    src = np.array(Image.open(src))
    src_vector = model.get(src)[0]['embedding']
    '''
    # src embedding vector 구하기
    model = load_simswap_model()
    app = load_app()
    #app = Face_detect_crop(name='antelope', root='/opt/ml/input/code/SimSwap/insightface_func/models')
    #app.prepare(ctx_id= 0, det_thresh=0.6, det_size=(640,640),mode='None')
    
    #####pil 2 img##
    src = np.array(Image.open(src))
    pic_a = src
    pic_a=np.array(pic_a)
    img_a_whole=cv2.cvtColor(pic_a, cv2.COLOR_RGB2BGR)
    ###############
    #img_a_whole = cv2.imread(pic_a)
    with torch.no_grad():
        img_a_align_crop, _ = app.get(img_a_whole,crop_size)
        img_a_align_crop_pil = Image.fromarray(cv2.cvtColor(img_a_align_crop[0],cv2.COLOR_BGR2RGB))
        img_a = transformer_Arcface(img_a_align_crop_pil)
        img_id = img_a.view(-1, img_a.shape[0], img_a.shape[1], img_a.shape[2])
        img_id = img_id.cuda()
        img_id_downsample = F.interpolate(img_id, size=(112,112))
        latend_id = model.netArc(img_id_downsample)
        latend_id = F.normalize(latend_id, p=2, dim=1)
        src_vector = latend_id
    # cosine similarity
    src_vector = src_vector.to('cpu')[0]
    similarities = np.dot(ref_vectors, src_vector) / (np.linalg.norm(ref_vectors, axis=1) * np.linalg.norm(src_vector))

    # 가장 유사한 이미지 3개 
    top3_img_idx = np.argsort(similarities)[::-1][:3]

    results = []
    for idx in top3_img_idx:
        file = files[idx]
        img = Image.open(os.path.join(path, file))
        results.append(img)

    return results

def get_result_images(src, refs):
    crop_size =opt.crop_size
    #refs : Image.open 객체 리스트
    #src : 사용자가 올린 이미지
    #output : PIL.Image
    # todo : simswap inference
    def lcm(a, b): return abs(a * b) / fractions.gcd(a, b) if a and b else 0

    transformer_Arcface = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    def _totensor(array):
        tensor = torch.from_numpy(array)
        img = tensor.transpose(0, 1).transpose(0, 2).contiguous()
        return img.float().div(255)

    results = []

    model = load_simswap_model()
    spNorm =SpecificNorm()
    app = load_app()
    #app = Face_detect_crop(name='antelope', root='/opt/ml/input/code/SimSwap/insightface_func/models')
    #app.prepare(ctx_id= 0, det_thresh=0.6, det_size=(640,640),mode='None')
    #####pil 2 img##
    src = np.array(Image.open(src))
    pic_a = src
    pic_a=np.array(pic_a)
    img_a_whole=cv2.cvtColor(pic_a, cv2.COLOR_RGB2BGR)
    ###############
    for ref in refs:
        with torch.no_grad():
            img_a_align_crop, _ = app.get(img_a_whole,crop_size)
            img_a_align_crop_pil = Image.fromarray(cv2.cvtColor(img_a_align_crop[0],cv2.COLOR_BGR2RGB))
            img_a = transformer_Arcface(img_a_align_crop_pil)
            img_id = img_a.view(-1, img_a.shape[0], img_a.shape[1], img_a.shape[2])

            # convert numpy to tensor
            img_id = img_id.cuda()

            #create latent id
            img_id_downsample = F.interpolate(img_id, size=(112,112))
            latend_id = model.netArc(img_id_downsample)
            latend_id = F.normalize(latend_id, p=2, dim=1)

            ############## Forward Pass ######################
            pic_b = ref
            #PIL to cv2
            pic_b=np.array(pic_b)
            img_b_whole=cv2.cvtColor(pic_b, cv2.COLOR_RGB2BGR)

            img_b_align_crop_list, b_mat_list = app.get(img_b_whole,crop_size)
            # detect_results = None
            swap_result_list = []

            b_align_crop_tenor_list = []

            for b_align_crop in img_b_align_crop_list:

                b_align_crop_tenor = _totensor(cv2.cvtColor(b_align_crop,cv2.COLOR_BGR2RGB))[None,...].cuda()

                swap_result = model(None, b_align_crop_tenor, latend_id, None, True)[0]
                swap_result_list.append(swap_result)
                b_align_crop_tenor_list.append(b_align_crop_tenor)

            if opt.use_mask:
                n_classes = 19
                net = BiSeNet(n_classes=n_classes)
                net.cuda()
                save_pth = os.path.join('/opt/ml/input/code/SimSwap/parsing_model/checkpoint', '79999_iter.pth')
                net.load_state_dict(torch.load(save_pth))
                net.eval()
            else:
                net =None
            logoclass = False
            result = reverse2wholeimage(b_align_crop_tenor_list, swap_result_list, b_mat_list, crop_size, img_b_whole, logoclass, \
                os.path.join(opt.output_path, 'result_whole_swapsingle.jpg'), opt.no_simswaplogo,pasring_model =net,use_mask=opt.use_mask, norm = spNorm)
            results.append(result)
    return results

def reupload_callback():
    del st.session_state["src"]
    st.session_state.page = "upload_page"

def home_callback():
    del st.session_state["src"]
    st.session_state.page = "home_page"

def show_resultPage():

    # side bar
    with st.sidebar:
        st.markdown("""
            <center>
            👔스타일 선택

            ↓

            📂 사진 업로드

            ↓

            <span style="font-family: 'Arial'; font-size: 18px; font-weight: bold; color: #ff0000;">🎉 결과 확인</span>
            </center>
        """, unsafe_allow_html=True)

    # 설명
    description = st.container()
    description.write("result 관련 설명...")
    
    st.divider()

    # reference 이미지
    refs = get_reference_images(st.session_state.domain, st.session_state.gender, st.session_state.src)

    # result 이미지
    results = get_result_images(st.session_state.src, refs)
    print(len(results))


    cols = st.columns(3)
    for i in range(3):
        col = cols[i]
        
        # image
        col.image(results[i])

        # download button
        img_byte = image_to_bytes(results[i])
        col.download_button("다운로드", data=img_byte, file_name=f"{st.session_state.domain}_{st.session_state.gender}_{i}.jpg", use_container_width=True)


    # button
    buttons = st.container()
    reupload_button = buttons.button("이미지 다시 업로드하기", use_container_width=True, on_click=reupload_callback)
    home_button = buttons.button("처음으로 돌아가기", use_container_width=True, on_click=home_callback)

