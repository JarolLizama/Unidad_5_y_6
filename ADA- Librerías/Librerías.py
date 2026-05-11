import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import os

# Importamos tus métodos externos
from lib_ordenamiento_externo import CLASES_EXTERNAS, METODOS_EXTERNOS, MODOS_IO

class AppOrdenamiento:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualizador de Ordenamiento Externo - ADA 1, 2 y 3")
        self.root.geometry("1000x700")
        self.root.configure(bg="#1e1e2e")

        self.ejecutando = False
        self.pausado = False
        self.instancia_algoritmo = None

        self._crear_interfaz()

    def _crear_interfaz(self):
        # --- PANEL LATERAL DE CONTROLES ---
        sidebar = tk.Frame(self.root, bg="#252539", width=250)
        sidebar.pack(side="left", fill="y", padx=5, pady=5)

        tk.Label(sidebar, text="CONFIGURACIÓN", fg="white", bg="#252539", font=("Arial", 12, "bold")).pack(pady=10)

        # Selección de Algoritmo
        tk.Label(sidebar, text="Algoritmo:", fg="#a78bfa", bg="#252539").pack()
        self.combo_algo = ttk.Combobox(sidebar, values=METODOS_EXTERNOS, state="readonly")
        self.combo_algo.current(0)
        self.combo_algo.pack(pady=5, padx=10)

        # Selección de Modo (TXT/Excel)
        tk.Label(sidebar, text="Modo I/O:", fg="#a78bfa", bg="#252539").pack()
        self.combo_modo = ttk.Combobox(sidebar, values=MODOS_IO, state="readonly")
        self.combo_modo.current(0)
        self.combo_modo.pack(pady=5, padx=10)

        # Velocidad
        tk.Label(sidebar, text="Retardo (seg):", fg="#a78bfa", bg="#252539").pack()
        self.slider_speed = tk.Scale(sidebar, from_=0.0, to=2.0, resolution=0.1, orient="horizontal", bg="#252539", fg="white")
        self.slider_speed.set(0.3)
        self.slider_speed.pack(fill="x", padx=20)

        # Botones
        self.btn_inicio = tk.Button(sidebar, text="INICIAR", command=self.iniciar_hilo, bg="#22c55e", fg="white", font=("bold"))
        self.btn_inicio.pack(fill="x", padx=20, pady=20)

        self.btn_pausa = tk.Button(sidebar, text="PAUSAR", command=self.toggle_pausa, bg="#f59e0b", fg="white")
        self.btn_pausa.pack(fill="x", padx=20, pady=5)

        # --- ÁREA PRINCIPAL (Visualización) ---
        main_area = tk.Frame(self.root, bg="#1e1e2e")
        main_area.pack(side="right", fill="both", expand=True)

        # Canvas para las barras (Representación de la RAM/Datos actuales)
        tk.Label(main_area, text="Vista de Datos (Proceso Interno)", fg="white", bg="#1e1e2e").pack()
        self.canvas = tk.Canvas(main_area, bg="#0f172a", height=200)
        self.canvas.pack(fill="x", padx=10, pady=5)

        # Monitor de Cintas (Archivos Externos)
        tk.Label(main_area, text="Simulación de Cintas (Almacenamiento)", fg="white", bg="#1e1e2e").pack()
        self.cintas_frame = tk.Frame(main_area, bg="#1e1e2e")
        self.cintas_frame.pack(fill="x", padx=10)
        
        self.txt_cintas = {}
        for c in ["A", "B", "C", "D"]:
            f = tk.Frame(self.cintas_frame, bg="#252539", bd=1, relief="sunken")
            f.pack(side="left", fill="both", expand=True, padx=2)
            tk.Label(f, text=f"Cinta {c}", bg="#252539", fg="#00d4ff").pack()
            self.txt_cintas[c] = tk.Label(f, text="-", fg="white", bg="#252539", font=("Courier", 8), wraplength=150)
            self.txt_cintas[c].pack(pady=5)

        # Log de Consola
        self.log_area = scrolledtext.ScrolledText(main_area, bg="#000000", fg="#22c55e", font=("Consolas", 9), height=15)
        self.log_area.pack(fill="both", expand=True, padx=10, pady=10)

    # --- CALLBACKS PARA EL ALGORITMO ---

    def callback_log(self, msg, color="#22c55e"):
        self.log_area.insert(tk.END, msg + "\n")
        self.log_area.see(tk.END)

    def callback_barras(self, arr, resaltados):
        self.canvas.delete("all")
        if not arr: return
        c_width = self.canvas.winfo_width()
        c_height = self.canvas.winfo_height()
        bar_w = c_width / len(arr)
        max_val = max(arr)

        for i, val in enumerate(arr):
            x0 = i * bar_w
            y0 = c_height - (val / max_val * (c_height - 20))
            x1 = (i + 1) * bar_w
            y1 = c_height
            color = resaltados.get(i, "#4f46e5")
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="#1e1e2e")
        self.root.update_idletasks()

    def callback_cintas(self, diccionario_cintas):
        for nombre, contenido in diccionario_cintas.items():
            letra = nombre.split("_")[-1].upper() # De 'cinta_A' saca 'A'
            if letra in self.txt_cintas:
                texto = ", ".join(map(str, contenido[:20])) # Solo mostramos los primeros 20
                if len(contenido) > 20: texto += "..."
                self.txt_cintas[letra].config(text=texto)

    def check_pausa(self):
        while self.pausado:
            time.sleep(0.1)

    def finalizar(self, resultado, path):
        self.ejecutando = False
        self.btn_inicio.config(state="normal", text="REINICIAR")
        messagebox.showinfo("Proceso Finalizado", f"Datos ordenados guardados en:\n{path}")

    # --- CONTROL DE HILOS ---

    def toggle_pausa(self):
        self.pausado = not self.pausado
        self.btn_pausa.config(text="REANUDAR" if self.pausado else "PAUSAR")

    def iniciar_hilo(self):
        if self.ejecutando: return
        
        algo_nombre = self.combo_algo.get()
        modo_io = self.combo_modo.get()
        delay = self.slider_speed.get()
        
        self.log_area.delete("1.0", tk.END)
        self.ejecutando = True
        self.btn_inicio.config(state="disabled")

        # Instanciar el algoritmo desde tu librería
        ClaseAlgo = CLASES_EXTERNAS[algo_nombre]
        self.instancia_algoritmo = ClaseAlgo(
            log_cb=self.callback_log,
            barra_cb=self.callback_barras,
            cinta_cb=self.callback_cintas,
            fin_cb=self.finalizar,
            pausa_fn=self.check_pausa,
            modo_io=modo_io
        )

        hilo = threading.Thread(target=self.instancia_algoritmo.ejecutar, args=(20, delay), daemon=True)
        hilo.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = AppOrdenamiento(root)
    root.mainloop()