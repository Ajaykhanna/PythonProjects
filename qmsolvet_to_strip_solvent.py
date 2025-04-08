import argparse
import os


# How to Use: python *.py ndyeAtoms snapshot1 snapshot2 snapshot3 ... qm_ifile mm_ifile qm_ofile mm_ofile


def qm_to_strip_solvent(ndyeAtoms, snapshots, qm_ifile, mm_ifile, qm_ofile, mm_ofile):
    """
    This function takes in parameters related to a molecular simulation and modifies input and output
    files to remove solvent molecules surrounding a specified number of dye atoms.

    :param ndyeAtoms: The number of dye atoms in the system
    :param snapshots: A list of directories containing input files for each snapshot
    :param qm_ifile: The input file for the QM (quantum mechanics) calculations
    :param mm_ifile: The input file for the molecular mechanics (MM) simulation
    :param qm_ofile: The output file name for the QM calculations
    :param mm_ofile: mm_ofile is a string variable that represents the name of the output file for the
    MM solvent after the QM atoms have been stripped
    """
    for snap in snapshots:
        qm_input_file = os.path.join(snap, qm_ifile)
        mm_input_file = os.path.join(snap, mm_ifile)
        qm_output_file = os.path.join(snap, qm_ofile)
        mm_output_file = os.path.join(snap, mm_ofile)

        if not os.path.exists(qm_input_file) or not os.path.exists(mm_input_file):
            print(f"Input files do not exist for snapshot {snap}. Skipping.")
            continue

        with open(qm_input_file, "r") as f:
            qm_file = f.readlines()

        with open(mm_input_file, "r") as f:
            mm_file = f.readlines()

        nAtoms_QM_solvent = int(qm_file[0])
        nAtoms_MM_solvent = int(mm_file[0])
        nAtoms_QM_to_MM_solvent = nAtoms_QM_solvent - ndyeAtoms
        new_nAtoms_MM_solvent = nAtoms_MM_solvent + nAtoms_QM_to_MM_solvent

        charges = [mm_file[x].split()[0] for x in range(2, nAtoms_QM_to_MM_solvent + 2)]
        qm_solvent = [
            qm_file[x].split()[0]
            for x in range(ndyeAtoms + 2, nAtoms_QM_to_MM_solvent + ndyeAtoms + 2)
        ]

        with open(qm_output_file, "w") as f:
            f.write(str(ndyeAtoms) + "\n\n")
            f.writelines(qm_file[2 : ndyeAtoms + 2])

        new_point_charges = [
            qm_file[ndyeAtoms + 2 :][i].replace(qm_solvent[i], charges[i])
            for i in range(nAtoms_QM_to_MM_solvent)
        ]
        new_mm_file = new_point_charges + mm_file[2:]

        with open(mm_output_file, "w") as f:
            f.write(f"{new_nAtoms_MM_solvent}\n\n")
            f.writelines(new_mm_file)

        print(f"Snapshots #{snap} is Done")


def main():
    parser = argparse.ArgumentParser(
        description="A program that converts snapshots with solvents to snapshots with stripped solvents."
    )
    parser.add_argument("ndyeAtoms", type=int, help="Number of dye atoms")
    parser.add_argument("snapshots", nargs="+", help="List of snapshots")
    parser.add_argument("qm_ifile", help="QM input file")
    parser.add_argument("mm_ifile", help="MM input file")
    parser.add_argument("qm_ofile", help="QM output file")
    parser.add_argument("mm_ofile", help="MM output file")

    args = parser.parse_args()

    qm_to_strip_solvent(
        args.ndyeAtoms,
        args.snapshots,
        args.qm_ifile,
        args.mm_ifile,
        args.qm_ofile,
        args.mm_ofile,
    )


if __name__ == "__main__":
    main()
