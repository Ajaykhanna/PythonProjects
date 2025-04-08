# Interactive Franck-Condon model system for a model system
# Show case the effect of Transition energy, relative displacement of the PES and
# Temperature on the Franck Condon Stick Spectra.
# The code is demonstrating the Franck-Condon principle, which describes the intensity
# distribution of vibrational transitions in a molecule during an electronic transition.
import matplotlib.pyplot as plt
import numpy as np

print("Franck-Condon Principle Demonstration")

# Input parameters
E = float(input("Enter electronic transition energy (eV): "))  # Example 2.5
w1 = float(input("Enter ground state vibrational frequency (eV): "))  # Example 0.3
w2 = float(input("Enter excited state vibrational frequency (eV): "))  # Example 0.1
D = float(input("Enter displacement between potentials (angstrom): "))  # Example 0.5
T = float(input("Enter temperature (K): "))  # Example 300.0

# Calculate vibrational energy levels
vib_levels1 = w1 * np.arange(31)
vib_levels2 = w2 * np.arange(31)

# Calculate FC factors
"""
The equation to calculate the Franck-Condon factors (fc) is:

fc = (S * v') * exp(-S * δ2/2) * (δ^(v' - v"))

Where:
S = Frequency ratio (w2/w1) = df
Taking the ratio w2/w1 gives the frequency scaling factor S that is used in the FC equation.

v' = Vibrational quantum number for ground state (vib_levels1)
δ = Displacement between ground and excited state potentials = D
v" = Vibrational quantum number for the excited state (vib_levels2)

Expansion:
(S * v') term: Frequency scaling of ground state vibrational wavefunctions
exp(-S * δ2/2) term: Overlap between ground and excited state wavefunctions
(δ^(v' - v")) term: Shifting of excited state wavefunctions relative to ground state

"""

df = w2 / w1
fc = (
    (df ** vib_levels1[:, None])
    * np.exp(-df * D**2 / 2)
    * (D ** (vib_levels1[:, None] - vib_levels2[None, :]))
)

# Calculate intensities
ints = fc**2 * np.exp(-vib_levels1[:, None] / T)

# Plot
plt.figure()
for i in range(31):
    plt.vlines(E + vib_levels2[i], 0, ints[i].max(), colors="C0", lw=1.5)
plt.xlabel("Energy (eV)")
plt.ylabel("Intensity (a.u.)")
plt.title("Franck-Condon Spectrum")
plt.show()

print("Spectrum displayed!")
