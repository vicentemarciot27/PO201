def read_file(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    i = 0
    n_lines = len(lines)
    
    # Lê os dados do cabeçalho
    dimension = None
    while i < n_lines:
        line = lines[i].strip()
        if line.startswith('DIMENSION'):
            dimension = int(line.split(':')[1])
        elif line.startswith('NODE_COORD_SECTION'):
            break
        i += 1
    
    # Lê coordenadas e demandas
    coord_section = False
    demand_section = False
    vertices = {}
    demands = {}
    
    while i < n_lines:
        line = lines[i].strip()
        
        if line.startswith('NODE_COORD_SECTION'):
            coord_section = True
            i += 1
            continue
        elif line.startswith('DEMAND_SECTION'):
            coord_section = False
            demand_section = True
            i += 1
            continue
        elif line.startswith('DEPOT_SECTION'):
            demand_section = False
            i += 1
            continue
        elif line.startswith('CAPACITIES'):
            i += 1
            capacities = lines[i].strip().split()
            i += 1
            continue
        elif line.startswith('FIXED_COSTS'):
            i += 1
            fixed_costs = lines[i].strip().split()
            i += 1
            continue
        elif line.startswith('COST_COEFFICIENTS'):
            i += 1
            cost_coefs = lines[i].strip().split()
            i += 1
            continue
        elif line.startswith('VEHICLES_AVAILABLE'):
            i += 1
            quantities = lines[i].strip().split()
            break
            
        if coord_section:
            try:
                id_, x, y = map(float, line.split())
                vertices[int(id_)] = (x, y)
            except ValueError:
                pass
                
        if demand_section:
            try:
                id_, demand = map(int, line.split())
                demands[id_] = demand
            except ValueError:
                pass
        
        i += 1
        
    return dimension, vertices, demands, capacities, fixed_costs, cost_coefs, quantities