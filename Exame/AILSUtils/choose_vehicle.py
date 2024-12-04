import random

def choose_vehicle(self, route):
    """Escolhe um veículo que possa atender à rota"""
    route_demand = sum(self.hfvrp.demands[i] for i in route[1:-1])
    
    # Filtra apenas veículos com capacidade suficiente
    valid_vehicles = [t for t in self.hfvrp.T 
                     if self.hfvrp.vehicle_capacity[t] >= route_demand]
    
    if not valid_vehicles:
        raise ValueError("Nenhum veículo disponível tem capacidade suficiente para atender esta rota")
        
    # Retorna o veículo com menor capacidade que atenda a demanda
    return min(valid_vehicles, key=lambda t: self.hfvrp.vehicle_capacity[t])