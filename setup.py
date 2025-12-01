"""
setup.py
Script de compilación para NeuroNet

Este script compila el código C++ y genera la extensión de Python
mediante Cython, permitiendo importar el motor de grafos desde Python.

Uso:
    python setup.py build_ext --inplace
"""

from setuptools import setup, Extension
from Cython.Build import cythonize
import os
import sys
import platform

# Detectar sistema operativo
is_windows = platform.system() == "Windows"

# Directorio base del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Directorios de código fuente
CPP_DIR = os.path.join(BASE_DIR, "src", "cpp")
CYTHON_DIR = os.path.join(BASE_DIR, "src", "cython")

# Configurar directorio de build corto para evitar problemas con rutas largas en Windows
if is_windows:
    BUILD_DIR = "C:\\nb"
    if not os.path.exists(BUILD_DIR):
        os.makedirs(BUILD_DIR)
    sys.argv.extend(['--build-lib', BUILD_DIR, '--build-temp', BUILD_DIR])

# Argumentos de compilación según el sistema operativo
if is_windows:
    extra_compile_args = ["/std:c++17", "/O2", "/EHsc"]
    extra_link_args = []
else:
    extra_compile_args = ["-std=c++17", "-O3", "-fPIC"]
    extra_link_args = ["-std=c++17"]

# Definir la extensión
extensions = [
    Extension(
        name="neuronet_core",  # Nombre del módulo Python resultante
        sources=[
            os.path.join(CYTHON_DIR, "grafo_wrapper.pyx"),
            os.path.join(CPP_DIR, "GrafoDisperso.cpp"),
        ],
        include_dirs=[CPP_DIR],
        language="c++",
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    )
]

# Configuración del paquete
setup(
    name="NeuroNet",
    version="1.0.0",
    description="Motor de análisis de grafos masivos con núcleo C++ y visualización Python",
    author="NeuroNet Team",
    author_email="neuronet@example.com",
    ext_modules=cythonize(
        extensions,
        compiler_directives={
            "language_level": "3",  # Python 3
            "boundscheck": False,   # Desactivar comprobación de límites para rendimiento
            "wraparound": False,    # Desactivar índices negativos para rendimiento
        }
    ),
    python_requires=">=3.7",
    install_requires=[
        "cython>=0.29",
        "networkx>=2.5",
        "matplotlib>=3.3",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pyvis>=0.1",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Cython",
        "Programming Language :: C++",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
)

if __name__ == "__main__":
    print("\n" + "="*60)
    print("NeuroNet - Compilación del motor de grafos")
    print("="*60)
    print(f"Sistema operativo: {platform.system()}")
    print(f"Python: {sys.version}")
    print(f"Directorio C++: {CPP_DIR}")
    print(f"Directorio Cython: {CYTHON_DIR}")
    print("="*60 + "\n")
