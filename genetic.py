import random
from copy import deepcopy
from math import copysign


# Функция, которую мы будем минимизировать
def fitness_function(x, y):
    return x ** 2 + 3 * y ** 2 + 2 * x * y


def ff(x):
    return fitness_function(x[0], x[1])


backup = deepcopy(fitness_function)


def reset_ff():
    global fitness_function
    fitness_function = deepcopy(backup)


# Создание начальной популяции
def create_population(size):
    population = []
    for _ in range(size):
        x = random.uniform(-10, 10)
        y = random.uniform(-10, 10)
        population.append((x, y))
    return population


# Выбор родителей с помощью турнирного отбора
def selection(population):
    selected = []
    for _ in range(2):
        tournament = random.sample(population, 2)
        tournament.sort(key=ff)
        selected.append(tournament[0])
    return selected


# Кроссинговер двух родителей
def crossover(parent1, parent2, crossover_rate):
    child1, child2 = 0, 0
    if random.random() < crossover_rate:
        x1, y1 = parent1
        x2, y2 = parent2
        child1 = (random.uniform(x1, x2), random.uniform(y1, y2))
        child2 = (random.uniform(x1, x2), random.uniform(y1, y2))
        # child = (x1 + x2) / 2, (y1 + y2) / 2
    return child1, child2


# Мутация гена
def mutate(individual, mutation_rate):
    x, y = individual
    if random.random() < mutation_rate:
        x += random.gauss(mu=0, sigma=1)
        y += random.gauss(mu=0, sigma=1)
    return x, y


stabilization = False


def toggle_stabilization():
    global stabilization
    stabilization ^= 1


def stabilization_func(size, n):
    return copysign(((-1) / (1 + 1 / n ** 2 * (size - n) ** 2) + 1), (n - size))


# Создание новой популяции с помощью кроссинговера и мутации
def reproduction(population, crossover_rate, mutation_rate):
    new_population = []
    if stabilization:
        crossover_rate += stabilization_func(len(population), args['population_size'])
    for _ in range(len(population)):
        parent1, parent2 = selection(population)
        children = crossover(parent1, parent2, crossover_rate)
        if children[0]:
            for child in children:
                mutate(child, mutation_rate)
            new_population.extend(children)
            # new_population.extend([parent1, parent2])
            # new_population.append(random.choice([parent1, parent2]))
    return new_population


# Набор аргументов
args = {'population_size': 0, 'generations': 0, 'crossover_rate': 0, 'mutation_rage': 0}


# Задание аргументов
def set_args(population_size, generations, crossover_rate, mutation_rate):
    if population_size > 1:
        args['population_size'] = population_size
    else:
        raise ValueError('Введите корректный размер популяции')
    if generations >= 0:
        args['generations'] = generations
    else:
        raise ValueError('Введите корректное количество поколений')
    if 0 <= crossover_rate <= 1:
        args['crossover_rate'] = crossover_rate
    else:
        raise ValueError('Введите корректный коэффициент размножения')
    if 0 <= mutation_rate <= 1:
        args['mutation_rage'] = mutation_rate
    else:
        raise ValueError('Введите корректный коэффициент мутации')


# Генератор популяций
def next_gen():
    population = create_population(args['population_size'])
    for _ in range(1 + args['generations']):
        yield population
        population = reproduction(population, deepcopy(args['crossover_rate']), args['mutation_rage'])
        if len(population) < 2:
            population = 0
        elif len(population) > 5000:
            population = population[0:5000]

# set_args(population_size=100, generations=100, crossover_rate=0.5, mutation_rate=0.3)
# i = 0
# for generation in next_gen():
#     if not generation:
#         print('Population is extinct')
#         break
#     generation.sort(key=lambda x: fitness_function(x[0], x[1]))
#     best_solution = generation[0]
#     print("Generation:", i, "Optimal solution:", best_solution,
#           "Fitness:", fitness_function(*best_solution), "Population size:", len(generation))
#     i += 1
#
# # Пример использования
# best_solution = genetic_algorithm(population_size=100, generations=10, crossover_rate=0.8, mutation_rate=0.2)
# print("Optimal solution:", best_solution, "Fitness:", fitness_function(*best_solution))
