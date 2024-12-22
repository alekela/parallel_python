from mpi4py import MPI


def f(x):
	return (1 - x**2) ** 0.5


def integral(start, stop, n):
	step = (stop - start) / (n - 1)
	sum = 0
	for i in range(n):
		sum += f(start + i * step)
	return sum * step


N = 10000000
world = MPI.COMM_WORLD
rank = world.Get_rank()
size = world.Get_size()

ns = [N // size for i in range(size)]
for i in range(N % size):
	ns[i] += 1

start = 1 / size * rank
stop = 1 / size * (rank + 1)

p = integral(start, stop, ns[rank])

if size > 1:
	total_integral = world.reduce(p, op=MPI.SUM)
else:
	total_integral = p

if rank == 0:
	print(4*total_integral)
