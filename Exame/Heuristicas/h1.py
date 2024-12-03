import random
from HFVRP import HFVRP

# Concentric Removal

"""
Esta estratégia remove um vértice vr escolhido aleatoriamente e os ωH1 - 1 vértices
mais próximos a ele. É chamada de concêntrica pois os vértices removidos estão
dentro de um raio de cobertura onde vr é o centro.
"""

def h1(hfvrp: HFVRP, routes: list[tuple[list[int], int]], omega: int) -> tuple[int, list[int]]:
    # escolhe um vértice aleatório
    vr = random.choice(hfvrp.Vc)
    
    # cria lista de tuplas (distância, vértice)
    vertices_distances = [(hfvrp.distances[(vr, v)], v) for v in hfvrp.Vc if v != vr]
    
    # ordena pela distância e pega os ωH1 - 1 mais próximos
    vertices_distances.sort()  # ordena pelo primeiro elemento da tupla (distância)
    vertices_to_remove = [v for _, v in vertices_distances[:omega * (len(routes) - 1)]]
    
    print("H1")
    print(f"Vertices to remove: {vertices_to_remove}")
    print(f"Routes: {routes}")
    
    return vr, vertices_to_remove
