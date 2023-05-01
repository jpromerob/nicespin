import numpy as np
import math
import time
import argparse
import pdb
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from mpl_toolkits.axes_grid1 import make_axes_locatable



def parse_args():

    parser = argparse.ArgumentParser(description='Pendulum Trajectory Plotter')

    parser.add_argument('-f', '--filename', type=str, help="Filename", default="data/trajectory.csv")  
    parser.add_argument('-m', '--mode', type=str, help="pixels or meters", default="pixels")  
    parser.add_argument('-tsp', '--sz-in-px', type=int, help="Target Size in Pixels", default=37)   
    parser.add_argument('-tsm', '--sz-in-m', type=float, help="Target Size in Meters", default=0.05)    

    return parser.parse_args()
   

if __name__ == '__main__':


    args = parse_args()

    target_diameter_m = args.sz_in_m
    target_diameter_px = args.sz_in_px

    if args.mode == 'pixels':
        mode_scaler = 1
        xy_units = 'px'
        v_units = 'px/s'
    elif args.mode == 'meters':
        mode_scaler = target_diameter_m/target_diameter_px
        xy_units = 'm'
        v_units = 'm/s'
    else:
        print("Wrong mode!")
        quit()

    # load data from CSV file
    data = np.genfromtxt(args.filename, delimiter=',', skip_header=1)

    # extract x, y, and t values from data
    x = data[:, 0]
    y = 640-data[:, 1]
    # pdb.set_trace()
    t = (data[:, 2]-data[0,2])/21


    dx = np.zeros(len(x))
    dy = np.zeros(len(x))
    d = np.zeros(len(x))
    dt = np.zeros(len(x))
    v = np.zeros(len(x))
    for idx in range(len(x)-1):
        dx[idx] = abs(x[idx+1]-x[idx])
        dy[idx] = abs(y[idx+1]-y[idx])
        dt[idx] = t[idx+1]-t[idx]
        d[idx] = math.sqrt(dx[idx]**2+dy[idx]**2)
        v[idx] = d[idx]/(dt[idx])
        # print(f" *** dx: {dx} | dy {dy} | dt {round(dt,3)} | v: {v[idx]}***")
        if dx[idx] == 0 and dy[idx] == 0:
            # pdb.set_trace()
            v[idx] = v[idx-1]
    v[-1] = v[idx]

    x = x*mode_scaler
    y = y*mode_scaler
    v = v*mode_scaler
    
    if args.mode == 'pixels':
        max_xy = 640
    else:
        max_xy = math.ceil(max(max(x),max(y)))

    # pdb.set_trace()

    window_size = 20
    weights = np.repeat(1.0, window_size) / window_size
    s_v = np.convolve(v, weights, mode='valid')
    lsv = len(s_v)

    fig = plt.figure() # figsize=(4,4)
    plt.plot(t,v, color='k')
    plt.plot(t[0:lsv],s_v, color='r')
    plt.savefig(f'images/Velocity_{xy_units}_per_s.png', dpi=300, bbox_inches='tight')
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
    cbar.set_label(f'Velocity [{v_units}]', labelpad = 5)
    # cbar.set_ticks([min(s_v), max(s_v)])
    # cbar.set_ticklabels(['\nSlow', 'Fast\n'])
    # cbar.ax.tick_params(which='both', length=0, width=0,  labelsize=0)
    plt.subplots_adjust(right=4)

    nb_ticks = 10
    # ax.minorticks_on()
    ax.xaxis.set_minor_locator(plt.MultipleLocator(10/(2*nb_ticks)))

    # set axis labels
    ax.set_xlabel('\nTime [s]')

    ax.set_xticks(np.linspace(0,int(max(t))+1, int(max(t))+2))
    ax.set_yticks([])
    ax.set_zticks([])
    
    if args.mode == 'pixels':
        ax.yaxis.set_minor_locator(plt.MultipleLocator(640/nb_ticks))
        ax.zaxis.set_minor_locator(plt.MultipleLocator(640/nb_ticks))
        ax.set_yticks([0, 640*0.6])# Set custom string ticks on the x-axis
        ax.set_zticks([0, 320, 640])
        ax.set_yticklabels(['0', '320'])
        ax.set_zticklabels([f'640', '320', '0'])
    else:
        ax.yaxis.set_minor_locator(plt.MultipleLocator(max_xy/nb_ticks))
        ax.zaxis.set_minor_locator(plt.MultipleLocator(max_xy/nb_ticks))
        ax.set_zticks([0, max_xy*0.5, max_xy])# Set custom string ticks on the x-axis
        ax.set_yticks([0, round(max_xy*0.6,1)])
        ax.set_zticklabels(['0', f'{round(max_xy/2,1)}', f'{max_xy}'])
        ax.set_yticklabels([f'{int(max_xy)}', f'{round(max_xy/2,1)}'])


    ax.set_ylabel(f'   x [{xy_units}]')
    ax.set_zlabel(f'y [{xy_units}]')
    ax.set_xlim([0, math.ceil(max(t))])
    ax.set_ylim([0, 1])
    ax.set_zlim([0, 1])

    # show plot
    plt.savefig(f'images/Trajectory_3D_{xy_units}_per_s.png', dpi=600, bbox_inches='tight')
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
    ax.set_xlabel(f'x [{xy_units}]')
    ax.set_ylabel(f'y [{xy_units}]')
    ax.set_xlim([0, max_xy])
    ax.set_ylim([0, max_xy])

    # show plot
    plt.savefig(f'images/Trajectory_2D_{xy_units}_per_s.png', dpi=300, bbox_inches='tight')
    # plt.show()