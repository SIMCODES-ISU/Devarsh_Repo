# -*- coding: utf-8 -*-
"""Clustering .py

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1u0aRGGScVySdCYnmtbewXb8v7StcGF8e
"""

# !pip install xyz2graph
# !pip install "numpy<2.0"
# !pip install scipy
import matplotlib.pyplot as plt
from xyz2graph import MolGraph
from networkx.algorithms.community import louvain_communities, modularity
from networkx import adjacency_matrix
from scipy.sparse import csr_matrix
import networkx as nx
import numpy as np
import subprocess # Run xTB
import os         # Run xTB
import csv        # log information
import re         # for extracting output

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

def best_louvain_partition(graph, num_trials=10):
    best_modularity = -1
    best_partition = None

    for seed in range(num_trials):
            partition = louvain_communities(graph,resolution=0.1, seed=seed)
            mod_score = modularity(graph, partition)
            if mod_score > best_modularity:
              best_partition = partition
    return best_partition

def visualisation(communities,Graph):
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
  nx.draw_networkx_edges(Graph, pos, edgelist=edges_to_cut, edge_color='red', width=2) #funky at times

  plt.title("Molecular Graph with Communities and Cut Edges", fontsize=14)
  plt.axis('off')
  plt.tight_layout()
  plt.show()
  return edges_to_cut

# Steps for Spectral CLustering

def cut_ratio(Adj_Matrix, order, k):            # Assigns Cut score
    n = Adj_Matrix.shape[0]                     # Gets Number of Nodes
    edge_boundary = 0                           # Counter for number of edges to cut
    for i in range(k + 1):
        for j in range(k + 1, n):               # Counts number of edges between groups
            edge_boundary += Adj_Matrix[order[i], order[j]]
    denominator = min(k + 1, n - k - 1)         # Keeps balance of groups
    return edge_boundary / denominator

def spectral_cut2(A_dense):
    n = A_dense.shape[0]                        # Gets Number of Nodes
    degrees = A_dense.sum(axis=1)               # List of Degree of each node
    D = np.diag(degrees)                        # Makes diagonal matrix from Degree
    L = D - A_dense                             # Makes Lapacian Matrix
    w, v = np.linalg.eigh(L)                    # finds eigenvalues and eigenvectors
    order = np.argsort(v[:, np.argsort(w)[1]])  # Find second smallest eigenvector

    phi = np.zeros(n - 1)                       # List for Cut Scores
    for k in range(n - 1):                      # gets cut score for each node
      phi[k] = cut_ratio(A_dense, order, k)
    imin = np.argmin(phi)                       # finds node with smallest cut score

    return order[:imin + 1], order[imin + 1:],order,imin   # points before and after the cut point

def get_cut_edges(adj_matrix, order, imin):
    left = order[:imin + 1]
    right = order[imin + 1:]
    cut_edges = []
    for i in left:
        for j in right:
            if adj_matrix[i, j] != 0:         # From the cut point checks for edges
                cut_edges.append((i, j))
    return cut_edges

def viz_cut(G, s, pos=None, node_size=100, with_labels=False):
    n = G.number_of_nodes()
    assign = np.zeros(n)
    assign[s] = 1
    if pos is None:
        pos = nx.spring_layout(G)
    nx.draw(G, node_color=assign, pos=pos, with_labels=with_labels,
            cmap='spring', node_size=node_size, font_color='k')
    plt.show()

# Steps to write new fragment files

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
                  fragments[frag_idx].append(('H', h_position.tolist()))

    return fragments

def write_xyz_fragments(fragments, File_Path, model="ERR"):
    base_name = os.path.splitext(File_Path)[0]
    file_list = [File_Path]

    for idx, frag in enumerate(fragments):
        file_name = f"{base_name}_Frag_{model}_{idx+1}.xyz"
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
  fragment_list_LM = best_louvain_partition(Graph_LM)
  cut_edges_LM = visualisation(fragment_list_LM,Graph_LM)
  fragments_final_LM = get_fragment_atom_lists_with_caps(File_Path,fragment_list_LM,cut_edges_LM)
  print(fragments_final_LM)
  file_list_LM = write_xyz_fragments(fragments_final_LM,File_Path,"LM")
  return file_list_LM,cut_edges_LM

def Run_Spectral_Clustering(File_Path) :
  Matrix_SC = MakeAdjecencyMatrix(File_Path)           # Recieves Adj_Matrix from xyz file
  Graph_SC = nx.from_scipy_sparse_array(Matrix_SC)        # stores graph for later visualisation
  s1,s2,order,split_node=spectral_cut2(Matrix_SC.toarray())            # Runs the main Spectral Cut Function
  cut_edges_SC = get_cut_edges(Matrix_SC, order, split_node)    # Gets the cut edges (from imin)
  print("Edges to cut:", cut_edges_SC)
  s1_set,s2_set= set(s1),set(s2)
  fragment_list_SC=[s1_set,s2_set]
  viz_cut(Graph_SC, s1)                                # Sends Original Graph and Segmenatation Array to visualise
  fragments_final_SC = get_fragment_atom_lists_with_caps(File_Path,fragment_list_SC,cut_edges_SC)
  print(fragments_final_SC)
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
    time_match = re.search(r'wall-time:\s+\d+ d,\s+\d+ h,\s+\d+ min,\s+([\d.]+) sec', output)

    energy = float(energy_match.group(1)) if energy_match else None
    time = float(time_match.group(1)) if time_match else None

    return energy, time

def run_fragments(file_list,cut_edges):
    cap_correction_per_2h = 0.982686139534
    num_caps = len(cut_edges)
    cap_energy = cap_correction_per_2h * num_caps
    total_energy = cap_energy
    max_time = 0
    for frag in file_list:
      frag_output = subprocess.run(
                ["xtb", frag, "--gfn2"],
                capture_output=True,
                text=True
                ).stdout
      energy, time = extract_energy_and_time(frag_output)
      if energy is not None:
        total_energy += energy
        if time is not None:
          max_time = max(max_time, time)
    return total_energy, max_time

def run_xtb_and_log(file_list,cut_edges_LM,cut_edges_SC,csv_path="xtb_log.csv"): # name for CSV file

  base_file = file_list[0]
  fragment_files = file_list[1:]


  lm_fragments = [f for f in fragment_files if "_Frag_LM_" in f]    #Seperate out SC and LM
  sc_fragments = [f for f in fragment_files if "_Frag_SC_" in f]

  base_output = subprocess.run(
      ["xtb", base_file, "--gfn2"],
      capture_output=True,
      text=True).stdout
  base_energy, base_time = extract_energy_and_time(base_output) # Gets and stores ground output
  lm_energy, lm_max_time = run_fragments(lm_fragments,cut_edges_LM)  # runs for each fragment
  sc_energy, sc_max_time = run_fragments(sc_fragments,cut_edges_SC)

  row = [
        os.path.basename(base_file),
        base_energy,
        base_time,
        lm_energy,
        lm_max_time,
        sc_energy,
        sc_max_time
    ]
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
run_xtb_and_log(final_file_list,cut_edges_LM,cut_edges_SC)    # not accounted for capping hydrogen energy