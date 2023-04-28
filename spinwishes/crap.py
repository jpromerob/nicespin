

import numpy as np


array_sz = 30
in_base = np.linspace(6.6e5,8e5,array_sz)
in_noise = np.random.randint(1, 11, size=array_sz)*1e2

out_deal = np.random.randint(200000, 215000, size=array_sz)

for i in range(array_sz):
    print(f"{5629256},{int(in_base[i]+in_noise[i])},{out_deal[i]}")