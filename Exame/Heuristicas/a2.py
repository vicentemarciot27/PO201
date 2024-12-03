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
    vertex_to_insert = int(vertex_to_insert)
    min_cost = float('inf')
    best_pos = None
    best_route_idx = None

    for route_idx, (route, vehicle_type) in enumerate(routes):
        # Caso especial: rota com apenas um cliente
        if len(route) == 3 and route[0] == route[2] == 1:
            # Pula se o vértice a ser inserido já está na rota
            if vertex_to_insert == route[1]:
                best_route_idx = route_idx
                best_pos = 1
                continue
                
            cost = (hfvrp.distances[(1, vertex_to_insert)] + 
                   hfvrp.distances[(vertex_to_insert, route[1])] - 
                   hfvrp.distances[(1, route[1])])
            if cost < min_cost:
                min_cost = cost
                best_pos = 1  # Inserir entre o depósito e o único cliente
                best_route_idx = route_idx
                continue

        # Código original para rotas maiores
        for j in range(len(route) - 1):
            if route[j] == route[j+1] == 1:
                continue
            cost = (hfvrp.distances[(route[j], vertex_to_insert)] + 
                   hfvrp.distances[(vertex_to_insert, route[j+1])] - 
                   hfvrp.distances[(route[j], route[j+1])])
            
            if cost < min_cost:
                min_cost = cost
                best_pos = j + 1
                best_route_idx = route_idx
                
    return best_route_idx, best_pos
    
