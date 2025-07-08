# Spectral Clustering Hyperparameter Tuning for Molecular Fragmentation


This repository explores how the number of clusters (K) affects the energy difference after fragmenting molecular structures using spectral clustering. We ran the analysis on two datasets:
- **Dipeptides** (smaller, simpler molecules)
- **Bioactives** (larger, more complex molecules)

The goal is to determine **optimal clustering parameters** to minimize energy difference after fragmentation, helping us better tune fragmentation strategies for different molecule types.


## How Cluster Number Is Decided

We use a dynamic strategy for choosing a range of cluster numbers based on the **size of the molecular graph**.

```python
def get_num_clusters_list(graph_size, min_clusters=2, min_frag_size=13, max_clusters_buffer=7):
    if graph_size < min_frag_size:
        # If graph is very small, limit cluster numbers strictly
        return list(range(2, min(5, graph_size)))

    # Maximum clusters should never exceed number of nodes - 1
    max_clusters = min(graph_size - 1, graph_size // min_frag_size + max_clusters_buffer)

    # Construct the cluster list with a wide spread
    num_clusters_list = list(range(min_clusters, max_clusters + 1))

    return num_clusters_list
```
> Explanation:
> For small graphs (less than 13 atoms), we restrict clustering to 2–4 and for larger molecules, we compute max_clusters dynamically.
> It is bounded by (graph_size // min_frag_size) + buffer to ensures we don’t over-fragment small molecules or under-fragment large ones. Returns a spread-out list of cluster counts to explore in the hyperparameter tuning

## Results
Running the script `spectral_clustering_hyperparameter_tuning.py` generates:
- `.csv` files that log:
    - File Name
    - Number of Clusters
    - Total Energy
    - Energy Difference

## Observations from the Plots

Heatmaps and scatter plots visualizing energy differences across different cluster counts.

![SC_seperate ranking scatter plot (Dipeptide)](https://github.com/user-attachments/assets/b78e60a9-373b-4d35-9aca-273c9582fd84)

![SC_seperate ranking Heatmap (Dipeptide)](https://github.com/user-attachments/assets/0f539478-98a8-46b1-aba1-c3d22de0436d)



### Dipeptide Molecules (simpler, compact)
- **Heatmap:** Optimal results are clustered around 3–6 clusters.
- **Scatter Plot:**  A concave-up trend, suggesting the sweet spot is around 4–6 clusters. Very low energy differences in this region.

![SC_seperate ranking scatter plot (Bioactive)](https://github.com/user-attachments/assets/74acb152-8b2c-4150-aa8f-d7bfb3186c95)

![SC_seperate ranking heatmap  (Bioactive)](https://github.com/user-attachments/assets/f966bf0d-de24-4310-b93a-88df80ad26d8)


### Bioactive Molecules (larger, diverse)
- **Heatmap:** Best results seen at clusters 3, 5, 7. Peaks (bad results) at clusters 8 and 11.
- **Scatter Plot:** Clusters 2 and 8 have high variance in energy difference.Clusters 2–7 and 12–14 have lower energy difference, but no single best parameter.


