"""
test_neuronet.py
Pruebas unitarias para el sistema NeuroNet

Ejecutar con: pytest tests/test_neuronet.py -v
"""

import pytest
import os
import sys

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Verificar si el módulo está compilado
try:
    import neuronet_core
    CORE_DISPONIBLE = True
except ImportError:
    CORE_DISPONIBLE = False


# Obtener la ruta al archivo de prueba
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
EJEMPLO_GRAFO = os.path.join(DATA_DIR, "ejemplo_grafo.txt")


@pytest.mark.skipif(not CORE_DISPONIBLE, reason="neuronet_core no compilado")
class TestGrafoDisperso:
    """Pruebas para la clase PyGrafoDisperso"""
    
    @pytest.fixture
    def grafo(self):
        """Fixture que crea un grafo y carga datos de prueba"""
        g = neuronet_core.PyGrafoDisperso()
        if os.path.exists(EJEMPLO_GRAFO):
            g.cargar_datos(EJEMPLO_GRAFO)
        return g
    
    def test_inicializacion(self):
        """Prueba la inicialización del grafo"""
        g = neuronet_core.PyGrafoDisperso()
        assert g is not None
        assert g.get_num_nodos() == 0
        assert g.get_num_aristas() == 0
    
    def test_cargar_datos(self, grafo):
        """Prueba la carga de datos desde archivo"""
        assert grafo.get_num_nodos() > 0
        assert grafo.get_num_aristas() > 0
    
    def test_cargar_archivo_inexistente(self):
        """Prueba el manejo de archivo inexistente"""
        g = neuronet_core.PyGrafoDisperso()
        resultado = g.cargar_datos("archivo_que_no_existe.txt")
        assert resultado == False
    
    def test_bfs(self, grafo):
        """Prueba la búsqueda BFS"""
        resultado = grafo.bfs(0, 2)
        assert len(resultado) > 0
        # El nodo de inicio debe estar en el resultado con distancia 0
        nodos = [n for n, d in resultado]
        distancias = [d for n, d in resultado]
        assert 0 in nodos
        assert min(distancias) == 0
        assert max(distancias) <= 2
    
    def test_bfs_profundidad_cero(self, grafo):
        """Prueba BFS con profundidad 0"""
        resultado = grafo.bfs(0, 0)
        assert len(resultado) == 1
        assert resultado[0] == (0, 0)
    
    def test_bfs_nodo_invalido(self, grafo):
        """Prueba BFS con nodo inválido"""
        resultado = grafo.bfs(-1, 2)
        assert len(resultado) == 0
    
    def test_dfs(self, grafo):
        """Prueba la búsqueda DFS"""
        resultado = grafo.dfs(0)
        assert len(resultado) > 0
        assert resultado[0] == 0  # El primer nodo debe ser el de inicio
    
    def test_obtener_grado(self, grafo):
        """Prueba la obtención del grado de un nodo"""
        grado = grafo.obtener_grado(0)
        assert grado >= 0
    
    def test_obtener_grado_nodo_invalido(self, grafo):
        """Prueba el grado de un nodo inválido"""
        grado = grafo.obtener_grado(-1)
        assert grado == -1
    
    def test_get_vecinos(self, grafo):
        """Prueba la obtención de vecinos"""
        vecinos = grafo.get_vecinos(0)
        grado = grafo.obtener_grado(0)
        assert len(vecinos) == grado
    
    def test_nodo_mayor_grado(self, grafo):
        """Prueba la identificación del nodo con mayor grado"""
        nodo, grado = grafo.get_nodo_mayor_grado()
        assert nodo >= 0
        assert grado >= 0
    
    def test_memoria_usada(self, grafo):
        """Prueba la estimación de memoria"""
        memoria = grafo.get_memoria_usada()
        assert memoria > 0
        
        memoria_mb = grafo.get_memoria_usada_mb()
        assert memoria_mb > 0
    
    def test_aristas_subgrafo(self, grafo):
        """Prueba la obtención de aristas del subgrafo"""
        aristas = grafo.get_aristas_subgrafo(0, 2)
        assert len(aristas) >= 0
        
        # Verificar que las aristas son tuplas válidas
        for origen, destino in aristas:
            assert origen >= 0
            assert destino >= 0
    
    def test_estadisticas(self, grafo):
        """Prueba la obtención de estadísticas"""
        stats = grafo.get_estadisticas()
        assert 'num_nodos' in stats
        assert 'num_aristas' in stats
        assert 'memoria_mb' in stats
        assert stats['num_nodos'] > 0


@pytest.mark.skipif(not CORE_DISPONIBLE, reason="neuronet_core no compilado")
class TestRendimiento:
    """Pruebas de rendimiento básicas"""
    
    def test_carga_rendimiento(self):
        """Prueba que la carga sea razonablemente rápida"""
        import time
        
        g = neuronet_core.PyGrafoDisperso()
        
        if os.path.exists(EJEMPLO_GRAFO):
            inicio = time.time()
            g.cargar_datos(EJEMPLO_GRAFO)
            duracion = time.time() - inicio
            
            # La carga debería tomar menos de 1 segundo para el archivo de prueba
            assert duracion < 1.0
    
    def test_bfs_rendimiento(self):
        """Prueba que BFS sea razonablemente rápido"""
        import time
        
        g = neuronet_core.PyGrafoDisperso()
        
        if os.path.exists(EJEMPLO_GRAFO):
            g.cargar_datos(EJEMPLO_GRAFO)
            
            inicio = time.time()
            g.bfs(0, 5)
            duracion = time.time() - inicio
            
            # BFS debería tomar menos de 0.1 segundos
            assert duracion < 0.1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
