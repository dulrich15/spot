"""
Matplotlib Animation Example

author: Jake Vanderplas
email: vanderplas@astro.washington.edu
website: http://jakevdp.github.com
license: BSD
Please feel free to use and modify this, but keep the above information. Thanks!
"""

from __future__ import division

import numpy as np
from numpy import sin, cos

from scipy import integrate
from scipy.fftpack import fft,ifft
from scipy.spatial.distance import pdist, squareform

from matplotlib import pyplot as plt
from matplotlib import animation

fig = plt.figure()

%s

ani = animation.FuncAnimation(fig, animate, init_func=init, frames=200, interval=20, blit=True)
ani.save('temp.mp4', fps=30, extra_args=['-vcodec', 'libx264', '-pix_fmt', 'yuv420p'])
