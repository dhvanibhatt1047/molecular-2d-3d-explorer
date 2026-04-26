from rdkit import Chem
from rdkit.Chem import Draw

# 1. Version Check
print(f"RDKit is alive! Version: {Chem.rdBase.rdkitVersion}")

# 2. Logic Check (Can it understand a molecule?)
mol = Chem.MolFromSmiles('CCO') # This is Ethanol
if mol:
    print("Success: RDKit understood the Ethanol string.")
    # This will create a 'molecule.png' in your folder
    Draw.MolToFile(mol, 'test_render.png')
    print("Success: RDKit rendered a 2D image.")
else:
    print("Error: RDKit installation is broken.")