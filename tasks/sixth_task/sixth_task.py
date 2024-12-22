import pylab
import matplotlib.pyplot as plt
import numpy as np
from mpi4py import MPI


def plot_sphere(ax, x, y, z, r, resolution, **kwargs):
	u = np.linspace(0, 2 * np.pi, resolution)
	v = np.linspace(0, np.pi, resolution)

	xx = r * np.outer(np.cos(u), np.sin(v)) + x
	yy = r * np.outer(np.sin(u), np.sin(v)) + y
	zz = r * np.outer(np.ones(np.size(u)), np.cos(v)) + z
	surface = ax.plot_surface(xx, yy, zz, rstride=4, cstride=4, **kwargs)
	return surface


def ROTATE_X(alpha, Y, Z, Vy, Vz):
	alpha = np.pi * alpha / 180.
	ry = Y * np.cos(alpha) - Z * np.sin(alpha)
	rz = Y * np.sin(alpha) + Z * np.cos(alpha)
	Y = ry
	Z = rz
	ry = Vy * np.cos(alpha) - Vz * np.sin(alpha)
	rz = Vy * np.sin(alpha) + Vz * np.cos(alpha)
	Vy = ry
	Vz = rz
	return Y, Z, Vy, Vz


def ROTATE_Y(alpha, X, Z, Vx, Vz):
	alpha = np.pi * alpha / 180.
	rx = X * np.cos(alpha) + Z * np.sin(alpha)
	rz = -X * np.sin(alpha) + Z * np.cos(alpha)
	X = rx
	Z = rz
	rx = Vx * np.cos(alpha) + Vz * np.sin(alpha)
	rz = -Vx * np.sin(alpha) + Vz * np.cos(alpha)
	Vx = rx
	Vz = rz
	return X, Z, Vx, Vz


def ROTATE_Z(alpha, X, Y, Vx, Vy):
	alpha = np.pi * alpha / 180.
	rx = X * np.cos(alpha) - Y * np.sin(alpha)
	ry = X * np.sin(alpha) + Y * np.cos(alpha)
	X = rx
	Y = ry
	rx = Vx * np.cos(alpha) - Vy * np.sin(alpha)
	ry = Vx * np.sin(alpha) + Vy * np.cos(alpha)
	Vx = rx
	Vy = ry
	return X, Y, Vx, Vy


def earth(x, y, z, R):
	surface = plot_sphere(ax, x, y, z, R, 100, color='b')


def FIND_R_cubed(x, y, z):
	R = np.sqrt(x ** 2 + y ** 2 + z ** 2)
	R3 = R ** 3
	return R3


def acc(x, R3):
	return -G * M * x / R3


def move(X, Y, Z, Vx, Vy, Vz):
	X += Vx * 60
	Y += Vy * 60
	Z += Vz * 60

	R3 = FIND_R_cubed(X, Y, Z)
	Vx += acc(X, R3) * 60
	Vy += acc(Y, R3) * 60
	Vz += acc(Z, R3) * 60
	return X, Y, Z, Vx, Vy, Vz


if __name__ == "__main__":
	comm = MPI.COMM_WORLD
	size = comm.Get_size()
	rank = comm.Get_rank()

	fig = plt.figure('rrr', [10., 10.])
	ax = fig.add_subplot(projection='3d')
	ax.grid(0)
	ax.set_xlabel('X')
	ax.set_ylabel('Y')
	ax.set_zlabel('Z')
	ax.view_init(elev=0, azim=0)
	ax.set_xlim(-9E6, 9E6)
	ax.set_ylim(-9E6, 9E6)
	ax.set_zlim(-9E6, 9E6)
	colors = ["r", "g", "b", 'c', 'm', 'y', 'k']
	
	if rank == 0:
		X = 0
		Y = 0
		Z = 0
		r = 0
		Clr = 0
		R = 6374E03
		earth(0, 0, 0, R)


	if rank > 0:
		R = 6374E03
		M = 5.972E24
		G = 6.67E-11
		h0 = 2000000
		V = 8000

		Y = 0
		X = R + h0 
		Z = 0 

		Clr = colors[rank - 1]
		r = R / (45 - (rank - 1) * 5)
		alpha = np.pi * (90 - 15 * (rank - 1)) / 180.
		phi = np.pi * (15 * (rank - 1)) / 180.
		AX = plot_sphere(ax, X, Y, Z, r, 10, color=Clr)
		R3 = FIND_R_cubed(X, Y, Z)

		Vx = V * np.cos(phi) * np.cos(alpha) + acc(X, R3) / 2. * 60
		Vy = V * np.cos(phi) * np.sin(alpha) + acc(Y, R3) / 2. * 60
		Vz = V * np.sin(phi) + acc(Z, R3) / 2. * 60

		Y, Z, Vy, Vz = ROTATE_X(-45 + 15 * (rank - 1), Y, Z, Vy, Vz)
		X, Z, Vx, Vz = ROTATE_Y(45 - 15 * (rank - 1), X, Z, Vx, Vz)
		X, Y, Vx, Vy = ROTATE_Z(-30 + 15 * (rank - 1), X, Y, Vx, Vy)
	
	comm.Barrier()

	for t in range(300):
		if rank == 0:
			message = []
		if rank > 0:
			X, Y, Z, Vx, Vy, Vz = move(X, Y, Z, Vx, Vy, Vz)
			message = [X, Y, Z, r, 10, Clr]
			comm.send(message, dest=0, tag=11)
		
		data = comm.gather(message, root=0) 
		if rank == 0:
			for i in range(1, size):
				plot_sphere(ax, data[i][0], data[i][1], data[i][2], data[i][3], data[i][4], color=data[i][5])
		comm.Barrier()

	pylab.savefig(f"{size-1}orbits.png")


# mpirun -np 8 python3 sixth_task.py
