import argparse
from tqdm import tqdm


def main(
    dye_atoms,
    lines_to_skip,
    snapshots,
    qm_atoms,
    input_file_template,
    output_file_template,
):
    """
    Convert Gaussian input files to XYZ format for QM:Dye + Solvent Files.

    Args:
        dye_atoms (int): Number of dye atoms.
        lines_to_skip (int): Number of Gaussian head lines to skip.
        snapshots (list): List of snapshot indices.
        qm_atoms (list): List of qm_atoms values corresponding to snapshots.
        input_file_template (str): Template for input filenames.
        output_file_template (str): Template for output filenames.
    """
    for index, snapshot in enumerate(
        tqdm(snapshots, desc="Converting Gaussian to XYZ")
    ):
        with open(input_file_template.format(snapshot), "r") as f:
            data = f.read().split("\n")
            data_dye = data[lines_to_skip : lines_to_skip + dye_atoms]
            data_solvent = data[
                lines_to_skip + dye_atoms : int(qm_atoms[index]) + lines_to_skip
            ]

        with open(output_file_template.format(snapshot), "w") as file:
            file.write(f"{qm_atoms[index]}\n\n")
            file.writelines(f"{line}\n" for line in data_dye)

        with open(output_file_template.format(snapshot), "a") as file:
            for line in data_solvent:
                if len(line) > 4:
                    file.writelines(f"{line[0]}{line[4:]}\n")
                else:
                    file.write(line + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert Gaussian input files to XYZ format for QM:Dye + Solvent Files."
    )
    parser.add_argument("dye_atoms", type=int, help="Number of dye atoms.")
    parser.add_argument(
        "lines_to_skip", type=int, help="Number of Gaussian head lines to skip."
    )
    parser.add_argument(
        "snapshots",
        type=lambda s: s.split(","),
        help="List of snapshot indices (comma-separated).",
    )
    parser.add_argument(
        "qm_atoms",
        type=lambda s: s.split(","),
        help="List of qm_atoms values corresponding to snapshots (comma-separated).",
    )
    parser.add_argument(
        "--input-file-template",
        default="nbdnh2_dmso_frame{}_ex.com",
        help='Template for input filenames. Use "{}" as a placeholder for the snapshot index.',
    )
    parser.add_argument(
        "--output-file-template",
        default="optex_geom{}.xyz",
        help='Template for output filenames. Use "{}" as a placeholder for the snapshot index.',
    )

    args = parser.parse_args()

    if len(args.snapshots) != len(args.qm_atoms):
        print("Error: The number of snapshots and qm_atoms must be equal.")
        exit(1)

    main(
        args.dye_atoms,
        args.lines_to_skip,
        args.snapshots,
        args.qm_atoms,
        args.input_file_template,
        args.output_file_template,
    )
