from HFVRP import HFVRP
from AILS import AILS
from utils import read_file

from Heuristicas.h1 import h1
from Heuristicas.h2 import h2

def read_instance(filename):
    hfvrp = HFVRP()
    
    # Lê os dados do arquivo
    dimension, vertices, demands, capacities, fixed_costs, cost_coefs, quantities = read_file(filename)
    
    hfvrp.dimension = dimension
    
    # Adiciona vértices e demandas
    for id_, (x, y) in vertices.items():
        demand = demands.get(id_, 0)
        hfvrp.add_vertex(id_, x, y, demand)
    
    # Adiciona tipos de veículos
    for i in range(len(capacities)):
        hfvrp.add_vehicle_type(
            i+1,
            float(capacities[i]),
            float(fixed_costs[i]),
            float(cost_coefs[i]),
            int(quantities[i])
        )
    
    hfvrp.calculate_distances()
    return hfvrp

if __name__ == "__main__":
    # Lê a instância
    hfvrp = read_instance("Taillard_20.txt")

    print(hfvrp)
    
    # Configura e executa o AILS
    ails = AILS(hfvrp)
    # initial_solution = ails.construct_initial_solution()
    # print(initial_solution)
    # print(f"Custo: {ails._evaluate_solution(initial_solution)}")
    # local_search = ails.local_search(initial_solution)
    # print(local_search)
    # print(f"Custo: {ails._evaluate_solution(local_search)}")
    # perturbation = ails.perturbation_procedure(reference_solution=local_search,
    #                                             removal_heuristic=h2, alpha=1)
    # print(perturbation)
    # print(f"Custo: {ails._evaluate_solution(perturbation)}")

    solution, solution_info = ails.solve()
    print(solution)
    print(f"Custo: {ails._evaluate_solution(solution)}")
    print(solution_info)

    
