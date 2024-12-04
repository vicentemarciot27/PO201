from HFVRP import HFVRP

def a1(hfvrp: HFVRP, routes: list[tuple[list[int], int]], vertex_to_insert: int) -> tuple[int, float]:
    """ This heuristic consists of inserting a vertex vi between vertices vˆj and vˆj+1, such that vˆj = arg minj∈Vp(vi) di,j.
    """
    # Procura por rotas vazias primeiro
    for route_idx, (route, vehicle_type) in enumerate(routes):
        if len(route) == 2:  # Rota só com depósito
            if hfvrp.demands[vertex_to_insert] <= hfvrp.vehicle_capacity[vehicle_type]:
                return route_idx, 1

    # find smallest distance from vertex to insert to any vertex in the route
    min_dist = float('inf')
    best_pos = None
    best_route_idx = None
    
    # Percorre cada rota
    for route_idx, (route, vehicle_type) in enumerate(routes):

        # check if vertex demand + total route demand > vehicle capacity
        if hfvrp.demands[vertex_to_insert] + sum(hfvrp.demands[v] for v in route if v != hfvrp.depot) > hfvrp.vehicle_capacity[vehicle_type]:
            continue

        for j in range(len(route) - 1):
            # Calcula a distância do vértice atual ao vértice a ser inserido
            dist = hfvrp.distances[(route[j], vertex_to_insert)]
            if dist < min_dist:
                min_dist = dist
                best_pos = j + 1  # Posição após o vértice mais próximo
                best_route_idx = route_idx
    
    return best_route_idx, best_pos