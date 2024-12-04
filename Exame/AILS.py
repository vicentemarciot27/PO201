import typing
import random
import math
import time

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
        self.config = config or {
            'lambda': 15,
            'eta': 0.7
        }
        
        # Melhor solução encontrada
        self.best_solution = None
        self.best_value = float('inf')
        
        # Solução de referência
        self.reference_solution = None
        
        # Parâmetros de controle
        self.removal_heuristics = [h1, h2]  # Lista de heurísticas de remoção disponíveis
        self.insertion_heuristics = [a1, a2]  # Lista de heurísticas de inserção disponíveis
        self.diversity_controls = {}  # Parâmetros de controle de diversidade por heurística

        self.omega = {
            h1: 1,
            h2: 1
        }
        
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
            print(f"Total demand: {total_demand}")
            print(f"Max capacity: {max_capacity}")
            m = math.ceil(total_demand / max_capacity)
            print(f"m: {m}")
            
            # cria rotas iniciais
            while True:  # tenta criar rotas iniciais até encontrar uma solução viável
                routes = []
                vertices_nao_atendidos_copy = vertices_nao_atendidos.copy()
                
                for _ in range(m):
                    if not vertices_nao_atendidos_copy:
                        break
                        
                    v1 = random.choice(vertices_nao_atendidos_copy)
                    route = [self.hfvrp.depot, v1, self.hfvrp.depot]
                    vehicle = 3
                    
                    # Se não encontrou veículo disponível, tenta novamente
                    if vehicle is None:
                        continue
                        
                    routes.append((route, vehicle))
                    vertices_nao_atendidos_copy.remove(v1)
                
                try:
                    while vertices_nao_atendidos_copy:
                        v = random.choice(vertices_nao_atendidos_copy)
                        best_route_idx, best_pos = a1(self.hfvrp, routes, v)
                        route = routes[best_route_idx][0]
                        route.insert(best_pos, v)
                        vertices_nao_atendidos_copy.remove(v)
                        
                        # Verifica viabilidade após cada inserção
                        if not self.hfvrp.check_solution_feasibility(routes):
                            raise ValueError("Solução inviável")
                            
                    # Se chegou aqui, a solução é viável
                    return routes
                    
                except:
                    # Se houve erro, tenta novamente
                    continue

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
            alpha: Probabilidade de alteração da solução
        """

        m_min = math.ceil(sum(self.hfvrp.demands[v] for v in self.hfvrp.Vc) / 
                         max(self.hfvrp.vehicle_capacity[t] for t in self.hfvrp.T))
        
        m_max = sum(self.hfvrp.vehicle_initial_quantity.values())

        # cria uma cópia profunda da solução de referência
        solution = [(list(route), vehicle) for route, vehicle in reference_solution]
        reference_solution = [(list(route), vehicle) for route, vehicle in reference_solution]

        insertion_heuristic = random.choice(self.insertion_heuristics)
        print(f"Heurística de inserção: {insertion_heuristic}")

        print(f"Solução inicial: {solution}")

        # Passo 1: Altera o número de rotas com probabilidade α
        if random.random() < alpha:
            current_m = len(solution)
            new_m = current_m + random.choice([-1, 1])  # aumenta ou diminui em 1
            print(f"Novo número de rotas: {new_m}")
            if m_min <= new_m <= m_max:
                if new_m < current_m:
                    # seleciona uma rota aleatória para remover
                    route_to_remove = random.randint(1, len(solution)-1)
                    removed_route = solution[route_to_remove]
                    
                    # remove a rota selecionada
                    solution.pop(route_to_remove)
                    
                    # para cada cliente da rota removida (exceto depósito)
                    for vertex in removed_route[0][1:-1]:
                        # tenta inserir o cliente em outra rota usando a heurística
                        best_route_idx, best_pos = insertion_heuristic(self.hfvrp, solution, vertex)
                        
                        if best_route_idx is not None and best_pos is not None:
                            solution[best_route_idx][0].insert(best_pos, vertex)
                            print(f"Cliente {vertex} reinserido na rota {best_route_idx}")
                        else:
                            print(f"Não foi possível inserir cliente {vertex}")
                            # se não conseguir inserir, retorna a solução original
                            return reference_solution
                else:
                    # adiciona uma rota
                    solution.append(([self.hfvrp.depot, self.hfvrp.depot], random.choice(self.hfvrp.T)))
        
        # Passo 2: Seleciona 2 rotas aleatórias e altera o tipo de veículo
        routes_to_change = random.sample(range(len(solution)), 2)
        for idx in routes_to_change:
            route = solution[idx][0]
            if random.random() < alpha:
                new_vehicle = choose_vehicle(self, route)
                if new_vehicle:
                    solution[idx] = (route, new_vehicle)


        for _ in range(math.ceil(self.omega[removal_heuristic])):
            vertex_to_remove, route_idx = removal_heuristic(self.hfvrp, solution)
            # remove o vértice da sua rota atual
            route = solution[route_idx][0]
            route.remove(vertex_to_remove)
            print(f"Removido {vertex_to_remove} da rota {route_idx}")
            
            # Tenta inserir normalmente primeiro
            best_route_idx, best_pos = insertion_heuristic(self.hfvrp, solution, vertex_to_remove)
            # Se não conseguiu inserir, tenta fazer upgrade nos veículos
            if best_route_idx is None:
                print(f"Tentando upgrade de veículos para inserir {vertex_to_remove}")
                for i, (route, vehicle_type) in enumerate(solution):
                    if vehicle_type < len(self.hfvrp.T) - 1:  # Verifica se pode fazer upgrade
                        # Tenta fazer upgrade do veículo
                        solution[i] = (route, vehicle_type + 1)
                        best_route_idx, best_pos = insertion_heuristic(self.hfvrp, solution, vertex_to_remove)
                        if best_route_idx is not None:
                            print(f"Upgrade bem sucedido! Veículo da rota {i} atualizado para tipo {vehicle_type + 1}")
                            break
                        else:
                            # Se não deu certo, reverte o upgrade
                            solution[i] = (route, vehicle_type)
            
            if best_route_idx is not None:
                solution[best_route_idx][0].insert(best_pos, vertex_to_remove)
                print(f"Reinserido {vertex_to_remove} na rota {best_route_idx}")
            else:
                print(f"Não foi possível inserir {vertex_to_remove} mesmo com upgrades")
                return reference_solution

        return solution

    def update_diversity_control(self, solution, reference_solution, removal_heuristic):
        pass

    def acceptance_criterion(self, solution, reference_solution):
        """
        Determina se uma solução deve se tornar a nova solução de referência.
        
        Args:
            solution: Nova solução candidata
            reference_solution: Solução de referência atual
        
        Returns:
            bool: True se a solução deve ser aceita como nova referência
        """
        # Parâmetros de controle
        lambda_ = self.config.get('lambda', 10)  # Número de iterações para média
        eta = self.config.get('eta', 0.5)  # Parâmetro de controle do threshold
        
        # Calcula f(s) - valor da solução atual
        f_s = self._evaluate_solution(solution)
        
        # Atualiza f_bar (média ponderada)
        if not hasattr(self, 'f_bar'):
            self.f_bar = f_s
            self.iteration = 1
        else:
            self.iteration += 1
            
        if self.iteration > lambda_:
            # Usa média ponderada com peso lambda^-1
            self.f_bar = self.f_bar * (1 - 1/lambda_) + f_s * (1/lambda_)
        else:
            # Usa média simples para as primeiras lambda iterações
            self.f_bar = (self.f_bar * (self.iteration - 1) + f_s) / self.iteration
        
        # Atualiza f (melhor solução nas últimas lambda iterações)
        if not hasattr(self, 'recent_solutions'):
            self.recent_solutions = []
        
        self.recent_solutions.append(f_s)
        if len(self.recent_solutions) > lambda_:
            self.recent_solutions.pop(0)
        
        f = min(self.recent_solutions)
        
        # Calcula b_bar (threshold de aceitação)
        b_bar = f + eta * (self.f_bar - f)
        
        # Decide se aceita a solução
        return f_s <= b_bar

    def stopping_criterion(self):
        """
        Verifica se o algoritmo deve parar.
        
        Returns:
            bool: True se o critério de parada foi atingido
        """
        # Número máximo de iterações
        max_iterations = self.config.get('max_iterations', 2000)
        
        # Número máximo de iterações sem melhoria
        max_no_improvement = self.config.get('max_no_improvement', 500)
        
        # Tempo máximo de execução em segundos
        max_time = self.config.get('max_time', 3600)  # 1 hora por padrão
        
        # Verifica se atingiu número máximo de iterações
        if self.iteration >= max_iterations:
            return True
        
        # Verifica se está há muito tempo sem melhoria
        if hasattr(self, 'last_improvement_iteration'):
            if self.iteration - self.last_improvement_iteration >= max_no_improvement:
                return True
        
        # Verifica se excedeu tempo máximo
        if hasattr(self, 'start_time'):
            if time.time() - self.start_time >= max_time:
                return True
        
        return False

    def solve(self):
        """Executa o algoritmo AILS"""
        import time
        
        # Marca tempo inicial
        self.start_time = time.time()
        self.iteration = 0
        self.last_improvement_iteration = 0
        
        # ETAPA 1: Construção da solução inicial
        initial_solution = self.construct_initial_solution()
        
        # ETAPA 2: Busca local inicial
        self.reference_solution = self.local_search(initial_solution)
        self.best_solution = self.reference_solution
        self.best_value = self._evaluate_solution(self.best_solution)
        
        # Loop principal do algoritmo
        while not self.stopping_criterion():
            self.iteration += 1
            
            # Tenta encontrar uma solução viável
            while True:
                # Escolhe uma heurística de remoção
                removal_heuristic = random.choice(self.removal_heuristics)
                print(f"Heurística de remoção: {removal_heuristic}")
                
                # ETAPA 3: Perturbação
                solution = self.perturbation_procedure(
                    reference_solution=self.reference_solution, 
                    removal_heuristic=removal_heuristic,
                    alpha=0.3
                )
                
                # Verifica viabilidade
                if self.hfvrp.check_solution_feasibility(solution):
                    print("Solução viável encontrada!")
                    print(f"Solução: {solution}")
                    print(f"Custo: {self._evaluate_solution(solution)}")
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
            
            # Atualiza melhor solução
            current_value = self._evaluate_solution(solution)
            if current_value < self.best_value:
                self.best_solution = solution
                self.best_value = current_value
                self.last_improvement_iteration = self.iteration
        
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
            # Pula rotas de tamanho 2 (apenas depósito-cliente-depósito)
            if len(rota) == 2:
                continue
                
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
