import torch
from torch import nn
import torch.nn.functional as F
from utils.pt.nnModuleBase import nnModuleBase
from utils.pl.plModuleBase import plModuleBase
from libs.basicIO import signal_save, compressor

class D(nnModuleBase):
    def forward(self, **batch):
        batch['x'] = (batch['x'] - .5) / .5
        return super().forward(**batch)

class MVLAB(plModuleBase):
    pass