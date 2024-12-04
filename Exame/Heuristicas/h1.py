import random
from HFVRP import HFVRP

# Concentric Removal
"""
Esta estratégia remove um vértice vr escolhido aleatoriamente de uma rota da solução.
É chamada de concêntrica pois os vértices removidos estão dentro de um raio de
cobertura onde vr é o centro.
"""

def h1(hfvrp: HFVRP, routes: list[tuple[list[int], int]]) -> tuple[int, int]:
    # escolhe uma rota não vazia aleatoriamente
    non_empty_routes = [i for i, (route, _) in enumerate(routes) if len(route) > 2]
    if not non_empty_routes:
        raise ValueError("Não há rotas não vazias disponíveis")
    route_idx = random.choice(non_empty_routes)
    route = routes[route_idx][0]
    
    # escolhe apenas entre os vértices internos da rota (exclui primeiro e último)
    vertex_to_remove = random.choice(route[1:-1])
    
    return vertex_to_remove, route_idx
