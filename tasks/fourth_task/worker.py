from mpi4py import MPI
import numpy
import sys


def f(x):
	return 1 / (1 + x**2)


def integral(start, n):
	sum = 0
	for i in range(start, start + n):
		sum += f(2*i * step) + 4 * f((2*i+1) * step) + f(2*(i+1) * step)
	return sum * step * 4 / 3


comm = MPI.Comm.Get_parent()
size = comm.Get_size()
rank = comm.Get_rank()
N = numpy.array(0)
comm.Bcast(N, root=0)

step = 1 / (N - 1)
N //= 2
ns = [N // size for i in range(size)]
for i in range(N % size):
	ns[i] += 1

start = 0 if rank == 0 else sum(ns[:rank])

PI = integral(start, ns[rank])

PI = numpy.array(PI)
comm.Reduce(PI, None, op=MPI.SUM, root=0)
comm.Disconnect()
