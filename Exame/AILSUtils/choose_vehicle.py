import random

def choose_vehicle(self, route):
    """Escolhe aleatoriamente um veículo que pode atender a rota e está disponível"""
    route_demand = sum(self.hfvrp.demands[i] for i in route[1:-1])
    
    # Filtra veículos com capacidade suficiente e quantidade disponível
    possiveis_veiculos = [t for t in self.hfvrp.T 
                         if self.hfvrp.vehicle_capacity[t] >= route_demand and 
                         self.hfvrp.vehicle_quantity[t] > 0]
    
    if possiveis_veiculos:
        chosen_vehicle = random.choice(possiveis_veiculos)
        # Reduz a quantidade disponível do veículo escolhido
        self.hfvrp.vehicle_quantity[chosen_vehicle] -= 1
        return chosen_vehicle
            
    return None