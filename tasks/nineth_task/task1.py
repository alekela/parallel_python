import random
import numpy as np
import matplotlib.pyplot as plt
from mpi4py import MPI

DNA_SIZE = 10  # DNA length
POP_SIZE = 10  # population size
CROSSOVER_RATE = 0.8  # mating probability (DNA crossover)
MUTATION_RATE = 0.03  # mutation probability
N_GENERATIONS = 200
X_BOUND = [0, 5]


def F(x):
    return np.sin(10 * x) * x + np.cos(2 * x) * x  # to find the maximum of this function


def translateDNA(pop):
    # pop представляет матрицу популяции, одна строка представляет ДНК, представленную двоичным кодом, а количество строк в матрице - это размер популяции
    x = [0] * POP_SIZE
    for i in range(POP_SIZE):
        for j in range(DNA_SIZE):
            x[i] = x[i] + (pop[i][j] * (2 ** j))
        x[i] = x[i] / float(2 ** DNA_SIZE - 1) * (X_BOUND[1] - X_BOUND[0]) + X_BOUND[0]
    return x


def crossover_and_mutation(pop, CROSSOVER_RATE=0.8):
    new_pop = []
    for father in pop:
        child = father
        if np.random.rand() < CROSSOVER_RATE:
            mother = pop[np.random.randint(0, POP_SIZE)]
            cross_points = np.random.randint(0, DNA_SIZE)
            child[cross_points:] = mother[cross_points:]
        child = mutation(child)
        new_pop.append(child)
    return new_pop


def mutation(child):
    if random.random() < MUTATION_RATE:
        mutate_point = random.randint(0, DNA_SIZE - 1)
        child[mutate_point] = 1 if child[mutate_point] == 0 else 0
    return child


def select(pop, fitness):
    w = [0] * POP_SIZE
    for i in range(POP_SIZE):
        w[i] = fitness[i] / max(fitness)
    idx = random.choices(range(POP_SIZE), weights=w, k=POP_SIZE)
    pop1 = [[0] * DNA_SIZE for i in range(POP_SIZE)]
    for i in range(POP_SIZE):
        for j in range(DNA_SIZE):
            pop1[i][j] = pop[i][j]
    for i in range(POP_SIZE):
        for j in range(DNA_SIZE):
            pop[i][j] = pop1[idx[i]][j]
    #        print(pop[i])
    return pop


def print_info(pop):
    max_fitness_index = fitness.index(max(fitness))
    print("max_fitness:", fitness[max_fitness_index])
    x = translateDNA(pop)
    print("Optimal genotype:", pop[max_fitness_index])
    print("(x):", (x[max_fitness_index]), "F(x) = ", F(x[max_fitness_index]))


def get_ans(pop, fitness):
    max_fitness_index = fitness.index(max(fitness))
    x = translateDNA(pop)
    return F(x[max_fitness_index])


if __name__ == "__main__":
    # plt.ioff()
    # x = np.linspace(*X_BOUND, 200)
    # plt.plot(x, F(x))
    # plt.savefig('graf01.png')
    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()

    MAX = 0.
    eps = 1.e-8
    k = 0

    # Создание исходной популяции
    pop = [[0] * DNA_SIZE for i in range(POP_SIZE)]
    for i in range(POP_SIZE):
        for j in range(DNA_SIZE):
            pop[i][j] = random.randint(0, 1)

    for k in range(N_GENERATIONS):
        x1 = translateDNA(pop)
        F_values = [0] * POP_SIZE
        for i in range(POP_SIZE):
            F_values[i] = F(x1[i])
        if 'sca' in globals():
            sca.remove()
        sca = plt.scatter(x1, F_values, s=25, lw=2, c='red', alpha=0.2)  # ; plt.pause(.2)

        x1 = translateDNA(pop)
        fitness = [0] * POP_SIZE
        pred = [0] * POP_SIZE
        for i in range(POP_SIZE):
            pred[i] = F(x1[i])
        for i in range(POP_SIZE):
            fitness[i] = pred[i] - min(pred) + 1e-3
        pop = select(pop, fitness)  # Select to generate a new population
        pop = crossover_and_mutation(pop)
        ans = get_ans(pop, fitness)
    #	if abs(F(x1[0])-MAX) < eps: break
    #	if F(x1[0])>MAX: MAX=F(x1[0])

    answers = comm.gather(ans, root=0)
    if rank == 0:
        max_index = answers.index(max(answers))
        for i in range(1, size):
            comm.send(max_index, dest=i, tag=110)
            
    if rank != 0:
        max_index = comm.recv(source=0, tag=110)

    if rank == max_index:
        print("Maximum answer from proccess number", rank, ":")
        print_info(pop)
