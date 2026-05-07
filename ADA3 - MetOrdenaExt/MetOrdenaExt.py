"""
Visualizador de Métodos de Ordenamiento Externo
1. Intercalación  2. Mezcla Directa  3. Mezcla Equilibrada
Compatible: Python 3.8+  |  Solo librería estándar (tkinter)
"""

import tkinter as tk
import random
import threading

# ══════ PALETA ══════
BG      = "#0d1117"
PANEL   = "#161b22"
BORDER  = "#30363d"
C_CMP   = "#58a6ff"
C_SWP   = "#f78166"
C_AUX   = "#d2a8ff"
C_DONE  = "#3fb950"
C_BAR   = "#21262d"
TXT_HI  = "#e6edf3"
TXT_LO  = "#8b949e"
BTN_BG  = "#21262d"
BTN_ACT = "#388bfd"
C_ERR   = "#f78166"

N_MIN, N_MAX = 2, 999999   # rango permitido


# ══════ ALGORITMOS ══════

def algo_intercalacion(arr):
    data, n, steps, size = arr[:], len(arr), [], 1
    while size < n:
        left = 0
        while left < n:
            mid   = min(left + size,     n)
            right = min(left + size * 2, n)
            i, j, merged = left, mid, []
            while i < mid and j < right:
                steps.append((data[:], [i, j], [], []))
                if data[i] <= data[j]:
                    merged.append(data[i]); i += 1
                else:
                    merged.append(data[j]); j += 1
            while i < mid:
                merged.append(data[i]); i += 1
            while j < right:
                merged.append(data[j]); j += 1
            for k, v in enumerate(merged):
                data[left + k] = v
                steps.append((data[:], [], [left + k], []))
            left += size * 2
        size *= 2
    steps.append((data[:], [], [], list(range(n)), True))
    return steps


def algo_mezcla_directa(arr):
    data, steps = arr[:], []

    def merge(lo, mid, hi):
        left, right = data[lo:mid+1], data[mid+1:hi+1]
        i = j = 0; k = lo
        while i < len(left) and j < len(right):
            steps.append((data[:], [lo+i, mid+1+j], [], []))
            if left[i] <= right[j]:
                data[k] = left[i]; i += 1
            else:
                data[k] = right[j]; j += 1
            steps.append((data[:], [], [k], [])); k += 1
        while i < len(left):
            data[k] = left[i]; i += 1; k += 1
            steps.append((data[:], [], [k-1], []))
        while j < len(right):
            data[k] = right[j]; j += 1; k += 1
            steps.append((data[:], [], [k-1], []))

    def sort(lo, hi):
        if lo >= hi: return
        mid = (lo + hi) // 2
        steps.append((data[:], [], [], list(range(lo, hi+1))))
        sort(lo, mid); sort(mid+1, hi); merge(lo, mid, hi)

    sort(0, len(data)-1)
    steps.append((data[:], [], [], list(range(len(data))), True))
    return steps


def algo_mezcla_equilibrada(arr):
    data, n, steps, size = arr[:], len(arr), [], 1
    while size < n:
        left = 0
        while left < n:
            mid   = min(left + size,     n)
            right = min(left + size * 2, n)
            rng   = list(range(left, right))
            i, j, merged = left, mid, []
            while i < mid and j < right:
                steps.append((data[:], [i, j], [], rng))
                if data[i] <= data[j]:
                    merged.append(data[i]); i += 1
                else:
                    merged.append(data[j]); j += 1
            while i < mid:
                merged.append(data[i]); i += 1
            while j < right:
                merged.append(data[j]); j += 1
            for k, v in enumerate(merged):
                data[left + k] = v
                steps.append((data[:], [], [left+k], rng))
            left += size * 2
        size *= 2
    steps.append((data[:], [], [], list(range(n)), True))
    return steps


# ══════ PANEL VISUALIZADOR ══════

class VisualizerPanel(tk.Frame):
    def __init__(self, master, desc, algo_func, get_n_func, **kw):
        super().__init__(master, bg=PANEL, **kw)
        self.algo_func = algo_func
        self.get_n     = get_n_func   # función que devuelve N actual
        self.arr       = []
        self.steps     = []
        self.idx       = 0
        self.running   = False
        self.speed_ms  = 60
        self._job      = None
        self._build(desc)
        self.generar()

    def _build(self, desc):
        tk.Label(self, text=desc, bg=PANEL, fg=TXT_LO,
                 font=("Courier New", 9), justify="left",
                 wraplength=860).pack(anchor="w", padx=12, pady=(8,0))

        self.canvas = tk.Canvas(self, bg=BG, height=210,
                                highlightthickness=1,
                                highlightbackground=BORDER)
        self.canvas.pack(fill="x", padx=10, pady=6)

        self.lbl_paso = tk.Label(self, text="Paso: 0 / 0",
                                 bg=PANEL, fg=TXT_LO,
                                 font=("Courier New", 10))
        self.lbl_paso.pack(anchor="e", padx=14)

        self.log = tk.Text(self, height=3, bg="#090e14", fg=TXT_LO,
                           font=("Courier New", 9), state="disabled",
                           relief="flat", insertbackground=TXT_HI)
        self.log.pack(fill="x", padx=10, pady=(0,6))

        ctrl = tk.Frame(self, bg=PANEL)
        ctrl.pack(fill="x", padx=10, pady=(0,10))

        def mkbtn(txt, cmd):
            b = tk.Button(ctrl, text=txt, command=cmd,
                          bg=BTN_BG, fg=TXT_HI,
                          activebackground=BTN_ACT,
                          activeforeground="#fff",
                          relief="flat", font=("Segoe UI", 10),
                          padx=10, pady=4, cursor="hand2",
                          bd=0, highlightthickness=0)
            b.pack(side="left", padx=3)
            return b

        mkbtn("⟳ Generar",  self.generar)
        self.btn_play = mkbtn("▶ Iniciar", self.toggle_play)
        mkbtn("⏭ Un Paso", self.un_paso)
        mkbtn("↺ Reset",   self.reset)

        tk.Label(ctrl, text="  Vel:", bg=PANEL, fg=TXT_LO,
                 font=("Segoe UI", 9)).pack(side="left")
        self.vel_var = tk.IntVar(value=50)
        tk.Scale(ctrl, from_=1, to=100, variable=self.vel_var,
                 orient="horizontal", length=100,
                 bg=PANEL, fg=TXT_LO, troughcolor=BORDER,
                 highlightthickness=0, showvalue=False,
                 command=self._vel).pack(side="left", padx=4)

        self.lbl_est = tk.Label(ctrl, text="● Listo",
                                bg=PANEL, fg=C_DONE,
                                font=("Segoe UI", 10))
        self.lbl_est.pack(side="right", padx=8)

    # ─── datos ────────────────────────────
    def generar(self):
        n = self.get_n()
        if n is None:
            return
        self.reset()
        self.arr = random.choices(range(1, n*10+1), k=n)
        self._log_clear()
        self._log(f"N={n}  Array: {self.arr}")
        self._draw(self.arr, [], [], [])
        self.lbl_est.config(text="● Listo", fg=C_DONE)

    def reset(self):
        self.running = False
        if self._job:
            self.after_cancel(self._job); self._job = None
        self.steps = []; self.idx = 0
        self.btn_play.config(text="▶ Iniciar")
        self.lbl_paso.config(text="Paso: 0 / 0")
        if self.arr:
            self._draw(self.arr, [], [], [])

    # ─── animación ────────────────────────
    def toggle_play(self):
        if self.running:
            self.running = False
            self.btn_play.config(text="▶ Continuar")
            self.lbl_est.config(text="● Pausado", fg=C_SWP)
        else:
            self.running = True
            self.btn_play.config(text="⏸ Pausar")
            if not self.steps:
                self.lbl_est.config(text="● Calculando…", fg=C_CMP)
                threading.Thread(target=self._calcular, daemon=True).start()
            else:
                self._animar()

    def _calcular(self):
        self.steps = self.algo_func(self.arr[:])
        self.idx = 0
        self.lbl_paso.config(text=f"Paso: 0 / {len(self.steps)}")
        self.lbl_est.config(text="● Animando", fg=C_CMP)
        if self.running:
            self._animar()

    def _animar(self):
        if not self.running or self.idx >= len(self.steps):
            self.running = False
            self.btn_play.config(text="▶ Iniciar")
            if self.steps and self.idx >= len(self.steps):
                self.lbl_est.config(text="✔ Completado", fg=C_DONE)
            return
        self._step(self.idx); self.idx += 1
        self._job = self.after(self.speed_ms, self._animar)

    def un_paso(self):
        if not self.steps:
            self.lbl_est.config(text="● Calculando…", fg=C_CMP)
            self.steps = self.algo_func(self.arr[:])
            self.idx = 0
            self.lbl_paso.config(text=f"Paso: 0 / {len(self.steps)}")
        if self.idx < len(self.steps):
            self._step(self.idx); self.idx += 1

    def _step(self, i):
        p    = self.steps[i]
        done = len(p) == 5 and p[4]
        arr, cmp, swp, aux = p[0], p[1], p[2], p[3]
        self._draw(arr, cmp, swp, aux, done)
        self.lbl_paso.config(text=f"Paso: {i+1} / {len(self.steps)}")
        if done:
            self._log(f"✔ Resultado: {arr}")
        elif cmp:
            vals = [arr[k] for k in cmp if k < len(arr)]
            self._log(f"  Comparando pos {cmp} → {vals}")

    def _vel(self, v):
        self.speed_ms = max(5, int(300 - (int(v)-1)*2.98))

    # ─── dibujo ───────────────────────────
    def _draw(self, arr, cmp, swp, aux, done=False):
        c = self.canvas; c.delete("all")
        W = c.winfo_width()  or 860
        H = c.winfo_height() or 210
        n = len(arr)
        if not n: return
        GAP   = 3
        bar_w = max(4, (W - GAP*(n+1)) // n)
        maxv  = max(arr) or 1
        PAD_B, PAD_T = 22, 10
        cs, ss, ax = set(cmp), set(swp), set(aux)

        for i, v in enumerate(arr):
            x1 = GAP + i*(bar_w+GAP); x2 = x1+bar_w
            bh = max(6, int((v/maxv)*(H-PAD_B-PAD_T)))
            y2 = H-PAD_B; y1 = y2-bh
            col = (C_DONE if done else
                   C_CMP  if i in cs else
                   C_SWP  if i in ss else
                   C_AUX  if i in ax else C_BAR)
            c.create_rectangle(x1, y1, x2, y2, fill=col, outline="")
            c.create_line(x1, y1, x2, y1, fill=self._light(col), width=2)
            if bar_w >= 16:
                c.create_text(x1+bar_w//2, y1-7, text=str(v),
                              fill=TXT_LO, font=("Courier New", 8))

        ley = [("Comparando",C_CMP),("Copiando",C_SWP),
               ("Aux/Cinta",C_AUX),("Ordenado",C_DONE)]
        lx = 8; ly = H-14
        for etq, col in ley:
            c.create_rectangle(lx, ly, lx+12, ly+10, fill=col, outline="")
            c.create_text(lx+16, ly+5, text=etq, anchor="w",
                          fill=TXT_LO, font=("Courier New", 8))
            lx += 100

    def _light(self, hx):
        try:
            r=min(255,int(hx[1:3],16)+45)
            g=min(255,int(hx[3:5],16)+45)
            b=min(255,int(hx[5:7],16)+45)
            return f"#{r:02x}{g:02x}{b:02x}"
        except: return hx

    def _log(self, msg):
        self.log.config(state="normal")
        self.log.insert("end", msg+"\n")
        self.log.see("end")
        self.log.config(state="disabled")

    def _log_clear(self):
        self.log.config(state="normal")
        self.log.delete("1.0","end")
        self.log.config(state="disabled")


# ══════ VENTANA PRINCIPAL ══════

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ordenamiento Externo — Visualizador")
        self.configure(bg=BG)
        self.geometry("960x870")
        self.minsize(760, 650)
        self._build()

    def _build(self):
        # Encabezado
        tk.Frame(self, bg=C_CMP, height=3).pack(fill="x")
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=18, pady=10)
        tk.Label(hdr, text="Métodos de Ordenamiento Externo",
                 font=("Segoe UI", 16, "bold"),
                 bg=BG, fg=TXT_HI).pack(side="left")
        tk.Label(hdr, text="Python · Tkinter · Estructuras de Datos",
                 font=("Courier New", 9),
                 bg=BG, fg=TXT_LO).pack(side="right", anchor="s")
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

        # ── Selector de N ──────────────────────────────
        n_frame = tk.Frame(self, bg=PANEL, pady=8)
        n_frame.pack(fill="x", padx=12, pady=(8, 4))

        tk.Label(n_frame,
                 text="Número de elementos:",
                 bg=PANEL, fg=TXT_HI,
                 font=("Segoe UI", 11, "bold")).pack(side="left", padx=(12,6))

        # Entry
        self.n_var = tk.StringVar(value="18")
        self.n_entry = tk.Entry(n_frame, textvariable=self.n_var,
                                width=5, bg="#0d1117", fg=TXT_HI,
                                font=("Courier New", 13, "bold"),
                                relief="flat", bd=4,
                                insertbackground=TXT_HI,
                                justify="center",
                                highlightthickness=2,
                                highlightbackground=BORDER,
                                highlightcolor=C_CMP)
        self.n_entry.pack(side="left", padx=4)

        tk.Label(n_frame,
                 text=f"(mín {N_MIN} elementos)",
                 bg=PANEL, fg=TXT_LO,
                 font=("Courier New", 9)).pack(side="left", padx=6)

        # Botones rápidos
        tk.Label(n_frame, text="  Rápido:",
                 bg=PANEL, fg=TXT_LO,
                 font=("Segoe UI", 9)).pack(side="left", padx=(16,2))

        for val in (10, 50, 100, 500, 1000):
            tk.Button(n_frame, text=str(val),
                      bg=BTN_BG, fg=TXT_LO,
                      activebackground=C_CMP,
                      activeforeground=BG,
                      relief="flat", font=("Courier New", 9, "bold"),
                      padx=7, pady=2, cursor="hand2",
                      bd=0, highlightthickness=0,
                      command=lambda v=val: self._set_n(v)
                      ).pack(side="left", padx=2)

        # Mensaje de error
        self.lbl_n_err = tk.Label(n_frame, text="",
                                  bg=PANEL, fg=C_ERR,
                                  font=("Courier New", 9))
        self.lbl_n_err.pack(side="left", padx=10)

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=12)

        # ── Barra de pestañas ──
        self.tab_bar = tk.Frame(self, bg=BG)
        self.tab_bar.pack(fill="x")

        self.contenido = tk.Frame(self, bg=BG)
        self.contenido.pack(fill="both", expand=True, padx=12, pady=8)

        datos = [
            (
                "1 · Intercalación",
                "INTERCALACIÓN (Straight Merging): fusiona bloques 1→2→4→8… en cada pasada. "
                "Simula ordenamiento en cintas/disco externo. O(n log n).",
                algo_intercalacion,
            ),
            (
                "2 · Mezcla Directa",
                "MEZCLA DIRECTA (Top-Down Merge Sort): divide recursivamente a la mitad "
                "y fusiona de vuelta. Azul=comparando, Rojo=copiando. O(n log n).",
                algo_mezcla_directa,
            ),
            (
                "3 · Mezcla Equilibrada",
                "MEZCLA EQUILIBRADA (Balanced Merge): 4 cintas virtuales (A,B→C,D). "
                "Distribuye y mezcla corridas equilibradamente. Lila=cinta auxiliar. O(n log n).",
                algo_mezcla_equilibrada,
            ),
        ]

        self.paneles  = []
        self.tab_btns = []

        for i, (titulo, desc, func) in enumerate(datos):
            panel = VisualizerPanel(self.contenido, desc, func,
                                    get_n_func=self.get_n)
            self.paneles.append(panel)

            btn = tk.Button(
                self.tab_bar, text=titulo,
                font=("Segoe UI", 10, "bold"),
                bg=BG, fg=TXT_LO,
                activebackground=PANEL,
                activeforeground=TXT_HI,
                relief="flat", padx=18, pady=8,
                cursor="hand2", bd=0,
                highlightthickness=0,
                command=lambda idx=i: self._tab(idx)
            )
            btn.pack(side="left")
            self.tab_btns.append(btn)

        tk.Frame(self.tab_bar, bg=BORDER, height=1).pack(
            side="bottom", fill="x")

        self._tab(0)

        # Pie
        pie = tk.Frame(self, bg=BORDER, height=24)
        pie.pack(fill="x", side="bottom")
        pie.pack_propagate(False)
        tk.Label(pie,
                 text="■ Comparando  ■ Copiando  ■ Aux/Cinta  ■ Ordenado  │  "
                      "Estructuras de Datos 2026",
                 font=("Courier New", 8),
                 bg=BORDER, fg=TXT_LO).pack(side="left", padx=10, pady=3)

    def _set_n(self, val):
        """Asigna N desde los botones rápidos y regenera."""
        self.n_var.set(str(val))
        self.lbl_n_err.config(text="")
        panel_activo = None
        for i, p in enumerate(self.paneles):
            if p.winfo_ismapped():
                panel_activo = p
                break
        if panel_activo:
            panel_activo.generar()

    def get_n(self):
        """Valida y devuelve el N actual. None si es inválido."""
        try:
            n = int(self.n_var.get())
        except ValueError:
            self.lbl_n_err.config(text=f"⚠ Escribe un número entero")
            self.n_entry.config(highlightbackground=C_ERR)
            return None

        if n < N_MIN:
            self.lbl_n_err.config(text=f"⚠ Mínimo {N_MIN}")
            self.n_entry.config(highlightbackground=C_ERR)
            return None

        self.lbl_n_err.config(text="")
        self.n_entry.config(highlightbackground=C_CMP)
        return n

    def _tab(self, idx):
        for p in self.paneles:
            p.pack_forget()
        for i, b in enumerate(self.tab_btns):
            if i == idx:
                b.config(bg=PANEL, fg=C_CMP,
                         highlightbackground=C_CMP,
                         highlightthickness=2)
            else:
                b.config(bg=BG, fg=TXT_LO, highlightthickness=0)
        self.paneles[idx].pack(fill="both", expand=True)


if __name__ == "__main__":
    App().mainloop()