import matplotlib.pyplot as plt

with open("data.csv") as f:
	f.readline()
	data = f.readlines()

data = list(map(lambda x: x.split(','), data))
n = list(map(lambda x: int(x[0]), data))
time = list(map(lambda x: float(x[1]), data))
time = [1/i for i in time]
ideal_time = [time[0] * i for i in n]
plt.plot(n, time)
plt.plot(n, ideal_time)
plt.xlabel("Количество процессов")
plt.ylabel("Величина, обратная времени выполнения, 1/с")
plt.grid()
plt.legend(["Реальные значения", "Идеальный случай"])
plt.show()