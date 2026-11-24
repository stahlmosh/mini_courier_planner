import heapq
import json
import math
import os
import random
import time


# --- Phase 2: Merge Sort ---
def merge_sort_parcels(parcels, key_fn):
    if len(parcels) <= 1:
        return parcels[:]
    mid = len(parcels) // 2
    left = merge_sort_parcels(parcels[:mid], key_fn)
    right = merge_sort_parcels(parcels[mid:], key_fn)
    return _merge(left, right, key_fn)


def _merge(left, right, key_fn):
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if key_fn(left[i]) <= key_fn(right[j]):
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


# --- Phase 2: 0/1 Knapsack (Dynamic Programming) ---
def knapsack_01_dp(parcels, capacity):
    n = len(parcels)
    W = int(round(capacity))
    dp = [[0] * (W + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        w_i = int(round(parcels[i - 1]["weight"]))
        v_i = int(round(parcels[i - 1]["value"]))
        for w in range(W + 1):
            if w_i <= w:
                dp[i][w] = max(dp[i - 1][w], dp[i - 1][w - w_i] + v_i)
            else:
                dp[i][w] = dp[i - 1][w]

    # Backtrack to recover chosen parcels
    selected = []
    w = W
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            item = parcels[i - 1]
            selected.append(item)
            w -= int(round(item["weight"]))
    selected.reverse()

    return dp[n][W], selected


# --- Phase 3: Dijkstra's Shortest Path ---
def dijkstra(graph, start):
    dist = {node: float("inf") for node in graph}
    prev = {node: None for node in graph}
    dist[start] = 0.0
    pq = [(0.0, start)]

    while pq:
        d_u, u = heapq.heappop(pq)
        if d_u > dist[u]:
            continue
        for v, w in graph.get(u, []):
            nd = d_u + w
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
    return dist, prev


def get_path(prev, start, end):
    if start == end:
        return [start]
    path = []
    curr = end
    while curr is not None:
        path.append(curr)
        if curr == start:
            break
        curr = prev.get(curr)
    if not path or path[-1] != start:
        return []
    path.reverse()
    return path


# --- Phase 3: Nearest-Neighbor TSP Approximation ---
def nearest_neighbor_tsp(depot, stops, dist_matrix):
    unvisited = list(dict.fromkeys(stops))  # unique stops preserving order
    curr = depot
    route = [depot]
    legs = []
    total_dist = 0.0

    while unvisited:
        nxt = min(unvisited, key=lambda node: dist_matrix[curr][node])
        leg_d = dist_matrix[curr][nxt]
        if math.isinf(leg_d):
            raise ValueError(f"No path from {curr} to {nxt}")
        legs.append((curr, nxt, leg_d))
        total_dist += leg_d
        route.append(nxt)
        unvisited.remove(nxt)
        curr = nxt

    if curr != depot:
        ret_d = dist_matrix[curr][depot]
        if math.isinf(ret_d):
            raise ValueError(f"No return path from {curr} to {depot}")
        legs.append((curr, depot, ret_d))
        total_dist += ret_d
        route.append(depot)

    return route, legs, total_dist


# --- Phase 4: Benchmark Across Input Sizes ---
def run_benchmarks(sizes=(10, 25, 50, 100), capacity=30):
    random.seed(42)
    rows = []

    for n in sizes:
        num_nodes = max(8, n // 2 + 4)
        nodes = ["DEPOT"] + [f"N{i}" for i in range(1, num_nodes)]
        parcels = [
            {
                "id": f"P{i+1:03d}",
                "dest": random.choice(nodes[1:]),
                "weight": random.randint(1, 10),
                "value": random.randint(20, 200),
                "priority": random.randint(1, 5),
                "deadline_hr": round(random.uniform(1.0, 12.0), 1),
            }
            for i in range(n)
        ]

        graph = {u: [] for u in nodes}
        for i in range(1, num_nodes):
            u, v = nodes[i - 1], nodes[i]
            w = round(random.uniform(2.0, 10.0), 1)
            graph[u].append([v, w])
            graph[v].append([u, w])
        for _ in range(num_nodes * 2):
            u, v = random.sample(nodes, 2)
            if all(nb != v for nb, _ in graph[u]):
                w = round(random.uniform(2.0, 12.0), 1)
                graph[u].append([v, w])
                graph[v].append([u, w])

        t0 = time.perf_counter()
        sp = merge_sort_parcels(parcels, lambda p: (-p["priority"], p["deadline_hr"], p["id"]))
        t1 = time.perf_counter()
        _, sel = knapsack_01_dp(sp, capacity)
        t2 = time.perf_counter()
        dm = {u: dijkstra(graph, u)[0] for u in nodes}
        t3 = time.perf_counter()
        _, _, _ = nearest_neighbor_tsp("DEPOT", [p["dest"] for p in sel], dm)
        t4 = time.perf_counter()

        rows.append((
            n,
            (t1 - t0) * 1000,
            (t2 - t1) * 1000,
            (t3 - t2) * 1000,
            (t4 - t3) * 1000,
        ))

    print("\n=== Phase 4: Runtime Benchmark (ms) ===")
    print(f"{'n':>4} | {'Sort':>9} | {'Knapsack':>9} | {'Dijkstra':>9} | {'NN-TSP':>9}")
    print("-" * 52)
    for n, s_ms, k_ms, d_ms, r_ms in rows:
        print(f"{n:>4} | {s_ms:>9.4f} | {k_ms:>9.4f} | {d_ms:>9.4f} | {r_ms:>9.4f}")

    # Optional chart if matplotlib is installed
    try:
        import matplotlib.pyplot as plt

        os.makedirs("outputs", exist_ok=True)
        ns = [r[0] for r in rows]
        plt.figure(figsize=(8, 4.5))
        plt.plot(ns, [r[1] for r in rows], marker="o", label="Merge Sort")
        plt.plot(ns, [r[2] for r in rows], marker="s", label="0/1 Knapsack DP")
        plt.plot(ns, [r[3] for r in rows], marker="^", label="All-Pairs Dijkstra")
        plt.plot(ns, [r[4] for r in rows], marker="d", label="Nearest-Neighbor TSP")
        plt.title("Mini-Courier Planner Stage Runtimes")
        plt.xlabel("Number of Parcels (n)")
        plt.ylabel("Time (ms)")
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.legend()
        plt.tight_layout()
        plt.savefig("outputs/runtime_chart.png", dpi=150)
        print("\nSaved chart to outputs/runtime_chart.png")
    except ImportError:
        print("\n(Tip: install matplotlib to auto-save outputs/runtime_chart.png)")


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base_dir, "data", "parcels.json"), "r") as f:
        parcels = json.load(f)
    with open(os.path.join(base_dir, "data", "graph.json"), "r") as f:
        graph = json.load(f)

    capacity = 15
    depot = "DEPOT"

    # Phase 2
    sorted_parcels = merge_sort_parcels(
        parcels, key_fn=lambda p: (-p["priority"], p["deadline_hr"], p["id"])
    )
    max_val, selected = knapsack_01_dp(sorted_parcels, capacity)

    # Phase 3
    dist_matrix = {}
    prev_maps = {}
    for u in graph:
        dist_matrix[u], prev_maps[u] = dijkstra(graph, u)

    stops = [p["dest"] for p in selected]
    route, legs, total_km = nearest_neighbor_tsp(depot, stops, dist_matrix)

    print("=== Sorted Parcels (Priority Desc, Deadline Asc) ===")
    for p in sorted_parcels:
        print(f"  {p['id']} -> {p['dest']} | prio={p['priority']} | deadline={p['deadline_hr']}h | wt={p['weight']}kg | val={p['value']}")

    print(f"\n=== Selected Trip Load (Capacity={capacity}kg, Max Value={max_val}) ===")
    for p in selected:
        print(f"  {p['id']} -> {p['dest']} (wt={p['weight']}kg, val={p['value']})")

    print("\n=== Delivery Route ===")
    print("  Route:", " -> ".join(route))
    for u, v, d in legs:
        path_str = " -> ".join(get_path(prev_maps[u], u, v))
        print(f"  {u} -> {v}: {d:.1f} km (path: {path_str})")
    print(f"  Total Distance: {total_km:.1f} km")

    run_benchmarks()


if __name__ == "__main__":
    main()
