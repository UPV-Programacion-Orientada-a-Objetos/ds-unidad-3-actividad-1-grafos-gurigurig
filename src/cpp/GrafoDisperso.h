/**
 * @file GrafoDisperso.h
 * @brief Implementación de grafo usando formato CSR (Compressed Sparse Row)
 * @author NeuroNet Team
 * 
 * Esta clase implementa un grafo dirigido utilizando el formato CSR
 * para una representación eficiente en memoria de matrices dispersas.
 */

#ifndef GRAFO_DISPERSO_H
#define GRAFO_DISPERSO_H

#include "GrafoBase.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <queue>
#include <stack>
#include <unordered_set>
#include <unordered_map>
#include <algorithm>
#include <chrono>

/**
 * @class GrafoDisperso
 * @brief Implementación concreta de GrafoBase usando formato CSR
 * 
 * El formato CSR utiliza tres vectores:
 * - row_ptr: Punteros al inicio de cada fila en column_indices
 * - column_indices: Índices de columna de los elementos no nulos
 * - values: Valores de las aristas (en este caso, todas son 1)
 * 
 * Para un grafo no ponderado, values puede omitirse, pero se mantiene
 * por extensibilidad.
 */
class GrafoDisperso : public GrafoBase {
private:
    // Vectores CSR para representación de la matriz de adyacencia
    std::vector<int> row_ptr;        ///< Punteros al inicio de cada fila
    std::vector<int> column_indices; ///< Índices de columna (destinos de aristas)
    std::vector<int> values;         ///< Valores de las aristas (peso = 1)
    
    int numNodos;                    ///< Número total de nodos
    int numAristas;                  ///< Número total de aristas
    
    // Para grado de entrada (requiere estructura adicional o cálculo)
    std::vector<int> gradoEntrada;   ///< Cache del grado de entrada por nodo
    
    /**
     * @brief Construye la estructura CSR a partir de una lista de aristas
     * @param aristas Vector de pares (origen, destino)
     * @param maxNodo El ID máximo de nodo encontrado
     */
    void construirCSR(std::vector<std::pair<int, int>>& aristas, int maxNodo);

public:
    /**
     * @brief Constructor por defecto
     */
    GrafoDisperso();
    
    /**
     * @brief Destructor
     */
    ~GrafoDisperso() override;

    // Implementaciones de métodos virtuales de GrafoBase
    bool cargarDatos(const std::string& filename) override;
    std::vector<std::pair<int, int>> BFS(int nodoInicio, int profundidadMaxima) override;
    std::vector<int> DFS(int nodoInicio) override;
    int obtenerGrado(int nodo) override;
    int obtenerGradoEntrada(int nodo) override;
    std::vector<int> getVecinos(int nodo) override;
    int getNumNodos() override;
    int getNumAristas() override;
    std::pair<int, int> getNodoMayorGrado() override;
    size_t getMemoriaUsada() override;
    std::vector<std::pair<int, int>> getAristasSubgrafo(int nodoInicio, int profundidadMaxima) override;
    
    /**
     * @brief Imprime información de debug del grafo
     */
    void printDebugInfo();
};

#endif // GRAFO_DISPERSO_H
