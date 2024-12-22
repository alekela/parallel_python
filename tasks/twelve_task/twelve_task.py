import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pymp

x, y, z = 0, 1, 10
rho, sigma, beta = 28, 10, 8 / 3
t0 = 0
tf = 10
dt = 0.008
t = np.arange(t0, tf + dt, dt)
n = len(t)


def f(t, r):  # определение системы уравнений Лоренца
    x, y, z = r
    return np.array([sigma * (y - x),  # ... dx/dt
                     rho * x - y - x * z,  # ... dy/dt
                     x * y - beta * z])  # ... dz/dt


def RK4(t, r, f, dt):  # определение метода Рунге-Кутты 4-го порядка
    k1 = dt * f(t, r)
    k2 = dt * f(t + dt / 2, r + k1 / 2)
    k3 = dt * f(t + dt / 2, r + k2 / 2)
    k4 = dt * f(t + dt, r + k3)
    return r + (k1 + 2 * k2 + 2 * k3 + k4) / 6


def update(i):  # кадры анимации
    ax.view_init(-6, -56 + i / 2)
    ax.clear()
    ax.set(facecolor='k')
    ax.set_axis_off()
    ax.plot(evol[:i, 0], evol[:i, 1], evol[:i, 2], color='lime', lw=0.9)
    file = "Anim_Lorenz/lorenz" + str(i) + ".png"
    plt.savefig(file)


r = [x, y, z]  # вектор начального состояния
# эволюция системы уравнений
evol = np.zeros((n, 3))
evol[0, 0], evol[0, 1], evol[0, 2] = r[0], r[1], r[2]
for i in range(n - 1):
    evol[i + 1] = RK4(t[i], [evol[i, 0], evol[i, 1], evol[i, 2]], f, dt)

# построение анимации параллельно с помощью pymp
fig = plt.figure('Atrator de Lorenz', facecolor='k', figsize=(10, 9))
fig.tight_layout()
ax = fig.add_subplot(2, 1, 2, projection='3d')

num_procs = 8
ns = pymp.shared.array((num_procs,))
for i in range(num_procs):
    ns[i] = n // num_procs * (i + 1)
for i in range(n % num_procs):
    ns[i] += 1

with pymp.Parallel(num_procs) as p:
    for i in p.range(0, num_procs):
        if i == 0:
            start = 0
            end = int(ns[i])
        else:
            start = int(ns[i - 1])
            end = int(ns[i])

        for j in range(start, end):
            update(j)
