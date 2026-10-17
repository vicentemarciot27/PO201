# PO201 - Exame Final

Implementação em Python da heurística AILS (Adaptive Iterated Local Search) para o problema de roteamento de veículos com frota heterogênea (HFVRP). Cada tipo de veículo tem capacidade, custo fixo, custo por distância e quantidade disponível próprios. O objetivo é atender a demanda de todos os clientes a partir de um depósito com o menor custo total.

A pasta `Java/` contém a implementação original do AILS-HVRP de Vinícius R. Máximo, usada como referência.

## Estrutura

```txt
Exame/                      implementação em Python
├── main.py                 lê a instância e executa o AILS
├── HFVRP.py                classe do problema: vértices, demandas, tipos de veículo, distâncias, viabilidade
├── AILS.py                 solução inicial, busca local, perturbação, controle de diversidade,
│                           critérios de aceitação e de parada
├── utils.py                leitura de arquivos de instância
├── AILSUtils/
│   └── choose_vehicle.py   sorteia um veículo capaz de atender uma rota
├── Heuristicas/
│   ├── a1.py               inserção pela menor distância
│   ├── a2.py               inserção pelo menor custo
│   ├── h1.py               remoção concêntrica
│   └── h2.py               remoção aleatória
└── Taillard_20.txt         instância usada por main.py
Java/                       AILS-HVRP original (licença MIT), com instâncias e soluções em Java/Instances/
```

## Como executar (Python)

Requisito: Python 3. Não há dependências externas.

```bash
cd Exame
python -m main
```

O programa imprime a instância, a melhor solução encontrada, o custo e um dicionário com iterações, tempo de execução e custo da solução inicial.

A execução para no primeiro destes limites, definidos em `AILS.stopping_criterion`:

| Critério | Chave em `config` | Padrão |
|---|---|---|
| Iterações | `max_iterations` | 4000 |
| Iterações sem melhoria | `max_no_improvement` | 1000 |
| Tempo | `max_time` | 900 s |

Para uma execução curta, passe os limites no `config`. O dicionário substitui o padrão inteiro, então inclua também `lambda`, `eta`, `d_beta`, `alpha` e `DEV`:

```python
ails = AILS(hfvrp, {'lambda': 20, 'eta': 0.2, 'd_beta': 15, 'alpha': 0.4, 'DEV': False,
                    'max_iterations': 30, 'max_time': 30})
```

Em Linux e macOS, `python -m main` falha com `UnicodeDecodeError` ao ler `Taillard_20.txt`. A linha `NAME` do arquivo tem um byte em Latin-1 (`0xb0`), e `utils.read_file` abre o arquivo com a codificação padrão do sistema, que é UTF-8 nesses sistemas. No Windows a leitura funciona. Para corrigir, troque `open(filename, 'r')` por `open(filename, 'r', encoding='latin-1')` em `utils.py`.

## Resultados em Taillard_20

Taillard_20 tem 100 clientes e 3 tipos de veículo. O melhor custo conhecido é 4760.67.

Medido em uma execução de cada:

| Implementação | Limite | Custo |
|---|---|---|
| Python, solução inicial | - | 7118.64 |
| Python, `Exame/` | 30 iterações (12 s) | 5849.34 |
| Java, `Java/` | 10 s | 4761.85 |

## Como executar (Java)

O repositório não inclui `AILS.jar`. Compile com um JDK (testado com JDK 21):

```bash
cd Java
javac -encoding UTF-8 -d bin $(find HVRP -name "*.java")
java -cp bin Metaheuristicas.AILS -file Instances/Taillard_13.txt -rounded false -variant HVRPFD -limit 10 -stoppingCriterion Time
```

`Java/README.md` descreve todos os parâmetros. O exemplo desse arquivo usa `Instances/Taillard_20.txt`, que não está em `Java/Instances/`; a cópia está em `Exame/`.

## Divisão de trabalho

- Carlos Eduardo Pereira Sampaio: busca local, procedimento de perturbação.
- Leonardo Fernandes Trevilato: construção da solução inicial, controle de diversidade.
- Marcio Vicente da Silva Filho: critério de aceitação, critério de parada, integração, cálculo do custo total, apresentação do trabalho.

## Referências

[1] Máximo, V. R., Nascimento, M. C. V. (2021). A hybrid adaptive iterated local search with diversification control to the capacitated vehicle routing problem. European Journal of Operational Research, 294, 1108-1119. https://doi.org/10.1016/j.ejor.2021.02.024

[2] Máximo, V. R., Cordeau, J.-F., Nascimento, M. C. V. (2022). An adaptive iterated local search heuristic for the Heterogeneous Fleet Vehicle Routing Problem. Computers & Operations Research, 148, 105954. https://doi.org/10.1016/j.cor.2022.105954
