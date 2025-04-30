import argparse
import os
from pathlib import Path


def print_startup_banner():
    """Prints a banner explaining how to run the script."""
    banner = """
    =======================================================================
    QM/MM Solvent Stripping Tool
    =======================================================================

    This script processes molecular simulation snapshots to separate QM atoms
    (dye) from the surrounding solvent molecules, updating QM and MM files.

    How to Use:
    python qmsolvet_to_strip_solvent.py <ndyeAtoms> <snapshot1> [<snapshot2> ...] <qm_ifile> <mm_ifile> <qm_ofile> <mm_ofile>

    Arguments:
      ndyeAtoms:      Integer, the number of atoms belonging to the dye molecule.
      snapshots:      One or more directory paths containing the snapshot data.
      qm_ifile:       Filename of the input QM file within each snapshot directory.
      mm_ifile:       Filename of the input MM file within each snapshot directory.
      qm_ofile:       Filename for the output QM file (dye atoms only).
      mm_ofile:       Filename for the output MM file (original MM solvent + QM solvent).

    Example:
    python qmsolvet_to_strip_solvent.py 15 snap_001 snap_002 qm_input.xyz mm_input.xyz qm_dye.xyz mm_solvent_combined.xyz
    =======================================================================
    """
    print(banner)


def process_snapshot(
    snapshot_dir: Path,
    ndye_atoms: int,
    qm_input_filename: str,
    mm_input_filename: str,
    qm_output_filename: str,
    mm_output_filename: str,
):
    """
    Processes a single snapshot directory to strip solvent atoms.

    Reads QM and MM input files, separates dye atoms from QM solvent atoms,
    updates atom counts, modifies charges for QM solvent atoms based on MM
    data, and writes new QM (dye only) and MM (combined solvent) output files.

    Args:
        snapshot_dir: Path object representing the snapshot directory.
        ndye_atoms: The number of dye atoms.
        qm_input_filename: Filename of the QM input file.
        mm_input_filename: Filename of the MM input file.
        qm_output_filename: Filename for the output QM file.
        mm_output_filename: Filename for the output MM file.
    """
    qm_input_file = snapshot_dir / qm_input_filename
    mm_input_file = snapshot_dir / mm_input_filename
    qm_output_file = snapshot_dir / qm_output_filename
    mm_output_file = snapshot_dir / mm_output_filename

    if not qm_input_file.is_file() or not mm_input_file.is_file():
        print(f"Warning: Input files not found in {snapshot_dir}. Skipping.")
        return

    try:
        with open(qm_input_file, "r") as f:
            qm_lines = f.readlines()
        with open(mm_input_file, "r") as f:
            mm_lines = f.readlines()

        # --- Data Extraction ---
        # First line is atom count, second is usually blank/comment
        header_offset = 2

        n_atoms_qm_total = int(qm_lines[0].strip())
        n_atoms_mm_solvent = int(mm_lines[0].strip())

        if n_atoms_qm_total < ndye_atoms:
            print(
                f"Error in {snapshot_dir}: Total QM atoms ({n_atoms_qm_total}) "
                f"is less than specified dye atoms ({ndye_atoms}). Skipping."
            )
            return

        n_atoms_qm_solvent = n_atoms_qm_total - ndye_atoms
        new_n_atoms_mm_solvent = n_atoms_mm_solvent + n_atoms_qm_solvent

        # Extract coordinates and original atom types/charges
        # Assumes XYZ format: AtomType X Y Z ...
        qm_dye_coords = qm_lines[header_offset : header_offset + ndye_atoms]
        qm_solvent_coords_lines = qm_lines[
            header_offset + ndye_atoms : header_offset + n_atoms_qm_total
        ]
        mm_solvent_coords_lines = mm_lines[header_offset:]

        # Extract original atom types/charges from the *beginning* of the MM solvent section
        # This assumes the first n_atoms_qm_solvent in the MM file correspond
        # to the types needed for the QM solvent atoms being moved.
        # It takes the first field (atom type/charge) from the relevant lines.
        if len(mm_lines) < header_offset + n_atoms_qm_solvent:
            print(
                f"Error in {snapshot_dir}: Not enough lines in MM input file "
                f"({len(mm_lines)}) to extract {n_atoms_qm_solvent} charges/types. Skipping."
            )
            return

        mm_solvent_types_for_qm = [
            line.split()[0]
            for line in mm_lines[header_offset : header_offset + n_atoms_qm_solvent]
        ]

        # --- Data Processing ---
        # Create new MM lines by replacing the atom type/charge in QM solvent lines
        # with the corresponding ones from the MM file.
        new_mm_solvent_lines = []
        if len(qm_solvent_coords_lines) != len(mm_solvent_types_for_qm):
            print(
                f"Error in {snapshot_dir}: Mismatch between QM solvent atoms "
                f"({len(qm_solvent_coords_lines)}) and extracted MM types "
                f"({len(mm_solvent_types_for_qm)}). Skipping."
            )
            return

        for i, qm_solvent_line in enumerate(qm_solvent_coords_lines):
            parts = qm_solvent_line.split()
            if not parts:
                continue  # Skip empty lines if any
            # Replace the first element (atom type) with the one from MM file
            parts[0] = mm_solvent_types_for_qm[i]
            new_mm_solvent_lines.append(" ".join(parts) + "\n")

        # Combine the newly formatted QM solvent lines with the original MM solvent lines
        combined_mm_solvent_lines = new_mm_solvent_lines + mm_solvent_coords_lines

        # --- File Writing ---
        # Write QM output file (dye only)
        with open(qm_output_file, "w") as f:
            f.write(f"{ndye_atoms}\n")
            f.write("\n")  # Assuming a blank line after atom count
            f.writelines(qm_dye_coords)

        # Write MM output file (combined solvent)
        with open(mm_output_file, "w") as f:
            f.write(f"{new_n_atoms_mm_solvent}\n")
            f.write("\n")  # Assuming a blank line after atom count
            f.writelines(combined_mm_solvent_lines)

        print(f"Snapshot {snapshot_dir.name} processed successfully.")

    except ValueError as e:
        print(
            f"Error processing {snapshot_dir}: Invalid number format in input files - {e}. Skipping."
        )
    except IndexError as e:
        print(
            f"Error processing {snapshot_dir}: File format error or missing data - {e}. Skipping."
        )
    except Exception as e:
        print(f"An unexpected error occurred processing {snapshot_dir}: {e}. Skipping.")


def main():
    """
    Main function to parse arguments and orchestrate the snapshot processing.
    """
    print_startup_banner()

    parser = argparse.ArgumentParser(
        description="Processes QM/MM snapshots to separate dye and solvent atoms.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "ndyeAtoms", type=int, help="Number of atoms belonging to the dye molecule."
    )
    parser.add_argument(
        "snapshots",
        nargs="+",
        help="One or more paths to snapshot directories.",
    )
    parser.add_argument(
        "qm_ifile", help="Filename of the QM input file (e.g., qm_input.xyz)."
    )
    parser.add_argument(
        "mm_ifile", help="Filename of the MM input file (e.g., mm_input.xyz)."
    )
    parser.add_argument(
        "qm_ofile", help="Filename for the output QM file (e.g., qm_dye_only.xyz)."
    )
    parser.add_argument(
        "mm_ofile",
        help="Filename for the output MM file (e.g., mm_solvent_combined.xyz).",
    )

    args = parser.parse_args()

    snapshot_dirs = [Path(snap) for snap in args.snapshots]

    # Validate snapshot directories
    valid_snapshot_dirs = []
    for snap_dir in snapshot_dirs:
        if not snap_dir.is_dir():
            print(f"Warning: Snapshot directory not found: {snap_dir}. Skipping.")
        else:
            valid_snapshot_dirs.append(snap_dir)

    if not valid_snapshot_dirs:
        print("Error: No valid snapshot directories found. Exiting.")
        return

    print(f"Processing {len(valid_snapshot_dirs)} snapshot directories...")

    for snap_dir in valid_snapshot_dirs:
        process_snapshot(
            snap_dir,
            args.ndyeAtoms,
            args.qm_ifile,
            args.mm_ifile,
            args.qm_ofile,
            args.mm_ofile,
        )

    print("\nProcessing complete.")


if __name__ == "__main__":
    main()
