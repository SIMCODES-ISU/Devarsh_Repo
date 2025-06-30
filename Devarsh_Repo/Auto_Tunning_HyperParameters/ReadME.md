# Adaptive Molecular Clustering with xTB and Clustering Models

This project builds upon the capabilities of **`clustering_v1.3`**, enhancing it with an automated hyperparameter tuning script to optimize molecular fragmentation based on energy metrics from **xTB** calculations.

## Overview

This script leverages graph-based clustering algorithms to fragment molecular structures (from `.xyz` files) and optimize the parameters of each clustering method based on energy differences with respect to the unfragmented molecule. It uses:

- **Louvain Method (LM)** for community-based clustering
- **Spectral Clustering (SC)** based on Laplacian eigenvectors

The tuning is done via the `auto_tune_clustering()` function which:
- Iteratively adjusts thresholds, resolution (LM), or cluster counts (SC)
- Compares the total energy of fragmented molecules to the original
- Logs best-performing hyperparameter sets in **CSV files**
- Notes down both **converged** and **non-converged** runs

## Purpose

The goal is to find hyperparameters that minimize the energy difference between the original and fragmented molecule. Over time, this data can reveal **patterns in optimal clustering parameters**, allowing for:
- Faster and more informed clustering runs
- Predefined hyperparameter heuristics
- Better initialization for real-time applications

##  Results 

The Script is being ran for the whole `PEPCONF/bioactive/xyz` , 235 peptides the resultant csv files are added and are analyzed below. 

Important Stats:
1.  % which converged
2.  Which model is better SC/LM? add stats 
3.  Modes for Thershold and Resolution pairs - LM
4.  Modes for Threshold and Resolution pairs - SC
5.  Average Error in Energy after optimised 
