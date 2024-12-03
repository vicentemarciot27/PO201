import random
from HFVRP import HFVRP

# Random Removal
"""
Esta heurística consiste em remover ωH2 vértices escolhidos 
aleatoriamente da solução. É a estratégia mais simples de 
remoção, servindo como baseline para comparação com outras
heurísticas mais sofisticadas.
"""

def h2(hfvrp: HFVRP, routes: list[tuple[list[int], int]], omega: int) -> list[int]:
    # escolhe ωH2 vértices aleatórios
    vertices_to_remove = random.sample(hfvrp.Vc, omega * (len(routes) - 1))
    print("H2")
    print(f"Vertices to remove: {vertices_to_remove}")
    print(f"Routes: {routes}")
    return vertices_to_remove
