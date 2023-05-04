import sys

def main(snapshots, qm_atoms):
    dye_atoms = 17
    lines_to_skip = 6  # Gaussian Lines

    for index, snapshot in enumerate(snapshots):
        with open(f'nbdnh2_dmso_frame{snapshot}_ex.com', 'r') as f:
            data = f.read().split('\n')
            print(f'QM-Atoms: {qm_atoms[index]}')
            data_dye = data[lines_to_skip:lines_to_skip + dye_atoms]
            data_solvent = data[lines_to_skip + dye_atoms:int(qm_atoms[index]) + lines_to_skip]

        with open(f'optex_geom{snapshot}.xyz', 'w') as file:
            file.write(f'{qm_atoms[index]}\n\n')
            file.writelines(f'{line}\n' for line in data_dye)

        with open(f'optex_geom{snapshot}.xyz', 'a') as file:
            for line in data_solvent:
                if len(line) > 4:
                    file.writelines(f'{line[0]}{line[4:]}\n')
                else:
                    file.write(line + '\n')

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python script.py <snapshots> <qm_atoms>")
        sys.exit(1)

    snapshots = sys.argv[1].split(',')
    qm_atoms = sys.argv[2].split(',')

    if len(snapshots) != len(qm_atoms):
        print("Error: The number of snapshots and qm_atoms must be equal.")
        sys.exit(1)

    main(snapshots, qm_atoms)
