# Download the required Data
!wget https://ucmerced.box.com/shared/static/1qivuf3teov6qm9oealjtrjgw1glpbwa.gz \ -O sample_data/f28_data.tar.gz && mkdir sample_data/f28_data && \
tar -zxvf sample_data/f28_data.tar.gz -C sample_data/f28_data

import numpy as np
import plotly.io as pio
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# Changing Default Template to Plotly White
pio.templates.default = "plotly_white"

# Constants
FWHM_0K = np.zeros(4)
FWHM_300K = np.zeros(4)
label = ["Gas", "PCM", "Strip", "Explicit"] # DMSO

# Conversion Factors
INVCM_TO_EV = float(0.00012398)

# File Paths
PATHS = [
    'sample_data/f28_data/nbdnh2_gas_frame28_vibronic_ems.dat',
    'sample_data/f28_data/nbdnh2_pcm_frame28_vibronic_ems.dat',
    'sample_data/f28_data/nbdnh2_stripped_dmso_frame28_vibronic_ems.dat', # exAIMD
    'sample_data/f28_data/nbdnh2_frame28_fc_qm47_traj2_run3.dat' # exAIMD
]

# Important Functions
# Load and process data
def load_process_data(paths):
    '''
    The `load_process_data` function is responsible for loading and
    processing the data from the specified file paths.
    '''
    data = [np.loadtxt(path, skiprows=7, usecols=(0,1,2)) for path in paths]
    curves_0K = [(d[:,0]*INVCM_TO_EV, d[:,1]/d[:,1].max()) for d in data]
    curves_300K = [(d[:,0]*INVCM_TO_EV, d[:,2]/d[:,2].max()) for d in data]
    return curves_0K, curves_300K

# FWHM Function
def FWHM(x: np.ndarray, y: np.ndarray, height: float = 0.5) -> float:
    '''
    The `FWHM` function is calculating the full width at half maximum
    (FWHM) of a given curve represented by `x` and `y` arrays.
    The function takes in three arguments: `x` and `y` arrays
    representing the curve, and `height` which is the fraction of the
    maximum height at which the FWHM is calculated (default value is 0.5).
    '''

    height_half_max = np.max(y) * height
    index_max = np.argmax(y)
    x_low = np.interp(height_half_max, y[:index_max+1], x[:index_max+1])
    x_high = np.interp(height_half_max, np.flip(y[index_max:]), np.flip(x[index_max:]))

    return abs(x_high - x_low)

# Align curves function
def align_curves(curves):
    '''
    The `align_curves` function is used to align the x-axis of the curves.
    It takes in a list of curves, where each curve is represented by a tuple of x and y arrays.
    '''
    x_ref = curves[0][0][0]
    return [(c[0]-c[0][0]+x_ref, c[1]) for c in curves]

# Load Data And Align Curves
curves_0K, curves_300K = load_process_data(PATHS)
curves_0K = align_curves(curves_0K)
curves_300K = align_curves(curves_300K)

# Compute FWHM of All
for idx, curve_0K in enumerate(curves_0K):
    FWHM_0K[idx] = FWHM(curve_0K[0], curve_0K[1])

for idx, curve_300K in enumerate(curves_300K):
    FWHM_300K[idx] = FWHM(curve_300K[0], curve_300K[1])

# Create subplots
fig = make_subplots(rows=1, cols=2,
                    subplot_titles=("Temperature: 0K", "Temperature: 300K"))

# Define color map
color_map = {"Gas": "#A084E8",
             "PCM": "orange",
             "Strip": "red",
             "Explicit": "black"}

# Add traces for 0K temperature
for idx, curve in enumerate(curves_0K):
    fig.add_trace(go.Scatter(x=curve[0], y=curve[1],
                             mode='lines',
                             name=f'{label[idx]}: {FWHM_0K[idx]:.3f}',
                             line=dict(color=color_map[label[idx]], dash='dash')),
                             row=1, col=1)

# Add traces for 300K temperature
for idx, curve in enumerate(curves_300K):
    fig.add_trace(go.Scatter(x=curve[0], y=curve[1],
                             mode='lines',
                             name=f'{label[idx]}: {FWHM_300K[idx]:.3f}',
                             line=dict(color=color_map[label[idx]])),
                             row=1, col=2)

# Update xaxis titles and range
fig.update_xaxes(title_text="Energy (eV)", range=[2.6, 3.8],  nticks=6, row=1, col=1)
fig.update_xaxes(title_text="Energy (eV)", range=[2.6, 3.8],  nticks=6, row=1, col=2)

# Update yaxis titles and range
fig.update_yaxes(title_text="Intensity", range=[0.0, 1.1], nticks=4, row=1, col=1)
fig.update_yaxes(range=[0.0, 1.1], nticks=3, row=1, col=2)

# Add layout
#fig.update_layout(height=600, width=1200,
#                  title_text="Energy vs Intensity")
fig.to_image('allign_offset_plots.png', scale=3)
fig.show()
