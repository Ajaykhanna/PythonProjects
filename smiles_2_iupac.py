import requests
CACTUS = "https://cactus.nci.nih.gov/chemical/structure/{0}/{1}"

def smiles_to_iupac(smiles):
    rep = "iupac_name"
    url = CACTUS.format(smiles, rep)
    response = requests.get(url)
    response.raise_for_status()
    return response.text

print(smiles_to_iupac('c1ccccc1'))
print(smiles_to_iupac('CC(=O)OC1=CC=CC=C1C(=O)O'))

# Output
# BENZENE
# 2-acetyloxybenzoic acid

# Another Methods with Pubchempy
import pubchempy
# Use the SMILES you provided
smiles = 'O=C(NCc1ccc(C(F)(F)F)cc1)[C@@H]1Cc2[nH]cnc2CN1Cc1ccc([N+](=O)[O-])cc1'
compounds = pubchempy.get_compounds(smiles, namespace='smiles')
match = compounds[0]
print(match.iupac_name)

[Out]:
(6S)-5-[(4-nitrophenyl)methyl]-N-[[4-(trifluoromethyl)phenyl]methyl]-3,4,6,7-tetrahydroimidazo[4,5-c]pyridine-6-carboxamide
