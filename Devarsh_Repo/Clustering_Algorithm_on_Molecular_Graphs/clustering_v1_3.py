# -*- coding: utf-8 -*-
"""Clustering_V1.3.py

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1u0aRGGScVySdCYnmtbewXb8v7StcGF8e
"""

# !pip install xyz2graph
# !pip install "numpy<2.0"
# !pip install scipy
# !pip install joblib
# !pip install scikit-learn
import matplotlib.pyplot as plt
from xyz2graph import MolGraph
from networkx.algorithms.community import louvain_communities, modularity
from networkx import adjacency_matrix
from scipy.sparse import csr_matrix
from sklearn.cluster import KMeans
import networkx as nx
import numpy as np
import subprocess # Run xTB
import os         # Run xTB
import csv        # log information
import re         # for extracting output
from joblib import Parallel, delayed # Parallel runs for xTB

## Additions in version 1.3 :
# Added parallelization of xTB runs
# Added out_ to all outputed files
# Added minutes for wall_time
#  Add more clusters in spectral clustering
#  Have a soft cap of fragment size (keep if at max 60ish)

# Pre-Processing Inputs

def MakeGraph(File_Path):
  mg = MolGraph()
  mg.read_xyz(File_Path)
  G = mg.to_networkx()
  return(G)

def MakeAdjecencyMatrix(File_Path):
  mg = MolGraph()
  mg.read_xyz(File_Path)
  G = mg.to_networkx()
  A = adjacency_matrix(G)
  return(A)                   # Provides a Adj_Matrix to work with

# Steps for louvain method

def best_louvain_partition(graph,res=0.1,num_trials=10):
    best_modularity = -1
    best_partition = None

    for seed in range(num_trials*17):
            partition = louvain_communities(graph,resolution = res, seed=seed)
            mod_score = modularity(graph, partition)
            if mod_score > best_modularity:
              best_partition = partition
    return best_partition


# Steps for Spectral Clustering

def spectral_cut2(A_dense, number_of_clusters):
    n = A_dense.shape[0]                        # Gets Number of Nodes
    degrees = A_dense.sum(axis=1)               # List of Degree of each node
    D = np.diag(degrees)                        # Makes diagonal matrix from Degree
    L = D - A_dense                             # Makes Lapacian Matrix
    w, v = np.linalg.eigh(L)                    # finds eigenvalues and eigenvectors
    eigvecs = v[:, 1:number_of_clusters+1]
    kmeans = KMeans(n_clusters=number_of_clusters, n_init=100)
    labels = kmeans.fit_predict(eigvecs)

    cluster_dict={}
    index = 0
    labels = list(labels)
    for i in labels:
      if i not in cluster_dict:
        cluster_dict[i] = set()
      cluster_dict[i].add(index)
      index+=1
    fragments = list(cluster_dict.values())

    return fragments   # a list of sets of fragments

def compute_average_fragment_size(communities):
    return sum(len(c) for c in communities) / len(communities)

def adaptive_clustering(G,method, threshold = 60, max_attempts=10):    # placing a limit on maxium fragment size
    resolution = 0.1         # Initial value for Louvain
    num_clusters = 2         # Initial number for Spectral
    communities = []

    for attempt in range(max_attempts):
        if method == 'LM':
            communities = best_louvain_partition(G, resolution)
        elif method == 'SC':
            communities = spectral_cut2(G.toarray(), num_clusters)

        avg_size = compute_average_fragment_size(communities)

        if avg_size <= threshold:     # checks if fragment is small enough
            break
        # Update resolution or number of clusters
        if method == 'LM':
            resolution += 0.05  # Louvain is sensitive (small changes)
        elif method == 'SC':
            num_clusters += 1   # Higher k —> smaller clusters
    return communities


def visualisation(communities,Graph,Model = "ERR"):
  node_to_comm = {}               # More storage but faster look up
  comm_id = 0
  for comm in communities:      # divives all nodes into communites
    for node in comm:
        node_to_comm[node] = comm_id
    comm_id += 1

  edges_to_cut = []
  edges_to_keep = []
  for u, v in Graph.edges():
    if node_to_comm[u] != node_to_comm[v]:    #If connects 2 clusters
        edges_to_cut.append((u, v))
    else:
        edges_to_keep.append((u, v))

  print("Edges to cut between communities:",edges_to_cut) # pre-processing for grpahing above [don't remove]

  num_comms = len(communities)
  colors = plt.cm.tab10.colors  # up to 10 distinct colors
  node_colors = [colors[node_to_comm[n] % len(colors)] for n in Graph.nodes()]

  plt.figure(figsize=(8, 6))
  pos = nx.spring_layout(Graph, seed=42)  # position nodes with spring layout
  nx.draw_networkx_nodes(Graph, pos, node_color=node_colors, node_size=100)
  nx.draw_networkx_edges(Graph, pos, edgelist=edges_to_keep, edge_color='gray')
  nx.draw_networkx_edges(Graph, pos, edgelist=edges_to_cut, edge_color='red', width=2)

  plt.title("Graph with Communities and Cut Edges by "+ Model, fontsize=14)
  plt.axis('off')
  plt.tight_layout()
  plt.show()
  return edges_to_cut


def read_xyz(File_Path):            #auxiliary function
  with open(File_Path, 'r') as f:
        lines = f.readlines()
  atoms = []
  coords = []
  for line in lines[2:]:  # skip count and comment lines
      parts = line.strip().split()
      atoms.append(parts[0])
      coords.append(np.array([float(x) for x in parts[1:4]]))
  return atoms, coords

def get_fragment_atom_lists_with_caps(File_Path, fragment_list,cut_edges):
    atoms, coords = read_xyz(File_Path)

    fragments = [[] for _ in range(len(fragment_list))]

    for frag_idx in range(len(fragment_list)):
        fragment = fragment_list[frag_idx]
        for j in fragment:
            fragments[frag_idx].append((atoms[j], coords[j]))
            # Check cut edges involving atom j
            for edge in cut_edges:
                if j in edge:
                  other = edge[1] if edge[0] == j else edge[0]
                  bond_vector = np.array(coords[other]) - np.array(coords[j]) # using vector math to palce H(cap) at the right place
                  unit_vector = bond_vector / np.linalg.norm(bond_vector)
                  h_position = np.array(coords[j]) + 1 * unit_vector        # Closer to actual distance, helps Molgraph make a bond
                  fragments[frag_idx].append(('H', h_position.tolist()))    # Add Distance Dictionary here

    return fragments

def write_xyz_fragments(fragments, File_Path, model="ERR"):
    base_name = os.path.splitext(File_Path)[0]
    file_list = [File_Path]

    for idx, frag in enumerate(fragments):
        #file_name = f"{base_name}_Frag_{model}_{idx+1}.xyz"       # easier to run jobs
        file_name = f"out_{base_name}_Frag_{model}_{idx+1}.xyz"
        with open(file_name, "w") as f:
            f.write(f"{len(frag)}\n")                      # Line 1: number of atoms
            f.write(f"Fragment {idx+1}\n")                 # Line 2: comment
            for atom, coord in frag:
                x, y, z = coord
                f.write(f"{atom} {x:.3f} {y:.3f} {z:.3f}\n")
        file_list.append(file_name)

    return file_list

# Running the Algorithms and generating files


def Run_Louvain_Clustering(File_Path):
  Graph_LM = MakeGraph(File_Path)
  fragment_list_LM = adaptive_clustering(Graph_LM,"LM")   # allows to impsoe a limit on avg. fragment length
  cut_edges_LM = visualisation(fragment_list_LM,Graph_LM, "LM")
  fragments_final_LM = get_fragment_atom_lists_with_caps(File_Path,fragment_list_LM,cut_edges_LM)
  #print(fragments_final_LM)
  file_list_LM = write_xyz_fragments(fragments_final_LM,File_Path,"LM")
  return file_list_LM,cut_edges_LM

def Run_Spectral_Clustering(File_Path) :
  Matrix_SC = MakeAdjecencyMatrix(File_Path)           # Recieves Adj_Matrix from xyz file
  Graph_viz_SC = MakeGraph(File_Path)                  # Graph for visaulaisation run
  fragment_list_SC = adaptive_clustering (Matrix_SC,"SC")    # allows to impsoe a limit on avg. fragment length
  cut_edges_SC = visualisation(fragment_list_SC,Graph_viz_SC, "SC")
  #print(cut_edges_SC)
  fragments_final_SC = get_fragment_atom_lists_with_caps(File_Path,fragment_list_SC,cut_edges_SC)
  #print(fragments_final_SC)
  file_list_SC = write_xyz_fragments(fragments_final_SC,File_Path,"SC")
  return file_list_SC,cut_edges_SC

def merge_fragment_lists(list1, list2):
    # Combine and remove duplicates
    combined = list(set(list1 + list2))

    # Identify base file: the one without "_Frag_LM_" or "_Frag_SC_"
    base_candidates = [f for f in combined if "_Frag_LM_" not in f and "_Frag_SC_" not in f]
    if len(base_candidates) != 1:
        raise ValueError("Expected exactly one base file (without _Frag_LM_ or _Frag_SC_), found: " + str(base_candidates))

    base_file = base_candidates[0]

    # Get LM and SC fragment files
    lm_files = sorted([f for f in combined if "_Frag_LM_" in f])
    sc_files = sorted([f for f in combined if "_Frag_SC_" in f])

    return [base_file] + lm_files + sc_files

# Running the xTB Model and fetching outputs

def extract_energy_and_time(output):
    energy_match = re.search(r'TOTAL ENERGY\s+(-?\d+\.\d+)', output)
    time_match = re.search(r'wall-time:\s+\d+ d,\s+\d+ h,\s+(\d+)\s+min,\s+([\d.]+)\s+sec', output)


    energy = float(energy_match.group(1)) if energy_match else None
    time = (int(time_match.group(1)) * 60 + float(time_match.group(2))) if time_match else None # Now handels outputs in mins and seconds

    return energy, time

cap_correction_per_2h = 0.982686139534    # Define Gloabally so function can use joblib.parallel

def run_fragment(frag):
    frag_output = subprocess.run(
        ["xtb", frag, "--gfn2"],
        capture_output=True,
        text=True).stdout

    energy, time = extract_energy_and_time(frag_output)
    return energy, time

def run_fragments_joblib(file_list, cut_edges, n_jobs=8):    # depends on cpus per core requested
    cap_energy = cap_correction_per_2h * len(cut_edges)

    results = Parallel(n_jobs=n_jobs)(
        delayed(run_fragment)(frag) for frag in file_list)                       #initiates parallel runs for run_fragment (speeding up the process)

    total_energy = cap_energy
    max_time = 0
    for energy, time in results:
        if energy is not None:
            total_energy += energy
            if time is not None:
                max_time = max(max_time, time)
    return total_energy, max_time


def run_xtb_and_log(file_list, cut_edges_LM, cut_edges_SC, csv_path="xtb_log.csv"): # name for CSV file

  base_file = file_list[0]
  fragment_files = file_list[1:]


  lm_fragments = [f for f in fragment_files if "_Frag_LM_" in f]    #Seperate out SC and LM
  sc_fragments = [f for f in fragment_files if "_Frag_SC_" in f]

  base_output = subprocess.run(["xtb", base_file, "--gfn2"],capture_output=True,text=True).stdout
  base_energy, base_time = extract_energy_and_time(base_output) # Gets and stores ground output
  lm_energy, lm_max_time = run_fragments_joblib(lm_fragments,cut_edges_LM)  # runs for each fragment
  sc_energy, sc_max_time = run_fragments_joblib(sc_fragments,cut_edges_SC)

  row = [
        os.path.basename(base_file),
        base_energy,
        base_time,
        lm_energy,
        lm_max_time,
        sc_energy,
        sc_max_time]
  write_header = not os.path.exists(csv_path)
  with open(csv_path, "a", newline="") as f:
    writer = csv.writer(f)
    if write_header:
      writer.writerow([
                "base file name",
                "ground energy",
                "ground time",
                "cumulated fragment energy (LM)",
                "max fragment time (LM)",
                "cumulated fragment energy (SC)",
                "max fragment time (SC)"
            ])
    writer.writerow(row)

File_Path = input("File Path >")
LM_List,cut_edges_LM = Run_Louvain_Clustering(File_Path)
SC_List,cut_edges_SC = Run_Spectral_Clustering(File_Path)
final_file_list = merge_fragment_lists(LM_List,SC_List)
run_xtb_and_log(final_file_list,cut_edges_LM,cut_edges_SC)