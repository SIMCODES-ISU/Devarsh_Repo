# Chemically-Aware Spectral Clustering on Molecular Graphs

This script explores how chemically-aware edge weighting in molecular graphs affects spectral clustering outcomes. Starting from `.xyz` molecular structure files, we construct graphs where atoms are nodes and bonds are edges, then apply spectral clustering to find fragment-like communities.

By default, spectral clustering treats all bonds equally. But here's the implementation of the assigning wieghts to bonds, to make them less likely to be cut making the cuts more chemically aware. 


## How Bond Weights Are Calculated

Here’s the core logic that makes the adjacency matrix chemically aware:

```
def Add_Weights(Adj_Matrix, File_Path):
    ideal_degrees = {'H': 1, 'C': 4, 'N': 3, 'O': 2, 'F': 1, ...}
    atoms, coord = read_xyz(File_Path)
    n = Adj_Matrix.shape[0]

    for i in range(n):
        element = atoms[i]
        num_of_bonds = int(np.sum(Adj_Matrix[i]))
        ideal = ideal_degrees.get(element, num_of_bonds)
        if num_of_bonds >= ideal:
            continue

        for j in range(n):
            if Adj_Matrix[i][j] == 1:
                neighbor = atoms[j]
                neighbor_bonds = int(np.sum(Adj_Matrix[j]))
                neighbor_ideal = ideal_degrees.get(neighbor, neighbor_bonds)

                missing_i = ideal - num_of_bonds
                missing_j = neighbor_ideal - neighbor_bonds

                # Weight assignment logic
                if missing_i > 0 and missing_j > 0:
                    weight = 3  # strong bond (likely double/triple)
                elif missing_i > 0 or missing_j > 0:
                    weight = 2  # moderately strong
                else:
                    weight = 1  # normal bond

                # Symmetric assignment
                Adj_Matrix[i][j] = weight
                Adj_Matrix[j][i] = weight
    return Adj_Matrix
```
>> Why this makes sense:
 A missing valence on an atom means it's more likely to bond, so any existing bond is more chemically significant. Stronger bonds should be penalized more in clustering, making them less likely to be split. This adds domain knowledge into a general-purpose algorithm.

## How I Verified It's Working

- Compare first 5 eigenvectors of the Laplacian: The eigenvectors values were completely different for Without weights
and With weights.
- Graph of eigenvalue spectrum were also different in the plot and overall distrubtion, indiacating changes made my adding weights. 


## Sample Results
Datasets Used :
- Bioactive
  <img width="1097" height="1303" alt="Appended photo (1)" src="https://github.com/user-attachments/assets/82750655-007c-4214-8307-9788b9131f4b" />
  For the last set of job `46/234` (19.5%) Converged, with Clusters number 2 and 8 have high variance in energy difference.Clusters 2–7 and 12–14 have lower energy difference, but no single best parameter.
  Whereas for this run `121/234` (51.7%) Converged, with lower overall varience and a sweet spot from 3-10 cluster number. Increasing covergnece by 32% and the average error decreases from 0.068 Hartree to 0.047 Hartree    having 30 % error reduction.


- Dipeptide

  For the last set of job `885/1260` (70.2%) Converged, suggesting the sweet spot is around 4–6 clusters, but cluster number of 2,7,8,9,10 had high varience . Whereas for this run `blah/1260` (blah%) Converged, with lower overall varience and a sweet spot from 3-10 cluster number. Increasing covergnece by blah% and the average error decreases from 0.017 Hartree to blah Hartree having  blah % error reduction.
 


