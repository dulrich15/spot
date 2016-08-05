from __future__ import division

import numpy as np
from numpy import sin, cos

from scipy import integrate
from scipy.fftpack import fft,ifft
from scipy.spatial.distance import pdist, squareform

import matplotlib
from matplotlib import pyplot as plt

from mpl_toolkits.mplot3d import Axes3D     # Import 3D plotting tools.
from scipy.special import jn                # Import Bessel function.

# matplotlib.rcParams['xtick.direction'] = 'out'
# matplotlib.rcParams['ytick.direction'] = 'out'

%s

plt.savefig('temp.png')
