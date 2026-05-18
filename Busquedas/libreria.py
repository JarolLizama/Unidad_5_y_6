"""
visualizador_busqueda.py
------------------------
Programa visual que muestra el funcionamiento
del algoritmo de búsqueda secuencial usando Tkinter.
Hace uso de todas las funciones de la librería.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import random
import libreria as bs  # <-- Asegúrate de que el nombre del archivo coincida

# ── Colores ──────────────────────────────────────────────
BG_MAIN       = "#1e1e2e"
BG_PANEL      = "#2a2a3e"
BG_CARD       = "#313149"
COLOR_IDLE    = "#4a4a6a"
COLOR_CURRENT = "#f5a623"   # amarillo  → comparando
COLOR_FOUND   = "#4caf50"   # verde     → encontrado
COLOR_MISSED  = "#e74c3c"   # rojo      → no era éste
COLOR_TEXT    = "#e0e0f0"
COLOR_ACCENT  = "#7c6af5"
COLOR_BTN     = "#5a4fcf"
COLOR_BTN_HOV = "#7c6af5"
FONT_TITLE    = ("Segoe UI", 18, "bold")
FONT_LABEL    = ("Segoe UI", 11)
FONT_SMALL    = ("Segoe UI", 9)
FONT_CELL     = ("Courier New", 15, "bold")
FONT_IDX      = ("Segoe UI", 8)

DELAY_MS = 700


class VisualizadorBusqueda:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualizador — Búsqueda Secuencial")
        self.root.configure(bg=BG_MAIN)
        self.root.resizable(True, True)
        self.root.minsize(750, 600)

        self.lista        = []
        self.objetivo     = None
        self.paso_actual  = 0
        self.buscando     = False
        self.after_id     = None

        self._build_ui()

    # ── Construcción de la interfaz ───────────────────────

    def _build_ui(self):
        # ── Título ──
        tk.Label(self.root, text="🔍  Búsqueda Secuencial",
                 font=FONT_TITLE, bg=BG_MAIN, fg=COLOR_ACCENT).pack(pady=(18, 4))
        
        # ── Panel de entrada ──
        entrada = tk.Frame(self.root, bg=BG_PANEL, padx=16, pady=12)
        entrada.pack(fill="x", padx=24, pady=(0, 10))

        tk.Label(entrada, text="Lista (separada por coma):", font=FONT_LABEL, bg=BG_PANEL, fg=COLOR_TEXT).grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.entry_lista = tk.Entry(entrada, font=FONT_LABEL, width=38, bg=BG_CARD, fg=COLOR_TEXT, relief="flat", bd=4)
        self.entry_lista.insert(0, "15, 19, 42, 8, 19, 5, 19, 11, 33, 7") # Puse varios '19' para probar buscar_todos
        self.entry_lista.grid(row=0, column=1, padx=(0, 12))

        tk.Label(entrada, text="Valor a buscar:", font=FONT_LABEL, bg=BG_PANEL, fg=COLOR_TEXT).grid(row=1, column=0, sticky="w", pady=(8, 0), padx=(0, 10))
        self.entry_obj = tk.Entry(entrada, font=FONT_LABEL, width=10, bg=BG_CARD, fg=COLOR_TEXT, relief="flat", bd=4)
        self.entry_obj.insert(0, "19")
        self.entry_obj.grid(row=1, column=1, sticky="w", pady=(8, 0))

        tk.Label(entrada, text="Velocidad:", font=FONT_SMALL, bg=BG_PANEL, fg="#888aaa").grid(row=1, column=2, sticky="e", padx=(20, 6), pady=(8, 0))
        self.vel_var = tk.IntVar(value=DELAY_MS)
        ttk.Scale(entrada, from_=200, to=1500, orient="horizontal", variable=self.vel_var, length=120).grid(row=1, column=3, pady=(8, 0))

        tk.Label(entrada, text="Generar aleatorios (cant.):", font=FONT_LABEL, bg=BG_PANEL, fg=COLOR_TEXT).grid(row=2, column=0, sticky="w", pady=(8, 0), padx=(0, 10))
        gen_frame = tk.Frame(entrada, bg=BG_PANEL)
        gen_frame.grid(row=2, column=1, sticky="w", pady=(8, 0))
        self.entry_cantidad = tk.Entry(gen_frame, font=FONT_LABEL, width=6, bg=BG_CARD, fg=COLOR_TEXT, relief="flat", bd=4)
        self.entry_cantidad.insert(0, "12")
        self.entry_cantidad.pack(side="left")
        tk.Button(gen_frame, text="🎲 Generar", command=self._generar_aleatorios, font=("Segoe UI", 9, "bold"), bg="#0288d1", fg="white", relief="flat", padx=10, pady=2, cursor="hand2").pack(side="left", padx=(10, 0))

        # ── Botones Principales (Animación) ──
        tk.Label(self.root, text="Animación Paso a Paso (usa buscar() y buscar_rango()):", font=FONT_SMALL, bg=BG_MAIN, fg="#888aaa").pack()
        btn_frame = tk.Frame(self.root, bg=BG_MAIN)
        btn_frame.pack(pady=4)

        self.btn_iniciar  = self._btn(btn_frame, "▶ Iniciar Animación", self._iniciar, COLOR_BTN)
        self.btn_paso     = self._btn(btn_frame, "⏭ Paso manual", self._paso_manual, "#2e7d32")
        self.btn_reinicio = self._btn(btn_frame, "↺ Limpiar", self._reiniciar, "#6d4c41")

        self.btn_iniciar.pack(side="left", padx=6)
        self.btn_paso.pack(side="left", padx=6)
        self.btn_reinicio.pack(side="left", padx=6)

        # ── Botones Secundarios (Otras Funciones de la librería) ──
        tk.Label(self.root, text="Herramientas Extra de la Librería (Ejecución Instantánea):", font=FONT_SMALL, bg=BG_MAIN, fg="#888aaa").pack(pady=(10, 0))
        lib_frame = tk.Frame(self.root, bg=BG_MAIN)
        lib_frame.pack(pady=4)

        self._btn(lib_frame, "Buscar Todos", self._ejecutar_buscar_todos, "#00838f").pack(side="left", padx=4)
        self._btn(lib_frame, "¿Contiene?", self._ejecutar_contiene, "#00838f").pack(side="left", padx=4)
        self._btn(lib_frame, "Buscar Condición (> Objetivo)", self._ejecutar_condicion, "#00838f").pack(side="left", padx=4)

        # ── Área de celdas ──
        self.canvas_frame = tk.Frame(self.root, bg=BG_MAIN)
        self.canvas_frame.pack(fill="both", expand=True, padx=24, pady=8)
        self.canvas = tk.Canvas(self.canvas_frame, bg=BG_MAIN, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # ── Panel de estado ──
        estado_frame = tk.Frame(self.root, bg=BG_PANEL, padx=14, pady=8)
        estado_frame.pack(fill="x", padx=24, pady=(0, 6))
        self.lbl_estado = tk.Label(estado_frame, text="Ingresa datos y elige una acción.", font=FONT_LABEL, bg=BG_PANEL, fg=COLOR_TEXT, anchor="w", justify="left")
        self.lbl_estado.pack(fill="x")

        # ── Contador ──
        self.lbl_comparaciones = tk.Label(self.root, text="", font=FONT_SMALL, bg=BG_MAIN, fg="#888aaa")
        self.lbl_comparaciones.pack(pady=(0, 10))

        self.root.bind("<Configure>", lambda e: self._redibujar_celdas())

    def _btn(self, parent, texto, cmd, color):
        return tk.Button(parent, text=texto, command=cmd, font=("Segoe UI", 10, "bold"), bg=color, fg="white", relief="flat", padx=12, pady=4, cursor="hand2")

    # ── Ejecución de Funciones Faltantes de la Librería ─────────────────

    def _preparar_ejecucion_rapida(self):
        """Detiene cualquier animación y prepara el arreglo para mostrar un resultado instantáneo."""
        if not self._parsear_entrada(): return False
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.buscando = False
        self.colores = [COLOR_IDLE] * len(self.lista)
        self.comparaciones = 0
        self._actualizar_contador()
        return True

    def _ejecutar_buscar_todos(self):
        """Usa bs.buscar_todos() de la librería."""
        if not self._preparar_ejecucion_rapida(): return
        
        indices = bs.buscar_todos(self.lista, self.objetivo)
        if indices:
            for idx in indices:
                self.colores[idx] = COLOR_FOUND
            self._actualizar_estado(f"🔎 buscar_todos(): El {self.objetivo} aparece en los índices {indices}")
        else:
            self._actualizar_estado(f"🔎 buscar_todos(): El {self.objetivo} no se encontró en ninguna parte.")
        self._redibujar_celdas()

    def _ejecutar_contiene(self):
        """Usa bs.contiene() de la librería."""
        if not self._preparar_ejecucion_rapida(): return
        
        existe = bs.contiene(self.lista, self.objetivo)
        self._redibujar_celdas() # Las celdas se quedan normales
        if existe:
            self._actualizar_estado(f"❓ contiene(): ¡Sí! El número {self.objetivo} existe en la lista.")
        else:
            self._actualizar_estado(f"❓ contiene(): No, el número {self.objetivo} no existe.")

    def _ejecutar_condicion(self):
        """Usa bs.buscar_con_condicion() de la librería con una función lambda."""
        if not self._preparar_ejecucion_rapida(): return
        
        # Condición: El elemento debe ser estrictamente mayor que nuestro objetivo
        condicion = lambda x: x > self.objetivo
        
        idx, valor = bs.buscar_con_condicion(self.lista, condicion)
        if idx != -1:
            self.colores[idx] = COLOR_FOUND
            self._actualizar_estado(f"⚙️ buscar_con_condicion(): El primer número MAYOR a {self.objetivo} es {valor} (Índice {idx})")
        else:
            self._actualizar_estado(f"⚙️ buscar_con_condicion(): No existe ningún número mayor a {self.objetivo}.")
        self._redibujar_celdas()

    # ── Lógica Original ──────────────────────────────────

    def _generar_aleatorios(self):
        try:
            n = int(self.entry_cantidad.get().strip())
            if n <= 0 or n > 40:
                messagebox.showwarning("Inválido", "Ingresa un número entre 1 y 40.")
                return
        except ValueError:
            return
        nuevos_datos = [random.randint(1, 99) for _ in range(n)]
        # Forzamos repeticiones a veces para que buscar_todos tenga sentido
        if random.random() > 0.5 and n > 3: 
            repetido = random.choice(nuevos_datos)
            nuevos_datos[random.randint(0, n-1)] = repetido
            nuevos_datos[random.randint(0, n-1)] = repetido

        self.entry_lista.delete(0, tk.END)
        self.entry_lista.insert(0, ", ".join(map(str, nuevos_datos)))
        self.entry_obj.delete(0, tk.END)
        self.entry_obj.insert(0, str(random.choice(nuevos_datos)))
        self._reiniciar()

    def _parsear_entrada(self):
        raw = self.entry_lista.get().strip()
        if not raw: return False
        try:
            self.lista = [int(x.strip()) for x in raw.split(",")]
        except ValueError:
            return False
        obj_raw = self.entry_obj.get().strip()
        if not obj_raw: return False
        try:
            self.objetivo = int(obj_raw)
        except ValueError:
            return False
        return True

    def _iniciar(self):
        if self.buscando: return
        if not self._parsear_entrada(): return
        self.paso_actual = 0
        self.comparaciones = 0
        self.buscando = True
        self.colores = [COLOR_IDLE] * len(self.lista)
        self.btn_paso.config(state="disabled")
        self._redibujar_celdas()
        self._actualizar_estado(f"Buscando {self.objetivo} en la lista…")
        self._animar_paso()

    def _animar_paso(self):
        if not self.buscando: return
        n = len(self.lista)
        if self.paso_actual >= n:
            resultado = bs.buscar(self.lista, self.objetivo)
            self._finalizar(resultado)
            return

        idx = bs.buscar_rango(self.lista, self.objetivo, self.paso_actual, self.paso_actual + 1)
        self.comparaciones += 1

        if idx != -1:
            self.colores[self.paso_actual] = COLOR_CURRENT
            self._redibujar_celdas()
            self._actualizar_estado(f"Índice {self.paso_actual}: {self.lista[self.paso_actual]} == {self.objetivo} ✔ Coincide")
            self.after_id = self.root.after(self.vel_var.get(), lambda: self._finalizar(self.paso_actual))
        else:
            self.colores[self.paso_actual] = COLOR_CURRENT
            self._redibujar_celdas()
            self._actualizar_estado(f"Índice {self.paso_actual}: {self.lista[self.paso_actual]} ≠ {self.objetivo} ✘ No coincide")
            def continuar():
                self.colores[self.paso_actual] = COLOR_MISSED
                self._redibujar_celdas()
                self.paso_actual += 1
                self.after_id = self.root.after(self.vel_var.get(), self._animar_paso)
            self.after_id = self.root.after(self.vel_var.get() // 2, continuar)

    def _paso_manual(self):
        if self.buscando: return
        if not self.lista:
            if not self._parsear_entrada(): return
            self.paso_actual = 0
            self.comparaciones = 0
            self.colores = [COLOR_IDLE] * len(self.lista)
            self._redibujar_celdas()
        n = len(self.lista)
        if self.paso_actual >= n:
            resultado = bs.buscar(self.lista, self.objetivo)
            self._finalizar(resultado)
            return
        idx = bs.buscar_rango(self.lista, self.objetivo, self.paso_actual, self.paso_actual + 1)
        self.comparaciones += 1
        if idx != -1:
            self.colores[self.paso_actual] = COLOR_CURRENT
            self._redibujar_celdas()
            self._finalizar(self.paso_actual)
        else:
            self.colores[self.paso_actual] = COLOR_MISSED
            self._redibujar_celdas()
            self.paso_actual += 1
            if self.paso_actual >= n:
                resultado = bs.buscar(self.lista, self.objetivo)
                self._finalizar(resultado)

    def _finalizar(self, resultado):
        self.buscando = False
        if resultado != -1:
            self.colores[resultado] = COLOR_FOUND
            self._redibujar_celdas()
            self._actualizar_estado(f"✅ ¡Elemento {self.objetivo} encontrado en el índice {resultado}! ({self.comparaciones} comparaciones)")
        else:
            self._actualizar_estado(f"❌ El elemento {self.objetivo} NO está en la lista. ({self.comparaciones} comparaciones)")
        self.btn_paso.config(state="normal")
        self._actualizar_contador()

    def _reiniciar(self):
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.lista = []
        self.objetivo = None
        self.paso_actual = 0
        self.buscando = False
        self.colores = []
        self.canvas.delete("all")
        self.btn_paso.config(state="normal")
        self._actualizar_estado("Ingresa una lista y un valor, luego presiona Iniciar.")
        self.lbl_comparaciones.config(text="")

    def _redibujar_celdas(self):
        self.canvas.delete("all")
        if not self.lista: return
        n = len(self.lista)
        ancho = self.canvas.winfo_width()
        alto = self.canvas.winfo_height()
        cel_max, cel_min, margen_h = 72, 36, 20
        cel_size = min(cel_max, max(cel_min, (ancho - margen_h * 2) // n - 6))
        gap = min(10, max(4, (ancho - margen_h * 2 - n * cel_size) // max(n - 1, 1)))
        total_w = n * cel_size + (n - 1) * gap
        x0 = (ancho - total_w) // 2
        y0 = (alto - cel_size - 22) // 2

        for i, val in enumerate(self.lista):
            x = x0 + i * (cel_size + gap)
            color = self.colores[i] if i < len(self.colores) else COLOR_IDLE
            self.canvas.create_rectangle(x + 3, y0 + 3, x + cel_size + 3, y0 + cel_size + 3, fill="#111122", outline="")
            self.canvas.create_rectangle(x, y0, x + cel_size, y0 + cel_size, fill=color, outline="#555577", width=2)
            font_size = max(10, min(16, cel_size // 4))
            self.canvas.create_text(x + cel_size // 2, y0 + cel_size // 2, text=str(val), font=("Courier New", font_size, "bold"), fill="white")
            self.canvas.create_text(x + cel_size // 2, y0 + cel_size + 12, text=f"[{i}]", font=("Segoe UI", 8), fill="#888aaa")

            if self.buscando and i == self.paso_actual and i < len(self.colores) and self.colores[i] == COLOR_CURRENT:
                ax = x + cel_size // 2
                self.canvas.create_polygon(ax - 8, y0 - 8, ax + 8, y0 - 8, ax, y0 - 2, fill=COLOR_CURRENT, outline="")
        self._actualizar_contador()

    def _actualizar_estado(self, msg):
        self.lbl_estado.config(text=msg)

    def _actualizar_contador(self):
        if hasattr(self, "comparaciones"):
            self.lbl_comparaciones.config(text=f"Comparaciones realizadas: {self.comparaciones}")

if __name__ == "__main__":
    root = tk.Tk()
    app  = VisualizadorBusqueda(root)
    root.mainloop()