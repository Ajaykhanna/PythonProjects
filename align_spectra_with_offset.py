import matplotlib.pyplot as plt
import numpy as np
import sys
import argparse
import os

# Conversion factor
INVCM_TO_EV = 1.0 / 8065.54429


def load_spectrum(filename):
    """Loads spectral data from a file, skipping header rows."""
    try:
        # skiprows=7 assumes a fixed header size. Consider making this flexible if needed.
        data = np.loadtxt(filename, skiprows=7, usecols=(0, 1, 2))
        if data.ndim == 1:  # Handle case with only one data row after skipping
            data = data.reshape(1, -1)
        if data.shape[0] == 0:
            print(
                f"Warning: No data found in {filename} after skipping header.",
                file=sys.stderr,
            )
            return None
        # Convert first column (wavenumber) to eV
        data[:, 0] = data[:, 0] * INVCM_TO_EV
        return data
    except FileNotFoundError:
        print(f"Error: File not found: {filename}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error loading file {filename}: {e}", file=sys.stderr)
        return None


def normalize_spectrum(data):
    """Normalizes the intensity columns (1 and 2) of the data."""
    if data is None or data.shape[0] == 0:
        return data

    # Normalize column 1 (index 1)
    max_val_1 = data[:, 1].max()
    if max_val_1 > 0:
        data[:, 1] /= max_val_1
    else:
        print(
            "Warning: Max intensity in column 1 is zero, skipping normalization.",
            file=sys.stderr,
        )

    # Normalize column 2 (index 2)
    max_val_2 = data[:, 2].max()
    if max_val_2 > 0:
        data[:, 2] /= max_val_2
    else:
        print(
            "Warning: Max intensity in column 2 is zero, skipping normalization.",
            file=sys.stderr,
        )

    return data


def get_alignment_index(data_len, alignment_mode, custom_index=0):
    """Determines the index to use for alignment based on the mode."""
    if alignment_mode == "left":
        return 0
    elif alignment_mode == "right":
        return data_len - 1
    elif alignment_mode == "center":
        return data_len // 2
    elif alignment_mode == "custom":
        if 0 <= custom_index < data_len:
            return custom_index
        else:
            print(
                f"Error: Custom index {custom_index} is out of bounds (0-{data_len-1}). Using left alignment.",
                file=sys.stderr,
            )
            return 0  # Default to left alignment on error
    else:
        print(
            f"Warning: Unknown alignment mode '{alignment_mode}'. Using left alignment.",
            file=sys.stderr,
        )
        return 0  # Default to left alignment


def calculate_offset(ref_data, data, alignment_mode, custom_index=0):
    """Calculates the energy offset needed to align data with ref_data."""
    min_len = min(len(ref_data), len(data))
    if min_len == 0:
        print("Warning: Cannot calculate offset with empty data.", file=sys.stderr)
        return 0.0

    align_idx = get_alignment_index(min_len, alignment_mode, custom_index)

    offset = data[align_idx, 0] - ref_data[align_idx, 0]
    return offset


def plot_spectra(ax, data, label, offset=0.0, column_index=1):
    """Plots a single spectrum on the given axes."""
    if data is not None and data.shape[0] > 0:
        ax.plot(data[:, 0] - offset, data[:, column_index], label=label)


def main():
    parser = argparse.ArgumentParser(
        description="""
    Plots and aligns spectra.
    The first file provided is the reference spectrum.
    Subsequent files are aligned to the reference based on the chosen alignment mode.
    Spectra are expected to have wavenumber (cm^-1) in the first column,
    and intensities in the second and third columns, with 7 header rows to skip.
    """
    )
    parser.add_argument("reference_file", help="Path to the reference spectrum file.")
    parser.add_argument(
        "spectra_files", nargs="+", help="Path(s) to the spectra file(s) to align."
    )
    parser.add_argument(
        "--align",
        choices=["left", "center", "right", "custom"],
        default="left",
        help="Alignment point: 'left' (start), 'center', 'right' (end), or 'custom' index (default: left).",
    )
    parser.add_argument(
        "--index",
        type=int,
        default=0,
        help="Custom index for alignment when --align=custom is used.",
    )
    parser.add_argument(
        "--output", default="plot.png", help="Output plot filename (default: plot.png)."
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="Resolution (DPI) for the saved plot (default: 300).",
    )

    args = parser.parse_args()

    if args.align == "custom" and args.index < 0:
        print("Error: Custom alignment index must be non-negative.", file=sys.stderr)
        sys.exit(1)

    # --- Load Reference Data ---
    ref_data = load_spectrum(args.reference_file)
    if ref_data is None:
        sys.exit(1)  # Exit if reference fails to load
    ref_data = normalize_spectrum(ref_data)
    ref_label = f"Reference ({os.path.basename(args.reference_file)})"

    # --- Set up Plot ---
    fig, axs = plt.subplots(
        1, 2, figsize=(12, 5), sharey=True
    )  # Share Y axis for easier comparison
    fig.suptitle(
        f"Spectra Aligned via '{args.align.capitalize()}'"
        + (f" at Index {args.index}" if args.align == "custom" else "")
    )

    # --- Plot Reference ---
    plot_spectra(axs[0], ref_data, ref_label, offset=0.0, column_index=1)
    plot_spectra(axs[1], ref_data, ref_label, offset=0.0, column_index=2)

    # --- Process and Plot Other Spectra ---
    for i, filename in enumerate(args.spectra_files):
        data = load_spectrum(filename)
        if data is None:
            continue  # Skip if loading failed

        data = normalize_spectrum(data)

        # Calculate offset based on alignment mode
        offset = calculate_offset(ref_data, data, args.align, args.index)

        label = f"Spectrum {i+1} ({os.path.basename(filename)})"

        # Plot aligned data
        plot_spectra(axs[0], data, label, offset=offset, column_index=1)
        plot_spectra(axs[1], data, label, offset=offset, column_index=2)

    # --- Final Plot Configuration ---
    axs[0].set_title("Intensity Column 1")
    axs[1].set_title("Intensity Column 2")

    for ax in axs:
        ax.set_xlabel("Energy (eV)")
        ax.set_ylabel("Normalized Intensity")
        ax.legend()
        ax.set_ylim(bottom=0)  # Start y-axis at 0
        # ax.set_ylim(0, 1.1) # Optional: Set fixed upper limit if desired
        ax.locator_params(axis="x", nbins=6)  # Adjust number of x-ticks
        ax.grid(True, linestyle="--", alpha=0.6)  # Add grid

    # --- Save Figure ---
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])  # Adjust layout to prevent title overlap
    try:
        fig.savefig(args.output, dpi=args.dpi)
        print(f"Plot saved to {args.output}")
    except Exception as e:
        print(f"Error saving plot: {e}", file=sys.stderr)

    # plt.show() # Uncomment to display the plot interactively


if __name__ == "__main__":
    main()
