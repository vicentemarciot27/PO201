import typing
import random
import math

# Internal imports
from HFVRP import HFVRP
from Heuristicas.a1 import a1
from Heuristicas.a2 import a2
from Heuristicas.h1 import h1
from Heuristicas.h2 import h2
from AILSUtils.choose_vehicle import choose_vehicle

class AILS:
    def __init__(self, hfvrp: HFVRP, config: typing.Optional[dict] = None):
        self.hfvrp = hfvrp
        self.config = config or {}
        
        # Melhor solução encontrada
        self.best_solution = None
        self.best_value = float('inf')
        
        # Solução de referência
        self.reference_solution = None
        
        # Parâmetros de controle
        self.removal_heuristics = ['h2']  # Lista de heurísticas de remoção disponíveis
        self.diversity_controls = {}  # Parâmetros de controle de diversidade por heurística
        
    def construct_initial_solution(self):
        iteration = 0
        while True:  # tenta até encontrar uma solução viável
            iteration += 1
            if iteration % 1000 == 0:
                print(f"Iteration {iteration}")
                input("Pressione Enter para continuar...")
                
            vertices_nao_atendidos = list(self.hfvrp.Vc)
            routes = []
            
            # Calcula m (número mínimo de rotas)
            total_demand = sum(self.hfvrp.demands[v] for v in self.hfvrp.Vc)
            max_capacity = max(self.hfvrp.vehicle_capacity[t] for t in self.hfvrp.T)
            m = math.ceil(total_demand / max_capacity)
            
            # cria rotas iniciais
            for _ in range(m):
                v1 = random.choice(vertices_nao_atendidos)
                route = [self.hfvrp.depot, v1, self.hfvrp.depot]
                vehicle = choose_vehicle(self, route)
                
                # Se não encontrou veículo disponível, tenta novamente
                if vehicle is None:
                    continue
                    
                routes.append((route, vehicle))
                vertices_nao_atendidos.remove(v1)

            print(f"Rotas iniciais: {routes}")
            
            # adiciona os vértices restantes
            try:
                tentativas = 0
                max_tentativas = m * len(vertices_nao_atendidos)
                while vertices_nao_atendidos and tentativas < max_tentativas:
                    v = random.choice(vertices_nao_atendidos)
                    best_route_idx, best_pos = a1(self.hfvrp, routes, v)
                    route = routes[best_route_idx][0]
                    route.insert(best_pos, v)
                    
                    # Verifica se a rota continua viável após inserção
                    if not self.hfvrp.check_route_feasibility(route, routes[best_route_idx][1]):
                        route.remove(v)  # Desfaz a inserção
                        tentativas += 1
                        continue
                        
                    vertices_nao_atendidos.remove(v)
                    
                # verifica viabilidade final
                if all(self.hfvrp.check_route_feasibility(route, vehicle) 
                       for route, vehicle in routes):
                    print("Solução viável encontrada!")
                    return routes
                else:
                    print("Solução inviável encontrada")
                    continue
            except Exception as e:
                print(f"Erro ao construir solução: {str(e)}")
                continue  # se algo der errado, tenta novamente


    def local_search(self, solution, max_iterations=1000):
        """
        Aplica busca local à solução usando movimentos 1-interchange e 2-opt*.
        """
        improved = True
        iteration = 0
        while improved and iteration < max_iterations:
            improved = False
            best_solution = solution
            best_value = self._evaluate_solution(solution)
            
            # 1-Interchange
            for i, (route_i, vehicle_i) in enumerate(solution):
                for j, (route_j, vehicle_j) in enumerate(solution):
                    if i == j:
                        continue
                    
                    for pos_i in range(1, len(route_i) - 1):
                        for pos_j in range(1, len(route_j) - 1):
                            new_route_i = route_i[:pos_i] + [route_j[pos_j]] + route_i[pos_i + 1:]
                            new_route_j = route_j[:pos_j] + [route_i[pos_i]] + route_j[pos_j + 1:]
                            
                            if (self.hfvrp.check_route_feasibility(new_route_i, vehicle_i) and
                                    self.hfvrp.check_route_feasibility(new_route_j, vehicle_j)):
                                new_solution = solution[:]
                                new_solution[i] = (new_route_i, vehicle_i)
                                new_solution[j] = (new_route_j, vehicle_j)
                                new_value = self._evaluate_solution(new_solution)
                                
                                if new_value < best_value:
                                    best_solution = new_solution
                                    best_value = new_value
                                    improved = True
            
            # 2-opt*
            for i, (route_i, vehicle_i) in enumerate(solution):
                for j, (route_j, vehicle_j) in enumerate(solution):
                    if i == j:
                        continue
                    
                    for pos_i in range(1, len(route_i) - 1):
                        for pos_j in range(1, len(route_j) - 1):
                            new_route_i = route_i[:pos_i] + route_j[pos_j:]
                            new_route_j = route_j[:pos_j] + route_i[pos_i:]
                            
                            if (self.hfvrp.check_route_feasibility(new_route_i, vehicle_i) and
                                    self.hfvrp.check_route_feasibility(new_route_j, vehicle_j)):
                                new_solution = solution[:]
                                new_solution[i] = (new_route_i, vehicle_i)
                                new_solution[j] = (new_route_j, vehicle_j)
                                new_value = self._evaluate_solution(new_solution)
                                
                                if new_value < best_value:
                                    best_solution = new_solution
                                    best_value = new_value
                                    improved = True
            
            solution = best_solution
            iteration += 1
        
        return solution

    def perturbation_procedure(self, reference_solution, removal_heuristic, alpha=0.3):
        """
        Aplica o procedimento de perturbação conforme o Algoritmo 3.
        
        Args:
            reference_solution: Solução de referência
            removal_heuristic: Heurística de remoção (H1 ou H2)
        """
        # Cria uma cópia da solução de referência
        solution = [list(x) for x in reference_solution]
        
        # Passo 2: Altera o número de rotas com probabilidade α
        if random.random() < alpha:
            m_min = math.ceil(sum(self.hfvrp.demands[v] for v in self.hfvrp.Vc) / 
                             max(self.hfvrp.vehicle_capacity[t] for t in self.hfvrp.T))
            m_max = len(self.hfvrp.Vc)  # máximo possível de rotas
            
            current_m = len(solution)
            new_m = current_m + random.choice([-1, 1])  # aumenta ou diminui em 1
            
            if m_min <= new_m <= m_max:
                if new_m > current_m:  # adiciona uma nova rota
                    v = random.choice([v for route, _ in solution for v in route[1:-1]])
                    new_route = [self.hfvrp.depot, v, self.hfvrp.depot]
                    vehicle = choose_vehicle(self, new_route)
                    if vehicle:
                        solution.append([new_route, vehicle])
                else:  # remove uma rota aleatória
                    removed_idx = random.randrange(len(solution))
                    removed_route = solution.pop(removed_idx)
                    # redistribui os vértices da rota removida
                    vertices = removed_route[0][1:-1]
                    for v in vertices:
                        best_route_idx, best_pos = a1(self.hfvrp, solution, v)
                        if best_route_idx is not None:
                            solution[best_route_idx][0].insert(best_pos, v)
        
        # Passo 3: Altera o tipo de veículo de duas rotas com probabilidade α
        if random.random() < alpha:
            routes_to_change = random.sample(range(len(solution)), 2)
            for idx in routes_to_change:
                route = solution[idx][0]
                new_vehicle = choose_vehicle(self, route)
                if new_vehicle:
                    solution[idx] = (route, new_vehicle)
        
        # Passo 4: Escolhe uma heurística de inserção aleatoriamente
        insertion_heuristics = [a1, a2]  # lista de heurísticas disponíveis
        chosen_heuristic = random.choice(insertion_heuristics)
        
        # Passo 5-8: Remove e reinsere vértices
        omega = 3  # número de vértices a serem removidos/reinseridos

        vertices_to_remove = []
        
        if removal_heuristic == 'h1':
            vr, vertices_to_remove = h1(self.hfvrp, solution, omega)
            vertices_to_remove = vertices_to_remove + [vr]
            
        elif removal_heuristic == 'h2':
            vertices_to_remove = h2(self.hfvrp, solution, omega)
            
        # Remove e reinsere cada vértice
        for vertex in vertices_to_remove:
            # Remove o vértice da sua rota atual
            for route_idx, (route, vehicle) in enumerate(solution):
                if vertex in route[1:-1]:
                    route.remove(vertex)
                    # Reinsere usando a heurística escolhida
                    best_route_idx, best_pos = chosen_heuristic(self.hfvrp, solution, vertex)
                    if best_route_idx is not None:
                        solution[best_route_idx][0].insert(best_pos, vertex)
                    break

        return solution

    def update_diversity_control(self, solution, reference_solution, removal_heuristic):
        # ETAPA 4: Atualizar o controle de diversidade
        # TODO: Implementar controle de diversidade
        pass

    def acceptance_criterion(self, solution, reference_solution):
        # ETAPA 5: Aplicar critério de aceitação
        # TODO: Implementar critério de aceitação
        pass

    def stopping_criterion(self):
        # ETAPA 6: Critério de parada
        # TODO: Implementar critério de parada
        pass

    def choose_removal_heuristic(self):
        # Escolhe aleatoriamente uma heurística de remoção
        return random.choice(self.removal_heuristics)

    def solve(self):
        """Executa o algoritmo AILS"""
        # ETAPA 1: Construção da solução inicial
        initial_solution = self.construct_initial_solution()
        
        # ETAPA 2: Busca local inicial
        self.reference_solution = self.local_search(initial_solution)
        self.best_solution = self.reference_solution
        
        # Loop principal do algoritmo
        while not self.stopping_criterion():
            # Tenta encontrar uma solução viável
            while True:
                # Escolhe uma heurística de remoção
                removal_heuristic = self.choose_removal_heuristic()
                
                # ETAPA 3: Perturbação
                solution = self.perturbation_procedure(
                    self.reference_solution, 
                    removal_heuristic
                )
                
                # Verifica viabilidade
                if self.hfvrp.check_solution_feasibility(solution):
                    print("Solução viável encontrada!")
                    print(f"Solução: {solution}")
                    print(f"Custo: {self._evaluate_solution(solution)}")
                    input("Pressione Enter para continuar...")
                    break
                else:
                    continue
            
            # ETAPA 2: Busca local
            solution = self.local_search(solution)
            
            # ETAPA 5: Atualiza controle de diversidade
            self.update_diversity_control(
                solution, 
                self.reference_solution, 
                removal_heuristic
            )
            
            # ETAPA 6: Critério de aceitação
            if self.acceptance_criterion(solution, self.reference_solution):
                self.reference_solution = solution
            
            if self._evaluate_solution(solution) < self.best_value:
                self.best_solution = solution
                self.best_value = self._evaluate_solution(solution)
        
        return self.best_solution

    def _evaluate_solution(self, solution):
        """
        Calcula o custo total de uma solução.
        
        Args:
            solution: Lista de tuplas (rota, tipo_veiculo), onde rota é uma lista de vértices
                     e tipo_veiculo é o tipo do veículo designado para a rota
        
        Returns:
            float: Custo total da solução
        """
        custo_total = 0
        
        for rota, tipo_veiculo in solution:
            # Custo fixo do veículo
            custo_total += self.hfvrp.vehicle_fixed_cost[tipo_veiculo]
            
            # Custo variável da rota
            for i in range(len(rota) - 1):
                origem = rota[i]
                destino = rota[i + 1]
                # Adiciona o custo da aresta multiplicado pelo custo variável do tipo de veículo
                custo_total += (self.hfvrp.distances[(origem, destino)] * 
                              self.hfvrp.vehicle_cost_coef[tipo_veiculo])
        
        return custo_total
