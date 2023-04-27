import numpy as np
import math
import matplotlib.pyplot as plt

def make_kernel_circle(r, k_sz,weight, kernel):
    # pdb.set_trace()
    var = int((k_sz+1)/2-1)
    a = np.arange(0, 2 * math.pi, 0.01)
    dx = np.round(r * np.sin(a)).astype("uint32")
    dy = np.round(r * np.cos(a)).astype("uint32")
    kernel[var + dx, var + dy] = weight


scaler = 0.08
k_sz = 39
pos_w = 0.8
neg_w = -1.0
print(k_sz)
kernel = np.zeros((k_sz, k_sz))
make_kernel_circle(0.46*k_sz, k_sz, pos_w*scaler, kernel)
make_kernel_circle(0.41*k_sz, k_sz, neg_w*scaler, kernel)
make_kernel_circle(0.36*k_sz, k_sz, pos_w*scaler, kernel)
make_kernel_circle(0.26*k_sz, k_sz, neg_w*scaler, kernel)


fig, ax = plt.subplots(figsize=(4,4))

ax.set_xticks([])
ax.set_yticks([])

plt.imshow(kernel, interpolation='nearest', cmap='binary')
plt.savefig("kernel.png", dpi=300, bbox_inches='tight')