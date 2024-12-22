import math
from random import random
from mpi4py import MPI


def func(z):
    return math.sin(math.pi * z / 180.) - 1. / z


def mutation(x0, x1):
    return random() * (x1 - x0) + x0


def crossover(x, eps, x0, x1):
    k = 99
    for i in range(8):
        for j in range(i + 1, 8):
            x[k][0] = (x[i][0] + x[j][0]) / 2
            k = k - 1
    for i in range(8):
        x[k][0] = inversion(x[i][0], eps)
        k = k - 1
        x[k][0] = inversion(x[i][0], eps)
        k = k - 1
    for i in range(8, k):
        x[i][0] = mutation(x0, x1)


# инверсия: поиск в окрестностях точки
def inversion(xx, eps):
    sign = 0;
    sign = sign + 1
    sign %= 2
    if (sign == 0):
        return xx - eps
    else:
        return xx + eps


# поиск решения с использованием ГА
def genetic(x0, x1, eps):
    population = [[0] * 2 for i in range(100)]
    iter = 0
    for i in range(100):  # Формирование начальной популяции
        population[i][0] = mutation(x0, x1)
        population[i][1] = func(population[i][0])
    population.sort(key=lambda x: abs(x[1]))
    stop_flag = 0
    while (abs(population[0][1]) > eps and iter < 1500000 and stop_flag == 0):
        iter += 1
        crossover(population, eps, x0, x1)
        for i in range(100):
            population[i][1] = func(population[i][0])
        population.sort(key=lambda x: abs(x[1]))
        comm.Barrier()
        if abs(population[0][1]) <= eps:
            signal = 1
        else:
            signal = 0
        comm.send(signal, dest=0, tag=11)
        ready = comm.gather(signal, root=0)
        if rank == 0:
            if 1 in ready:
                ready_index = ready.index(1)
                stop_flag = 1
            else:
                stop_flag = 0
                ready_index = -1
                
            for i in range(1, size):
                comm.send(ready_index, dest=i, tag=110)
                comm.send(stop_flag, dest=i, tag=111)
                
        if rank != 0:
            ready_index = comm.recv(source=0, tag=110)
            stop_flag = comm.recv(source=0, tag=111)
        comm.Barrier()

    if rank == ready_index:
        print("Answer from proccess number", rank, ":")
        print(iter, " iterations")
        print(population[0])


if __name__ == "__main__":
    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()
    genetic(1.0, 10.0, 1.e-9)
