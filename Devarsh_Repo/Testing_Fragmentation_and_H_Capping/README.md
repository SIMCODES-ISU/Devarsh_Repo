# Fragmentation of PHE-THR


This directory contains the results on the fragmentation of the **Phenylalanyl-Threonine (PHE-THR)** dipeptide. The molecule has been manually fragmented into substructures, each capped with hydrogen atoms. We wanted to get an idea how close do we get to the actual energy value by capping the fragments, sum up all the fragments and then substracting contribution by H2.
---

## File Naming Convention

Each structure file is named according to the following pattern:

*PHE_THR_5_FragA_B.xyz*

Where:
- `A` > Index representing the **fragmentation pattern** (e.g., 1 to 4).
- `B` > Index of the **specific structure** within that fragmentation pattern.

Example:
- `PHE_THR_5_Frag2_3.xyz` corresponds to the **3rd structure** of **fragmentation pattern 2**.


## Ground Truth Energy

The **ground truth** for comparison is the **total energy** of the **entire PHE-THR peptide**, calculated using the same method applied to each fragment. To ensures consistent benchmarking across fragmentations.

## Methods and Flags Used

### Model: GFN2-xTB

We use the [**GFN2-xTB**](https://github.com/grimme-lab/xtb) model, a semi-empirical tight-binding method known for its reliable **energy predictions** of organic molecules, peptides, and biomolecular structures. The molecular structurs can be reviewed using [xyz2graph](https://github.com/zotko/xyz2graph) live demo where the contents of .xyz file can be pasted. 

`GFN2 -xTB --acc 1`  is used to set a tighter convergence threshold (accuracy) for SCC convergence. The number of after *acc* can be between 0.0001 to 1000 and lower the number more accurate calculation happens.

`GFN2 -xTB --opt`  is running the xTB model and then tries to optimize the geometry of peptide. Predicting a more realistic energy of the peptide after adding the hydrogen caps.
