import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def plot_autocorrelation(data_file: str) -> None:
    """
    Plots the autocorrelation function of the energy data from a file.

    The function reads energy data from the specified file, extracts the fourth column,
    and generates an autocorrelation plot to visualize the correlation of the data with its lagged values.
    The plot includes a title, x-axis label, grid, and is displayed using matplotlib.

    Args:
        data_file (str): The path to the data file containing the energy data.
                         The file is expected to have at least four columns, with the fourth column
                         representing the energy values to be analyzed.

    Returns:
        None
    """
    try:
        # Load the data from the file
        data_file = np.loadtxt(data_file)

        # Extract the energy data from the fourth column
        data = data_file[:, 3]

        # Create a pandas Series from the data
        data_series = pd.Series(data)

        # Create the autocorrelation plot
        plt.figure()  # Create a new figure
        pd.plotting.autocorrelation_plot(data_series)

        # Add title and labels
        plt.title("Autocorrelation Plot")
        plt.xlabel("Lags")
        plt.grid(True)

        # Save the plot to a file
        plt.savefig("autocorrelation_plot.png", dpi=300)
        # Display the plot
        print("The Autocorrelation plot for the data is:")
        plt.show()

    except FileNotFoundError:
        print(f"Error: The file '{data_file}' was not found.")
    except IndexError:
        print(
            "Error: The data file does not have enough columns. Ensure it has at least four columns."
        )
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    # Example usage:
    file_path = str(sys.argv[1])
    plot_autocorrelation(file_path)
