from mpi4py import MPI

world = MPI.COMM_WORLD
rank = world.Get_rank()

M = world.Get_size()
N = 840

r = list(range(rank * N // M + 1, (rank+1)*N//M + 1))
print("Proccess number:", rank, "List:", *r, "Sum:", sum(r))
