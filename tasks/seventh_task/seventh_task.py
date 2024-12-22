from mpi4py import MPI
import numpy as np
import math
import pylab
import matplotlib.patches
import matplotlib.lines
import matplotlib.path

# Подготовка анимации
comm = MPI.COMM_WORLD  # оформление коммуникатора (команды исполнителей)
rank = comm.Get_rank()  # номер компьютера, исполняющего код
size = comm.Get_size()  # количество компьютеров в коммуникаторе
m1, m2, m3 = 400, 1, 0.0
X = [[0., 0., 0],
     [0., 0., 0],
     [0., 0., 0]]
Y = [[0., 0., 0],
     [0., 0., 0],
     [0., 0., 0]]


# Определение силы гравитационного взаимодейсивия
def acc(x, R, M, m):
    return -M * m * x / (R ** 3)


# Определение составляющих ускорения
def acc(x, R, m):
    return -m * x / (R ** 3)


def orbit(x1, y1, SPEED, direction):
    x = x1
    y = y1
    alpha = math.radians(direction)
    # Стартовая позиция тела
    if rank == 1: c = "r"
    if rank == 2: c = "g"
    if rank == 3: c = "b"
    ball = matplotlib.patches.Circle((x, y), radius=r, fill=True, color=c)
    Vx = SPEED * math.cos(alpha)
    Vy = SPEED * math.sin(alpha)
    return Vx, Vy, ball


# Расчет ускорений
def ACC(x, y, X, Y):
    if rank == 1:
        R = math.sqrt(X[0][1] * X[0][1] + Y[0][1] * Y[0][1])
        Acc1x = acc(X[0][1], R, m2)
        Acc1y = acc(Y[0][1], R, m2)
        R = math.sqrt(X[0][2] * X[0][2] + Y[0][2] * Y[0][2])
        Acc2x = acc(X[0][2], R, m3)
        Acc2y = acc(Y[0][2], R, m3)
    if rank == 2:
        R = math.sqrt(X[1][0] * X[1][0] + Y[1][0] * Y[1][0])
        Acc1x = acc(X[1][0], R, m1)
        Acc1y = acc(Y[1][0], R, m1)
        R = math.sqrt(X[1][2] * X[1][2] + Y[1][2] * Y[1][2])
        Acc2x = acc(X[1][2], R, m3)
        Acc2y = acc(Y[1][2], R, m3)
    if rank == 3:
        R = math.sqrt(X[2][0] * X[2][0] + Y[2][0] * Y[2][0])
        Acc1x = acc(X[2][0], R, m1)
        Acc1y = acc(Y[2][0], R, m1)
        R = math.sqrt(X[2][1] * X[2][1] + Y[2][1] * Y[2][1])
        Acc2x = acc(X[2][1], R, m2)
        Acc2y = acc(Y[2][1], R, m2)
    return Acc1x, Acc1y, Acc2x, Acc2y


def move(x, y, Vx, Vy, Acc1x, Acc1y, Acc2x, Acc2y, h):
    Vx = Vx + (Acc1x + Acc2x) * h / 2.
    Vy = Vy + (Acc1y + Acc2y) * h / 2.
    # определяем текущие координаты спутника в космосе
    x = x + Vx * h
    y = y + Vy * h
    return x, y, Vx, Vy


# размещение на орбите
r = 0.05
if rank == 0:
    pylab.xlim(-7, 7)
    pylab.ylim(-7, 7)
    pylab.grid()
    axes = pylab.gca()
    axes.set_aspect("equal")
    #   N = int(input("Введите максимальное число кадров: "))
    N = 22000
    x1 = comm.recv(source=1)  # comm.send(x, dest=0)
    y1 = comm.recv(source=1)  # comm.send(y, dest=0)
    x2 = comm.recv(source=2)  # comm.send(x, dest=0)
    y2 = comm.recv(source=2)  # comm.send(y, dest=0)
    x3 = comm.recv(source=3)  # comm.send(x, dest=0)
    y3 = comm.recv(source=3)  # comm.send(y, dest=0)
    X[0][1] = -(x2 - x1)
    X[1][0] = -X[0][1]
    X[0][2] = -(x3 - x1)
    X[2][0] = -X[0][2]
    X[1][2] = -(x3 - x2)
    X[2][1] = -X[1][2]
    #   comm.bcast(X)
    Y[0][1] = -(y2 - y1)
    Y[1][0] = -Y[0][1]
    Y[0][2] = -(y3 - y1)
    Y[2][0] = -Y[0][2]
    Y[1][2] = -(y3 - y2)
    Y[2][1] = -Y[1][2]
    comm.send(X, dest=1)
    comm.send(Y, dest=1)
    comm.send(X, dest=2)
    comm.send(Y, dest=2)
    comm.send(X, dest=3)
    comm.send(Y, dest=3)
    ball1 = comm.recv(source=1)  # comm.send(ball, dest=0)
    ball2 = comm.recv(source=2)  # comm.send(ball, dest=0)
    ball3 = comm.recv(source=3)  # comm.send(ball, dest=0)
    axes.add_patch(ball1)
    axes.add_patch(ball2)
    axes.add_patch(ball3)
    pylab.savefig('Pics/Ball0.png')
    comm.send(N, dest=1)
    comm.send(N, dest=2)
    comm.send(N, dest=3)
    h = 0.05
    acc0 = 10 * min(m1, m2) / max(X[0], key=abs) ** 2
    for t in range(1, N):
        acc11x, acc11y, acc12x, acc12y = comm.recv(source=1)
        acc21x, acc21y, acc22x, acc22y = comm.recv(source=2)
        acc31x, acc31y, acc32x, acc32y = comm.recv(source=3)
        accmax = max(acc11x, acc11y, acc12x, acc12y, acc21x, acc21y, acc22x, acc22y, acc31x, acc31y, acc32x, acc32y)
        h = h * (acc0 / accmax)
        # print(h)
        acc0 = accmax
        comm.send(h, dest=1)
        comm.send(h, dest=2)
        comm.send(h, dest=3)

        comm.send(N - 1 - t, dest=1)
        comm.send(N - 1 - t, dest=2)
        comm.send(N - 1 - t, dest=3)
        X[0][1] = -(x2 - x1)
        X[1][0] = -X[0][1]
        X[0][2] = -(x3 - x1)
        X[2][0] = -X[0][2]
        X[1][2] = -(x3 - x2)
        X[2][1] = -X[1][2]

        Y[0][1] = -(y2 - y1)
        Y[1][0] = -Y[0][1]
        Y[0][2] = -(y3 - y1)
        Y[2][0] = -Y[0][2]
        Y[1][2] = -(y3 - y2)
        Y[2][1] = -Y[1][2]

        comm.send(X, dest=1)
        comm.send(Y, dest=1)
        comm.send(X, dest=2)
        comm.send(Y, dest=2)
        comm.send(X, dest=3)
        comm.send(Y, dest=3)

        x1 = comm.recv(source=1)
        y1 = comm.recv(source=1)
        ball1.remove()
        ball1 = comm.recv(source=1)
        x2 = comm.recv(source=2)
        y2 = comm.recv(source=2)
        ball2.remove()
        ball2 = comm.recv(source=2)
        x3 = comm.recv(source=3)
        y3 = comm.recv(source=3)
        ball3.remove()
        ball3 = comm.recv(source=3)
        axes.add_patch(ball1)
        axes.add_patch(ball2)
        axes.add_patch(ball3)
        file = 'Pics/Ball' + str(t) + '.png'
        pylab.savefig(file)
if 1 <= rank <= 3:
    # вектор данных x1, y1, v1, dir
    if rank == 1: x, y, V, dir = 0, -.0, 0, 0.
    if rank == 2: x, y, V, dir = 6, -.0, 2.85, 90.
    if rank == 3: x, y, V, dir = 7, 0, 2.15, 90.
    comm.send(x, dest=0)
    comm.send(y, dest=0)
    X = comm.recv(source=0)  # comm.send(X,dest=1)
    Y = comm.recv(source=0)  # comm.send(Y,dest=1)
    Vx, Vy, ball = orbit(x, y, V, dir)
    comm.send(ball, dest=0)
    c = comm.recv(source=0)  # comm.send(N,dest=1)
    print(c)
    while (c > 0):
        acc1x, acc1y, acc2x, acc2y = ACC(x, y, X, Y)
        comm.send((acc1x, acc1y, acc2x, acc2y), dest=0)
        h = comm.recv(source=0)
        x, y, Vx, Vy = move(x, y, Vx, Vy, acc1x, acc1y, acc2x, acc2y, h)
        if rank == 1: c = "r"
        if rank == 2: c = "g"
        if rank == 3: c = "b"
        ball = matplotlib.patches.Circle((x, y), radius=r, fill=True, color=c)
        c = comm.recv(source=0)  # comm.send(N-1-t, dest=1)
        comm.send(x, dest=0)
        comm.send(y, dest=0)
        comm.send(ball, dest=0)
        X = comm.recv(source=0)  # comm.send(X,dest=1)
        Y = comm.recv(source=0)  # comm.send(Y,dest=1)
    comm.send(x, dest=0)
    comm.send(y, dest=0)
    comm.send(ball, dest=0)


# mpirun -np 7 python3 seventh_task.py
# ffmpeg -r 1 -i "Pics/Balls%d.png" res.avi

