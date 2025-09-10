# setup.py
from setuptools import setup
from setuptools.extension import Extension
from Cython.Build import cythonize
import numpy as np

extensions = [
    Extension("lee_adaptive", ["lee_adaptive.pyx"], include_dirs=[np.get_include()])
]

setup(ext_modules=cythonize(extensions, compiler_directives={"language_level": "3"}))
