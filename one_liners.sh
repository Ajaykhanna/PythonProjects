#!/bin/bash

# This script performs a one-liner analysis of the dataset 'acn_sE0.npy' and saves a histogram with statistics.
python -c "import numpy as np; import matplotlib.pyplot as plt; d=np.load('acn_sE0.npy').flatten(); \
stats = (f'Mean: {d.mean():.2f}\nStd: {d.std():.2f}\nMin: {d.min():.2f}\nMax: {d.max():.2f}\nDrift: {np.diff(d).mean():.2e}'); \
plt.hist(d, bins=50, label=stats); plt.legend(); plt.title('Dataset Analysis'); plt.savefig('histogram.png')"

# Alternatively, if you want to keep it strictly to one line without the stats in the legend:
python -c "import numpy as np; import matplotlib.pyplot as plt; data=np.load('acn_sE0.npy'); plt.hist(data.flatten(), bins=50); plt.title('Data Histogram'); plt.savefig('histogram.png')"

# To print the statistics to the console:
python -c "import numpy as np; data=np.load('acn_sE0.npy'); print(data.min()), print(data.max()), print(data.mean()), print(data.std())"
