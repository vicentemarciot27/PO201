# PO201 - Exame Final

# Divisão de Trabalho
- Carlos Eduardo Pereira Sampaio: Busca local, Procedimento de perturbação.
- Leonardo Fernandes Trevilato: Construção da solução inicial, Controle de diversidade.
- Marcio Vicente da Silva Filho: Critério de aceitação, Critério de parada, Integração, Cálculo do custo total, Apresentação do trabalho.

# Estrutura Principal

## HFVRP.py
- Classe principal que representa o problema de Roteamento de Veículos Heterogêneos (Heterogeneous Fleet Vehicle Routing Problem)
- Gerencia os dados do problema como vértices, demandas, tipos de veículos e distâncias
- Inclui métodos para verificar viabilidade de rotas e soluções

## AILS.py
Implementa o algoritmo AILS (Adaptive Iterative Local Search)

Principais componentes:
- Construção de solução inicial
- Busca local 
- Procedimento de perturbação
- Critérios de aceitação e parada

## main.py
- Ponto de entrada do programa
- Lê os dados da instância do problema
- Inicializa e executa o algoritmo AILS

# Subpastas e Utilitários

## AILSUtils/
- **choose_vehicle.py**: Função para selecionar veículos aleatoriamente que podem atender uma rota

## Heuristicas/
Contém as heurísticas de inserção e remoção:
- **a1.py**: Inserção baseada na menor distância
- **a2.py**: Inserção baseada no menor custo
- **h1.py**: Remoção concêntrica
- **h2.py**: Remoção aleatória

## utils.py
- Funções utilitárias para leitura de arquivos de instância

## Taillard_20.txt
Arquivo de instância com dados do problema

Contém informações sobre:
- Coordenadas dos clientes
- Demandas
- Capacidades dos veículos
- Custos fixos e variáveis
- Quantidade disponível de cada tipo de veículo

# Como executar

Navegue para a pasta Exame 

```
cd Exame
```

Execute o script principal

```
python -m main
```
