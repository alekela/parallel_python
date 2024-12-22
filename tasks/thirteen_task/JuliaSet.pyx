import numpy as np
from cython cimport boundscheck, wraparound
from cython.parallel cimport prange

cdef inline double norm2(double complex z) nogil:
    return z.real * z.real + z.imag * z.imag

cdef  int escape(double complex c1,  int max, double border ) nogil:
      cdef:
        double complex z = 0 +1j*0 
        int r=-1
        int k
        double complex c0 = -0.2+1j*0.75
      z=c1
      for k in range(1,max+1):
            z = z*z + c0  # Самая Главная Формула
            if norm2(z) > border*border: 
                r=k
                break
      return int(r)
def calc(int ppoints, int qpoints, double pmin, double pmax, double qmin, 
            double qmax,int max_iterations, double infinity_border):
       cdef:
           int ip,iq
           double hp=(pmax-pmin)/(ppoints-1)
           double hq=(qmax-qmin)/(qpoints-1)
           double complex c
           int[:, ::1] image
       image = np.zeros((ppoints, qpoints), dtype=np.int32)
       with nogil:
           for ip in prange(ppoints):
               for iq in prange(qpoints):
                    c= (pmin+ip*hp)+1j*(qmin+iq*hq)
                    image[ip,iq] = escape(c, max_iterations, infinity_border )
       return np.asarray(image)
