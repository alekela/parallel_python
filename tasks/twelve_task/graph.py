import matplotlib.pyplot as plt

with open("time.txt") as f:
	f.readline()
	data = f.readlines()

data = list(map(lambda x: x.split(','), data))
times = list(map(lambda x: float(x[1]), data))
ns = list(map(lambda x: float(x[0]), data))
plt.grid()
plt.xlabel("Кол-во процессов")
plt.ylabel("Время, сек")
plt.scatter(ns, times, color='b')
plt.plot(ns, times, color='b')
plt.savefig("time_graph.png")