from HFVRP import HFVRP

def a1(hfvrp: HFVRP, routes: list[tuple[list[int], int]], vertex_to_insert: int) -> tuple[int, float]:
    """ This heuristic consists of inserting a vertex vi between vertices vˆj and vˆj+1, such that vˆj = arg minj∈Vp(vi) di,j.
    """
    # find smallest distance from vertex to insert to any vertex in the route
    min_dist = float('inf')
    best_pos = None
    best_route_idx = None
    
    # Percorre cada rota
    for route_idx, (route, vehicle_type) in enumerate(routes):
        # Caso especial: rota com apenas um cliente
        if len(route) == 3 and route[0] == route[2] == 1:
            # Pula se o vértice a ser inserido já está na rota
            if vertex_to_insert == route[1]:
                best_route_idx = route_idx
                best_pos = 1
                break
                
            dist = (hfvrp.distances[(1, vertex_to_insert)] + 
                   hfvrp.distances[(vertex_to_insert, route[1])])
            if dist < min_dist:
                min_dist = dist
                best_pos = 1  # Inserir entre o depósito e o único cliente
                best_route_idx = route_idx
                continue

        # Código para rotas maiores
        for j in range(len(route) - 1):
            if route[j] == route[j+1] == 1:
                continue
            # Calcula a distância do vértice atual ao vértice a ser inserido
            dist = hfvrp.distances[(route[j], vertex_to_insert)]
            if dist < min_dist:
                min_dist = dist
                best_pos = j + 1  # Posição após o vértice mais próximo
                best_route_idx = route_idx
                
    return best_route_idx, best_pos