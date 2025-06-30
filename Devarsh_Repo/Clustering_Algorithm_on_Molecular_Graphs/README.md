# Molecular Fragmentation via Graph Clustering

This repository contains a Python code for fragmenting molecular .xyz files using graph-based clustering techniques (Louvain and Spectral 
clustering). It visualizes clusters, identifies inter-cluster bonds, caps fragment ends with hydrogen, generates new .xyz fragment files, 
and evaluates energies via xTB calculations.

## Features

- Converts `.xyz` molecules into graph representations.
- Applies **Louvain community detection** and **Spectral clustering** to identify molecular substructures.
- Determines which bonds to "cut" between clusters.
- Adds hydrogen atoms at cut sites to preserve chemical valency.
- Generates new capped `.xyz` fragments.
- Runs **xTB** energy calculations on the original and fragment systems.
- Logs fragment energies and runtimes into a `.csv`.

## Requirments
```
pip install xyz2graph
pip install "numpy<2.0"
pip install scipy
pip install matplotlib
pip install networkx
pip install joblib
pip install scikit-learn
```
Also a working Conda environment is needed with `xTB` installed to run the calculations.

## How it works 

1. Graph Construction
     - `MakeGraph()` and `MakeAdjecencyMatrix()` use xyz2graph to parse the molecule and represent it as a networkx graph
        and adjacencymatrix.

2. Louvain Clustering
     - `best_louvain_partition()` finds the optimal community partition (highiest modularity).

     - `visualisation()` plots the graph, highlighting intra- and inter-cluster edges.

     - `Run_Louvain_Clustering(`) handles the full process for Louvain clustering using the Louvain_communtiy package in networkx.

3. Spectral Clustering
     - `spectral_cut2()` computes the graph Laplacian and uses the second-smallest eigenvector to determine the best binary cut.

     - `get_cut_edges()` identifies inter-cluster edges.

     - `viz_cut()` visualizes spectral clustering results.

     - `Run_Spectral_Clustering()` wraps the process.

4. Fragment Creation with Hydrogen Caps
     - `get_fragment_atom_lists_with_caps() ` adds hydrogen atoms at cut points to preserve molecular nature.

     - `write_xyz_fragments()` writes .xyz files for each capped fragment.

5. xTB Energy Calculations
     - `run_fragments()` computes energy for each fragment and applies a correction for capping hydrogens.

     - `run_xtb_and_log()` computes base and fragment energies and logs results to xtb_log.csv.
       
  
xtb-log.csv is the ouput for running the program on 20 randomly slected proteins/peptides. 

## Features Added in v1.3

1. Parallelization of xTB Runs with Joblib

- Utilized `joblib.Parallel` and `delayed` to run multiple xTB energy calculations concurrently, significantly reduces total runtime, especially when dealing with multiple fragments.

2. Prefixed Output Files with out_

 - All generated output files are now prefixed with `out_` This makes it easier to distinguish between input and output files and simplifies batch job scheduling or cleanup.

3. Wall Time Now Includes Minutes

 - The wall time for jobs is now reported in both minutes and seconds for more precise time tracking.

4. Increased Flexibility in Spectral Clustering
   
- The number of clusters in Spectral Clustering is now more configurable. Clustering is improved by using `KMeans` on the eigenvectors of the Laplacian matrix, allowing for more control over fragment generation.

5. Soft Cap on Fragment Size (~60 Atoms)

- Introduced a average "soft" upper limit for fragment sizes (around 60 atoms).

- Helps maintain reasonable computational cost per fragment and ensures balanced distribution in clustering.

