import numpy as np
import matplotlib.pyplot as plt
import time
from matplotlib.pyplot import imshow, show, cm

import JuliaSet
      
t = time.time()
pmin, pmax, qmin, qmax = -2, 2, -2, 2
# пусть c = p + iq
ppoints, qpoints = 2000, 2000
max_iterations = 100
infinity_border = 10
img=JuliaSet.calc(ppoints, qpoints,pmin, pmax, qmin, qmax,max_iterations,infinity_border)
print ('Execution time:', time.time() - t)

plt.imsave('Finish.png',img.T, cmap=cm.gist_ncar)
#plt.show()
# транспонируем картинку, чтобы оси были направлены правильно
