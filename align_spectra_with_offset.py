# The code creates a normalized plot using the matplotlib library in Python. It imports the necessary
# libraries (matplotlib.pyplot, numpy, and sys) and defines a conversion factor from inverse
# centimeters to electron volts. Plots the reference data, which is the first argument and 
#, then plot the remaining spectra arguments 2 and onwards and align them with respect to the 
# desired offset. Here, it aligns with the first index of the x-axis of the reference data. 
import matplotlib.pyplot as plt
import numpy as np
import sys

# Conversion factor  
invcm_to_eV = 1.0/8065.54429
offset = int(0)

# Set up plot
fig, axs = plt.subplots(1, 2, figsize=(10,5))
filename = str(sys.argv[1])
ref_data = np.loadtxt(f'{filename}', skiprows=7, usecols=(0,1,2))
ref_data[:,0] = ref_data[:,0] * invcm_to_eV

# Plot reference
axs[0].plot(ref_data[:,0], ref_data[:,1]/ref_data[:,1].max(), label='Explicit')
axs[1].plot(ref_data[:,0], ref_data[:,2]/ref_data[:,2].max(), label='Explicit')

# Process each file provided as command line argument 
for i, filename in enumerate(sys.argv[2:]):

    # Load data
    data = np.loadtxt(filename, skiprows=7, usecols=(0,1,2))
    
    # Convert x-axis to eV
    data[:,0] = data[:,0] * invcm_to_eV
    
    # Normalize y-axis
    data[:,1] /= data[:,1].max() 
    data[:,2] /= data[:,2].max()

    label = f'File {i+1}'

    # Plot 0K data
    if i == 0:
       # Reference plot  
       axs[0].plot(data[:,0], data[:,1], label=label)
    else:
       # Align to reference 
       offset = data[offset,offset] - ref_data[offset,offset]
       axs[0].plot(data[:,0] - offset, data[:,1]/ref_data[0,1], label=label)

    # Plot 300K data
    if i == 0:
       # Reference plot
       axs[1].plot(data[:,0], data[:,2], label=label)  
    else:
       # Align to reference
       offset = data[0,0] - ref_data[0,0]
       axs[1].plot(data[:,0] - offset, data[:,2]/ref_data[0,2], label=label)
        
# Add axes labels  
axs[0].set_xlabel('Energy (eV)')
axs[0].set_ylabel('Intensity')
axs[1].set_xlabel('Energy (eV)')
axs[1].set_ylabel('Intensity')

# Add legend
axs[0].legend()
axs[1].legend() 

# Set axes limits
axs[0].set_ylim(0, 1.1) 
axs[1].set_ylim(0, 1.1)

# Set number of ticks
axs[0].locator_params(axis='x', nbins=5)
axs[1].locator_params(axis='x', nbins=5)

# Save figure
fig.tight_layout()
fig.savefig('plot.png', dpi=300)
