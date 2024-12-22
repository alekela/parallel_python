from setuptools import Extension, setup
from Cython.Build import cythonize
import numpy

ext_modules = [
    Extension(
        "juliaset",
        ["JuliaSet.pyx"],
        extra_compile_args=['-fopenmp'],
        extra_link_args=['-fopenmp'],
    )
]

setup(
    name='juliaset',
    ext_modules=cythonize("JuliaSet.pyx"),
    include_dirs=[numpy.get_include()],

)