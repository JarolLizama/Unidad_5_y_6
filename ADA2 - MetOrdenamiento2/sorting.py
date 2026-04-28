import tkinter as tk
from tkinter import ttk, messagebox
import time
import random

# ─────────────────────────────────────────
#  COLORES
# ─────────────────────────────────────────
BG       = "#1e1e2e"
CARD     = "#2a2a3e"
ACCENT   = "#7c6fff"
FG       = "#cdd6f4"
FG2      = "#6c7086"
ENTRY_BG = "#313244"

ALGO_COLORS = {
    "Shell Sort": "#ff79c6",
    "Quick Sort": "#bd93f9",
    "Heap Sort":  "#50fa7b",
    "Radix Sort": "#ffb86c",
}

BAR_NORMAL  = "#5555aa"
BAR_ACTIVE  = "#ff5555"   # elemento que se mueve / compara
BAR_SORTED  = "#50fa7b"   # ya ordenado
BAR_PIVOT   = "#ffb86c"   # pivote (quicksort)
BAR_COMPARE = "#ff79c6"   # comparando

# ─────────────────────────────────────────
#  GENERADORES – producen cada paso
# ─────────────────────────────────────────
def shell_sort_steps(arr):
    a = arr[:]
    n = len(a)
    gap = n // 2
    while gap > 0:
        for i in range(gap, n):
            temp = a[i]
            j = i
            while j >= gap and a[j - gap] > temp:
                a[j] = a[j - gap]
                yield list(a), [j, j - gap], [], [], f"Gap={gap}  moviendo {temp}  pos {j-gap}→{j}"
                j -= gap
            a[j] = temp
            yield list(a), [j], [], [], f"Gap={gap}  colocando {temp} en pos {j}"
        gap //= 2
    yield list(a), [], [], list(range(n)), "¡Ordenado!"


def quick_sort_steps(arr):
    a = arr[:]

    def _qs(lo, hi):
        if lo >= hi:
            return
        pivot_val = a[(lo + hi) // 2]
        pivot_idx = (lo + hi) // 2
        i, j = lo, hi
        while i <= j:
            while a[i] < pivot_val:
                yield list(a), [i], [pivot_idx], [], f"Buscando desde izq: a[{i}]={a[i]} < pivot={pivot_val}"
                i += 1
            while a[j] > pivot_val:
                yield list(a), [j], [pivot_idx], [], f"Buscando desde der: a[{j}]={a[j]} > pivot={pivot_val}"
                j -= 1
            if i <= j:
                a[i], a[j] = a[j], a[i]
                yield list(a), [i, j], [pivot_idx], [], f"Intercambio a[{i}]↔a[{j}]"
                i += 1
                j -= 1
        yield from _qs(lo, j)
        yield from _qs(i, hi)

    yield from _qs(0, len(a) - 1)
    yield list(a), [], [], list(range(len(a))), "¡Ordenado!"


def heap_sort_steps(arr):
    a = arr[:]
    n = len(a)

    def heapify(n, i):
        largest = i
        l, r = 2*i+1, 2*i+2
        if l < n and a[l] > a[largest]: largest = l
        if r < n and a[r] > a[largest]: largest = r
        if largest != i:
            a[i], a[largest] = a[largest], a[i]
            yield list(a), [i, largest], [], [], f"Heapify: intercambio pos {i}↔{largest}"
            yield from heapify(n, largest)

    for i in range(n//2-1, -1, -1):
        yield from heapify(n, i)
        yield list(a), [i], [], [], f"Construyendo heap en pos {i}"

    for i in range(n-1, 0, -1):
        a[0], a[i] = a[i], a[0]
        yield list(a), [0, i], [], list(range(i+1, n)), f"Extrayendo máximo a pos {i}"
        yield from heapify(i, 0)

    yield list(a), [], [], list(range(n)), "¡Ordenado!"


def radix_sort_steps(arr):
    a = arr[:]
    if not a:
        return
    max_val = max(a)
    exp = 1
    while max_val // exp > 0:
        n = len(a)
        output = [0] * n
        count  = [0] * 10
        for i in range(n):
            idx = (a[i] // exp) % 10
            count[idx] += 1
            yield list(a), [i], [], [], f"Dígito exp={exp}: a[{i}]={a[i]}  → cubo {idx}"
        for i in range(1, 10):
            count[i] += count[i-1]
        for i in range(n-1, -1, -1):
            idx = (a[i] // exp) % 10
            output[count[idx]-1] = a[i]
            count[idx] -= 1
        for i in range(n):
            a[i] = output[i]
        yield list(a), [], [], [], f"Pasada exp={exp} completada"
        exp *= 10
    yield list(a), [], [], list(range(len(a))), "¡Ordenado!"


GENERATORS = {
    "Shell Sort": shell_sort_steps,
    "Quick Sort": quick_sort_steps,
    "Heap Sort":  heap_sort_steps,
    "Radix Sort": radix_sort_steps,
}

# ─────────────────────────────────────────
#  APLICACIÓN
# ─────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Algoritmos de Ordenamiento – Paso a Paso")
        self.geometry("950x680")
        self.configure(bg=BG)
        self.resizable(True, True)

        self._gen      = None   # generador activo
        self._running  = False
        self._after_id = None
        self._speed    = 300    # ms entre pasos

        self._build()

    # ─── UI ──────────────────────────────────────────────────────────────────
    def _build(self):
        # Header
        hdr = tk.Frame(self, bg="#181825", height=52)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="Algoritmos de Ordenamiento – Paso a Paso",
                 font=("Segoe UI", 15, "bold"), bg="#181825", fg=FG
                 ).pack(side="left", padx=20)

        # Body
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=14, pady=10)

        self._panel_left(body)
        self._panel_right(body)

    def _panel_left(self, parent):
        left = tk.Frame(parent, bg=CARD, width=240, padx=14, pady=14)
        left.pack(side="left", fill="y", padx=(0, 12))
        left.pack_propagate(False)

        # Algoritmo
        tk.Label(left, text="ALGORITMO", font=("Segoe UI", 9, "bold"),
                 bg=CARD, fg=FG2).pack(anchor="w", pady=(0, 6))

        self.algo_var = tk.StringVar(value="Shell Sort")
        for name, color in ALGO_COLORS.items():
            f = tk.Frame(left, bg=CARD)
            f.pack(fill="x", pady=2)
            tk.Label(f, text="●", font=("Segoe UI", 11), bg=CARD, fg=color).pack(side="left")
            tk.Radiobutton(f, text=name, variable=self.algo_var, value=name,
                           font=("Segoe UI", 11), bg=CARD, fg=FG,
                           selectcolor=CARD, activebackground=CARD,
                           activeforeground=color, highlightthickness=0,
                           cursor="hand2").pack(side="left")

        tk.Frame(left, bg=ENTRY_BG, height=1).pack(fill="x", pady=12)

        # Cantidad
        tk.Label(left, text="CANTIDAD", font=("Segoe UI", 9, "bold"),
                 bg=CARD, fg=FG2).pack(anchor="w", pady=(0, 4))

        qty_row = tk.Frame(left, bg=CARD)
        qty_row.pack(fill="x", pady=(0, 6))
        self.qty_var = tk.StringVar(value="8")
        tk.Spinbox(qty_row, from_=2, to=20, textvariable=self.qty_var,
                   font=("Segoe UI", 12), bg=ENTRY_BG, fg=FG,
                   insertbackground=FG, buttonbackground=ENTRY_BG,
                   relief="flat", width=4).pack(side="left", ipady=4)

        # Velocidad
        tk.Label(left, text="VELOCIDAD", font=("Segoe UI", 9, "bold"),
                 bg=CARD, fg=FG2).pack(anchor="w", pady=(8, 2))

        self.speed_var = tk.IntVar(value=300)
        speed_scale = tk.Scale(
            left, variable=self.speed_var, from_=50, to=1000,
            orient="horizontal", bg=CARD, fg=FG, troughcolor=ENTRY_BG,
            highlightthickness=0, sliderrelief="flat",
            label="", showvalue=False, command=self._update_speed,
        )
        speed_scale.pack(fill="x")

        spd_row = tk.Frame(left, bg=CARD)
        spd_row.pack(fill="x")
        tk.Label(spd_row, text="Rápido", font=("Segoe UI", 8), bg=CARD, fg=FG2).pack(side="left")
        tk.Label(spd_row, text="Lento",  font=("Segoe UI", 8), bg=CARD, fg=FG2).pack(side="right")

        tk.Frame(left, bg=ENTRY_BG, height=1).pack(fill="x", pady=12)

        # Botones
        tk.Button(left, text="▶  INICIAR", font=("Segoe UI", 12, "bold"),
                  bg=ACCENT, fg="white", relief="flat", pady=9,
                  cursor="hand2", command=self._start).pack(fill="x", pady=(0, 4))

        tk.Button(left, text="⏸  PAUSAR", font=("Segoe UI", 11),
                  bg=ENTRY_BG, fg=FG, relief="flat", pady=7,
                  cursor="hand2", command=self._pause).pack(fill="x", pady=(0, 4))

        tk.Button(left, text="⏭  PASO", font=("Segoe UI", 11),
                  bg=ENTRY_BG, fg=FG, relief="flat", pady=7,
                  cursor="hand2", command=self._step).pack(fill="x", pady=(0, 4))

        tk.Button(left, text="↺  REINICIAR", font=("Segoe UI", 11),
                  bg=ENTRY_BG, fg=FG2, relief="flat", pady=7,
                  cursor="hand2", command=self._reset).pack(fill="x")

        tk.Frame(left, bg=ENTRY_BG, height=1).pack(fill="x", pady=12)

        # Leyenda
        tk.Label(left, text="LEYENDA", font=("Segoe UI", 9, "bold"),
                 bg=CARD, fg=FG2).pack(anchor="w", pady=(0, 4))
        for color, label in [
            (BAR_NORMAL,  "Normal"),
            (BAR_ACTIVE,  "Activo / moviendo"),
            (BAR_PIVOT,   "Pivote"),
            (BAR_COMPARE, "Comparando"),
            (BAR_SORTED,  "Ordenado"),
        ]:
            row = tk.Frame(left, bg=CARD)
            row.pack(anchor="w", pady=1)
            tk.Label(row, text="■", font=("Segoe UI", 12), bg=CARD, fg=color).pack(side="left")
            tk.Label(row, text=label, font=("Segoe UI", 9), bg=CARD, fg=FG2).pack(side="left", padx=4)

    def _panel_right(self, parent):
        right = tk.Frame(parent, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        # Info actual
        info = tk.Frame(right, bg=CARD, padx=14, pady=10)
        info.pack(fill="x", pady=(0, 10))

        self.lbl_algo = tk.Label(info, text="—", font=("Segoe UI", 14, "bold"),
                                  bg=CARD, fg=ACCENT)
        self.lbl_algo.pack(side="left")

        self.lbl_step = tk.Label(info, text="", font=("Segoe UI", 10),
                                  bg=CARD, fg=FG2)
        self.lbl_step.pack(side="left", padx=16)

        self.lbl_time = tk.Label(info, text="", font=("Segoe UI", 10),
                                  bg=CARD, fg="#ffb86c")
        self.lbl_time.pack(side="right")

        # Canvas de barras
        self.canvas = tk.Canvas(right, bg=CARD, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Mensaje de estado
        self.lbl_msg = tk.Label(right, text="Presiona INICIAR para comenzar",
                                 font=("Segoe UI", 10), bg=BG, fg=FG2)
        self.lbl_msg.pack(pady=6)

        # Arreglo actual (texto)
        self.lbl_arr = tk.Label(right, text="", font=("Courier", 10),
                                 bg=BG, fg=FG2)
        self.lbl_arr.pack()

    # ─── control ─────────────────────────────────────────────────────────────
    def _make_array(self):
        try:
            qty = int(self.qty_var.get())
        except Exception:
            qty = 8
        qty = max(2, min(20, qty))
        return [random.randint(5, 100) for _ in range(qty)]

    def _start(self):
        self._stop_loop()
        arr  = self._make_array()
        name = self.algo_var.get()
        self._gen = GENERATORS[name](arr)
        self._start_time = time.perf_counter()
        self._step_count = 0
        color = ALGO_COLORS[name]
        self.lbl_algo.config(text=f"  {name}", fg=color)
        self.lbl_msg.config(text="Ejecutando...")
        self._draw_bars(arr, [], [], [])
        self._running = True
        self._loop()

    def _loop(self):
        if not self._running:
            return
        finished = self._step()
        if not finished:
            self._after_id = self.after(self._speed, self._loop)

    def _step(self, *_):
        """Avanza un paso. Devuelve True si terminó."""
        if self._gen is None:
            return True
        try:
            state, active, pivot, sorted_idx, msg = next(self._gen)
            self._step_count += 1
            elapsed = (time.perf_counter() - self._start_time) * 1000
            self.lbl_step.config(text=f"Paso {self._step_count}")
            self.lbl_time.config(text=f"{elapsed:.1f} ms")
            self.lbl_msg.config(text=msg)
            self.lbl_arr.config(text=str(state))
            self._draw_bars(state, active, pivot, sorted_idx)
            return False
        except StopIteration:
            self._running = False
            self.lbl_msg.config(text="✔ Completado")
            return True

    def _pause(self):
        self._running = not self._running
        if self._running:
            self._loop()

    def _reset(self):
        self._stop_loop()
        self._gen = None
        self.canvas.delete("all")
        self.lbl_msg.config(text="Presiona INICIAR para comenzar")
        self.lbl_step.config(text="")
        self.lbl_time.config(text="")
        self.lbl_arr.config(text="")
        self.lbl_algo.config(text="—", fg=ACCENT)

    def _stop_loop(self):
        self._running = False
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None

    def _update_speed(self, *_):
        self._speed = self.speed_var.get()

    # ─── dibujo ──────────────────────────────────────────────────────────────
    def _draw_bars(self, arr, active, pivot, sorted_idx):
        self.canvas.delete("all")
        self.canvas.update_idletasks()

        W = self.canvas.winfo_width()
        H = self.canvas.winfo_height()
        if W < 10 or H < 10:
            return

        n      = len(arr)
        max_v  = max(arr) if arr else 1
        pad    = 12
        gap    = 4
        bar_w  = (W - 2*pad - gap*(n-1)) / n
        bar_w  = max(bar_w, 4)

        for i, val in enumerate(arr):
            x0 = pad + i * (bar_w + gap)
            x1 = x0 + bar_w
            bar_h = max(4, int((val / max_v) * (H - 60)))
            y0 = H - 30 - bar_h
            y1 = H - 30

            if i in sorted_idx:
                color = BAR_SORTED
            elif i in active:
                color = BAR_ACTIVE
            elif i in pivot:
                color = BAR_PIVOT
            else:
                color = BAR_NORMAL

            # sombra
            self.canvas.create_rectangle(x0+2, y0+2, x1+2, y1+2,
                                          fill="#111122", outline="")
            # barra
            self.canvas.create_rectangle(x0, y0, x1, y1,
                                          fill=color, outline="", width=0)
            # valor
            if bar_w > 18:
                self.canvas.create_text(
                    (x0+x1)//2, y0-8, text=str(val),
                    font=("Segoe UI", 8), fill=FG2,
                )


if __name__ == "__main__":
    app = App()
    app.mainloop()