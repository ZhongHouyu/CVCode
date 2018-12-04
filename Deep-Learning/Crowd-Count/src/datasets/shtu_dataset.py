# -*- coding:utf-8 -*-
# ------------------------
# written by Songjian Chen
# 2018-10
# ------------------------
from torch.utils.data import Dataset
import os
import skimage.io
import skimage.transform
from skimage.color import grey2rgb
import numpy as np
import cv2


def get_data(mode="train", zoom_size=4):
    # index train_image ground_truth
    data_path = "./data/shtu_dataset/preprocessed/{0}".format(mode) \
        if mode == "train" else "./data/shtu_dataset/original/part_A_final/test_data/images/"
    ground_truth = "./data/shtu_dataset/preprocessed/{0}_density".format(mode) \
        if mode == "train" else "./data/shtu_dataset/preprocessed/test_density/"
    data_files = [filename for filename in os.listdir(data_path) if os.path.isfile(os.path.join(data_path, filename))]
    # double the training set
    # data_files *= 2
    result = []
    num_files = len(data_files)
    index = 0
    for file_name in data_files:
        # load images
        img = skimage.io.imread(os.path.join(data_path, file_name), as_grey=False).astype(np.float32)
        img = grey2rgb(img)
        ht = img.shape[0]
        wd = img.shape[1]
        ht_1 = (ht // 8) * 8
        wd_1 = (wd // 8) * 8
        img = cv2.resize(img, (wd_1, ht_1), interpolation=cv2.INTER_AREA)
        # load densities
        den = np.load(os.path.join(ground_truth, os.path.splitext(file_name)[0] + '.npy')).astype(np.float32)
        ht_1 = ht_1 // zoom_size
        wd_1 = wd_1 // zoom_size
        den = cv2.resize(den, (wd_1, ht_1), interpolation=cv2.INTER_AREA)
        den *= ((wd * ht) // (wd_1 * ht_1))
        index += 1
        # print load speed
        if index % 100 == 0 or index == len(data_files):
            print("load {0}/{1} images ".format(index, num_files))
        result.append([img, den])

    return result


class ShanghaiTechDataset(Dataset):

    def __init__(self, mode="train", zoom_size=4, transform=None):
        self.zoom_size = zoom_size
        self.dataset = get_data(mode=mode, zoom_size=zoom_size)
        self.transform = transform

    def __getitem__(self, item):
        img, den = self.dataset[item]
        if self.transform is not None:
            img = self.transform(img)
        return img, den

    def __len__(self):
        return len(self.dataset)