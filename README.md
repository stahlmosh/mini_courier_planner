# Mini-Courier Planner (ETCCDA302 Capstone)

A Python prototype for **Design & Analysis of Algorithms (ETCCDA302)** that prioritizes parcels, selects an optimal load for a single delivery trip, computes shortest paths, builds a delivery route, and benchmarks stage runtimes across input sizes.

## Phase 1: Design & Architecture
- **Parcel attributes:** `id`, `dest` (target node), `weight` (kg), `value` (utility score), `priority` (1–5, 5 = highest), and `deadline_hr`.
- **Graph format:** Weighted adjacency list (`dict[node_id, list[[neighbor_id, distance_km]]]`) with `"DEPOT"` as the starting and ending point.
- **Pipeline flow:**
  1. **Merge Sort** sorts parcels by highest priority, earliest deadline, then parcel ID.
  2. **0/1 Knapsack (Dynamic Programming)** picks the highest-value parcel subset within vehicle weight capacity.
  3. **Dijkstra's Algorithm** finds shortest paths and distances between nodes.
  4. **Nearest-Neighbor TSP** orders the unique selected stops starting and ending at `DEPOT`.

## How to Run in VS Code
1. Open the project folder in VS Code.
2. Make sure `data/parcels.json` and `data/graph.json` are in place.
3. Open the integrated terminal (`Ctrl + `` ` ``) and run:
   ```bash
   python courier_planner.py
