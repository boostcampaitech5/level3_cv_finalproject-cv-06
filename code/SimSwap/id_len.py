'''
Author: Naiyuan liu
Github: https://github.com/NNNNAI
Date: 2021-11-23 17:03:58
LastEditors: Naiyuan liu
LastEditTime: 2021-11-24 19:19:43
Description: 
'''

import os
import glob

if __name__ == '__main__':
    data_path = '/opt/ml/input/data/train_data'
    train_path = '/opt/ml/input/data/crop_ali_224_new_data'

    train_folders = glob.glob(data_path + '/*')
    a = []
    for i in train_folders:
        a.append(len(os.listdir(i)))
        if len(os.listdir(i))==1:
            print(i)
    a.sort()
    #print(a)

