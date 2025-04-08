#! /usr/bin/env python
# Creating On-Demand TeraChem Input Files

# Printing Developer Information
print("*********| Chef-TeraChem | **********")
print(
    " A python script to create on-demand TeraChem input files for various types of calculations"
)
print("Require python >=3, last-tested with python=3.6 on Oct.10.2020")
print("Written by Ajay Khanna")
print("Oct.10.2020 | UC-Merced | Dr. Isborb's Lab")
print()

# Print Script Capababilities
print("Current Options:")
print(
    "Gs-Energy[0], Gs-Optimization[1], Gs-Frequency[2], Ex-Energy[3] Ex-Optimization[4], Ex-Frequency[5]"
)
print("Example type 1 for Ground state optimization")

# List of Solvent's dielectric constants (Taken from Gaussian (http://gaussian.com/scrf/) last accessed: Oct.10.2020)
solvent_list = {
    "water": 78.3553,
    "acetonitrile": 35.688,
    "methanol": 32.613,
    "ethanol": 24.852,
    "isoquinoline": 11.00,
    "quinoline": 9.16,
    "chloroform": 4.7113,
    "diethylether": 4.2400,
    "dichloromethane": 8.93,
    "dichloroethane": 10.125,
    "carbontetrachloride": 2.2280,
    "benzene": 2.2706,
    "toluene": 2.3741,
    "chlorobenzene": 5.6968,
    "nitromethane": 36.562,
    "heptane": 1.9113,
    "cyclohexane": 2.0165,
    "aniline": 6.8882,
    "acetone": 20.493,
    "tetrahydrofuran": 7.4257,
    "dimethylsulfoxide": 46.826,
    "argon": 1.430,
    "krypton": 1.519,
    "xenon": 1.706,
    "n-octanol": 9.8629,
    "1,1,1-trichloroethane": 7.0826,
    "1,1,2-trichloroethane": 7.1937,
    "1,2,4-trimethylbenzene": 2.3653,
    "1,2-dibromoethane": 4.9313,
    "1,2-ethanediol": 40.245,
    "1,4-dioxane": 2.2099,
    "1-bromo-2-methylpropane": 7.7792,
    "1-bromooctane": 5.0244,
    "1-bromopentane": 6.269,
    "1-bromopropane": 8.0496,
    "1-butanol": 17.332,
    "1-chlorohexane": 5.9491,
    "1-chloropentane": 6.5022,
    "1-chloropropane": 8.3548,
    "1-decanol": 7.5305,
    "1-fluorooctane": 3.89,
    "1-heptanol": 11.321,
    "1-hexanol": 12.51,
    "1-hexene": 2.0717,
    "1-hexyne": 2.615,
    "1-iodobutane": 6.173,
    "1-iodohexadecane": 3.5338,
    "1-iodopentane": 5.6973,
    "1-iodopropane": 6.9626,
    "1-nitropropane": 23.73,
    "1-nonanol": 8.5991,
    "1-pentanol": 15.13,
    "1-pentene": 1.9905,
    "1-propanol": 20.524,
    "2,2,2-trifluoroethanol": 26.726,
    "2,2,4-trimethylpentane": 1.9358,
    "2,4-dimethylpentane": 1.8939,
    "2,4-dimethylpyridine": 9.4176,
    "2,6-dimethylpyridine": 7.1735,
    "2-bromopropane": 9.3610,
    "2-butanol": 15.944,
    "2-chlorobutane": 8.3930,
    "2-heptanone": 11.658,
    "2-hexanone": 14.136,
    "2-methoxyethanol": 17.2,
    "2-methyl-1-propanol": 16.777,
    "2-methyl-2-propanol": 12.47,
    "2-methylpentane": 1.89,
    "2-methylpyridine": 9.9533,
    "2-nitropropane": 25.654,
    "2-octanone": 9.4678,
    "2-pentanone": 15.200,
    "2-propanol": 19.264,
    "2-propen-1-ol": 19.011,
    "3-methylpyridine": 11.645,
    "3-pentanone": 16.78,
    "4-heptanone": 12.257,
    "4-methyl-2-pentanone": 12.887,
    "4-methylpyridine": 11.957,
    "5-nonanone": 10.6,
    "aceticacid": 6.2528,
    "acetophenone": 17.44,
    "a-chlorotoluene": 6.7175,
    "anisole": 4.2247,
    "benzaldehyde": 18.220,
    "benzonitrile": 25.592,
    "benzylalcohol": 12.457,
    "bromobenzene": 5.3954,
    "bromoethane": 9.01,
    "bromoform": 4.2488,
    "butanal": 13.45,
    "butanoicacid": 2.9931,
    "butanone": 18.246,
    "butanonitrile": 24.291,
    "butylamine": 4.6178,
    "butylethanoate": 4.9941,
    "carbondisulfide": 2.6105,
    "cis-1,2-dimethylcyclohexane": 2.06,
    "cis-decalin": 2.2139,
    "cyclohexanone": 15.619,
    "cyclopentane": 1.9608,
    "cyclopentanol": 16.989,
    "cyclopentanone": 13.58,
    "decalin-mixture": 2.196,
    "dibromomethane": 7.2273,
    "dibutylether": 3.0473,
    "diethylamine": 3.5766,
    "diethylsulfide": 5.723,
    "diiodomethane": 5.32,
    "diisopropylether": 3.38,
    "dimethyldisulfide": 9.6,
    "diphenylether": 3.73,
    "dipropylamine": 2.9112,
    "e-1,2-dichloroethene": 2.14,
    "e-2-pentene": 2.051,
    "ethanethiol": 6.667,
    "ethylbenzene": 2.4339,
    "ethylethanoate": 5.9867,
    "ethylmethanoate": 8.3310,
    "ethylphenylether": 4.1797,
    "fluorobenzene": 5.42,
    "formamide": 108.94,
    "formicacid": 51.1,
    "hexanoicacid": 2.6,
    "iodobenzene": 4.5470,
    "iodoethane": 7.6177,
    "iodomethane": 6.8650,
    "isopropylbenzene": 2.3712,
    "m-cresol": 12.44,
    "mesitylene": 2.2650,
    "methylbenzoate": 6.7367,
    "methylbutanoate": 5.5607,
    "methylcyclohexane": 2.024,
    "methylethanoate": 6.8615,
    "methylmethanoate": 8.8377,
    "methylpropanoate": 6.0777,
    "m-xylene": 2.3478,
    "n-butylbenzene": 2.36,
    "n-decane": 1.9846,
    "n-dodecane": 2.0060,
    "n-hexadecane": 2.0402,
    "n-hexane": 1.8819,
    "nitrobenzene": 34.809,
    "nitroethane": 28.29,
    "n-methylaniline": 5.9600,
    "n-methylformamide-mixture": 181.56,
    "n,n-dimethylacetamide": 37.781,
    "n,n-dimethylformamide": 37.219,
    "n-nonane": 1.9605,
    "n-octane": 1.9406,
    "n-pentadecane": 2.0333,
    "n-pentane": 1.8371,
    "n-undecane": 1.9910,
    "o-chlorotoluene": 4.6331,
    "o-cresol": 6.76,
    "o-dichlorobenzene": 9.9949,
    "o-nitrotoluene": 25.669,
    "o-xylene": 2.5454,
    "pentanal": 10.0,
    "pentanoicacid": 2.6924,
    "pentylamine": 4.2010,
    "pentylethanoate": 4.7297,
    "perfluorobenzene": 2.029,
    "p-isopropyltoluene": 2.2322,
    "propanal": 18.5,
    "propanoicacid": 3.44,
    "propanonitrile": 29.324,
    "propylamine": 4.9912,
    "propylethanoate": 5.5205,
    "p-xylene": 2.2705,
    "pyridine": 12.978,
    "sec-butylbenzene": 2.3446,
    "tert-butylbenzene": 2.3447,
    "tetrachloroethene": 2.268,
    "tetrahydrothiophene-s,s-dioxide": 43.962,
    "tetralin": 2.771,
    "thiophene": 2.7270,
    "thiophenol": 4.2728,
    "trans-decalin": 2.1781,
    "tributylphosphate": 8.1781,
    "trichloroethene": 3.422,
    "triethylamine": 2.3832,
    "xylene-mixture": 2.3879,
    "z-1,2-dichloroethene": 9.2,
}

# User Inputs For The Molecule
mol_name = str(input("Enter the name of the Molecule: "))
print(
    "Note you should have your {0} xyz file located in the same folder or you can provide path to file".format(
        mol_name
    )
)
calc_type = int(
    input("Enter the type of calculation you are interested(0,1,2,3,4,5): ")
)
funcnl_type = str(input("Enter the name of the functional: "))
basis_set_type = str(input("Enter the basis-set: "))
charge = int(input("Enter the charge: "))
multiplicity = int(input("Enter the multiplicity: "))
if calc_type >= 3:
    exst = "y"
else:
    exst = "n"

# Include Solvent Effects
cosmo = str(input("Turn on Solvent Effects?(y/n): "))
epsilon = []
if cosmo == "y":
    solvet = [str(input("Enter the name of the solvent: ")).lower()]
    # Substring Key match in dictionary
    res = [solvent_list[key] for key in solvet]
    epsilon.append(res[0])
    # print(res[0])

# 1. Ground State Gas Phase Energy Calculations
if (calc_type == 0) and (cosmo == "n"):
    f = open("{0}_gs_energy.in".format(mol_name), "w")
    f.write(
        "# Job info: {0} ground state energy calculations in gas phase\n".format(
            mol_name
        )
    )
    f.write("#\n")
    f.write("# {0} coordinate filename (or path) \n".format(mol_name))
    f.write("coordinates         {0}.xyz\n".format(mol_name).lower())
    f.write("# Charge & Multiplicity \n")
    f.write("charge              {0}\n".format(charge))
    f.write("spinmult            {0}\n".format(multiplicity))
    f.write("# Basis-Sets, Level of theory & Type of Job\n")
    f.write("basis               {0}\n".format(basis_set_type))
    f.write("method              {0}\n".format(funcnl_type).lower())
    f.write("run                 energy\n")
    f.write("# Hardware Information\n")
    f.write("gpus                4\n")
    f.write("safemode            no\n")
    f.write(
        "# Controlling Precison and DFT-Grid (Expert Options, read manual before removing '#'sign)\n"
    )
    f.write("#precision          double\n")
    f.write("#threall            1.0e-15\n")
    f.write("#convthre           3.0e-07\n")
    f.write("#dftgrid            5\n")
    f.write("#end")
    f.close()
# ------------------------------------------------------------------------------------------------------------
# 2. Ground State Implicit Solvent Energy Calculations
elif (calc_type == 0) and (cosmo == "y"):
    f = open("{0}_gs_energy_cosmo.in".format(mol_name), "w")
    f.write(
        "# Job info: {0} ground state energy calculations in cosmo\n".format(mol_name)
    )
    f.write("#\n")
    f.write("# {0} coordinate filename\n".format(mol_name))
    f.write("coordinates         {0}.xyz\n".format(mol_name).lower())
    f.write("# Charge & Multiplicity \n")
    f.write("charge              {0}\n".format(charge))
    f.write("spinmult            {0}\n".format(multiplicity))
    f.write("# Basis-Sets, Level of theory & Type of Job\n")
    f.write("basis               {0}\n".format(basis_set_type))
    f.write("method              {0}\n".format(funcnl_type).lower())
    f.write("run                 energy\n")
    f.write("# Solvent model and dielectric constant\n")  # Turning on Terachem COSMO
    f.write("pcm                 cosmo\n")
    f.write("epsilon             {0}\n".format(epsilon[0]))
    f.write("# Hardware Information\n")
    f.write("gpu                 4\n")
    f.write("safemode            no\n")
    f.write("# Expert options read the mannual before removing '#'sign \n")
    f.write("#pcm_scale          1\n")
    f.write("#pcm_grid           lebedev\n")
    f.write("#pcmgrid_h          7\n")
    f.write("#pcmgrid_heavy      7\n")
    f.write("#precision          double\n")
    f.write("#threall            1.0e-15\n")
    f.write("#convthre           3.0e-07\n")
    f.write("#dftgrid            5\n")
    f.write("end")
    f.close()
# ------------------------------------------------------------------------------------------------------------
# 3. Ground State Gas Phase Optimization
elif (calc_type == 1) and (cosmo == "n"):
    f = open("{0}_gs_opt.in".format(mol_name), "w")
    f.write("# Job info: {0} ground state optimization in Gas Phase\n".format(mol_name))
    f.write("#\n")
    f.write("# {0} coordinate filename (or path) \n".format(mol_name))
    f.write("coordinates         {0}.xyz\n".format(mol_name).lower())
    f.write("# Charge & Multiplicity \n")
    f.write("charge              {0}\n".format(charge))
    f.write("spinmult            {0}\n".format(multiplicity))
    f.write("# Basis-Sets, Level of theory & Type of Job\n")
    f.write("basis               {0}\n".format(basis_set_type))
    f.write("method              {0}\n".format(funcnl_type).lower())
    f.write("run                 minimize\n")
    f.write("new_minimizer       yes\n")
    f.write("# Hardware Information\n")
    f.write("gpus                4\n")
    f.write("safemode            no\n")
    f.write(
        "# Controlling Precison and DFT-Grid (Expert Options, read manual before removing '#'sign)\n"
    )
    f.write("#precision           double\n")
    f.write("#threall             1.0e-15\n")
    f.write("#convthre            3.0e-07\n")
    f.write("#dftgrid             5\n")
    f.write("#end")
    f.close()
# ------------------------------------------------------------------------------------------------------------
# 4. Ground State Implicit Solvent Optimization
elif (calc_type == 1) and (cosmo == "y"):
    f = open("{0}_gs_cosmo_opt.in".format(mol_name), "w")
    f.write("# Job info: {0} ground state cosmo optimization\n".format(mol_name))
    f.write("#\n")
    f.write("# {0} coordinate filename\n".format(mol_name))
    f.write("coordinates         {0}.xyz\n".format(mol_name).lower())
    f.write("# Charge & Multiplicity \n")
    f.write("charge              {0}\n".format(charge))
    f.write("spinmult            {0}\n".format(multiplicity))
    f.write("# Basis-Sets, Level of theory & Type of Job\n")
    f.write("basis               {0}\n".format(basis_set_type))
    f.write("method              {0}\n".format(funcnl_type).lower())
    f.write("run                 minimize\n")
    f.write("new_minimizer       yes\n")
    f.write("# Solvent model and dielectric constant\n")  # Turning on Terachem COSMO
    f.write("pcm                 cosmo\n")
    f.write("epsilon             {0}\n".format(epsilon[0]))
    f.write("# Hardware Information\n")
    f.write("gpu                 4\n")
    f.write("safemode            no\n")
    f.write("# Expert options read the mannual before removing '#'-sign \n")
    f.write("#pcm_scale          1\n")
    f.write("#pcm_grid           lebedev\n")
    f.write("#precision          double\n")
    f.write("#threall            1.0e-15\n")
    f.write("#convthre           3.0e-07\n")
    f.write("#dftgrid            5\n")
    f.write("end")
    f.close()
# ------------------------------------------------------------------------------------------------------------
# 5. Ground State Gas Phase Frequency Calculations
elif (calc_type == 2) and (cosmo == "n"):
    f = open("{0}_gs_freq.in".format(mol_name), "w")
    f.write(
        "# Job info: {0} ground state frequency calculations in gas phase\n".format(
            mol_name
        )
    )
    f.write("#\n")
    f.write("# {0} coordinate filename (or path) \n".format(mol_name))
    f.write("coordinates         {0}.xyz\n".format(mol_name).lower())
    f.write("# Charge & Multiplicity \n")
    f.write("charge              {0}\n".format(charge))
    f.write("spinmult            {0}\n".format(multiplicity))
    f.write("# Basis-Sets, Level of theory & Type of Job\n")
    f.write("basis               {0}\n".format(basis_set_type))
    f.write("method              {0}\n".format(funcnl_type).lower())
    f.write("run                 frequencies\n")
    f.write("mincheck            false\n")  # Default=True
    f.write("# Hardware Information\n")
    f.write("gpus                4\n")
    f.write("safemode            no\n")
    f.write(
        "# Controlling Precison and DFT-Grid (Expert Options, read manual before removing '#'sign)\n"
    )
    f.write("#precision           double\n")
    f.write("#threall             1.0e-15\n")
    f.write("#convthre            3.0e-07\n")
    f.write("#dftgrid             5\n")
    f.write("#end")
    f.close()
# ------------------------------------------------------------------------------------------------------------
# 6. Ground State Implicit Solvent Frequency Calculations
elif (calc_type == 2) and (cosmo == "y"):
    f = open("{0}_gs_cosmo_freq.in".format(mol_name), "w")
    f.write(
        "# Job info: {0} ground state requency calculations in cosmo\n".format(mol_name)
    )
    f.write("#\n")
    f.write("# {0} coordinate filename\n".format(mol_name))
    f.write("coordinates         {0}.xyz\n".format(mol_name).lower())
    f.write("# Charge & Multiplicity \n")
    f.write("charge              {0}\n".format(charge))
    f.write("spinmult            {0}\n".format(multiplicity))
    f.write("# Basis-Sets, Level of theory & Type of Job\n")
    f.write("basis               {0}\n".format(basis_set_type))
    f.write("method              {0}\n".format(funcnl_type).lower())
    f.write("run                 frequencies\n")
    f.write("mincheck            false\n")
    f.write("# Solvent model and dielectric constant\n")  # Turning on Terachem COSMO
    f.write("pcm                 cosmo\n")
    f.write("epsilon             {0}\n".format(epsilon[0]))
    f.write("# Hardware Information\n")
    f.write("gpu                 4\n")
    f.write("safemode            no\n")
    f.write("# Expert options read the mannual before removing '#'-sign \n")
    f.write("#pcm_scale          1\n")
    f.write("#pcm_grid           lebedev\n")
    f.write("#precision          double\n")
    f.write("#threall            1.0e-15\n")
    f.write("#convthre           3.0e-07\n")
    f.write("#dftgrid            5\n")
    f.write("end")
    f.close()
# ------------------------------------------------------------------------------------------------------------
# 5. Excited State Gas Phase Energy Calculations
elif (calc_type == 3) and (cosmo == "n"):
    f = open("{0}_ex_energy.in".format(mol_name), "w")
    f.write(
        "# Job info: {0} excited state energy calculations in gas phase\n".format(
            mol_name
        )
    )
    f.write("#\n")
    f.write("# {0} coordinate filename (or path) \n".format(mol_name))
    f.write("coordinates         {0}.xyz\n".format(mol_name).lower())
    f.write("# Charge & Multiplicity \n")
    f.write("charge              {0}\n".format(charge))
    f.write("spinmult            {0}\n".format(multiplicity))
    f.write("# Basis-Sets, Level of theory & Type of Job\n")
    f.write("basis               {0}\n".format(basis_set_type))
    f.write("method              {0}\n".format(funcnl_type))
    f.write("run                 energy\n")
    f.write("# Excited sate of interest\n")
    f.write("cis                 yes\n")  # Turn on excited state calculation
    f.write(
        "cistarget           1\n"
    )  # Target state of interest (State for which optimization will proceed)
    f.write("cisnumstates        6\n")  # Total number of states to be solved
    f.write("cisguessvecs        12\n")
    f.write("# Hardware Information\n")
    f.write("gpus                4\n")
    f.write("safemode            no\n")
    f.write(
        "# Expert options read the mannual before removing '#'sign \n"
    )  # Expert Options
    f.write("#pcm_scale          1\n")
    f.write("#pcm_grid           lebedev\n")
    f.write("#precision          double\n")
    f.write("#threall            1.0e-15\n")
    f.write("#convthre           3.0e-07\n")
    f.write("#dftgrid            5\n")
    f.write("end")
    f.close()
# ------------------------------------------------------------------------------------------------------------
# 6. Excited State Implicit Solvent Energy Calculations
elif (calc_type == 3) and (cosmo == "y"):
    f = open("{0}_ex_cosmo_energy.in".format(mol_name), "w")
    f.write(
        "# Job info: {0} Excited state energy calculations in cosmo\n".format(mol_name)
    )
    f.write("#\n")
    f.write("# {0} coordinate filename\n".format(mol_name))
    f.write("coordinates         {0}.xyz\n".format(mol_name).lower())
    f.write("# Charge & Multiplicity \n")
    f.write("charge              {0}\n".format(charge))
    f.write("spinmult            {0}\n".format(multiplicity))
    f.write("# Basis-Sets, Level of theory & Type of Job\n")
    f.write("basis               {0}\n".format(basis_set_type))
    f.write("method              {0}\n".format(funcnl_type).lower())
    f.write("run                 energy\n")
    f.write("# Solvent model and dielectric constant\n")  # Turning on Terachem COSMO
    f.write("pcm                 cosmo\n")
    f.write("epsilon             {0}\n".format(epsilon[0]))
    f.write("# Excited sate options\n")
    f.write("cis                 yes\n")  # Turn on excited state calculation
    f.write(
        "cistarget           1\n"
    )  # Target state of interest (State for which optimization will proceed)
    f.write("cisnumstates        6\n")  # Total number of states to be solved
    f.write("cisguessvecs        12\n")
    f.write("# Hardware Information\n")
    f.write("gpu                 4\n")
    f.write("safemode            no\n")
    f.write("# Expert options read the mannual before removing '#'-sign \n")
    f.write("#pcm_scale          1\n")
    f.write("#pcm_grid           lebedev\n")
    f.write("#precision          double\n")
    f.write("#threall            1.0e-15\n")
    f.write("#convthre           3.0e-07\n")
    f.write("#dftgrid            5\n")
    f.write("end")
    f.close()
# ------------------------------------------------------------------------------------------------------------
# 7. Excited State Gas Phase Optimization
elif (calc_type == 4) and (cosmo == "n"):
    f = open("{0}_ex_opt.in".format(mol_name), "w")
    f.write(
        "# Job info: {0} Excited state optimization in gas phase\n".format(mol_name)
    )
    f.write("#\n")
    f.write("# {0} coordinate filename (or path) \n".format(mol_name))
    f.write("coordinates         {0}.xyz\n".format(mol_name).lower())
    f.write("# Charge & Multiplicity \n")
    f.write("charge              {0}\n".format(charge))
    f.write("spinmult            {0}\n".format(multiplicity))
    f.write("# Basis-Sets, Level of theory & Type of Job\n")
    f.write("basis               {0}\n".format(basis_set_type))
    f.write("method              {0}\n".format(funcnl_type))
    f.write("run                 minimize\n")
    f.write("new_minimizer       yes\n")
    f.write("# Excited sate of interest\n")
    f.write("cis                 yes\n")  # Turn on excited state calculation
    f.write(
        "cistarget           1\n"
    )  # Target state of interest (State for which optimization will proceed)
    f.write("cisnumstates        6\n")  # Total number of states to be solved
    f.write("cisguessvecs        12\n")
    f.write("# Hardware Information\n")
    f.write("gpus                4\n")
    f.write("safemode            no\n")
    f.write("# Expert options read the mannual before removing '#'sign \n")
    f.write("#precision          double\n")
    f.write("#threall            1.0e-15\n")
    f.write("#convthre           3.0e-07\n")
    f.write("#dftgrid            5\n")
    f.write("end")
    f.close()
# ------------------------------------------------------------------------------------------------------------
# 8. Excited State Implicit Solvent Optimization
elif (calc_type == 4) and (cosmo == "y"):
    f = open("{0}_ex_cosmo_opt.in".format(mol_name), "w")
    f.write("# Job info: {0} Excited state optimization in cosmo\n".format(mol_name))
    f.write("#\n")
    f.write("# {0} coordinate filename\n".format(mol_name))
    f.write("coordinates         {0}.xyz\n".format(mol_name).lower())
    f.write("# Charge & Multiplicity \n")
    f.write("charge              {0}\n".format(charge))
    f.write("spinmult            {0}\n".format(multiplicity))
    f.write("# Basis-Sets, Level of theory & Type of Job\n")
    f.write("basis               {0}\n".format(basis_set_type))
    f.write("method              {0}\n".format(funcnl_type).lower())
    f.write("run                 minimize\n")
    f.write("new_minimizer       yes\n")
    f.write("# Solvent model and dielectric constant\n")  # Turning on Terachem COSMO
    f.write("pcm                 cosmo\n")
    f.write("epsilon             {0}\n".format(epsilon[0]))
    f.write("# Excited sate options\n")
    f.write("cis                 yes\n")  # Turn on excited state calculation
    f.write(
        "cistarget           1\n"
    )  # Target state of interest (State for which optimization will proceed)
    f.write("cisnumstates        6\n")  # Total number of states to be solved
    f.write("cisguessvecs        12\n")
    f.write("# Hardware Information\n")
    f.write("gpu                 4\n")
    f.write("safemode            no\n")
    f.write("# Expert options read the mannual before removing '#'sign \n")
    f.write("#pcm_scale          1\n")
    f.write("#pcm_grid           lebedev\n")
    f.write("#precision          double\n")
    f.write("#threall            1.0e-15\n")
    f.write("#convthre           3.0e-07\n")
    f.write("#dftgrid            5\n")
    f.write("end")
    f.close()
# ------------------------------------------------------------------------------------------------------------
# 9. Excited State Gas Phase Frequency calculations
elif (calc_type == 5) and (cosmo == "n"):
    f = open("{0}_ex_freq.in".format(mol_name), "w")
    f.write("# Job info: {0} Excited state frequency calculations\n".format(mol_name))
    f.write("#\n")
    f.write("# {0} coordinate filename (or path) \n".format(mol_name))
    f.write("coordinates         {0}.xyz\n".format(mol_name).lower())
    f.write("# Charge & Multiplicity \n")
    f.write("charge              {0}\n".format(charge))
    f.write("spinmult            {0}\n".format(multiplicity))
    f.write("# Basis-Sets, Level of theory & Type of Job\n")
    f.write("basis               {0}\n".format(basis_set_type))
    f.write("method              {0}\n".format(funcnl_type))
    f.write("run                 frequencies\n")
    f.write("mincheck            false\n")
    f.write("# Excited sate of interest\n")
    f.write("cis                 yes\n")  # Turn on excited state calculation
    f.write(
        "cistarget           1\n"
    )  # Target state of interest (State for which optimization will proceed)
    f.write("cisnumstates        6\n")  # Total number of states to be solved
    f.write("cisguessvecs        12\n")
    f.write("# Hardware Information\n")
    f.write("gpus                4\n")
    f.write("safemode            no\n")
    f.write("# Expert options read the mannual before removing '#'sign \n")
    f.write("#precision          double\n")
    f.write("#threall            1.0e-15\n")
    f.write("#convthre           3.0e-07\n")
    f.write("#dftgrid            5\n")
    f.write("end")
    f.close()
# ------------------------------------------------------------------------------------------------------------
# 10. Excited State Implicit Solvent Frequency Calculations
elif (calc_type == 5) and (cosmo == "y"):
    f = open("{0}_ex_cosmo_freq.in".format(mol_name), "w")
    f.write(
        "# Job info: {0} Excited state frequency calculations in cosmo\n".format(
            mol_name
        )
    )
    f.write("#\n")
    f.write("# {0} coordinate filename\n".format(mol_name))
    f.write("coordinates         {0}.xyz\n".format(mol_name).lower())
    f.write("# Charge & Multiplicity \n")
    f.write("charge              {0}\n".format(charge))
    f.write("spinmult            {0}\n".format(multiplicity))
    f.write("# Basis-Sets, Level of theory & Type of Job\n")
    f.write("basis               {0}\n".format(basis_set_type))
    f.write("method              {0}\n".format(funcnl_type).lower())
    f.write("run                 frequencies\n")
    f.write("mincheck            false\n")
    f.write("# Solvent model and dielectric constant\n")  # Turning on Terachem COSMO
    f.write("pcm                 cosmo\n")
    f.write("epsilon             {0}\n".format(epsilon[0]))
    f.write("# Excited sate options\n")
    f.write("cis                 yes\n")  # Turn on excited state calculation
    f.write(
        "cistarget           1\n"
    )  # Target state of interest (State for which optimization will proceed)
    f.write("cisnumstates        6\n")  # Total number of states to be solved
    f.write("cisguessvecs        12\n")
    f.write("# Hardware Information\n")
    f.write("gpu                 4\n")
    f.write("safemode            no\n")
    f.write("# Expert options read the mannual before removing '#'sign \n")
    f.write("#pcm_scale          1\n")
    f.write("#pcm_grid           lebedev\n")
    f.write("#precision          double\n")
    f.write("#threall            1.0e-15\n")
    f.write("#convthre           3.0e-07\n")
    f.write("#dftgrid            5\n")
    f.write("end")
    f.close()
# -------------------------------------------------------------------------------------------------------------
print("Task Completed Successfully")
print("Buy the developer a beer")
