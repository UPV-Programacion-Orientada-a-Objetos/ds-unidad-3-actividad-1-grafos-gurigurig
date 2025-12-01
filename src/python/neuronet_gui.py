"""
neuronet_gui.py
Interfaz Gráfica de Usuario para NeuroNet

Esta aplicación proporciona una GUI basada en Tkinter para interactuar
con el motor de grafos C++ de NeuroNet. Permite cargar datasets,
ejecutar algoritmos y visualizar resultados.

Autor: NeuroNet Team
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
import time

# Añadir directorio raíz al path para encontrar el módulo compilado
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT_DIR)

# Intentar importar el módulo compilado
try:
    import neuronet_core
    CORE_DISPONIBLE = True
except ImportError:
    CORE_DISPONIBLE = False
    print("[GUI] Advertencia: El módulo neuronet_core no está compilado.")
    print("[GUI] Ejecute 'python setup.py build_ext --inplace' para compilar.")

# Importar librerías de visualización
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib
    matplotlib.use('TkAgg')
    MATPLOTLIB_DISPONIBLE = True
except ImportError:
    MATPLOTLIB_DISPONIBLE = False

try:
    import networkx as nx
    NETWORKX_DISPONIBLE = True
except ImportError:
    NETWORKX_DISPONIBLE = False


class ConsoleRedirector:
    """Redirige la salida estándar a un widget de texto."""
    
    def __init__(self, text_widget):
        self.text_widget = text_widget
        
    def write(self, string):
        self.text_widget.configure(state='normal')
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)
        self.text_widget.configure(state='disabled')
        
    def flush(self):
        pass


class NeuroNetGUI:
    """
    Clase principal de la interfaz gráfica de NeuroNet.
    
    Attributes:
        root: Ventana principal de Tkinter
        grafo: Instancia del wrapper PyGrafoDisperso
    """
    
    def __init__(self, root):
        """
        Inicializa la interfaz gráfica.
        
        Args:
            root: Ventana raíz de Tkinter
        """
        self.root = root
        self.root.title("NeuroNet - Análisis de Redes Masivas")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Inicializar el grafo
        self.grafo = None
        if CORE_DISPONIBLE:
            self.grafo = neuronet_core.PyGrafoDisperso()
        
        # Variables de estado
        self.archivo_cargado = tk.StringVar(value="Ninguno")
        self.num_nodos = tk.StringVar(value="0")
        self.num_aristas = tk.StringVar(value="0")
        self.memoria_usada = tk.StringVar(value="0 MB")
        self.tiempo_carga = tk.StringVar(value="0.00 s")
        self.nodo_mayor_grado = tk.StringVar(value="-")
        
        # Configurar estilos
        self._configurar_estilos()
        
        # Crear la interfaz
        self._crear_interfaz()
        
        # Redirigir salida de consola
        self._configurar_consola()
        
        # Log inicial
        self._log("="*50)
        self._log("NeuroNet - Sistema de Análisis de Grafos Masivos")
        self._log("="*50)
        
        if not CORE_DISPONIBLE:
            self._log("[ADVERTENCIA] El módulo neuronet_core no está disponible.")
            self._log("[ADVERTENCIA] Ejecute: python setup.py build_ext --inplace")
        else:
            self._log("[INFO] Motor C++ inicializado correctamente.")
        
        if not NETWORKX_DISPONIBLE:
            self._log("[ADVERTENCIA] NetworkX no está instalado. Visualización limitada.")
        
        if not MATPLOTLIB_DISPONIBLE:
            self._log("[ADVERTENCIA] Matplotlib no está instalado. Sin gráficos.")
    
    def _configurar_estilos(self):
        """Configura los estilos visuales de la aplicación."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar colores
        style.configure('Title.TLabel', font=('Helvetica', 16, 'bold'))
        style.configure('Header.TLabel', font=('Helvetica', 12, 'bold'))
        style.configure('Info.TLabel', font=('Helvetica', 10))
        style.configure('Action.TButton', font=('Helvetica', 10, 'bold'))
    
    def _crear_interfaz(self):
        """Crea todos los widgets de la interfaz."""
        # Frame principal con grid
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # === Panel de control (izquierda) ===
        control_frame = ttk.LabelFrame(main_frame, text="Panel de Control", padding="10")
        control_frame.grid(row=0, column=0, rowspan=3, sticky="nsew", padx=(0, 10))
        
        # Sección: Carga de datos
        ttk.Label(control_frame, text="Carga de Datos", style='Header.TLabel').pack(pady=(0, 10))
        
        ttk.Button(
            control_frame, 
            text="📂 Cargar Dataset", 
            command=self._cargar_archivo,
            style='Action.TButton',
            width=25
        ).pack(pady=5)
        
        ttk.Separator(control_frame, orient='horizontal').pack(fill='x', pady=15)
        
        # Sección: Análisis
        ttk.Label(control_frame, text="Análisis", style='Header.TLabel').pack(pady=(0, 10))
        
        ttk.Button(
            control_frame,
            text="🔍 Identificar Nodo Crítico",
            command=self._identificar_nodo_critico,
            width=25
        ).pack(pady=5)
        
        ttk.Separator(control_frame, orient='horizontal').pack(fill='x', pady=15)
        
        # Sección: Búsqueda BFS
        ttk.Label(control_frame, text="Búsqueda BFS", style='Header.TLabel').pack(pady=(0, 10))
        
        params_frame = ttk.Frame(control_frame)
        params_frame.pack(pady=5)
        
        ttk.Label(params_frame, text="Nodo inicio:").grid(row=0, column=0, padx=5, pady=2)
        self.entry_nodo_inicio = ttk.Entry(params_frame, width=10)
        self.entry_nodo_inicio.grid(row=0, column=1, padx=5, pady=2)
        self.entry_nodo_inicio.insert(0, "0")
        
        ttk.Label(params_frame, text="Profundidad:").grid(row=1, column=0, padx=5, pady=2)
        self.entry_profundidad = ttk.Entry(params_frame, width=10)
        self.entry_profundidad.grid(row=1, column=1, padx=5, pady=2)
        self.entry_profundidad.insert(0, "2")
        
        ttk.Button(
            control_frame,
            text="▶ Ejecutar BFS",
            command=self._ejecutar_bfs,
            width=25
        ).pack(pady=10)
        
        ttk.Button(
            control_frame,
            text="📊 Visualizar Subgrafo",
            command=self._visualizar_subgrafo,
            width=25
        ).pack(pady=5)
        
        ttk.Separator(control_frame, orient='horizontal').pack(fill='x', pady=15)
        
        # Sección: Búsqueda DFS
        ttk.Label(control_frame, text="Búsqueda DFS", style='Header.TLabel').pack(pady=(0, 10))
        
        dfs_frame = ttk.Frame(control_frame)
        dfs_frame.pack(pady=5)
        
        ttk.Label(dfs_frame, text="Nodo inicio:").grid(row=0, column=0, padx=5, pady=2)
        self.entry_nodo_dfs = ttk.Entry(dfs_frame, width=10)
        self.entry_nodo_dfs.grid(row=0, column=1, padx=5, pady=2)
        self.entry_nodo_dfs.insert(0, "0")
        
        ttk.Button(
            control_frame,
            text="▶ Ejecutar DFS",
            command=self._ejecutar_dfs,
            width=25
        ).pack(pady=10)
        
        # === Panel de estadísticas (arriba derecha) ===
        stats_frame = ttk.LabelFrame(main_frame, text="Estadísticas del Grafo", padding="10")
        stats_frame.grid(row=0, column=1, sticky="nsew", pady=(0, 10))
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill='x')
        
        labels = [
            ("Archivo:", self.archivo_cargado),
            ("Nodos:", self.num_nodos),
            ("Aristas:", self.num_aristas),
            ("Memoria:", self.memoria_usada),
            ("Tiempo carga:", self.tiempo_carga),
            ("Nodo más crítico:", self.nodo_mayor_grado),
        ]
        
        for i, (label, var) in enumerate(labels):
            ttk.Label(stats_grid, text=label, style='Info.TLabel').grid(
                row=i//3, column=(i%3)*2, sticky='e', padx=5, pady=2
            )
            ttk.Label(stats_grid, textvariable=var, font=('Helvetica', 10, 'bold')).grid(
                row=i//3, column=(i%3)*2+1, sticky='w', padx=5, pady=2
            )
        
        # === Panel de visualización (centro derecha) ===
        self.viz_frame = ttk.LabelFrame(main_frame, text="Visualización del Subgrafo", padding="10")
        self.viz_frame.grid(row=1, column=1, sticky="nsew", pady=(0, 10))
        main_frame.rowconfigure(1, weight=1)
        
        # Canvas para matplotlib
        if MATPLOTLIB_DISPONIBLE:
            self.fig, self.ax = plt.subplots(figsize=(6, 4))
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.viz_frame)
            self.canvas.get_tk_widget().pack(fill='both', expand=True)
            self.ax.set_title("Ejecute un BFS para visualizar el subgrafo")
            self.ax.axis('off')
            self.canvas.draw()
        else:
            ttk.Label(
                self.viz_frame, 
                text="Matplotlib no disponible\nInstale: pip install matplotlib",
                font=('Helvetica', 12)
            ).pack(expand=True)
        
        # === Consola (abajo) ===
        console_frame = ttk.LabelFrame(main_frame, text="Consola de Salida", padding="5")
        console_frame.grid(row=2, column=1, sticky="nsew")
        
        self.console = scrolledtext.ScrolledText(
            console_frame, 
            height=10, 
            state='disabled',
            font=('Consolas', 9),
            bg='#1e1e1e',
            fg='#00ff00'
        )
        self.console.pack(fill='both', expand=True)
    
    def _configurar_consola(self):
        """Configura la redirección de la consola."""
        # Redirigir stdout
        sys.stdout = ConsoleRedirector(self.console)
    
    def _log(self, mensaje):
        """Escribe un mensaje en la consola."""
        self.console.configure(state='normal')
        self.console.insert(tk.END, mensaje + "\n")
        self.console.see(tk.END)
        self.console.configure(state='disabled')
        self.root.update_idletasks()
    
    def _cargar_archivo(self):
        """Abre un diálogo para seleccionar y cargar un dataset."""
        if not CORE_DISPONIBLE:
            messagebox.showerror("Error", "El módulo neuronet_core no está disponible.")
            return
        
        archivo = filedialog.askopenfilename(
            title="Seleccionar Dataset",
            filetypes=[
                ("Archivos de texto", "*.txt"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if archivo:
            self._log(f"\n{'='*50}")
            self._log(f"Cargando archivo: {archivo}")
            self._log(f"{'='*50}")
            
            # Ejecutar en hilo separado para no bloquear la GUI
            def cargar():
                try:
                    exito = self.grafo.cargar_datos(archivo)
                    
                    if exito:
                        # Actualizar estadísticas
                        self.archivo_cargado.set(os.path.basename(archivo))
                        self.num_nodos.set(f"{self.grafo.get_num_nodos():,}")
                        self.num_aristas.set(f"{self.grafo.get_num_aristas():,}")
                        self.memoria_usada.set(f"{self.grafo.get_memoria_usada_mb():.2f} MB")
                        self.tiempo_carga.set(f"{self.grafo.tiempo_carga:.3f} s")
                        
                        self._log("\n[GUI] Archivo cargado exitosamente.")
                    else:
                        messagebox.showerror("Error", "No se pudo cargar el archivo.")
                        
                except Exception as e:
                    self._log(f"[ERROR] {str(e)}")
                    messagebox.showerror("Error", f"Error al cargar: {str(e)}")
            
            threading.Thread(target=cargar, daemon=True).start()
    
    def _identificar_nodo_critico(self):
        """Identifica el nodo con mayor grado en el grafo."""
        if not self._verificar_grafo_cargado():
            return
        
        self._log("\n" + "="*50)
        self._log("Identificando nodo más crítico (mayor grado)...")
        self._log("="*50)
        
        try:
            nodo, grado = self.grafo.get_nodo_mayor_grado()
            self.nodo_mayor_grado.set(f"Nodo {nodo} (grado: {grado})")
            
            self._log(f"\n[RESULTADO] Nodo más crítico: {nodo}")
            self._log(f"[RESULTADO] Grado de salida: {grado}")
            
        except Exception as e:
            self._log(f"[ERROR] {str(e)}")
    
    def _ejecutar_bfs(self):
        """Ejecuta una búsqueda BFS desde el nodo especificado."""
        if not self._verificar_grafo_cargado():
            return
        
        try:
            nodo_inicio = int(self.entry_nodo_inicio.get())
            profundidad = int(self.entry_profundidad.get())
        except ValueError:
            messagebox.showerror("Error", "Ingrese valores numéricos válidos.")
            return
        
        self._log("\n" + "="*50)
        self._log(f"Ejecutando BFS desde nodo {nodo_inicio} con profundidad {profundidad}")
        self._log("="*50)
        
        try:
            resultado = self.grafo.bfs(nodo_inicio, profundidad)
            
            self._log(f"\n[RESULTADO] Nodos visitados: {len(resultado)}")
            
            # Mostrar primeros nodos
            if len(resultado) <= 20:
                for nodo, dist in resultado:
                    self._log(f"  Nodo {nodo} - Distancia: {dist}")
            else:
                for nodo, dist in resultado[:10]:
                    self._log(f"  Nodo {nodo} - Distancia: {dist}")
                self._log(f"  ... y {len(resultado) - 10} nodos más")
                
        except Exception as e:
            self._log(f"[ERROR] {str(e)}")
    
    def _ejecutar_dfs(self):
        """Ejecuta una búsqueda DFS desde el nodo especificado."""
        if not self._verificar_grafo_cargado():
            return
        
        try:
            nodo_inicio = int(self.entry_nodo_dfs.get())
        except ValueError:
            messagebox.showerror("Error", "Ingrese un valor numérico válido.")
            return
        
        self._log("\n" + "="*50)
        self._log(f"Ejecutando DFS desde nodo {nodo_inicio}")
        self._log("="*50)
        
        try:
            resultado = self.grafo.dfs(nodo_inicio)
            
            self._log(f"\n[RESULTADO] Nodos visitados: {len(resultado)}")
            
            # Mostrar primeros nodos
            if len(resultado) <= 20:
                self._log(f"  Orden DFS: {resultado}")
            else:
                self._log(f"  Primeros 20 nodos: {resultado[:20]}")
                self._log(f"  ... y {len(resultado) - 20} nodos más")
                
        except Exception as e:
            self._log(f"[ERROR] {str(e)}")
    
    def _visualizar_subgrafo(self):
        """Visualiza el subgrafo resultante de un BFS."""
        if not self._verificar_grafo_cargado():
            return
        
        if not MATPLOTLIB_DISPONIBLE or not NETWORKX_DISPONIBLE:
            messagebox.showerror(
                "Error", 
                "Se requiere matplotlib y networkx para visualización."
            )
            return
        
        try:
            nodo_inicio = int(self.entry_nodo_inicio.get())
            profundidad = int(self.entry_profundidad.get())
        except ValueError:
            messagebox.showerror("Error", "Ingrese valores numéricos válidos.")
            return
        
        self._log("\n" + "="*50)
        self._log(f"Generando visualización del subgrafo...")
        self._log("="*50)
        
        try:
            # Obtener aristas del subgrafo
            aristas = self.grafo.get_aristas_subgrafo(nodo_inicio, profundidad)
            
            if not aristas:
                self._log("[ADVERTENCIA] No se encontraron aristas para visualizar.")
                return
            
            # Limitar número de aristas para visualización
            max_aristas = 500
            if len(aristas) > max_aristas:
                self._log(f"[INFO] Limitando visualización a {max_aristas} aristas de {len(aristas)}")
                aristas = aristas[:max_aristas]
            
            # Crear grafo de NetworkX (SOLO para dibujar, no para calcular)
            G = nx.DiGraph()
            G.add_edges_from(aristas)
            
            # Limpiar el canvas
            self.ax.clear()
            
            # Configurar colores por nivel
            bfs_result = self.grafo.bfs(nodo_inicio, profundidad)
            nivel_nodo = {nodo: nivel for nodo, nivel in bfs_result if nodo in G.nodes()}
            
            # Colores por nivel
            colores = []
            for nodo in G.nodes():
                if nodo == nodo_inicio:
                    colores.append('#ff0000')  # Rojo para el nodo inicial
                elif nodo in nivel_nodo:
                    nivel = nivel_nodo[nodo]
                    if nivel == 1:
                        colores.append('#ff9900')  # Naranja para nivel 1
                    else:
                        colores.append('#3399ff')  # Azul para otros niveles
                else:
                    colores.append('#cccccc')  # Gris para nodos sin nivel
            
            # Dibujar el grafo
            pos = nx.spring_layout(G, k=2, iterations=50)
            
            nx.draw_networkx_nodes(G, pos, ax=self.ax, node_color=colores, 
                                   node_size=300, alpha=0.9)
            nx.draw_networkx_edges(G, pos, ax=self.ax, edge_color='#666666',
                                   arrows=True, arrowsize=10, alpha=0.5)
            nx.draw_networkx_labels(G, pos, ax=self.ax, font_size=8)
            
            self.ax.set_title(f"Subgrafo desde nodo {nodo_inicio} (profundidad {profundidad})\n"
                              f"Nodos: {G.number_of_nodes()} | Aristas: {G.number_of_edges()}")
            self.ax.axis('off')
            
            # Añadir leyenda
            from matplotlib.lines import Line2D
            legend_elements = [
                Line2D([0], [0], marker='o', color='w', markerfacecolor='#ff0000', 
                       markersize=10, label='Nodo inicio'),
                Line2D([0], [0], marker='o', color='w', markerfacecolor='#ff9900', 
                       markersize=10, label='Nivel 1'),
                Line2D([0], [0], marker='o', color='w', markerfacecolor='#3399ff', 
                       markersize=10, label='Nivel 2+'),
            ]
            self.ax.legend(handles=legend_elements, loc='upper left')
            
            self.canvas.draw()
            
            self._log(f"[GUI] Visualización generada: {G.number_of_nodes()} nodos, "
                      f"{G.number_of_edges()} aristas")
            
        except Exception as e:
            self._log(f"[ERROR] Error al visualizar: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _verificar_grafo_cargado(self) -> bool:
        """Verifica si hay un grafo cargado."""
        if not CORE_DISPONIBLE:
            messagebox.showerror("Error", "El módulo neuronet_core no está disponible.")
            return False
        
        if self.grafo.get_num_nodos() == 0:
            messagebox.showwarning("Advertencia", "Primero debe cargar un dataset.")
            return False
        
        return True


def main():
    """Punto de entrada principal de la aplicación."""
    root = tk.Tk()
    app = NeuroNetGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
