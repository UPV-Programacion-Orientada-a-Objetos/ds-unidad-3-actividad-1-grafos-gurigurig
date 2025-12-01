/**
 * @file GrafoBase.h
 * @brief Clase abstracta que define la interfaz base para grafos dispersos
 * @author NeuroNet Team
 * 
 * Esta clase abstracta define los métodos virtuales puros que toda
 * implementación de grafo debe proporcionar para el sistema NeuroNet.
 */

#ifndef GRAFO_BASE_H
#define GRAFO_BASE_H

#include <string>
#include <vector>
#include <utility>

/**
 * @class GrafoBase
 * @brief Interfaz abstracta para la representación de grafos
 * 
 * Define los métodos esenciales para cargar datos, realizar búsquedas
 * y obtener información topológica del grafo.
 */
class GrafoBase {
public:
    /**
     * @brief Destructor virtual para permitir destrucción polimórfica
     */
    virtual ~GrafoBase() = default;

    /**
     * @brief Carga los datos del grafo desde un archivo de texto
     * @param filename Ruta al archivo en formato Edge List (NodoOrigen NodoDestino)
     * @return true si la carga fue exitosa, false en caso contrario
     */
    virtual bool cargarDatos(const std::string& filename) = 0;

    /**
     * @brief Realiza una búsqueda en anchura (BFS) desde un nodo origen
     * @param nodoInicio ID del nodo desde donde iniciar la búsqueda
     * @param profundidadMaxima Límite de profundidad para la búsqueda
     * @return Vector de pares (nodo, distancia) con los nodos visitados
     */
    virtual std::vector<std::pair<int, int>> BFS(int nodoInicio, int profundidadMaxima) = 0;

    /**
     * @brief Realiza una búsqueda en profundidad (DFS) desde un nodo origen
     * @param nodoInicio ID del nodo desde donde iniciar la búsqueda
     * @return Vector con los IDs de los nodos visitados en orden DFS
     */
    virtual std::vector<int> DFS(int nodoInicio) = 0;

    /**
     * @brief Obtiene el grado de salida de un nodo específico
     * @param nodo ID del nodo
     * @return Número de aristas salientes del nodo
     */
    virtual int obtenerGrado(int nodo) = 0;

    /**
     * @brief Obtiene el grado de entrada de un nodo específico
     * @param nodo ID del nodo
     * @return Número de aristas entrantes al nodo
     */
    virtual int obtenerGradoEntrada(int nodo) = 0;

    /**
     * @brief Obtiene los nodos vecinos (conectados) de un nodo dado
     * @param nodo ID del nodo
     * @return Vector con los IDs de los nodos vecinos
     */
    virtual std::vector<int> getVecinos(int nodo) = 0;

    /**
     * @brief Obtiene el número total de nodos en el grafo
     * @return Cantidad de nodos
     */
    virtual int getNumNodos() = 0;

    /**
     * @brief Obtiene el número total de aristas en el grafo
     * @return Cantidad de aristas
     */
    virtual int getNumAristas() = 0;

    /**
     * @brief Encuentra el nodo con el mayor grado (más conexiones)
     * @return Par (ID del nodo, grado) del nodo más conectado
     */
    virtual std::pair<int, int> getNodoMayorGrado() = 0;

    /**
     * @brief Estima la memoria utilizada por la estructura del grafo
     * @return Memoria en bytes
     */
    virtual size_t getMemoriaUsada() = 0;

    /**
     * @brief Obtiene las aristas del subgrafo resultante de un BFS
     * @param nodoInicio Nodo de inicio para el BFS
     * @param profundidadMaxima Profundidad máxima de la búsqueda
     * @return Vector de pares (nodoOrigen, nodoDestino) representando las aristas
     */
    virtual std::vector<std::pair<int, int>> getAristasSubgrafo(int nodoInicio, int profundidadMaxima) = 0;
};

#endif // GRAFO_BASE_H
