class HFVRP:
    def __init__(self):
        # Dados básicos do problema
        self.dimension = 0
        self.depot = 1
        
        # Conjuntos principais
        self.V = []  # Conjunto de vértices (1 é o depósito)
        self.Vc = [] # Conjunto de clientes (V \ {1})
        self.T = []  # Tipos de veículos
        
        # Dados dos clientes
        self.demands = {}    # Demandas dos clientes
        self.coords = {}     # Coordenadas dos pontos (x,y)
        self.distances = {}  # Matriz de distâncias
        
        # Dados dos veículos
        self.vehicle_capacity = {}   # Capacidades por tipo
        self.vehicle_fixed_cost = {} # Custos fixos por tipo
        self.vehicle_cost_coef = {}  # Coeficientes de custo por tipo
        self.vehicle_initial_quantity = {} # Quantidade inicial disponível por tipo
        self.vehicle_quantity = {}   # Quantidade disponível por tipo
        
    def add_vertex(self, id_: int, x: float, y: float, demand: float):
        """Adiciona um vértice ao problema"""
        self.coords[id_] = (x, y)
        self.demands[id_] = demand
        self.V.append(id_)
        if id_ != self.depot:
            self.Vc.append(id_)
            
    def add_vehicle_type(self, type_id, capacity, fixed_cost, cost_coef, quantity):
        """Adiciona um tipo de veículo com suas características"""
        self.T.append(type_id)
        self.vehicle_capacity[type_id] = capacity
        self.vehicle_fixed_cost[type_id] = fixed_cost
        self.vehicle_cost_coef[type_id] = cost_coef
        self.vehicle_initial_quantity[type_id] = quantity
        self.vehicle_quantity[type_id] = quantity
        
    def calculate_distances(self):
        """Calcula distâncias euclidianas entre todos os pares de vértices"""
        for i in self.V:
            for j in self.V:
                if i < j:  # Evita calcular duas vezes
                    xi, yi = self.coords[i]
                    xj, yj = self.coords[j]
                    dist = ((xi - xj)**2 + (yi - yj)**2)**0.5
                    self.distances[(i,j)] = dist
                    self.distances[(j,i)] = dist
    
    def get_travel_cost(self, i, j, vehicle_type):
        """Retorna o custo de viagem entre i e j usando veículo do tipo especificado"""
        return self.distances[(i,j)] * self.vehicle_cost_coef[vehicle_type]
        
    def check_route_feasibility(self, route, vehicle_type):
        """Verifica se uma rota é viável para um tipo de veículo
        
        Retorna False se:
        """
        # Verifica se a rota começa e termina no depósito
        if not route or len(route) < 3 or route[0] != self.depot or route[-1] != self.depot:
            print("Rota inviável: não começa ou termina no depósito")
            return False
        
        # Verifica se não há repetição de clientes (exceto depósito)
        clients = [v for v in route if v != self.depot]
        if len(clients) != len(set(clients)):
            print("Rota inviável: há repetição de clientes")
            # para o código 
            print(f"Clientes repetidos na rota: {route}")
            print(f"Clientes únicos: {set(clients)}")
            print(f"Clientes duplicados: {[x for x in clients if clients.count(x) > 1]}")
            raise ValueError("Rota inviável: há repetição de clientes")

            return False
        
        # Verifica se a demanda total não excede a capacidade
        total_demand = sum(self.demands[i] for i in route if i != self.depot)
        if total_demand > self.vehicle_capacity[vehicle_type]:
            # print("Rota inviável: demanda total excede a capacidade do veículo")
            # print(f"Rota: {route}")
            # # Escreva um breakdown das demandas
            # print(f"Breakdown das demandas: {total_demand} > {self.vehicle_capacity[vehicle_type]}")
            # input("Pressione Enter para continuar...")
            return False
        
        # print(f"Rota: {route}")
        # print("Rota viável")
        return True
    
    def check_solution_feasibility(self, solution):
        """Verifica se uma solução é viável"""
        for route, vehicle_type in solution:
            if not self.check_route_feasibility(route, vehicle_type):
                return False
        return True

    def __str__(self):
        return (f"HFVRP Instance with:\n"
                f"- {len(self.Vc)} customers\n"
                f"- {len(self.T)} vehicle types\n"
                f"- Total demand: {sum(self.demands.values())}\n"
                f"- Total available fleet capacity: {[self.vehicle_capacity[t] * self.vehicle_quantity[t] for t in self.T]}\n"
                f"- Total fleet size: {sum(self.vehicle_quantity.values())} vehicles")

    def factibilize_solution(self, solution):
        """Tenta tornar uma solução inviável em viável
        
        Retorna:
        - (solution, success): Tupla com a solução modificada e um booleano indicando sucesso
        """
        
        max_attempts = 100  # Evita loop infinito
        attempt = 0
        
        while not self.check_solution_feasibility(solution) and attempt < max_attempts:
            modified = False
            
            # Tenta ajustar rotas problemáticas
            for i, (route, vehicle_type) in enumerate(solution):
                if not self.check_route_feasibility(route, vehicle_type):
                    # Tenta encontrar veículo com maior capacidade
                    better_vehicle = self._find_better_vehicle(vehicle_type)
                    if better_vehicle:
                        solution[i] = (route, better_vehicle)
                        modified = True
                        continue
                    
                    # Se não conseguiu trocar veículo, divide a rota
                    if len(route) > 3:  # Só divide se tiver mais de um cliente
                        route1, route2 = self._split_route(route)
                        solution[i] = (route1, vehicle_type)
                        solution.append((route2, vehicle_type))
                        modified = True
            
            if not modified:
                return solution, False
            
            attempt += 1
        
        return solution, self.check_solution_feasibility(solution)

    def _find_better_vehicle(self, current_type):
        """Encontra veículo com maior capacidade disponível"""
        best_type = None
        best_capacity = self.vehicle_capacity[current_type]
        
        for t in self.T:
            if (self.vehicle_quantity[t] > 0 and 
                self.vehicle_capacity[t] > best_capacity):
                best_type = t
                best_capacity = self.vehicle_capacity[t]
        
        return best_type

    def _split_route(self, route):
        """Divide uma rota em duas partes balanceadas"""
        if len(route) <= 3:  # Depósito-Cliente-Depósito
            return route, [self.depot, self.depot]
        
        # Remove depósito do início e fim
        clients = route[1:-1]
        mid = len(clients) // 2
        
        route1 = [self.depot] + clients[:mid] + [self.depot]
        route2 = [self.depot] + clients[mid:] + [self.depot]
        
        return route1, route2
