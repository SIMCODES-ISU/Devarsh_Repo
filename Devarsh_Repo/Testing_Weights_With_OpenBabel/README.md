# Chemically Aware Bond Weighting With Open Babel

This script uses and tests to assign more chemically accurate bond weights to molecular adjacency matrices using **Open Babel**, a cheminformatics toolkit. The weights represent bond orders (e.g., single, double, triple bonds, and aromatic bonds), making the adjacency matrix more reflective of real molecular structures.

## `get_bond_order_adjacency_openbabel(xyz_file)`

```
def get_bond_order_adjacency_openbabel(xyz_file):
    obConversion = openbabel.OBConversion()
    obConversion.SetInFormat("xyz")

    mol = openbabel.OBMol()
    success obConversion.ReadFile(mol, xyz_file)
    if not success:
        raise ValueError(f"Failed to read file: {xyz_file}")

    num_atoms = mol.NumAtoms()
    adj_matrix = np.zeros((num_atoms, num_atoms))

    for bond in openbabel.OBMolBondIter(mol):
        begin_idx = bond.GetBeginAtomIdx() - 1  # OB is 1-indexed
        end_idx = bond.GetEndAtomIdx() - 1

        order = bond.GetBondOrder()
        if bond.IsAromatic():
            order = 1.5 

        adj_matrix[begin_idx][end_idx] = order
        adj_matrix[end_idx][begin_idx] = order

    return adj_matrix

```

## Results From Test Runs 

 Ran Dev Set for **Convergence Performance**, Dev Set is a subset of the all 0-th order conformer of bioactive peptides from the datset.

| Bond Weights (Single, Aromatic, Double, Triple) | Method Description               | Dev Set Convergence (%) |
|--------------------------------------------------|----------------------------------|--------------------------|
| —                                                | Valency Weight (Add_Weights)    | **46.15%**                |
| 1, 2, 3, 4                                        | Open Babel                      | 28.21%                   |
| 1, 2, 2, 3                                        | Open Babel                      | 25.64%                   |
| 1, 5, 5, 5                                        | Open Babel                      | 23.08%                   |
| 1, 1.75, 2, 3                                     | Open Babel                      | 23.08%                   |
| 1, 2, 2.5, 3                                      | Open Babel                      | 23.08%                   |
| 1, 2.5, 2, 3                                      | Open Babel                      | 20.51%                   |
| 1, 2, 3, 3                                        | Open Babel                      | 20.51%                   |
| 1, 1.5, 2, 3                                      | Open Babel                      | 20.51%                   |
| 1, 1, 2, 3                                        | Open Babel                      | 15.38%                   |

I tried assigning multiple bond wieghts patterns to optimize convergence, but orginal method using Graph Degres and Ideal Valency out perform the convergnce results obtained by Open Babel. It makes more sense to use the `Add_Weights` function for current runs and parameter tuning. 


