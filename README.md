Devarsh_Repo [SIMCODES ISU]
==============================
This repository contains the experimental code writen for the project : Automating the fragmetnation of proteins for the SIMCODES REU program. This repositories code can be used as foundation and to make a protein fragmentation package once requirements are meet. 


#  Protein Fragmentation Project - Onboarding Guide

Welcome to the project! This guide will help you get up to speed with the goal, workflow, and first tasks to contribute effectively.


##  Problem Statement :

### In Layman's Terms:
Quantum chemical calculations on large biological molecules like proteins are extremely computationally expensive. To make these calculations feasible, we break down proteins into smaller fragments. QM energy calculation can be 0(n<sup> 7 </sup>), this means if we divided n (size of fragment) into 2 halfs it gives a ~99.22% reduction in computation time. However, this fragmentation must preserve chemical accuracy and should have similar total energy of all fragments to be useful.  

### In Mathematical Terms:
We aim to minimize the **average energy difference** introduced by fragmentation :
> **Objective**:  avg( |E_predicted(fragmented) - E_full(protein)| ) < 0.01 Hartree

We try to minimize energy differecne, while maximizing number of fragments!

##  Approach Overview

1. **Fragmentation by Graph Clustering**: Represent molecules as graphs and fragment them using clustering algorithms (e.g., Louvain, Spectral).
2. **Energy Estimation**: Use the xTB GFN2 method to compute energies of original and fragmented structures.
3. **Model Validation**: Track and minimize the difference in predicted energy between the full molecule and its fragments by adding features and experimenting.


##  Current Goal

> **Bring average energy difference < 0.01 Hartree**

Approaches which could he helpful (yet to be tried) :
-  Use stricter fragmentation rules (cut only if **C–C** or **C–O** bond).
-  Experiment with different clustering methods: [RDKit Butina Clustering](https://www.rdkit.org/docs/source/rdkit.ML.Cluster.Butina.html).
-  Once validated, scale approach to **larger peptides** and eventually **full proteins**.



##  Repository Walkthrough (Follow in Order)

| Sequence | Repository | Purpose |
|----------|-------------------|---------|
| 1 | `Devarsh_Repo/Testing_Fragmentation_and_H_Capping` | Hand Capping Fragmetns, good starting point for basic logic. |
| 2 | `Devarsh_Repo/Clustering_Algorithm_on_Molecular_Graphs` | Reade, clustering_V1.2.py and clustering_v1_3.py clustering logic |
| 3 | ` Devarsh_Repo/Auto_Tunning_HyperParameters` | Just go through readme for basic idea |
| 4 | `Devarsh_Repo/Tuning_Spectral_Clustering_Hyperparamters` | Hyperparameter tuning function (basic grid search implementation) |
| 5 | `Devarsh_Repo/SC_with_weights` | Go through readme, overall code structure is same as before. |
| 6 | `Devarsh_Repo/Testing_Weights_With_OpenBabel` | Go through readme, overall code structure is same as before. |



## First Tasks for New Collaborators

### Codebase Familiarization
- [ ] Explore all repositories listed above (readme.md files quite descriptive)

### Testing (Helps Familiarize with functions and pipeline)
- [ ] Write **pytest** unit tests for `clustering_v1.3.py`
    - Try edge cases like no file, invalid file, incorrect format, not an valid graph  
        - Check before accepting the file 
        - valid graph : nx.is_connected()
    - Double the molecule to expect almost double energy 
        - Add to detached peptides (offsetting ones coordinates )
        - Remove H’s and connect to same peptides 
    - Change the line ordering in file and expect same output (graph clustering should be independent of order)
        - Rewrite the main file in random offset and check for energy
        - Do the same things for the separate fragments(equating different ordering of same fragments) 
    - Count number of elements before and after (others same, H should increase by multiple of 2)
        - Make a dictionary for elements found before and after 
        - Elements which are not H should stay the same 
        - H should increase by the 2*len(cut_edges)
    - Try to rebuild original molecule from fragment files 
        - Add functionality to capping so that it doesn't change lenght while capping(when called by testing fucntion)
        - Compare the xyz files, look for duplicate entries and re-make original files 
        - Check for the same energy  
    - Add random but same offset to atom coordinates(energy should be preserved)
        - Add a random integer offset to coordinates of main and fragment file 
        - Equate the energy shouldn’t be any different 
    - Check total number of atoms,edges in the resultant fragment graphs
        - Do Graph.number_of_nodes() and Graph.number_of_edges
        - Nodes and edges should strictly increase after fragmenting 


###  Dataset
- [ ] Create a **Dev Set** of ~50 well-distributed peptides.
  - Aim: ~15 minutes runtime for iterative testing of features. (Full dataset validation might take upwards of 36-48 hours!)

###  Environment & HPC Setup
- [ ] Write a **Bash script** to:
  - Setup a Conda environment on Nova.
- [ ] Write a **SLURM script** to:
  - Submit jobs on **Nova HPC cluster** (not Nova OnDemand).
  - Refer to: https://www.hpc.iastate.edu/guides/nova


##  Concepts to Read Up On

| Topic | Notes |
|-------|-------|
| `xTB GFN2` | Quantum chemistry method used for energy estimation. |
| `Louvain & Spectral Clustering` | Graph-based clustering for fragment generation. |
| `Butina Clustering` | Similarity-based clustering provided by RDKit. |
| `joblib.delayed & parallelization` | Efficient multiprocessing for model runs. |


We’re excited to have you on board let's accelerate protein modeling together! 

### Copyright

Copyright (c) 2025, Devarsh Shroff


#### Acknowledgements
 
Project based on the 
[Computational Molecular Science Python Cookiecutter](https://github.com/molssi/cookiecutter-cms) version 1.11.
