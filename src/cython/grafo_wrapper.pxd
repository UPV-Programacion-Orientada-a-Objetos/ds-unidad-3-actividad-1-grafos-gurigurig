# grafo_wrapper.pxd
# Declaraciones de las clases C++ para Cython

from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.pair cimport pair

# Declaración de la clase C++ GrafoDisperso
cdef extern from "GrafoDisperso.h":
    cdef cppclass GrafoDisperso:
        GrafoDisperso() except +
        bint cargarDatos(string filename)
        vector[pair[int, int]] BFS(int nodoInicio, int profundidadMaxima)
        vector[int] DFS(int nodoInicio)
        int obtenerGrado(int nodo)
        int obtenerGradoEntrada(int nodo)
        vector[int] getVecinos(int nodo)
        int getNumNodos()
        int getNumAristas()
        pair[int, int] getNodoMayorGrado()
        size_t getMemoriaUsada()
        vector[pair[int, int]] getAristasSubgrafo(int nodoInicio, int profundidadMaxima)
        void printDebugInfo()
