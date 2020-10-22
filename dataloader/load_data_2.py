# -*- coding: utf-8 -*-
import torchvision.transforms as transforms
import os
import torch
import numpy as np
from torch.utils.data import Dataset, DataLoader
import time
import cv2
from scipy.interpolate import griddata
from tutils import *
from torch import nn
from dataloader import data_process, print_img, uv2bw


os.environ["CUDA_VISIBLE_DEVICES"] = "4"

ori_image_dir = 'data_2000/Mesh_Film/npy/'

EPOCH = 1
test_BATCH_SIZE = 100


class filmDataset_old(Dataset):
    """
    Using with Dataset generated by Qiyuan / Liuli
    """
    def __init__(self, npy_dir, load_mod="all", npy_dir_2=None):
        self.npy_dir = npy_dir
        self.npy_list = np.array([x.path for x in os.scandir(npy_dir) if x.name.endswith(".npy")])
        print("Dataset Length: ", len(self.npy_list))
        if npy_dir_2!=None:
            self.npy_list_2 = np.array([x.path for x in os.scandir(npy_dir_2) if x.name.endswith(".npy")])
            self.npy_list = np.append(self.npy_list, self.npy_list_2)
        self.npy_list.sort()
        self.load_mod = load_mod

    def __getitem__(self, index):
        npy_path = self.npy_list[index]
        """loading"""
        # data = np.load(self.npy_dir + '/' + npy_name, allow_pickle=True)[()]
        data = np.load(npy_path, allow_pickle=True)[()]
        ori = data['ori']
        ab = data['ab']
        # bmap = data['bmap']
        depth = data['depth']
        normal = data['normal']
        uv = data['uv']
        cmap = data['cmap']
        background = data['background']
        
        if self.load_mod == "all":
            return torch.from_numpy(ori), \
               torch.from_numpy(ab), \
               torch.from_numpy(depth), \
               torch.from_numpy(normal), \
               torch.from_numpy(cmap), \
               torch.from_numpy(uv), \
               torch.from_numpy(background)
        # ori_1080 = data['ori_1080']

        elif self.load_mod == "uvbw":
            ### ----------- Generate BW map ---------------
            uv_2 = data_process.reprocess_auto(uv.transpose((1,2,0)), "uv")
            mask = data_process.reprocess_auto(background.transpose((1,2,0)), "background")
            bw = uv2bw.uv2backward_trans_3(uv_2, mask)
            bw = data_process.process_auto(bw, "bw")
            bw = bw.transpose((2,0,1))
            ### --------------------------------------------
            return  torch.from_numpy(cmap), \
                torch.from_numpy(uv), \
                torch.from_numpy(bw), \
               torch.from_numpy(background)

        elif self.load_mod == "test_uvbw_mapping":
            ### ----------- Generate BW map ---------------
            uv_2 = data_process.reprocess_auto(uv.transpose((1,2,0)), "uv")
            mask = data_process.reprocess_auto(background.transpose((1,2,0)), "background")
            bw = uv2bw.uv2backward_trans_3(uv_2, mask)
            bw = data_process.process_auto(bw, "bw")
            bw = bw.transpose((2,0,1))
            ### --------------------------------------------
            return  torch.from_numpy(cmap), \
                torch.from_numpy(uv), \
                torch.from_numpy(bw), \
               torch.from_numpy(background), \
               torch.from_numpy(ori)

    def __len__(self):
        return len(self.npy_list)