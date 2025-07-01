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
For Bioactive peptides, `Spectral Clustering ` seems to be a superior method, we could test it out for all the peptides provided in `PEPCONF/bioactive/xyz` and can find a method which is better for all use cases. 

### Spectral Clustering 

-  77 Peptides converged to target energy differecne out of 235 (Success rate of 32%)
-  We can use this table to speed up calculations and to initialize the Spectral Clustering Model
 
 #### Most Frequent Parameter Pairs (SC)

| Threshold, Num Clusters   | Frequency |
|---------|-----------|
| 40,2    | 21        |
| 45,2    | 20        |
| 50,2    | 17        |
| 40,5    | 15        |
| 40,6    | 13        |
| 40,4    | 12        |
| 40,3    | 9         |
| 40,15   | 8         |
| 40,8    | 8         |
| 75,2    | 8         |
| 40,14   | 7         |
| 70,15   | 6         |
| 80,2    | 6         |
| 40,11   | 5         |
| 85,15   | 5         |
| 40,12   | 4         |
| 40,13   | 4         |
| 50,10   | 4         |
| 40,10   | 4         |
| 50,7    | 4         |

>  **Entries Covered**: 180  
>  **Optimal Values Found For**: 76.50% of entries

![SC scatter plot ](https://github.com/user-attachments/assets/16a5a89c-2478-47ee-b2dd-d2fb262b02b1)


 ### Louvian Method 

-  72 Peptides converged to target energy differecne out of 235 (Success rate of 30.6%)
-  We can use this table to speed up calculations and to initialize the Louvian Method Clustering Model
 
 #### Most Frequent Parameter Pairs (LM)

| Resolution, Threshold | Frequency |
|------------|-----------|
| 0.1,40     | 39        |
| 0.2,40     | 34        |
| 0.3,40     | 8         |
| 1.2,40     | 8         |
| 1.2,50     | 8         |
| 1,40       | 7         |
| 0.4,40     | 7         |
| 0.5,40     | 7         |
| 0.8,40     | 6         |
| 3,40       | 6         |
| 3,70       | 6         |
| 0.9,40     | 5         |
| 3,50       | 5         |
| 2.9,40     | 4         |
| 3,45       | 4         |
| 1.6,40     | 3         |
| 3,85       | 3         |
| 1.2,60     | 3         |
| 2.7,50     | 3         |
| 2.2,40     | 3         |

> **Entries Covered**: 169  
> **Optimal Values Found For**: 66%

![LM Scatter Plot ](https://github.com/user-attachments/assets/80689025-b30a-4e59-b04d-49517afbeff0)


 
