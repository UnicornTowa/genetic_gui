import random
from copy import deepcopy
from math import copysign


# Функция, которую мы будем минимизировать
def fitness_function(x, y):
    return x ** 2 + 3 * y ** 2 + 2 * x * y


# Другое представление функции
def ff(x):
    return fitness_function(x[0], x[1])


# Копия исходной функции и метод сброса,
# (для возврата к исходной функции после использования кастомной)
backup = deepcopy(fitness_function)


def reset_ff():
    global fitness_function
    fitness_function = deepcopy(backup)


# Хранение, сброс и изменения границ
ranges = {'x1': -10, 'x2': 10, 'y1': -10, 'y2': 10}


def reset_ranges():
    ranges['x1'] = -10
    ranges['y1'] = -10
    ranges['x2'] = 10
    ranges['y2'] = 10


def set_ranges(x1, x2, y1, y2):
    ranges['x1'] = x1
    ranges['x2'] = x2
    ranges['y1'] = y1
    ranges['y2'] = y2


# Создание начальной популяции
def create_population(size):
    population = []
    for _ in range(size):
        x = random.uniform(ranges['x1'], ranges['x2'])
        y = random.uniform(ranges['y1'], ranges['y2'])
        population.append((x, y))
    return population


# Выбор 2-х родителей с помощью турнирного отбора
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
        # Запрет скрещивания с самим собой
        if child1 == child2:
            return 0, 0
    return child1, child2


# Мутация
def mutate(individual, mutation_rate):
    x, y = individual
    if random.random() < mutation_rate:
        x += random.gauss(mu=0, sigma=1)
        y += random.gauss(mu=0, sigma=1)
    return x, y

# delta - параметр, показывающий движение
# лучшего найденного решения
delta = 1


def set_delta(new_delta):
    global delta
    delta = new_delta

# Альтернативный метод мутации с переменным sigma
def mutate_new(individual, mutation_rate, sigma=1):
    x, y = individual
    if random.random() < mutation_rate:
        if random.random() < 0.5:
            x += random.gauss(mu=0, sigma=sigma)
            y += random.gauss(mu=0, sigma=sigma)
        else:
            x += random.gauss(mu=0, sigma=1 / sigma)
            y += random.gauss(mu=0, sigma=1 / sigma)
    return x, y


# Стабилизация численности популяции (вкл/выкл)
stabilization = False


def toggle_stabilization():
    global stabilization
    stabilization ^= 1


# Функция стабилизации, чем сильнее численность популяции отклоняется от исходной,
# тем более сильное корректирующее воздействие оказывается на crossover_rate
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
        if children[0]:  # = если кроссинговер произошел
            for child in children:
                mutate_new(child, mutation_rate, sigma=delta)
            new_population.extend(children)
    return new_population


# Набор аргументов
args = {'population_size': 0, 'generations': 0, 'crossover_rate': 0, 'mutation_rage': 0}


# Задание аргументов, с проверками корректности значений
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


# Генератор, итеративно создающий популяции
def next_gen():
    population = create_population(args['population_size'])
    for _ in range(1 + args['generations']):
        yield population
        population = reproduction(population, deepcopy(args['crossover_rate']), args['mutation_rage'])
        # Остановка если популяция вымерла
        if len(population) < 2:
            population = 0
        # Отсечение при превышении порога численности популяции
        elif len(population) > 5000:
            population = population[0:5000]
