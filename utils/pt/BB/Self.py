import torch
import numpy as np
import torch.nn as nn
import torch.nn.functional as F
from utils.pt.building_block import BB

class Self(BB): 
    def start(self):
        self.upstream_name = 'Self_x_var_upstream'
        self.Self_fn = str(self.kwargs.get('fn', 'lossfn'))
        self.Self_fn_params = self.kwargs.get('params', None)
        self.Self_input = list(self.kwargs.get('input', []))
        # self.Self_output = list(self.kwargs.get('output', []))
        
        self.Self_inputString = []
        for i in self.Self_input: # x: denotes `upstream` tensor
            if isinstance(i, str):
                self.Self_inputString.append(f'{i}=eBatch.get("{i}", {self.upstream_name})')
            elif isinstance(i, (list, tuple)):
                if len(i) == 1:
                    self.Self_inputString.append(f'{i[0]}={self.upstream_name}')
                elif len(i) == 2:
                    self.Self_inputString.append(f'{i[0]}=eBatch.get("{i[1]}", {self.upstream_name})')
                else:
                    assert False, '`type(i)={}` | It must be `str` or `list or tuple with length 1 or 2`'.format(type(i))
            else:
                assert False, '`type(i)={}` | It must be `str` or `list or tuple with length 1 or 2`'.format(type(i))

        self.Self_inputString = ', '.join(self.Self_inputString)
        
        if isinstance(self.Self_fn_params, dict) and len(self.Self_fn_params) > 0:
            self.Self_inputString = self.Self_inputString + ', **self.Self_fn_params'

        print('@@@@@@@@@@@@', self.Self_fn, self.Self_inputString)
    def forward(self, Self_x_var_upstream, eBatch):
        print(self.Self_fn, Self_x_var_upstream)
        fn = getattr(eBatch['Self'], self.Self_fn)
        return eval(f'fn({self.Self_inputString})')