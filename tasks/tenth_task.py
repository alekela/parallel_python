import pymp

num_procs = 4
N = int(input("Enter N: "))
ns = pymp.shared.array((num_procs,))
for i in range(num_procs):
	ns[i] = N // num_procs * (i+1)
for i in range(N % num_procs):
	ns[i] += 1

A = pymp.shared.array((N,))
B = pymp.shared.array((N-1,))
summa_A = pymp.shared.array((num_procs,))
summa_B = pymp.shared.array((num_procs,))

with pymp.Parallel(num_procs) as p:
	for i in p.range(0, num_procs):
		if i == 0:
			start = 0
			end = int(ns[i])
		else:
			start = int(ns[i-1])
			end = int(ns[i])
		
		for j in range(start, end):
			A[j] = j+1
		
		s = 0
		for j in range(start, end):
			s += A[j]
		with p.lock:
			summa_A[i] = s

with pymp.Parallel(num_procs) as p:
	for i in p.range(0, num_procs):
		if i == 0:
			start = 0
			end = int(ns[i]) 
		elif i == num_procs -1:
			start = int(ns[i-1])
			end = int(ns[i]) - 1	
		else:
			start = int(ns[i-1])
			end = int(ns[i])

		for j in range(start, end):
			B[j] = (A[j] + A[j+1]) / 2
		
		s = 0
		for j in range(start, end):
			s += B[j]
		with p.lock:
			summa_B[i] = s
	
print("Array A:", A)
print("Sum of array A:", sum(summa_A))
print("Array B:", B)
print("Sum of array B:", sum(summa_B))
