import numpy as np
from mpi4py import MPI

oldcomm = MPI.COMM_WORLD
oldcommdup = oldcomm.Dup()

numprocs = oldcommdup.Get_size()
myid = oldcommdup.Get_rank()
server = 0
color = (myid == server)
print("color =  ", color, "  myid= ", myid)

splitcomm = oldcomm.Split(color=color, key=myid)

if color == 0:
    remote_leader_rank = server
else:
    remote_leader_rank = 1

inter_comm = splitcomm.Create_intercomm(0, oldcommdup, remote_leader_rank)

oldcommdup.Free()
if myid == server:
    for i in range(numprocs-1):
        message = inter_comm.recv(source=i)
        print("Process rank ", myid, "  received  ", message, " from  ", i)
else:
    counter = myid
    inter_comm.send(counter, dest=0)
    print("Process rank ", myid, " send ", counter)
