import matplotlib.patches
import pylab
from random import randint
from mpi4py import MPI
import numpy as np


def patch_from_velocity(point, V, color, r, dt):
	x = point[0] + V[0] * dt
	y = point[1] + V[1] * dt
	if x -r < 0:
		x = 2 * r - x
		V[0], V[1] = -V[0], V[1]
	elif x + r > 1:
		x = 2 * (1 - r) - x
		V[0], V[1] = -V[0], V[1]
	if y -r < 0:
		y = 2 * r - y
		V[0], V[1] = V[0], -V[1]
	elif y + r > 1:
		y = 2 * (1 - r) - y
		V[0], V[1] = V[0], -V[1]
	point[0], point[1] = x, y
	circle = matplotlib.patches.Circle((x, y), radius=r, fill=True, color=color)
	return circle


	
comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()


if rank == 0:
	pylab.xlim(0, 1)
	pylab.ylim(0, 1)
	axes = pylab.gca()
	axes.set_aspect('equal')

	r = 0.05
	V = 0.02
	dt = 1
	Vs = []
	points = []
	colors = ["r", "g", "b"]
	for i in range(size-1):
		x = randint(r * 100, 100 - r * 100) / 100
		y = randint(r * 100, 100 - r * 100) / 100
		points.append([x, y])

		angle = randint(0, 359)
		Vx = V * np.cos(angle / 180 * np.pi)
		Vy = V * np.sin(angle / 180 * np.pi)
		Vs.append([Vx, Vy])
		
		message = [r, dt, points[-1], Vs[-1], colors[i%3]]
		comm.send(message, dest=i+1, tag=11)


if rank > 0:
	message = comm.recv(source=0, tag=11)
	r = message[0]
	dt = message[1]
	point = message[2]
	Vel = message[3]
	color = message[4]

comm.Barrier()

for t in range(1000):
	if rank > 0:	
		circle = patch_from_velocity(point, Vel, color, r, dt)
	if rank == 0:
		circle = None

	circles = comm.gather(circle, root=0)
	if rank == 0:
		circles = circles[1:]
		for figure in circles:
			axes.add_patch(figure)

		pylab.savefig(f"Pics/Balls{t}.png")

		for figure in circles:
			figure.remove()
	print(f"Process {rank} finished {t} iteration")
	comm.Barrier()

# mpirun -np 2 python3 balls.py
# ffmpeg -r 1 -i "Pics/Balls%d.png" Balls.avi




