"""
╔══════════════════════════════════════════════════════════════════╗
║         app_ordenamiento.py                                     ║
║  Aplicación Visual de Ordenamiento (ADA1 + ADA2 + ADA3)        ║
║                                                                  ║
║  Integra:                                                        ║
║    • lib_ordenamiento_interno.py  (ADA2 - Internos)            ║
║    • lib_ordenamiento_externo.py  (ADA1/ADA3 - Externos)       ║
║                                                                  ║
║  UI con Tkinter:                                                 ║
║    - Tabs: Ordenamiento Interno | Externo                       ║
║    - Canvas de barras animadas                                   ║
║    - Log de pasos con colores                                    ║
║    - Tarjetas de cintas (solo externos)                         ║
║    - Controles: Ejecutar / Pausar / Detener / Velocidad         ║
╚══════════════════════════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import os

# ── Importar las dos librerías ────────────────────────────────────
from lib_ordenamiento_interno import (
    METODOS_INTERNOS, CLASES_INTERNAS, generar_datos,
    C_CMP, C_SWP, C_AUX, C_DONE, C_READ
)
from lib_ordenamiento_externo import (
    METODOS_EXTERNOS, CLASES_EXTERNAS, MODOS_IO,
    TXT_LO, TXT_MID, TXT_HI, CINTA_COLORES
)

# ══════════════════════════════════════════════════════════════════
#  PALETA DE COLORES DE LA APP
# ══════════════════════════════════════════════════════════════════
BG_DARK   = "#0f172a"
BG_PANEL  = "#1e293b"
BG_CARD   = "#253047"
BG_INPUT  = "#334155"
FG_WHITE  = "#f1f5f9"
FG_MUTED  = "#94a3b8"
FG_DIM    = "#64748b"
ACCENT    = "#6366f1"
ACCENT2   = "#818cf8"
BAR_DEF   = "#475569"

CINTA_HEX = {
    "cinta_A": "#00d4ff", "cinta_B": "#a78bfa",
    "cinta_C": "#22c55e", "cinta_D": "#f59e0b",
    "datos":   "#e2e8f0", "entrada": "#e2e8f0",
    "temp1":   "#ff6b6b", "temp2":   "#f59e0b",
    "resultado":"#22c55e",
}

COLOR_MAP = {
    C_CMP:  C_CMP,
    C_SWP:  C_SWP,
    C_AUX:  C_AUX,
    C_DONE: C_DONE,
    C_READ: C_READ,
}


# ══════════════════════════════════════════════════════════════════
#  WIDGET: CANVAS DE BARRAS
# ══════════════════════════════════════════════════════════════════

class BarChart(tk.Canvas):
    """Canvas que dibuja barras proporcionales al valor del array."""

    def __init__(self, master, **kw):
        super().__init__(master, bg=BG_DARK, highlightthickness=0, **kw)
        self._arr = []
        self._hi  = {}

    def update_data(self, arr, highlights):
        self._arr = arr
        self._hi  = highlights
        self.after(0, self._draw)

    def _draw(self):
        self.delete("all")
        arr = self._arr
        if not arr:
            return
        W = self.winfo_width()  or 600
        H = self.winfo_height() or 200
        n = len(arr)
        if n == 0:
            return
        mx = max(arr) if max(arr) > 0 else 1
        bw = max(2, W / n)
        pad = 4

        for i, v in enumerate(arr):
            x0 = i * bw + pad
            x1 = (i + 1) * bw - pad
            bh = int((v / mx) * (H - 20))
            y0 = H - bh - 4
            y1 = H - 4
            color = self._hi.get(i, BAR_DEF)
            self.create_rectangle(x0, y0, x1, y1,
                                  fill=color, outline="", width=0)
            # valor encima si las barras son suficientemente anchas
            if bw > 22 and bh > 14:
                self.create_text((x0 + x1) / 2, y0 - 6,
                                 text=str(v), fill=FG_WHITE,
                                 font=("Consolas", 7))


# ══════════════════════════════════════════════════════════════════
#  WIDGET: LOG CON COLORES
# ══════════════════════════════════════════════════════════════════

class ColorLog(tk.Text):
    """Text widget con método log(msg, color) thread-safe."""

    def __init__(self, master, **kw):
        kw.setdefault("bg", BG_DARK)
        kw.setdefault("fg", FG_WHITE)
        kw.setdefault("font", ("Consolas", 9))
        kw.setdefault("state", "disabled")
        kw.setdefault("wrap", "word")
        super().__init__(master, **kw)

    def log(self, msg, color=FG_WHITE):
        color = color or FG_WHITE
        tag = f"col_{color.replace('#','')}"
        self.after(0, self._write, msg, color, tag)

    def _write(self, msg, color, tag):
        self.configure(state="normal")
        self.tag_configure(tag, foreground=color)
        self.insert("end", msg + "\n", tag)
        self.see("end")
        self.configure(state="disabled")

    def clear(self):
        self.after(0, self._clear)

    def _clear(self):
        self.configure(state="normal")
        self.delete("1.0", "end")
        self.configure(state="disabled")


# ══════════════════════════════════════════════════════════════════
#  WIDGET: TARJETA DE CINTA
# ══════════════════════════════════════════════════════════════════

class CintaCard(tk.Frame):
    """Tarjeta visual que muestra el contenido de una cinta."""

    def __init__(self, master, nombre, **kw):
        super().__init__(master, bg=BG_CARD, relief="flat",
                         highlightbackground=CINTA_HEX.get(nombre, ACCENT),
                         highlightthickness=2, **kw)
        color = CINTA_HEX.get(nombre, ACCENT)
        tk.Label(self, text=nombre.upper().replace("_", " "),
                 bg=BG_CARD, fg=color,
                 font=("Consolas", 9, "bold")).pack(anchor="w", padx=6, pady=(4, 0))
        self._txt = tk.Text(self, bg=BG_DARK, fg=FG_WHITE,
                            font=("Consolas", 8), state="disabled",
                            height=3, wrap="word", relief="flat",
                            highlightthickness=0)
        self._txt.pack(fill="both", expand=True, padx=4, pady=4)

    def set_data(self, datos):
        self._txt.configure(state="normal")
        self._txt.delete("1.0", "end")
        preview = datos[:40]
        texto = "  ".join(str(x) for x in preview)
        if len(datos) > 40:
            texto += f"  … (+{len(datos)-40})"
        self._txt.insert("end", texto)
        self._txt.configure(state="disabled")


# ══════════════════════════════════════════════════════════════════
#  TAB: ORDENAMIENTO INTERNO
# ══════════════════════════════════════════════════════════════════

class TabInterno(tk.Frame):

    def __init__(self, master):
        super().__init__(master, bg=BG_DARK)
        self._thread = None
        self._gen    = None
        self._paused = False
        self._stop   = False
        self._running= False
        self._build()

    # ── Construcción UI ──────────────────────────────────────────

    def _build(self):
        # ── Panel superior: controles ─────────────────────────
        ctrl = tk.Frame(self, bg=BG_PANEL, pady=8)
        ctrl.pack(fill="x", padx=10, pady=(10, 0))

        tk.Label(ctrl, text="Método:", bg=BG_PANEL, fg=FG_MUTED,
                 font=("Arial", 10)).grid(row=0, column=0, padx=(12,4))
        self.cb_metodo = ttk.Combobox(ctrl, values=METODOS_INTERNOS,
                                      state="readonly", width=16)
        self.cb_metodo.set(METODOS_INTERNOS[0])
        self.cb_metodo.grid(row=0, column=1, padx=4)

        tk.Label(ctrl, text="Elementos:", bg=BG_PANEL, fg=FG_MUTED,
                 font=("Arial", 10)).grid(row=0, column=2, padx=(16, 4))
        self.sp_n = tk.Spinbox(ctrl, from_=5, to=120, width=5,
                               bg=BG_INPUT, fg=FG_WHITE,
                               buttonbackground=BG_INPUT,
                               insertbackground=FG_WHITE, relief="flat")
        self.sp_n.delete(0, "end"); self.sp_n.insert(0, "30")
        self.sp_n.grid(row=0, column=3, padx=4)

        tk.Label(ctrl, text="Velocidad:", bg=BG_PANEL, fg=FG_MUTED,
                 font=("Arial", 10)).grid(row=0, column=4, padx=(16, 4))
        self.sl_vel = tk.Scale(ctrl, from_=1, to=10, orient="horizontal",
                               bg=BG_PANEL, fg=FG_WHITE, troughcolor=BG_INPUT,
                               highlightthickness=0, length=100)
        self.sl_vel.set(5)
        self.sl_vel.grid(row=0, column=5, padx=4)

        # Botones
        btn_style = {"font": ("Arial", 10, "bold"), "relief": "flat",
                     "cursor": "hand2", "padx": 14, "pady": 4}
        self.btn_run = tk.Button(ctrl, text="▶ Ejecutar",
                                 bg=ACCENT, fg=FG_WHITE,
                                 command=self._ejecutar, **btn_style)
        self.btn_run.grid(row=0, column=6, padx=(20, 4))
        self.btn_paus = tk.Button(ctrl, text="⏸ Pausar",
                                  bg="#ca8a04", fg=FG_WHITE,
                                  command=self._pausar, **btn_style)
        self.btn_paus.grid(row=0, column=7, padx=4)
        self.btn_stop = tk.Button(ctrl, text="⏹ Detener",
                                  bg="#dc2626", fg=FG_WHITE,
                                  command=self._detener, **btn_style)
        self.btn_stop.grid(row=0, column=8, padx=4)

        # ── Status bar ────────────────────────────────────────
        self.lbl_status = tk.Label(self, text="Listo.",
                                   bg=BG_PANEL, fg=FG_MUTED,
                                   font=("Consolas", 9), anchor="w")
        self.lbl_status.pack(fill="x", padx=10)

        # ── Canvas de barras ──────────────────────────────────
        self.chart = BarChart(self, height=220)
        self.chart.pack(fill="x", padx=10, pady=6)

        # ── Info de complejidad ───────────────────────────────
        self.lbl_info = tk.Label(self, text="",
                                 bg=BG_DARK, fg=ACCENT2,
                                 font=("Consolas", 9))
        self.lbl_info.pack(fill="x", padx=14)

        # ── Log ───────────────────────────────────────────────
        log_frame = tk.Frame(self, bg=BG_DARK)
        log_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        tk.Label(log_frame, text="📋 Log de pasos",
                 bg=BG_DARK, fg=FG_MUTED,
                 font=("Arial", 9, "bold")).pack(anchor="w")
        sb = tk.Scrollbar(log_frame)
        sb.pack(side="right", fill="y")
        self.log = ColorLog(log_frame, yscrollcommand=sb.set, height=10)
        self.log.pack(fill="both", expand=True)
        sb.config(command=self.log.yview)

    # ── Métodos de control ────────────────────────────────────────

    _INFO = {
        "Burbuja":    "Burbuja — O(n²) peor/promedio · O(n) mejor",
        "Inserción":  "Inserción — O(n²) peor/promedio · O(n) mejor",
        "Selección":  "Selección — O(n²) todos los casos",
        "Shell Sort": "Shell Sort — O(n log² n) con secuencia de Knuth",
        "Quick Sort": "Quick Sort — O(n log n) promedio · O(n²) peor",
        "Merge Sort": "Merge Sort — O(n log n) todos los casos",
        "Heap Sort":  "Heap Sort  — O(n log n) todos los casos",
    }

    def _ejecutar(self):
        if self._running:
            return
        metodo = self.cb_metodo.get()
        try:
            n = int(self.sp_n.get())
            if n < 2 or n > 120:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Elementos: entero entre 2 y 120")
            return

        self._stop   = False
        self._paused = False
        self._running= True
        self.log.clear()
        self.lbl_info.config(text=self._INFO.get(metodo, ""))
        self.lbl_status.config(text=f"Ejecutando {metodo}…", fg=C_CMP)

        datos = generar_datos(n)
        fn    = CLASES_INTERNAS[metodo]
        self._gen = fn(datos)

        delay = (11 - self.sl_vel.get()) * 0.04

        self.log.log(f"▶ {metodo}  |  n={n}  |  datos={datos}", ACCENT2)
        self._thread = threading.Thread(target=self._run_gen,
                                        args=(delay,), daemon=True)
        self._thread.start()

    def _run_gen(self, delay):
        try:
            for snap, hi, msg in self._gen:
                if self._stop:
                    break
                while self._paused and not self._stop:
                    time.sleep(0.05)
                self.chart.update_data(snap, hi)
                self.log.log(f"  {msg}", self._color_for_hi(hi))
                time.sleep(delay)
            if not self._stop:
                self.lbl_status.config(text="✔ Completado.", fg=C_DONE)
                self.log.log("✔ ¡Ordenamiento completado!", C_DONE)
        except Exception as e:
            self.lbl_status.config(text=f"Error: {e}", fg="#ff6b6b")
        finally:
            self._running = False

    def _color_for_hi(self, hi):
        if not hi:
            return FG_MUTED
        vals = list(hi.values())
        if C_SWP in vals: return C_SWP
        if C_CMP in vals: return C_CMP
        if C_DONE in vals: return C_DONE
        return FG_MUTED

    def _pausar(self):
        self._paused = not self._paused
        txt = "▶ Reanudar" if self._paused else "⏸ Pausar"
        self.btn_paus.config(text=txt)
        self.lbl_status.config(
            text="En pausa." if self._paused else "Reanudando…",
            fg=C_READ if self._paused else C_CMP)

    def _detener(self):
        self._stop   = True
        self._paused = False
        self._running= False
        self.lbl_status.config(text="Detenido.", fg="#ff6b6b")
        self.log.log("⏹ Detenido por el usuario.", "#ff6b6b")


# ══════════════════════════════════════════════════════════════════
#  TAB: ORDENAMIENTO EXTERNO
# ══════════════════════════════════════════════════════════════════

class TabExterno(tk.Frame):

    def __init__(self, master):
        super().__init__(master, bg=BG_DARK)
        self._thread  = None
        self._algo    = None
        self._paused  = False
        self._running = False
        # Directorio del proyecto (donde vive este script)
        self._tmpdir  = os.path.dirname(os.path.abspath(__file__))
        self._build()

    # ── Construcción UI ──────────────────────────────────────────

    def _build(self):
        # ── Controles superiores ──────────────────────────────
        ctrl = tk.Frame(self, bg=BG_PANEL, pady=8)
        ctrl.pack(fill="x", padx=10, pady=(10, 0))

        tk.Label(ctrl, text="Método:", bg=BG_PANEL, fg=FG_MUTED,
                 font=("Arial", 10)).grid(row=0, column=0, padx=(12, 4))
        self.cb_metodo = ttk.Combobox(ctrl, values=METODOS_EXTERNOS,
                                      state="readonly", width=20)
        self.cb_metodo.set(METODOS_EXTERNOS[0])
        self.cb_metodo.grid(row=0, column=1, padx=4)

        tk.Label(ctrl, text="Modo E/S:", bg=BG_PANEL, fg=FG_MUTED,
                 font=("Arial", 10)).grid(row=0, column=2, padx=(16, 4))
        self.cb_modo = ttk.Combobox(ctrl, values=MODOS_IO,
                                    state="readonly", width=8)
        self.cb_modo.set("TXT")
        self.cb_modo.grid(row=0, column=3, padx=4)

        tk.Label(ctrl, text="Elementos:", bg=BG_PANEL, fg=FG_MUTED,
                 font=("Arial", 10)).grid(row=0, column=4, padx=(16, 4))
        self.sp_n = tk.Spinbox(ctrl, from_=4, to=80, width=5,
                               bg=BG_INPUT, fg=FG_WHITE,
                               buttonbackground=BG_INPUT,
                               insertbackground=FG_WHITE, relief="flat")
        self.sp_n.delete(0, "end"); self.sp_n.insert(0, "16")
        self.sp_n.grid(row=0, column=5, padx=4)

        tk.Label(ctrl, text="Velocidad:", bg=BG_PANEL, fg=FG_MUTED,
                 font=("Arial", 10)).grid(row=0, column=6, padx=(16, 4))
        self.sl_vel = tk.Scale(ctrl, from_=1, to=10, orient="horizontal",
                               bg=BG_PANEL, fg=FG_WHITE, troughcolor=BG_INPUT,
                               highlightthickness=0, length=100)
        self.sl_vel.set(5)
        self.sl_vel.grid(row=0, column=7, padx=4)

        btn_style = {"font": ("Arial", 10, "bold"), "relief": "flat",
                     "cursor": "hand2", "padx": 14, "pady": 4}
        self.btn_run = tk.Button(ctrl, text="▶ Ejecutar",
                                 bg=ACCENT, fg=FG_WHITE,
                                 command=self._ejecutar, **btn_style)
        self.btn_run.grid(row=0, column=8, padx=(20, 4))
        self.btn_paus = tk.Button(ctrl, text="⏸ Pausar",
                                  bg="#ca8a04", fg=FG_WHITE,
                                  command=self._pausar, **btn_style)
        self.btn_paus.grid(row=0, column=9, padx=4)
        self.btn_stop = tk.Button(ctrl, text="⏹ Detener",
                                  bg="#dc2626", fg=FG_WHITE,
                                  command=self._detener, **btn_style)
        self.btn_stop.grid(row=0, column=10, padx=4)

        self.btn_abrir = tk.Button(ctrl, text="📂 Abrir carpeta",
                                   bg="#0f766e", fg=FG_WHITE,
                                   state="disabled", **btn_style)
        self.btn_abrir.grid(row=0, column=11, padx=(12, 4))

        # ── Status ────────────────────────────────────────────
        self.lbl_status = tk.Label(self, text="Listo.",
                                   bg=BG_PANEL, fg=FG_MUTED,
                                   font=("Consolas", 9), anchor="w")
        self.lbl_status.pack(fill="x", padx=10)

        # ── Canvas ────────────────────────────────────────────
        self.chart = BarChart(self, height=180)
        self.chart.pack(fill="x", padx=10, pady=4)

        # ── Tarjetas de cintas ────────────────────────────────
        cintas_frame = tk.Frame(self, bg=BG_DARK)
        cintas_frame.pack(fill="x", padx=10, pady=4)
        tk.Label(cintas_frame, text="💾 Cintas magnéticas",
                 bg=BG_DARK, fg=FG_MUTED,
                 font=("Arial", 9, "bold")).pack(anchor="w")
        self._cards_frame = tk.Frame(cintas_frame, bg=BG_DARK)
        self._cards_frame.pack(fill="x")
        self._cards = {}
        for nombre in ["datos", "cinta_A", "cinta_B", "cinta_C", "cinta_D",
                       "temp1", "temp2", "entrada", "resultado"]:
            card = CintaCard(self._cards_frame, nombre, width=150)
            self._cards[nombre] = card

        # ── Log ───────────────────────────────────────────────
        log_frame = tk.Frame(self, bg=BG_DARK)
        log_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        tk.Label(log_frame, text="📋 Log de operaciones en disco",
                 bg=BG_DARK, fg=FG_MUTED,
                 font=("Arial", 9, "bold")).pack(anchor="w")
        sb = tk.Scrollbar(log_frame)
        sb.pack(side="right", fill="y")
        self.log = ColorLog(log_frame, yscrollcommand=sb.set, height=10)
        self.log.pack(fill="both", expand=True)
        sb.config(command=self.log.yview)

    def _update_cards(self, d: dict):
        """Muestra las tarjetas relevantes según el dict {nombre: datos}."""
        # ocultar todas
        for c in self._cards.values():
            c.pack_forget()
        # mostrar solo las presentes
        for nombre, datos in d.items():
            if nombre in self._cards:
                self._cards[nombre].set_data(datos)
                self._cards[nombre].pack(side="left", padx=4, pady=2,
                                         fill="both", expand=True)

    # ── Control ───────────────────────────────────────────────────

    def _ejecutar(self):
        if self._running:
            return
        metodo = self.cb_metodo.get()
        modo   = self.cb_modo.get()
        try:
            n = int(self.sp_n.get())
            if n < 4 or n > 80:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Elementos: entero entre 4 y 80")
            return

        self._paused  = False
        self._running = True
        self.log.clear()
        self.btn_abrir.config(state="disabled", text="📂 Abrir carpeta")
        for c in self._cards.values():
            c.pack_forget()

        delay = (11 - self.sl_vel.get()) * 0.08
        self.lbl_status.config(text=f"Ejecutando {metodo} [{modo}]…", fg=C_CMP)
        self.log.log(f"▶ {metodo}  |  modo={modo}  |  n={n}", ACCENT2)
        self.log.log(f"   Carpeta de trabajo: {self._tmpdir}", FG_DIM)

        def _fin(res, path):
            self._running = False
            nombre_archivo = os.path.basename(path)
            self.lbl_status.config(
                text=f"✔ Completado — {len(res)} elementos ordenados → {nombre_archivo}",
                fg=C_DONE)
            self.log.log(f"\n✔ Resultado guardado en:", C_DONE)
            self.log.log(f"   {path}", C_DONE)
            self.chart.update_data(res, {i: C_DONE for i in range(len(res))})
            # Botón para abrir la carpeta del proyecto
            def _abrir_carpeta():
                import subprocess, sys
                carpeta = os.path.dirname(path)
                if sys.platform == "win32":
                    subprocess.Popen(["explorer", carpeta])
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", carpeta])
                else:
                    subprocess.Popen(["xdg-open", carpeta])
            self.after(0, lambda: self.btn_abrir.config(
                state="normal",
                command=_abrir_carpeta,
                text="📂 Abrir carpeta",
            ))

        def _pausa_fn():
            while self._paused:
                time.sleep(0.05)

        self._algo = CLASES_EXTERNAS[metodo](
            log_cb   = self.log.log,
            barra_cb = self.chart.update_data,
            cinta_cb = lambda d: self.after(0, self._update_cards, d),
            fin_cb   = _fin,
            pausa_fn = _pausa_fn,
            modo_io  = modo,
            carpeta  = self._tmpdir,
        )
        self._thread = threading.Thread(
            target=self._run_algo, args=(n, delay), daemon=True)
        self._thread.start()

    def _run_algo(self, n, delay):
        try:
            self._algo.ejecutar(n, delay)
        except InterruptedError:
            self.log.log("⏹ Detenido por el usuario.", "#ff6b6b")
            self.lbl_status.config(text="Detenido.", fg="#ff6b6b")
            self._running = False
        except Exception as e:
            self.log.log(f"⚠ Error: {e}", "#ff6b6b")
            self.lbl_status.config(text=f"Error: {e}", fg="#ff6b6b")
            self._running = False

    def _pausar(self):
        self._paused = not self._paused
        txt = "▶ Reanudar" if self._paused else "⏸ Pausar"
        self.btn_paus.config(text=txt)
        self.lbl_status.config(
            text="En pausa." if self._paused else "Reanudando…",
            fg=C_READ if self._paused else C_CMP)

    def _detener(self):
        if self._algo:
            self._algo.detener()
        self._paused  = False
        self._running = False


# ══════════════════════════════════════════════════════════════════
#  VENTANA PRINCIPAL
# ══════════════════════════════════════════════════════════════════

class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Visualizador de Ordenamiento — ADA1 · ADA2 · ADA3")
        self.geometry("1100x780")
        self.minsize(900, 640)
        self.configure(bg=BG_DARK)
        self._apply_style()
        self._build()

    def _apply_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook",
                         background=BG_DARK, borderwidth=0)
        style.configure("TNotebook.Tab",
                         background=BG_PANEL, foreground=FG_MUTED,
                         padding=[16, 6], font=("Arial", 11, "bold"))
        style.map("TNotebook.Tab",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", FG_WHITE)])
        style.configure("TCombobox",
                         fieldbackground=BG_INPUT, background=BG_INPUT,
                         foreground=FG_WHITE, selectbackground=ACCENT)

    def _build(self):
        # Encabezado
        hdr = tk.Frame(self, bg=BG_PANEL, pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr,
                 text="⚡ Visualizador de Ordenamiento",
                 bg=BG_PANEL, fg=FG_WHITE,
                 font=("Arial", 16, "bold")).pack(side="left", padx=20)
        tk.Label(hdr,
                 text="ADA1 (Externo) · ADA2 (Interno) · ADA3 (E/S TXT & Excel)",
                 bg=BG_PANEL, fg=FG_DIM,
                 font=("Arial", 9)).pack(side="left", padx=4)

        # Leyenda de colores
        ley = tk.Frame(self, bg=BG_DARK)
        ley.pack(fill="x", padx=14, pady=4)
        leyenda = [
            (C_CMP,  "Comparando"),
            (C_SWP,  "Intercambio"),
            (C_AUX,  "Auxiliar/Pivote"),
            (C_DONE, "Ordenado"),
            (C_READ, "Lectura"),
        ]
        for color, label in leyenda:
            f = tk.Frame(ley, bg=BG_DARK)
            f.pack(side="left", padx=8)
            tk.Canvas(f, width=14, height=14, bg=color,
                      highlightthickness=0).pack(side="left", padx=(0, 3))
            tk.Label(f, text=label, bg=BG_DARK, fg=FG_MUTED,
                     font=("Arial", 8)).pack(side="left")

        # Notebook con dos tabs
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.tab_int = TabInterno(nb)
        self.tab_ext = TabExterno(nb)

        nb.add(self.tab_int, text="  🔢 Ordenamiento Interno  ")
        nb.add(self.tab_ext, text="  📼 Ordenamiento Externo  ")

        # Pie
        pie = tk.Label(self,
                       text="Internos: Burbuja · Inserción · Selección · Shell · Quick · Merge · Heap  |  "
                            "Externos: Intercalación · Mezcla Directa · Mezcla Equilibrada (4 cintas)",
                       bg=BG_DARK, fg=FG_DIM, font=("Arial", 8))
        pie.pack(pady=(0, 6))


# ══════════════════════════════════════════════════════════════════
#  PUNTO DE ENTRADA
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = App()
    app.mainloop()