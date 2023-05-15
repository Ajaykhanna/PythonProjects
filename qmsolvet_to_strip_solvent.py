import sys

def qm_to_strip_solvent(ndyeAtoms, snapshots, qm_ifile, mm_ifile, qm_ofile, mm_ofile):
    """
    The function qm_to_strip_solvent takes in parameters related to molecular dynamics simulations and
    modifies input files to remove solvent molecules and add charges to the remaining atoms.
    
    :param ndyeAtoms: The number of atoms in the dye molecule
    :param snapshots: The list of snapshot numbers for which the function will perform the QM/MM
    calculations
    :param qm_ifile: The name of the input file containing the QM solvent coordinates and charges
    :param mm_ifile: The name of the input file containing the molecular mechanics (MM) coordinates and
    charges
    :param qm_ofile: qm_ofile is a string variable that represents the name of the output file for the
    QM region after removing the solvent molecules
    :param mm_ofile: mm_ofile is a string variable that represents the name of the output file for the
    modified MM solvent file
    """
    nAtoms_dye = ndyeAtoms
    
    for snap in snapshots:
        print(f'Snapshots #{snap} is Done')
        qm_file = open(f'{snap}/{qm_ifile}').readlines()
        mm_file = open(f'{snap}/{mm_ifile}').readlines()
        
        nAtoms_QM_solvent = int(qm_file[0])
        nAtoms_MM_solvent = int(mm_file[0])
        nAtoms_QM_to_MM_solvent = nAtoms_QM_solvent - nAtoms_dye
        new_nAtoms_MM_solvent = nAtoms_MM_solvent + nAtoms_QM_to_MM_solvent

        charges = [mm_file[x].split()[0] for x in range(2, nAtoms_QM_to_MM_solvent + 2)]
        qm_solvent = [qm_file[x].split()[0] for x in range(nAtoms_dye + 2, nAtoms_QM_to_MM_solvent + nAtoms_dye + 2)]

        with open(f'{snap}/{qm_ofile}', 'w') as f:
            f.write(str(nAtoms_dye) + '\n')
            f.write('\n')
            for line in range(2, nAtoms_dye + 2):
                f.write(str(qm_file[line]))

        new_point_charges = []
        for i in range(0, nAtoms_QM_to_MM_solvent):
            new_point_charges.append(qm_file[nAtoms_dye+2:][i].replace(qm_solvent[i], charges[i]))

        new_mm_file = new_point_charges + mm_file[2:]
        with open(f'{snap}/{mm_ofile}', 'w') as f:
            f.write(str(new_nAtoms_MM_solvent) + '\n')
            f.write('\n')
            for line in range(len(new_mm_file)):
                f.write(str(new_mm_file[line]))

if __name__ == '__main__':
    print(f'Help: python *.py int:ndyeAtoms list:(1,2,3) str:qm_ifile, mm_ifile, qm_ofile, mm_ofile')
    ndyeAtoms = int(sys.argv[1])
    snapshots = list(sys.argv[2].split(','))
    qm_ifile, mm_ifile = str(sys.argv[3]), str(sys.argv[4])
    qm_ofile, mm_ofile = str(sys.argv[5]), str(sys.argv[6])

    qm_to_strip_solvent(ndyeAtoms, snapshots, qm_ifile, mm_ifile, qm_ofile, mm_ofile)
