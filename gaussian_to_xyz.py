snapshots = [7,10,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,30,31,32,33,34,35]
qm_atoms = [189,195,201,207,195,207,189,189,183,189,189,195,183,183,201,189,195,189,189,189,183,177,201,189,195]

for index, i in enumerate(snapshots):
    with open('mecou_meoh_frame'+str(i)+'_ex.com', 'r') as f:
        data = f.read()
        data = data.split('\n')
        print(f'QM-AToms: {qm_atoms[index]}')
        data_dye = data[6:33]
        data_solvent = data[33:qm_atoms[index]+6]
    with open('optex_geom'+str(i)+'.xyz', 'w') as file:
        file.write(str(qm_atoms[index])+'\n\n')
        for line in data_dye:
            file.write(str(line)+'\n')
    with open('optex_geom'+str(i)+'.xyz', 'a') as file:
        for line in data_solvent:
            file.write(str(line[0]+line[4:])+'\n')
