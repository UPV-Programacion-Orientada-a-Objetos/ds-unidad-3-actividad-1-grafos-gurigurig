/**
 * @file GrafoDisperso.cpp
 * @brief Implementación de los métodos de GrafoDisperso
 * @author NeuroNet Team
 */

#include "GrafoDisperso.h"

GrafoDisperso::GrafoDisperso() : numNodos(0), numAristas(0) {
    std::cout << "[C++ Core] Inicializando GrafoDisperso..." << std::endl;
}

GrafoDisperso::~GrafoDisperso() {
    // Los vectores se limpian automáticamente
}

void GrafoDisperso::construirCSR(std::vector<std::pair<int, int>>& aristas, int maxNodo) {
    numNodos = maxNodo + 1;
    numAristas = aristas.size();
    
    // Inicializar vectores
    row_ptr.resize(numNodos + 1, 0);
    gradoEntrada.resize(numNodos, 0);
    
    // Contar el número de aristas salientes por nodo
    for (const auto& arista : aristas) {
        row_ptr[arista.first + 1]++;
        gradoEntrada[arista.second]++;
    }
    
    // Calcular prefijos acumulados para row_ptr
    for (int i = 1; i <= numNodos; i++) {
        row_ptr[i] += row_ptr[i - 1];
    }
    
    // Llenar column_indices y values
    column_indices.resize(numAristas);
    values.resize(numAristas, 1); // Todas las aristas tienen peso 1
    
    // Vector temporal para llevar el conteo de inserción por fila
    std::vector<int> currentPos(row_ptr.begin(), row_ptr.end() - 1);
    
    for (const auto& arista : aristas) {
        int origen = arista.first;
        int destino = arista.second;
        int pos = currentPos[origen]++;
        column_indices[pos] = destino;
    }
    
    // Ordenar los índices de columna dentro de cada fila para acceso eficiente
    for (int i = 0; i < numNodos; i++) {
        std::sort(column_indices.begin() + row_ptr[i], 
                  column_indices.begin() + row_ptr[i + 1]);
    }
}

bool GrafoDisperso::cargarDatos(const std::string& filename) {
    std::cout << "[C++ Core] Cargando dataset '" << filename << "'..." << std::endl;
    
    auto startTime = std::chrono::high_resolution_clock::now();
    
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "[C++ Core] Error: No se pudo abrir el archivo " << filename << std::endl;
        return false;
    }
    
    std::vector<std::pair<int, int>> aristas;
    std::string linea;
    int maxNodo = 0;
    int lineaNum = 0;
    
    while (std::getline(file, linea)) {
        lineaNum++;
        
        // Ignorar líneas vacías o comentarios (comienzan con #)
        if (linea.empty() || linea[0] == '#') {
            continue;
        }
        
        std::istringstream iss(linea);
        int origen, destino;
        
        if (iss >> origen >> destino) {
            aristas.emplace_back(origen, destino);
            maxNodo = std::max(maxNodo, std::max(origen, destino));
        }
    }
    
    file.close();
    
    // Construir estructura CSR
    construirCSR(aristas, maxNodo);
    
    auto endTime = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(endTime - startTime);
    
    std::cout << "[C++ Core] Carga completa. Nodos: " << numNodos 
              << " | Aristas: " << numAristas << std::endl;
    std::cout << "[C++ Core] Estructura CSR construida. Memoria estimada: " 
              << getMemoriaUsada() / (1024.0 * 1024.0) << " MB." << std::endl;
    std::cout << "[C++ Core] Tiempo de carga: " << duration.count() << " ms." << std::endl;
    
    return true;
}

std::vector<std::pair<int, int>> GrafoDisperso::BFS(int nodoInicio, int profundidadMaxima) {
    std::cout << "[C++ Core] Ejecutando BFS desde nodo " << nodoInicio 
              << " con profundidad maxima " << profundidadMaxima << "..." << std::endl;
    
    auto startTime = std::chrono::high_resolution_clock::now();
    
    std::vector<std::pair<int, int>> resultado; // (nodo, distancia)
    
    if (nodoInicio < 0 || nodoInicio >= numNodos) {
        std::cerr << "[C++ Core] Error: Nodo de inicio invalido." << std::endl;
        return resultado;
    }
    
    std::vector<bool> visitado(numNodos, false);
    std::queue<std::pair<int, int>> cola; // (nodo, nivel)
    
    cola.push({nodoInicio, 0});
    visitado[nodoInicio] = true;
    
    while (!cola.empty()) {
        auto [nodoActual, nivel] = cola.front();
        cola.pop();
        
        resultado.emplace_back(nodoActual, nivel);
        
        if (nivel >= profundidadMaxima) {
            continue;
        }
        
        // Obtener vecinos usando la estructura CSR
        int inicio = row_ptr[nodoActual];
        int fin = row_ptr[nodoActual + 1];
        
        for (int i = inicio; i < fin; i++) {
            int vecino = column_indices[i];
            if (!visitado[vecino]) {
                visitado[vecino] = true;
                cola.push({vecino, nivel + 1});
            }
        }
    }
    
    auto endTime = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(endTime - startTime);
    
    std::cout << "[C++ Core] BFS completado. Nodos encontrados: " << resultado.size() 
              << ". Tiempo ejecucion: " << duration.count() / 1000.0 << " ms." << std::endl;
    
    return resultado;
}

std::vector<int> GrafoDisperso::DFS(int nodoInicio) {
    std::cout << "[C++ Core] Ejecutando DFS desde nodo " << nodoInicio << "..." << std::endl;
    
    std::vector<int> resultado;
    
    if (nodoInicio < 0 || nodoInicio >= numNodos) {
        std::cerr << "[C++ Core] Error: Nodo de inicio invalido." << std::endl;
        return resultado;
    }
    
    std::vector<bool> visitado(numNodos, false);
    std::stack<int> pila;
    
    pila.push(nodoInicio);
    
    while (!pila.empty()) {
        int nodoActual = pila.top();
        pila.pop();
        
        if (visitado[nodoActual]) {
            continue;
        }
        
        visitado[nodoActual] = true;
        resultado.push_back(nodoActual);
        
        // Obtener vecinos en orden inverso para mantener orden natural
        int inicio = row_ptr[nodoActual];
        int fin = row_ptr[nodoActual + 1];
        
        for (int i = fin - 1; i >= inicio; i--) {
            int vecino = column_indices[i];
            if (!visitado[vecino]) {
                pila.push(vecino);
            }
        }
    }
    
    std::cout << "[C++ Core] DFS completado. Nodos visitados: " << resultado.size() << std::endl;
    
    return resultado;
}

int GrafoDisperso::obtenerGrado(int nodo) {
    if (nodo < 0 || nodo >= numNodos) {
        return -1;
    }
    return row_ptr[nodo + 1] - row_ptr[nodo];
}

int GrafoDisperso::obtenerGradoEntrada(int nodo) {
    if (nodo < 0 || nodo >= numNodos) {
        return -1;
    }
    return gradoEntrada[nodo];
}

std::vector<int> GrafoDisperso::getVecinos(int nodo) {
    std::vector<int> vecinos;
    
    if (nodo < 0 || nodo >= numNodos) {
        return vecinos;
    }
    
    int inicio = row_ptr[nodo];
    int fin = row_ptr[nodo + 1];
    
    vecinos.reserve(fin - inicio);
    for (int i = inicio; i < fin; i++) {
        vecinos.push_back(column_indices[i]);
    }
    
    return vecinos;
}

int GrafoDisperso::getNumNodos() {
    return numNodos;
}

int GrafoDisperso::getNumAristas() {
    return numAristas;
}

std::pair<int, int> GrafoDisperso::getNodoMayorGrado() {
    int maxGrado = 0;
    int nodoMax = -1;
    
    for (int i = 0; i < numNodos; i++) {
        int grado = obtenerGrado(i);
        if (grado > maxGrado) {
            maxGrado = grado;
            nodoMax = i;
        }
    }
    
    std::cout << "[C++ Core] Nodo con mayor grado de salida: " << nodoMax 
              << " (grado: " << maxGrado << ")" << std::endl;
    
    return {nodoMax, maxGrado};
}

size_t GrafoDisperso::getMemoriaUsada() {
    size_t memoria = 0;
    
    // Memoria de row_ptr
    memoria += row_ptr.capacity() * sizeof(int);
    
    // Memoria de column_indices
    memoria += column_indices.capacity() * sizeof(int);
    
    // Memoria de values
    memoria += values.capacity() * sizeof(int);
    
    // Memoria de gradoEntrada
    memoria += gradoEntrada.capacity() * sizeof(int);
    
    return memoria;
}

std::vector<std::pair<int, int>> GrafoDisperso::getAristasSubgrafo(int nodoInicio, int profundidadMaxima) {
    std::cout << "[C++ Core] Obteniendo aristas del subgrafo desde nodo " << nodoInicio << "..." << std::endl;
    
    std::vector<std::pair<int, int>> aristas;
    
    if (nodoInicio < 0 || nodoInicio >= numNodos) {
        return aristas;
    }
    
    // Primero hacemos BFS para encontrar los nodos en el subgrafo
    std::unordered_set<int> nodosEnSubgrafo;
    std::queue<std::pair<int, int>> cola;
    
    cola.push({nodoInicio, 0});
    nodosEnSubgrafo.insert(nodoInicio);
    
    while (!cola.empty()) {
        auto [nodoActual, nivel] = cola.front();
        cola.pop();
        
        if (nivel >= profundidadMaxima) {
            continue;
        }
        
        int inicio = row_ptr[nodoActual];
        int fin = row_ptr[nodoActual + 1];
        
        for (int i = inicio; i < fin; i++) {
            int vecino = column_indices[i];
            
            // Agregar arista
            aristas.emplace_back(nodoActual, vecino);
            
            if (nodosEnSubgrafo.find(vecino) == nodosEnSubgrafo.end()) {
                nodosEnSubgrafo.insert(vecino);
                cola.push({vecino, nivel + 1});
            }
        }
    }
    
    std::cout << "[C++ Core] Subgrafo obtenido. Nodos: " << nodosEnSubgrafo.size() 
              << " | Aristas: " << aristas.size() << std::endl;
    
    return aristas;
}

void GrafoDisperso::printDebugInfo() {
    std::cout << "\n=== Debug Info ===" << std::endl;
    std::cout << "Nodos: " << numNodos << std::endl;
    std::cout << "Aristas: " << numAristas << std::endl;
    std::cout << "Memoria: " << getMemoriaUsada() / (1024.0 * 1024.0) << " MB" << std::endl;
    
    std::cout << "\nrow_ptr (primeros 10): ";
    for (int i = 0; i < std::min(10, (int)row_ptr.size()); i++) {
        std::cout << row_ptr[i] << " ";
    }
    std::cout << std::endl;
    
    std::cout << "column_indices (primeros 20): ";
    for (int i = 0; i < std::min(20, (int)column_indices.size()); i++) {
        std::cout << column_indices[i] << " ";
    }
    std::cout << std::endl;
    std::cout << "==================\n" << std::endl;
}
