from mpi4py import MPI
import numpy
import sys

maxp=1
comm = MPI.COMM_SELF.Spawn(sys.executable, args=['worker.py'],maxprocs=maxp)
N = numpy.array(100000000)
comm.Bcast(N, root=MPI.ROOT)

PI = numpy.array(0.0)
comm.Reduce(None, PI, op=MPI.SUM, root=MPI.ROOT)
print(PI)
comm.Disconnect()