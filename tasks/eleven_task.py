import pymp
import numpy


# функция слияния отсортированных массивов
def merge(list1, list2):
	size1 = len(list1)
	size2 = len(list2)
	res = []
	i, j = 0, 0
	while i < size1 and j < size2:
		if list1[i] < list2[j]:
			res.append(list1[i])
			i += 1
		else:
			res.append(list2[j])
			j += 1
	res.extend(list1[i:])
	res.extend(list2[j:])
	return res


N=1000000
proc_num = 4
values = (numpy.float32(numpy.random.uniform(low=-5.0, high=5.0, size=N))).tolist()
result = pymp.shared.array((N,))

# разбиение начального массива на 4, сортировка каждого куска параллельно
with pymp.Parallel(proc_num) as p:
	for i in p.range(0, proc_num):
		with p.lock:
			local_values = values[N // proc_num * i:N // proc_num * (i + 1)]
			local_values.sort()
			for j in range(len(local_values)):
				result[N // proc_num * i + j] = local_values[j]

# Слияние первого куска со вторым и третьего с четвертым (параллельно на двух ядрах)
with pymp.Parallel(2) as p:
	for i in p.range(0, 2):
		list1 = result[N // proc_num * (2*i):N // proc_num * (2*i + 1)]
		list2 = result[N // proc_num * (2*i + 1):N // proc_num * (2*i + 2)]
		res = merge(list1, list2)
		for j in range(len(res)):
			result[N // 2 * i + j] = res[j]

# слияние двух отсортированных кусков
list1 = result[:N//2]
list2 = result[N//2:]
res = merge(list1, list2)
print("Массив отсортирован")
print("Проверка на то, что отсортированный параллельно массив совпадает с отсортированным обычным способом: ", res == sorted(values))