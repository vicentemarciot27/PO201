import random
from HFVRP import HFVRP

# Random Removal
"""
Esta heurística consiste em remover um vértice aleatório de uma rota da solução.
É a estratégia mais simples de remoção, servindo como baseline para comparação com outras
heurísticas mais sofisticadas.
"""

def h2(hfvrp: HFVRP, routes: list[tuple[list[int], int]]) -> list[int]:
    # escolhe uma rota não vazia aleatoriamente
    non_empty_routes = [i for i, (route, _) in enumerate(routes) if len(route) > 2]
    if not non_empty_routes:
        raise ValueError("Não há rotas não vazias disponíveis")
    route_idx = random.choice(non_empty_routes)
    route = routes[route_idx][0]
    # escolhe apenas entre os vértices internos da rota (exclui primeiro e último)
    vertex_to_remove = random.choice(route[1:-1])
    return vertex_to_remove, route_idx
