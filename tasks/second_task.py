from mpi4py import MPI
import argparse


world = MPI.COMM_WORLD
rank = world.Get_rank()
size = world.Get_size()

parser = argparse.ArgumentParser()
parser.add_argument("message")

args = parser.parse_args()

message = int(args.message)

if rank == 0:
    message = world.recv(source=1, tag=11)
    print(f"Computer number {rank} receive message {message}")
elif rank == size-1:
    message *= 2 * (rank % 2) - 1
    world.send(message, dest=rank-1, tag=11)
    print(f"Computer number {rank} send message {message}")
else:
    message = world.recv(source=rank+1, tag=11)
    message *= 2 * (rank % 2) - 1
    world.send(message, dest=rank-1, tag=11)
    print(f"Computer number {rank} send message {message}")
