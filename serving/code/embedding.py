import sys
sys.path.append("code\SimSwap") #todo : 경로 수정

from myFunc import get_embedding, load_models
from PIL import Image
import os
import numpy as np

# model load
app, model = load_models()

# img
path = "serving/data/id/female/noBangs_long/"
files = os.listdir(path)
files = [file for file in files if file.lower().endswith(('.jpg', '.jpeg', '.png'))]

vectors = np.empty((len(files),512))
for i, file in enumerate(files):
    img_dir = path + file
    embedding_vec = get_embedding(app, model, img_dir)[0]
    vectors[i] = embedding_vec.detach().cpu().numpy()

np.savez(path + "embedding_vectors.npz", data = vectors)



