from HFVRP import HFVRP

# A2: Insertion by Cost
"""
Esta heurística consiste em inserir um vértice vi entre dois vértices adjacentes vj e vj+1,
de forma que vj seja o vértice que minimize o custo adicional da inserção, dado por:
    ci,j + ci,j+1 - cj,j+1
onde:
- ci,j é o custo entre os vértices i e j
- ci,j+1 é o custo entre os vértices i e j+1  
- cj,j+1 é o custo entre os vértices j e j+1
"""

def a2(hfvrp: HFVRP, routes: list[tuple[list[int], int]], vertex_to_insert: int) -> tuple[int, float]:

    # Procura por rotas vazias primeiro
    for route_idx, (route, vehicle_type) in enumerate(routes):
        if len(route) == 2:  # Rota só com depósito
            if hfvrp.demands[vertex_to_insert] <= hfvrp.vehicle_capacity[vehicle_type]:
                return route_idx, 1

    # find smallest cost from vertex to insert to any vertex in the route
    min_cost = float('inf')
    best_pos = None
    best_route_idx = None
    
    # Percorre cada rota
    for route_idx, (route, vehicle_type) in enumerate(routes):

        # check if vertex demand + total route demand > vehicle capacity
        if hfvrp.demands[vertex_to_insert] + sum(hfvrp.demands[v] for v in route if v != hfvrp.depot) > hfvrp.vehicle_capacity[vehicle_type]:
            continue

        for j in range(len(route) - 1):
            # Calcula o custo considerando o coeficiente do veículo
            custo_atual = hfvrp.distances[(route[j], route[j+1])] * hfvrp.vehicle_cost_coef[vehicle_type]
            custo_novo = (hfvrp.distances[(route[j], vertex_to_insert)] * hfvrp.vehicle_cost_coef[vehicle_type] +
                         hfvrp.distances[(vertex_to_insert, route[j+1])] * hfvrp.vehicle_cost_coef[vehicle_type])
            
            # Custo incremental é a diferença entre o novo custo e o custo atual
            cost = custo_novo - custo_atual
            
            if cost < min_cost:
                min_cost = cost
                best_pos = j + 1  # Posição após o vértice mais próximo
                best_route_idx = route_idx
                
    return best_route_idx, best_pos
    
