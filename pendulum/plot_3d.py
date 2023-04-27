import numpy as np
import math
import pdb
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from mpl_toolkits.axes_grid1 import make_axes_locatable


# load data from CSV file
data = np.genfromtxt('pendulum_8s.csv', delimiter=',', skip_header=1)

# extract x, y, and t values from data
x = data[:, 0]
y = 640-data[:, 1]
# pdb.set_trace()
t = (data[:, 2]-data[0,2])/21

v = np.zeros(len(x))
for idx in range(len(x)-1):
    dx = abs(x[idx+1]-x[idx])
    dy = abs(y[idx+1]-y[idx])
    dt = t[idx+1]-t[idx]
    d = math.sqrt(dx**2+dy**2)
    v[idx] = d/(dt)
    # print(f" *** dx: {dx} | dy {dy} | dt {round(dt,3)} | v: {v[idx]}***")
    if dx == 0 and dy == 0:
        # pdb.set_trace()
        v[idx] = v[idx-1]
v[-1] = v[idx]


window_size = 20
weights = np.repeat(1.0, window_size) / window_size
s_v = np.convolve(v, weights, mode='valid')
lsv = len(s_v)

fig = plt.figure() # figsize=(4,4)
plt.plot(t,v, color='k')
plt.plot(t[0:lsv],s_v, color='r')
plt.savefig("velocity.png", dpi=300, bbox_inches='tight')
plt.clf()


# create 3D plot
scale_3d = 6
fig = plt.figure(figsize=(0.5*scale_3d,1*scale_3d)) # figsize=(4,4)
ax = fig.add_subplot(111,projection='3d')
ratio_t_xy = 2.5
ax.set_box_aspect([ratio_t_xy,1,1])
ax.view_init(elev=22, azim=-50)
plt.grid(True)
scatter = ax.scatter(t[0:lsv],x[0:lsv],y[0:lsv],c=s_v, cmap='gnuplot', s=6)
cbar = plt.colorbar(scatter, orientation='vertical', pad=0.08, shrink=0.5)
cbar.set_label('Speed [px/s]', labelpad = -20)
cbar.set_ticks([min(s_v), max(s_v)])
cbar.set_ticklabels(['\nSlow', 'Fast\n'])
# cbar.ax.tick_params(which='both', length=0, width=0,  labelsize=0)
plt.subplots_adjust(right=4)

nb_ticks = 8
ax.minorticks_on()
ax.xaxis.set_minor_locator(plt.MultipleLocator(max(t)/(ratio_t_xy*nb_ticks)))
ax.yaxis.set_minor_locator(plt.MultipleLocator(640/nb_ticks))
ax.zaxis.set_minor_locator(plt.MultipleLocator(640/nb_ticks))

# set axis labels
ax.set_xlabel('Time [s]')
ax.set_ylabel('   x [px]')
ax.set_zlabel('y [px]')
# pdb.set_trace()

ax.set_xticks(np.linspace(0,int(max(t))+1, int(max(t))+2))
ax.set_yticks([0, 400])# Set custom string ticks on the x-axis
ax.set_zticks([0, 320, 640])
ax.set_yticklabels(['     0', '320'])
ax.set_zticklabels(['640', '320', '0'])
ax.set_xlim([0,int(max(t))+1])

# show plot
plt.savefig("trajectory_3D.png", dpi=600, bbox_inches='tight')
# plt.show()
plt.clf()

# pdb.set_trace()

# create 2D plot
fig = plt.figure(figsize=(5,4)) # figsize=(4,4)
ax = fig.add_subplot(111)
plt.grid(True)
scatter = ax.scatter(x[0:lsv], y[0:lsv], c=t[0:lsv], cmap='viridis', s=6)

# set colorbar and labels
cbar = plt.colorbar(scatter)
cbar.set_label('Time [s]')
ax.set_xlabel('x coordinate [px]')
ax.set_ylabel('y coordinate [px]')
ax.set_xlim([0,640])
ax.set_ylim([0,640])

# show plot
plt.savefig("trajectory_2D.png", dpi=300, bbox_inches='tight')
# plt.show()