# distutils: language = c++

"""
grafo_wrapper.pyx
Wrapper de Cython para exponer la clase GrafoDisperso de C++ a Python

Este módulo actúa como puente entre el motor de procesamiento C++ de alto
rendimiento y la interfaz Python para visualización y control.
"""

from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp.pair cimport pair
from cython.operator cimport dereference as deref

import time

# Importar la declaración de la clase C++
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


cdef class PyGrafoDisperso:
    """
    Wrapper Python para la clase C++ GrafoDisperso.
    
    Esta clase encapsula el motor de grafos C++ y proporciona una interfaz
    Pythonica para interactuar con él desde la GUI.
    
    Attributes:
        _grafo: Puntero a la instancia C++ de GrafoDisperso
        _tiempo_carga: Tiempo de carga del último dataset
        _archivo_cargado: Nombre del archivo actualmente cargado
    """
    cdef GrafoDisperso* _grafo
    cdef double _tiempo_carga
    cdef str _archivo_cargado
    
    def __cinit__(self):
        """Inicializa el wrapper creando una nueva instancia de GrafoDisperso"""
        self._grafo = new GrafoDisperso()
        self._tiempo_carga = 0.0
        self._archivo_cargado = ""
        print("[Cython] Wrapper inicializado correctamente.")
    
    def __dealloc__(self):
        """Libera la memoria del objeto C++"""
        if self._grafo != NULL:
            del self._grafo
            print("[Cython] Memoria liberada.")
    
    def cargar_datos(self, str filename) -> bool:
        """
        Carga un dataset desde un archivo de texto.
        
        Args:
            filename: Ruta al archivo en formato Edge List
            
        Returns:
            bool: True si la carga fue exitosa
        """
        print(f"[Cython] Solicitud recibida: Cargar archivo '{filename}'")
        
        cdef string cpp_filename = filename.encode('utf-8')
        cdef bint resultado
        
        inicio = time.time()
        resultado = self._grafo.cargarDatos(cpp_filename)
        self._tiempo_carga = time.time() - inicio
        
        if resultado:
            self._archivo_cargado = filename
            print(f"[Cython] Archivo cargado exitosamente en {self._tiempo_carga:.3f} segundos.")
        else:
            print("[Cython] Error al cargar el archivo.")
        
        return resultado
    
    def bfs(self, int nodo_inicio, int profundidad_maxima) -> list:
        """
        Ejecuta búsqueda en anchura (BFS) desde un nodo.
        
        Args:
            nodo_inicio: ID del nodo de inicio
            profundidad_maxima: Límite de profundidad
            
        Returns:
            list: Lista de tuplas (nodo, distancia)
        """
        print(f"[Cython] Solicitud recibida: BFS desde Nodo {nodo_inicio}, Profundidad {profundidad_maxima}.")
        
        cdef vector[pair[int, int]] resultado = self._grafo.BFS(nodo_inicio, profundidad_maxima)
        
        # Convertir a lista Python
        py_resultado = [(p.first, p.second) for p in resultado]
        
        print(f"[Cython] Retornando {len(py_resultado)} nodos a Python.")
        return py_resultado
    
    def dfs(self, int nodo_inicio) -> list:
        """
        Ejecuta búsqueda en profundidad (DFS) desde un nodo.
        
        Args:
            nodo_inicio: ID del nodo de inicio
            
        Returns:
            list: Lista de IDs de nodos visitados
        """
        print(f"[Cython] Solicitud recibida: DFS desde Nodo {nodo_inicio}.")
        
        cdef vector[int] resultado = self._grafo.DFS(nodo_inicio)
        
        py_resultado = list(resultado)
        print(f"[Cython] Retornando {len(py_resultado)} nodos a Python.")
        return py_resultado
    
    def obtener_grado(self, int nodo) -> int:
        """
        Obtiene el grado de salida de un nodo.
        
        Args:
            nodo: ID del nodo
            
        Returns:
            int: Grado de salida del nodo
        """
        return self._grafo.obtenerGrado(nodo)
    
    def obtener_grado_entrada(self, int nodo) -> int:
        """
        Obtiene el grado de entrada de un nodo.
        
        Args:
            nodo: ID del nodo
            
        Returns:
            int: Grado de entrada del nodo
        """
        return self._grafo.obtenerGradoEntrada(nodo)
    
    def get_vecinos(self, int nodo) -> list:
        """
        Obtiene los nodos vecinos de un nodo dado.
        
        Args:
            nodo: ID del nodo
            
        Returns:
            list: Lista de IDs de nodos vecinos
        """
        cdef vector[int] vecinos = self._grafo.getVecinos(nodo)
        return list(vecinos)
    
    def get_num_nodos(self) -> int:
        """Retorna el número total de nodos en el grafo."""
        return self._grafo.getNumNodos()
    
    def get_num_aristas(self) -> int:
        """Retorna el número total de aristas en el grafo."""
        return self._grafo.getNumAristas()
    
    def get_nodo_mayor_grado(self) -> tuple:
        """
        Encuentra el nodo con mayor grado de salida.
        
        Returns:
            tuple: (id_nodo, grado)
        """
        print("[Cython] Solicitud recibida: Obtener nodo con mayor grado.")
        
        cdef pair[int, int] resultado = self._grafo.getNodoMayorGrado()
        
        return (resultado.first, resultado.second)
    
    def get_memoria_usada(self) -> int:
        """
        Obtiene la memoria utilizada por la estructura del grafo.
        
        Returns:
            int: Memoria en bytes
        """
        return self._grafo.getMemoriaUsada()
    
    def get_memoria_usada_mb(self) -> float:
        """
        Obtiene la memoria utilizada en megabytes.
        
        Returns:
            float: Memoria en MB
        """
        return self._grafo.getMemoriaUsada() / (1024.0 * 1024.0)
    
    def get_aristas_subgrafo(self, int nodo_inicio, int profundidad_maxima) -> list:
        """
        Obtiene las aristas del subgrafo resultante de un BFS.
        
        Args:
            nodo_inicio: Nodo de inicio
            profundidad_maxima: Profundidad máxima de búsqueda
            
        Returns:
            list: Lista de tuplas (origen, destino)
        """
        print(f"[Cython] Solicitud recibida: Subgrafo desde Nodo {nodo_inicio}.")
        
        cdef vector[pair[int, int]] aristas = self._grafo.getAristasSubgrafo(
            nodo_inicio, profundidad_maxima
        )
        
        py_aristas = [(a.first, a.second) for a in aristas]
        
        print(f"[Cython] Retornando lista de adyacencia local a Python.")
        return py_aristas
    
    def print_debug_info(self):
        """Imprime información de debug del grafo."""
        self._grafo.printDebugInfo()
    
    @property
    def tiempo_carga(self) -> float:
        """Tiempo de carga del último dataset."""
        return self._tiempo_carga
    
    @property
    def archivo_cargado(self) -> str:
        """Nombre del archivo actualmente cargado."""
        return self._archivo_cargado
    
    def get_estadisticas(self) -> dict:
        """
        Obtiene estadísticas generales del grafo.
        
        Returns:
            dict: Diccionario con estadísticas
        """
        nodo_max, grado_max = self.get_nodo_mayor_grado()
        
        return {
            'num_nodos': self.get_num_nodos(),
            'num_aristas': self.get_num_aristas(),
            'memoria_mb': self.get_memoria_usada_mb(),
            'tiempo_carga': self._tiempo_carga,
            'archivo': self._archivo_cargado,
            'nodo_mayor_grado': nodo_max,
            'mayor_grado': grado_max
        }
