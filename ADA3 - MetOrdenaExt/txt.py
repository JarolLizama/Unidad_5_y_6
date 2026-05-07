"""
Ordenamiento Externo con Archivos Reales
=========================================
Simula cintas magnéticas usando archivos .txt en disco.

Archivos generados en la carpeta  cintas/  junto al script:
  - datos.txt          → entrada original
  - cinta_A.txt        → cinta A
  - cinta_B.txt        → cinta B
  - cinta_C.txt        → cinta C  (mezcla equilibrada)
  - cinta_D.txt        → cinta D  (mezcla equilibrada)
  - resultado.txt      → salida ordenada final

Compatible: Python 3.8+  |  Solo tkinter (stdlib)
"""

import tkinter as tk
from tkinter import filedialog, scrolledtext
import random
import threading
import os
import time

# ══════ PALETA ══════
BG      = "#0a0d12"
PANEL   = "#111720"
PANEL2  = "#161d2a"
BORDER  = "#1e2d40"
C_CMP   = "#00d4ff"    # cian  – comparando
C_SWP   = "#ff6b6b"    # rojo  – escribiendo
C_AUX   = "#a78bfa"    # lila  – cinta auxiliar
C_DONE  = "#22c55e"    # verde – completado
C_BAR   = "#1e2d40"    # barra normal
C_READ  = "#f59e0b"    # naranja – leyendo archivo
TXT_HI  = "#e2e8f0"
TXT_LO  = "#64748b"
TXT_MID = "#94a3b8"
BTN_BG  = "#1e2d40"
BTN_HOV = "#00d4ff"
C_ERR   = "#ff6b6b"
C_WARN  = "#f59e0b"

CINTA_COLORES = {
    "A": "#00d4ff",
    "B": "#a78bfa",
    "C": "#22c55e",
    "D": "#f59e0b",
}

# ══════ UTILIDADES DE ARCHIVO ══════

def carpeta_cintas():
    """Devuelve la ruta de la carpeta 'cintas/' junto al script."""
    base = os.path.dirname(os.path.abspath(__file__))
    ruta = os.path.join(base, "cintas")
    os.makedirs(ruta, exist_ok=True)
    return ruta

def ruta(nombre):
    return os.path.join(carpeta_cintas(), nombre)

def escribir_cinta(nombre, numeros):
    """Escribe lista de enteros en archivo, uno por línea."""
    with open(ruta(nombre), "w") as f:
        for n in numeros:
            f.write(f"{n}\n")

def leer_cinta(nombre):
    """Lee archivo y devuelve lista de enteros."""
    path = ruta(nombre)
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        lineas = f.read().strip().split("\n")
    return [int(x) for x in lineas if x.strip()]

def tamanio_cinta(nombre):
    path = ruta(nombre)
    if not os.path.exists(path):
        return 0
    return os.path.getsize(path)


# ══════ ALGORITMOS CON ARCHIVOS ══════

class AlgoritmoBase:
    """Clase base: ejecuta el algoritmo y emite eventos al log/UI."""

    def __init__(self, log_cb, barra_cb, cinta_cb, fin_cb, pausa_fn):
        self.log   = log_cb    # log_cb(msg, color)
        self.barra = barra_cb  # barra_cb(arr, highlights)
        self.cinta = cinta_cb  # cinta_cb(dict nombre→contenido)
        self.fin   = fin_cb    # fin_cb(resultado_list)
        self.pausa = pausa_fn  # pausa_fn() → bloquea si pausado
        self._stop = False

    def detener(self):
        self._stop = True

    def _chk(self):
        if self._stop:
            raise InterruptedError
        self.pausa()

    def _mostrar_cintas(self, *nombres):
        d = {}
        for n in nombres:
            d[n] = leer_cinta(n)
        self.cinta(d)


class Intercalacion(AlgoritmoBase):
    """
    Straight Merging con archivos:
    datos.txt → cinta_A.txt + cinta_B.txt → fusión → cinta_A.txt → …
    """
    def ejecutar(self, n_elem, delay):
        self.log("═" * 50, TXT_LO)
        self.log("INTERCALACIÓN CON ARCHIVOS", C_CMP)
        self.log("═" * 50, TXT_LO)

        # Generar datos
        datos = random.choices(range(1, n_elem * 10 + 1), k=n_elem)
        escribir_cinta("datos.txt", datos)
        self.log(f"✦ datos.txt generado ({n_elem} elementos)", C_READ)
        self._mostrar_cintas("datos.txt")
        self.barra(datos, {})
        time.sleep(delay)
        self._chk()

        data = datos[:]
        size = 1
        n    = len(data)
        paso = 0

        while size < n:
            self._chk()
            paso += 1
            self.log(f"\n── Pasada {paso} (bloque={size}) ──", TXT_MID)

            # Distribuir en cinta_A y cinta_B
            cA, cB = [], []
            i = 0
            toggle = True
            while i < n:
                bloque = data[i:i+size]
                if toggle:
                    cA.extend(bloque)
                else:
                    cB.extend(bloque)
                toggle = not toggle
                i += size

            escribir_cinta("cinta_A.txt", cA)
            escribir_cinta("cinta_B.txt", cB)
            self.log(f"  → cinta_A.txt ({len(cA)} nums) | cinta_B.txt ({len(cB)} nums)", C_AUX)
            self._mostrar_cintas("cinta_A.txt", "cinta_B.txt")
            time.sleep(delay)
            self._chk()

            # Mezclar cinta_A + cinta_B → data
            resultado = []
            left = 0
            while left < n:
                mid   = min(left + size,     n)
                right = min(left + size * 2, n)
                i2, j = left, mid
                while i2 < mid and j < right:
                    self._chk()
                    hi = {i2: C_CMP, j: C_CMP}
                    self.barra(data, hi)
                    time.sleep(delay * 0.3)
                    if data[i2] <= data[j]:
                        resultado.append(data[i2]); i2 += 1
                    else:
                        resultado.append(data[j]);  j  += 1
                while i2 < mid:
                    resultado.append(data[i2]); i2 += 1
                while j < right:
                    resultado.append(data[j]);  j  += 1
                left += size * 2

            data = resultado
            escribir_cinta("datos.txt", data)
            self.log(f"  ✔ fusión → datos.txt actualizado", C_DONE)
            self.barra(data, {})
            self._mostrar_cintas("datos.txt")
            time.sleep(delay)
            size *= 2

        escribir_cinta("resultado.txt", data)
        self.log("\n✔ ORDENADO → resultado.txt", C_DONE)
        self._mostrar_cintas("resultado.txt")
        self.fin(data)


class MezclaDirecta(AlgoritmoBase):
    """
    Top-Down Merge Sort con archivos:
    Usa entrada.txt, temp1.txt, temp2.txt como buffers de trabajo.
    """
    def ejecutar(self, n_elem, delay):
        self.log("═" * 50, TXT_LO)
        self.log("MEZCLA DIRECTA CON ARCHIVOS", C_CMP)
        self.log("═" * 50, TXT_LO)

        datos = random.choices(range(1, n_elem * 10 + 1), k=n_elem)
        escribir_cinta("entrada.txt", datos)
        self.log(f"✦ entrada.txt generado ({n_elem} elementos)", C_READ)
        self._mostrar_cintas("entrada.txt")
        self.barra(datos, {})
        time.sleep(delay)
        self._chk()

        data  = datos[:]
        steps = []

        # Generar pasos con merge sort
        def merge(lo, mid, hi):
            left  = data[lo:mid+1]
            right = data[mid+1:hi+1]
            i = j = 0; k = lo
            while i < len(left) and j < len(right):
                if left[i] <= right[j]:
                    data[k] = left[i]; i += 1
                else:
                    data[k] = right[j]; j += 1
                steps.append(("merge", data[:], lo, mid, hi, k))
                k += 1
            while i < len(left):
                data[k] = left[i]; i += 1; k += 1
                steps.append(("merge", data[:], lo, mid, hi, k-1))
            while j < len(right):
                data[k] = right[j]; j += 1; k += 1
                steps.append(("merge", data[:], lo, mid, hi, k-1))

        def sort(lo, hi, nivel=0):
            if lo >= hi: return
            mid = (lo + hi) // 2
            steps.append(("div", data[:], lo, mid, hi, nivel))
            sort(lo, mid, nivel+1)
            sort(mid+1, hi, nivel+1)
            merge(lo, mid, hi)
            steps.append(("merged", data[:], lo, mid, hi, nivel))

        sort(0, len(data)-1)

        paso_div = 0
        for ev, arr_snap, lo, mid, hi, extra in steps:
            self._chk()
            if ev == "div":
                paso_div += 1
                # Escribir mitades en temp files
                left_part  = arr_snap[lo:mid+1]
                right_part = arr_snap[mid+1:hi+1]
                escribir_cinta("temp1.txt", left_part)
                escribir_cinta("temp2.txt", right_part)
                hi_dict = {k: C_AUX for k in range(lo, hi+1)}
                self.barra(arr_snap, hi_dict)
                self.log(f"  División [{lo}..{mid}] y [{mid+1}..{hi}] → temp1/2.txt", C_AUX)
                self._mostrar_cintas("temp1.txt", "temp2.txt")
                time.sleep(delay * 0.5)
            elif ev == "merge":
                k_pos = extra
                hi_dict = {k_pos: C_SWP, lo: C_CMP, hi: C_CMP}
                self.barra(arr_snap, hi_dict)
                time.sleep(delay * 0.2)
                escribir_cinta("entrada.txt", arr_snap)
            elif ev == "merged":
                hi_dict = {k: C_DONE for k in range(lo, hi+1)}
                self.barra(arr_snap, hi_dict)
                self.log(f"  ✔ Fusión [{lo}..{hi}] → entrada.txt", C_DONE)
                self._mostrar_cintas("entrada.txt")
                time.sleep(delay * 0.4)

        escribir_cinta("resultado.txt", data)
        self.log("\n✔ ORDENADO → resultado.txt", C_DONE)
        self._mostrar_cintas("resultado.txt")
        self.fin(data)


class MezclaEquilibrada(AlgoritmoBase):
    """
    Balanced Merge con 4 cintas reales:
    cinta_A + cinta_B → cinta_C + cinta_D → cinta_A + cinta_B → …
    """
    def ejecutar(self, n_elem, delay):
        self.log("═" * 50, TXT_LO)
        self.log("MEZCLA EQUILIBRADA CON ARCHIVOS (4 cintas)", C_CMP)
        self.log("═" * 50, TXT_LO)

        datos = random.choices(range(1, n_elem * 10 + 1), k=n_elem)
        escribir_cinta("datos.txt", datos)
        self.log(f"✦ datos.txt generado ({n_elem} elementos)", C_READ)

        # Distribución inicial: datos → cinta_A y cinta_B alternando
        cA, cB = [], []
        for idx, v in enumerate(datos):
            (cA if idx % 2 == 0 else cB).append(v)

        escribir_cinta("cinta_A.txt", cA)
        escribir_cinta("cinta_B.txt", cB)
        self.log(f"✦ Distribución inicial:", C_AUX)
        self.log(f"   cinta_A.txt → {len(cA)} elementos", CINTA_COLORES["A"])
        self.log(f"   cinta_B.txt → {len(cB)} elementos", CINTA_COLORES["B"])
        self._mostrar_cintas("cinta_A.txt", "cinta_B.txt")
        self.barra(datos, {})
        time.sleep(delay)
        self._chk()

        data = datos[:]
        n    = len(data)
        size = 1
        pasada = 0
        # Alternar entre (A,B→C,D) y (C,D→A,B)
        pares = [("cinta_A.txt","cinta_B.txt","cinta_C.txt","cinta_D.txt"),
                 ("cinta_C.txt","cinta_D.txt","cinta_A.txt","cinta_B.txt")]

        while size < n:
            self._chk()
            ent1, ent2, sal1, sal2 = pares[pasada % 2]
            pasada += 1
            self.log(f"\n── Pasada {pasada} (bloque={size})", TXT_MID)
            self.log(f"   Leyendo : {ent1} + {ent2}", C_READ)
            self.log(f"   Escribiendo: {sal1} + {sal2}", C_SWP)

            inp1 = leer_cinta(ent1)
            inp2 = leer_cinta(ent2)

            # Reconstruir data combinando ambas cintas en orden de bloques
            data_ent = []
            i1 = i2 = 0
            toggle = True
            while i1 < len(inp1) or i2 < len(inp2):
                if toggle and i1 < len(inp1):
                    data_ent.extend(inp1[i1:i1+size]); i1 += size
                elif not toggle and i2 < len(inp2):
                    data_ent.extend(inp2[i2:i2+size]); i2 += size
                else:
                    if i1 < len(inp1):
                        data_ent.extend(inp1[i1:i1+size]); i1 += size
                    elif i2 < len(inp2):
                        data_ent.extend(inp2[i2:i2+size]); i2 += size
                toggle = not toggle

            # Mezclar bloques y distribuir en sal1/sal2
            out1, out2 = [], []
            left = 0
            t2 = True
            while left < len(data_ent):
                mid2  = min(left + size,     len(data_ent))
                right = min(left + size * 2, len(data_ent))
                ia, jb = left, mid2
                merged = []
                while ia < mid2 and jb < right:
                    self._chk()
                    hi_d = {ia: C_CMP, jb: C_CMP}
                    self.barra(data_ent, hi_d)
                    time.sleep(delay * 0.15)
                    if data_ent[ia] <= data_ent[jb]:
                        merged.append(data_ent[ia]); ia += 1
                    else:
                        merged.append(data_ent[jb]); jb += 1
                while ia < mid2:
                    merged.append(data_ent[ia]); ia += 1
                while jb < right:
                    merged.append(data_ent[jb]); jb += 1

                if t2:
                    out1.extend(merged)
                else:
                    out2.extend(merged)
                t2 = not t2
                left += size * 2

            data_ent = out1 + out2
            # Reordenar intercalando bloques
            resultado = []
            i1 = i2 = 0
            tog = True
            while i1 < len(out1) or i2 < len(out2):
                bs = size * 2
                if tog and i1 < len(out1):
                    resultado.extend(out1[i1:i1+bs]); i1 += bs
                elif not tog and i2 < len(out2):
                    resultado.extend(out2[i2:i2+bs]); i2 += bs
                else:
                    if i1 < len(out1):
                        resultado.extend(out1[i1:i1+bs]); i1 += bs
                    elif i2 < len(out2):
                        resultado.extend(out2[i2:i2+bs]); i2 += bs
                tog = not tog
            data = resultado if resultado else out1 + out2

            escribir_cinta(sal1, out1)
            escribir_cinta(sal2, out2)
            self.log(f"   {sal1}: {len(out1)} nums | {sal2}: {len(out2)} nums", C_DONE)
            self._mostrar_cintas(sal1, sal2)
            self.barra(data, {})
            time.sleep(delay)
            size *= 2

        # El resultado queda en la última cinta de salida
        ult_sal1 = pares[(pasada-1) % 2][2]
        ult_sal2 = pares[(pasada-1) % 2][3]
        final    = leer_cinta(ult_sal1) + leer_cinta(ult_sal2)
        # Ordenar final (última fusión puede necesitar merge)
        final.sort()
        escribir_cinta("resultado.txt", final)
        self.log("\n✔ ORDENADO → resultado.txt", C_DONE)
        self._mostrar_cintas("resultado.txt")
        self.barra(final, {i: C_DONE for i in range(len(final))})
        self.fin(final)


# ══════ WIDGET: TARJETA DE CINTA ══════

class TarjetaCinta(tk.Frame):
    def __init__(self, master, nombre, color, **kw):
        super().__init__(master, bg=PANEL2, highlightthickness=1,
                         highlightbackground=color, **kw)
        self.color  = color
        self.nombre = nombre

        tk.Label(self, text=f"📼 {nombre}", bg=PANEL2,
                 fg=color, font=("Courier New", 9, "bold")).pack(
                     anchor="w", padx=6, pady=(4,0))

        self.lbl_info = tk.Label(self, text="vacía",
                                 bg=PANEL2, fg=TXT_LO,
                                 font=("Courier New", 8))
        self.lbl_info.pack(anchor="w", padx=6)

        self.txt = tk.Text(self, height=3, bg="#080c10", fg=color,
                           font=("Courier New", 8), state="disabled",
                           relief="flat", bd=0, wrap="word")
        self.txt.pack(fill="x", padx=4, pady=(2,4))

    def actualizar(self, datos):
        n = len(datos)
        kb = tamanio_cinta(self.nombre) / 1024
        self.lbl_info.config(text=f"{n} elementos · {kb:.1f} KB")
        self.txt.config(state="normal")
        self.txt.delete("1.0", "end")
        preview = datos[:40]
        txt = " ".join(str(x) for x in preview)
        if len(datos) > 40:
            txt += f"  … (+{len(datos)-40} más)"
        self.txt.insert("end", txt)
        self.txt.config(state="disabled")

    def limpiar(self):
        self.lbl_info.config(text="vacía")
        self.txt.config(state="normal")
        self.txt.delete("1.0", "end")
        self.txt.config(state="disabled")


# ══════ WIDGET: VISUALIZADOR DE BARRAS ══════

class BarrasCanvas(tk.Canvas):
    def __init__(self, master, **kw):
        super().__init__(master, bg=BG, height=160,
                         highlightthickness=1,
                         highlightbackground=BORDER, **kw)
        self._arr = []
        self._hi  = {}

    def dibujar(self, arr, highlights=None):
        self._arr = arr
        self._hi  = highlights or {}
        self.delete("all")
        W = self.winfo_width()  or 800
        H = self.winfo_height() or 160
        n = len(arr)
        if not n: return
        GAP   = 2
        bar_w = max(2, (W - GAP*(n+1)) // n)
        maxv  = max(arr) or 1
        PAD_B = 18

        for i, v in enumerate(arr):
            x1 = GAP + i*(bar_w+GAP); x2 = x1+bar_w
            bh = max(3, int((v/maxv)*(H-PAD_B-8)))
            y2 = H-PAD_B; y1 = y2-bh
            col = self._hi.get(i, C_BAR)
            self.create_rectangle(x1, y1, x2, y2, fill=col, outline="")
            if bar_w >= 14:
                self.create_text(x1+bar_w//2, y1-6, text=str(v),
                                 fill=TXT_LO, font=("Courier New", 7))

        # leyenda
        ley = [("Comparando",C_CMP),("Escribiendo",C_SWP),
               ("Cinta aux",C_AUX),("Ordenado",C_DONE),("Leyendo",C_READ)]
        lx = 6; ly = H-13
        for etq, col in ley:
            self.create_rectangle(lx, ly, lx+10, ly+9, fill=col, outline="")
            self.create_text(lx+14, ly+4, text=etq, anchor="w",
                             fill=TXT_LO, font=("Courier New", 7))
            lx += 88


# ══════ VENTANA PRINCIPAL ══════

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ordenamiento Externo con Archivos — Visualizador")
        self.configure(bg=BG)
        self.geometry("1000x900")
        self.minsize(800, 700)
        self.resizable(True, True)

        self._algo     = None
        self._thread   = None
        self._pausado  = threading.Event()
        self._pausado.set()   # set = no pausado
        self._delay    = 0.3

        self._build()

    # ══ UI ══════════════════════════════════

    def _build(self):
        # Franja superior
        tk.Frame(self, bg=C_CMP, height=3).pack(fill="x")

        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=16, pady=10)
        tk.Label(hdr, text="Ordenamiento Externo con Archivos",
                 font=("Segoe UI", 15, "bold"),
                 bg=BG, fg=TXT_HI).pack(side="left")
        tk.Label(hdr, text="cintas/  →  resultado.txt",
                 font=("Courier New", 9),
                 bg=BG, fg=TXT_LO).pack(side="right", anchor="s")
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")

        # ── Fila de configuración ──
        cfg = tk.Frame(self, bg=PANEL, pady=8)
        cfg.pack(fill="x", padx=12, pady=(8,4))

        # N elementos
        tk.Label(cfg, text="Elementos:", bg=PANEL, fg=TXT_HI,
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=(10,4))
        self.n_var = tk.StringVar(value="20")
        tk.Entry(cfg, textvariable=self.n_var, width=7,
                 bg="#0a0d12", fg=C_CMP,
                 font=("Courier New", 12, "bold"),
                 relief="flat", bd=4, justify="center",
                 insertbackground=C_CMP,
                 highlightthickness=2,
                 highlightbackground=BORDER,
                 highlightcolor=C_CMP).pack(side="left", padx=4)

        for v in (10, 50, 100, 500, 1000, 5000):
            tk.Button(cfg, text=str(v), bg=BTN_BG, fg=TXT_LO,
                      activebackground=C_CMP, activeforeground=BG,
                      relief="flat", font=("Courier New", 8, "bold"),
                      padx=6, pady=2, cursor="hand2", bd=0,
                      command=lambda x=v: self.n_var.set(str(x))
                      ).pack(side="left", padx=2)

        tk.Frame(cfg, bg=BORDER, width=1, height=28).pack(side="left", padx=10)

        # Velocidad
        tk.Label(cfg, text="Velocidad:", bg=PANEL, fg=TXT_HI,
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=(4,4))
        self.vel_var = tk.IntVar(value=50)
        tk.Scale(cfg, from_=1, to=100, variable=self.vel_var,
                 orient="horizontal", length=110,
                 bg=PANEL, fg=TXT_LO, troughcolor=BORDER,
                 highlightthickness=0, showvalue=False,
                 command=self._vel_changed).pack(side="left", padx=4)

        # Cargar archivo propio
        tk.Frame(cfg, bg=BORDER, width=1, height=28).pack(side="left", padx=10)
        tk.Button(cfg, text="📂 Cargar .txt",
                  bg=BTN_BG, fg=C_READ,
                  activebackground=C_READ, activeforeground=BG,
                  relief="flat", font=("Segoe UI", 9),
                  padx=8, pady=3, cursor="hand2", bd=0,
                  command=self._cargar_archivo).pack(side="left", padx=4)

        self.lbl_archivo = tk.Label(cfg, text="(sin archivo cargado)",
                                    bg=PANEL, fg=TXT_LO,
                                    font=("Courier New", 8))
        self.lbl_archivo.pack(side="left", padx=4)

        self._datos_externos = None

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=12)

        # ── Botones de algoritmo ──
        alg_frame = tk.Frame(self, bg=BG)
        alg_frame.pack(fill="x", padx=12, pady=8)

        algos = [
            ("🔀 Intercalación",    Intercalacion,     C_CMP),
            ("⚡ Mezcla Directa",   MezclaDirecta,     C_AUX),
            ("⚖️ Mezcla Equilibrada", MezclaEquilibrada, C_DONE),
        ]
        self._algo_cls = None
        self._algo_btns = []
        for txt, cls, col in algos:
            b = tk.Button(alg_frame, text=txt,
                          bg=PANEL2, fg=col,
                          activebackground=col, activeforeground=BG,
                          relief="flat", font=("Segoe UI", 10, "bold"),
                          padx=14, pady=7, cursor="hand2", bd=0,
                          highlightthickness=2,
                          highlightbackground=BORDER,
                          command=lambda c=cls, bt=None, cl=col: self._sel_algo(c, cl))
            b.pack(side="left", padx=6)
            b.config(command=lambda c=cls, cl=col, btn=b: self._sel_algo(c, cl, btn))
            self._algo_btns.append((b, cls, col))

        tk.Frame(alg_frame, bg=BORDER, width=1).pack(side="left", padx=10, fill="y")

        self.btn_run   = tk.Button(alg_frame, text="▶ EJECUTAR",
                                   bg=C_DONE, fg=BG,
                                   activebackground="#16a34a",
                                   activeforeground=BG,
                                   relief="flat",
                                   font=("Segoe UI", 10, "bold"),
                                   padx=14, pady=7, cursor="hand2", bd=0,
                                   state="disabled",
                                   command=self._ejecutar)
        self.btn_run.pack(side="left", padx=4)

        self.btn_pause = tk.Button(alg_frame, text="⏸ Pausar",
                                   bg=BTN_BG, fg=TXT_LO,
                                   activebackground=C_WARN,
                                   activeforeground=BG,
                                   relief="flat",
                                   font=("Segoe UI", 10),
                                   padx=10, pady=7, cursor="hand2", bd=0,
                                   state="disabled",
                                   command=self._pausar)
        self.btn_pause.pack(side="left", padx=4)

        self.btn_stop  = tk.Button(alg_frame, text="■ Detener",
                                   bg=BTN_BG, fg=TXT_LO,
                                   activebackground=C_ERR,
                                   activeforeground=BG,
                                   relief="flat",
                                   font=("Segoe UI", 10),
                                   padx=10, pady=7, cursor="hand2", bd=0,
                                   state="disabled",
                                   command=self._detener)
        self.btn_stop.pack(side="left", padx=4)

        self.lbl_estado = tk.Label(alg_frame, text="● Selecciona un algoritmo",
                                   bg=BG, fg=TXT_LO,
                                   font=("Segoe UI", 9))
        self.lbl_estado.pack(side="right", padx=10)

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=12)

        # ── Visualización de barras ──
        self.barras = BarrasCanvas(self)
        self.barras.pack(fill="x", padx=12, pady=8)

        # ── Cintas (tarjetas) ──
        cintas_frame = tk.Frame(self, bg=BG)
        cintas_frame.pack(fill="x", padx=12, pady=(0,6))

        tk.Label(cintas_frame, text="Estado de cintas / archivos:",
                 bg=BG, fg=TXT_MID,
                 font=("Courier New", 9, "bold")).pack(anchor="w", pady=(0,4))

        self._tarjetas = {}
        grid = tk.Frame(cintas_frame, bg=BG)
        grid.pack(fill="x")

        cintas_def = [
            ("datos.txt",    "#64748b"),
            ("cinta_A.txt",  CINTA_COLORES["A"]),
            ("cinta_B.txt",  CINTA_COLORES["B"]),
            ("cinta_C.txt",  CINTA_COLORES["C"]),
            ("cinta_D.txt",  CINTA_COLORES["D"]),
            ("resultado.txt","#22c55e"),
        ]
        for col_idx, (nombre, color) in enumerate(cintas_def):
            t = TarjetaCinta(grid, nombre, color)
            t.grid(row=0, column=col_idx, sticky="nsew", padx=3, pady=2)
            grid.columnconfigure(col_idx, weight=1)
            self._tarjetas[nombre] = t

        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=12)

        # ── Log ──
        log_frame = tk.Frame(self, bg=BG)
        log_frame.pack(fill="both", expand=True, padx=12, pady=6)

        lh = tk.Frame(log_frame, bg=BG)
        lh.pack(fill="x")
        tk.Label(lh, text="Log de operaciones:", bg=BG, fg=TXT_MID,
                 font=("Courier New", 9, "bold")).pack(side="left")
        tk.Button(lh, text="🗑 Limpiar", bg=BTN_BG, fg=TXT_LO,
                  relief="flat", font=("Courier New", 8),
                  padx=6, pady=2, cursor="hand2", bd=0,
                  command=self._limpiar_log).pack(side="right")

        self.log_txt = scrolledtext.ScrolledText(
            log_frame, height=9,
            bg="#060a0f", fg=TXT_MID,
            font=("Courier New", 9),
            state="disabled", relief="flat",
            insertbackground=TXT_HI)
        self.log_txt.pack(fill="both", expand=True, pady=4)

        # Tags de color para el log
        for tag, color in [("cian",C_CMP),("lila",C_AUX),("verde",C_DONE),
                            ("rojo",C_ERR),("naranja",C_READ),("gris",TXT_LO),
                            ("blanco",TXT_HI),("mid",TXT_MID)]:
            self.log_txt.tag_config(tag, foreground=color)

        # Pie
        pie = tk.Frame(self, bg=BORDER, height=22)
        pie.pack(fill="x", side="bottom")
        pie.pack_propagate(False)
        self.lbl_ruta = tk.Label(pie,
                                  text=f"Carpeta cintas: {carpeta_cintas()}",
                                  font=("Courier New", 8),
                                  bg=BORDER, fg=TXT_LO)
        self.lbl_ruta.pack(side="left", padx=10, pady=2)

    # ══ LÓGICA ══════════════════════════════

    def _vel_changed(self, v):
        val = int(v)
        # 1→1.5s  50→0.3s  100→0.02s
        self._delay = max(0.02, 1.5 - (val-1)/99 * 1.48)

    def _sel_algo(self, cls, color, btn=None):
        self._algo_cls = cls
        for b, c, col in self._algo_btns:
            b.config(highlightbackground=BORDER, bg=PANEL2)
        if btn:
            btn.config(highlightbackground=color, bg="#1a2535")
        self.btn_run.config(state="normal")
        self.lbl_estado.config(text=f"● {cls.__name__} seleccionada", fg=color)

    def _cargar_archivo(self):
        path = filedialog.askopenfilename(
            title="Seleccionar archivo de datos",
            filetypes=[("Texto", "*.txt"), ("Todos", "*.*")]
        )
        if not path:
            return
        try:
            with open(path) as f:
                contenido = f.read()
            nums = []
            for tok in contenido.replace(",", " ").replace(";", " ").split():
                try:
                    nums.append(int(tok))
                except ValueError:
                    pass
            if not nums:
                self._log("⚠ No se encontraron números en el archivo", C_ERR)
                return
            self._datos_externos = nums
            self.n_var.set(str(len(nums)))
            nombre = os.path.basename(path)
            self.lbl_archivo.config(text=f"✔ {nombre} ({len(nums)} nums)",
                                     fg=C_DONE)
            self._log(f"✦ Archivo cargado: {nombre} — {len(nums)} números", C_READ)
        except Exception as e:
            self._log(f"⚠ Error al cargar: {e}", C_ERR)

    def _ejecutar(self):
        if self._thread and self._thread.is_alive():
            return
        try:
            n = int(self.n_var.get())
            if n < 2:
                self._log("⚠ Mínimo 2 elementos", C_ERR); return
        except ValueError:
            self._log("⚠ Número inválido", C_ERR); return

        # Limpiar tarjetas
        for t in self._tarjetas.values():
            t.limpiar()
        self.barras.dibujar([])

        self._pausado.set()
        self.btn_run.config(state="disabled")
        self.btn_pause.config(state="normal")
        self.btn_stop.config(state="normal")
        self.btn_pause.config(text="⏸ Pausar")

        algo = self._algo_cls(
            log_cb   = self._log,
            barra_cb = self._cb_barra,
            cinta_cb = self._cb_cinta,
            fin_cb   = self._cb_fin,
            pausa_fn = self._pausado.wait
        )
        self._algo = algo

        # Si hay datos externos los usamos
        def _run():
            try:
                if self._datos_externos and len(self._datos_externos) == n:
                    # Usar datos del archivo cargado
                    datos_orig = self._datos_externos[:]
                    escribir_cinta("datos.txt", datos_orig)
                algo.ejecutar(n, self._delay)
            except InterruptedError:
                self._log("\n■ Detenido por el usuario.", C_ERR)
                self.btn_run.config(state="normal")
                self.btn_pause.config(state="disabled")
                self.btn_stop.config(state="disabled")
            except Exception as e:
                self._log(f"\n⚠ Error: {e}", C_ERR)
                self.btn_run.config(state="normal")
                self.btn_pause.config(state="disabled")
                self.btn_stop.config(state="disabled")

        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()

    def _pausar(self):
        if self._pausado.is_set():
            self._pausado.clear()
            self.btn_pause.config(text="▶ Continuar")
            self.lbl_estado.config(text="● Pausado", fg=C_WARN)
        else:
            self._pausado.set()
            self.btn_pause.config(text="⏸ Pausar")
            self.lbl_estado.config(text="● Ejecutando…", fg=C_CMP)

    def _detener(self):
        if self._algo:
            self._pausado.set()   # desbloquear si estaba pausado
            self._algo.detener()
        self.btn_run.config(state="normal")
        self.btn_pause.config(state="disabled", text="⏸ Pausar")
        self.btn_stop.config(state="disabled")

    # ── Callbacks desde hilos ──
    def _log(self, msg, color=None):
        tag = {
            C_CMP: "cian", C_AUX: "lila", C_DONE: "verde",
            C_ERR: "rojo", C_READ: "naranja", TXT_LO: "gris",
            TXT_HI: "blanco", TXT_MID: "mid", C_SWP: "rojo",
            C_WARN: "naranja",
        }.get(color, "mid")
        def _do():
            self.log_txt.config(state="normal")
            self.log_txt.insert("end", msg + "\n", tag)
            self.log_txt.see("end")
            self.log_txt.config(state="disabled")
        self.after(0, _do)

    def _cb_barra(self, arr, hi):
        self.after(0, lambda: self.barras.dibujar(arr, hi))

    def _cb_cinta(self, cintas_dict):
        def _do():
            for nombre, datos in cintas_dict.items():
                if nombre in self._tarjetas:
                    self._tarjetas[nombre].actualizar(datos)
        self.after(0, _do)

    def _cb_fin(self, resultado):
        def _do():
            self.lbl_estado.config(text="✔ Completado", fg=C_DONE)
            self.btn_run.config(state="normal")
            self.btn_pause.config(state="disabled", text="⏸ Pausar")
            self.btn_stop.config(state="disabled")
            self.barras.dibujar(resultado,
                                {i: C_DONE for i in range(len(resultado))})
            self._log(f"✔ resultado.txt escrito — {len(resultado)} elementos ordenados",
                      C_DONE)
            self._log(f"   Ruta: {ruta('resultado.txt')}", TXT_LO)
        self.after(0, _do)

    def _limpiar_log(self):
        self.log_txt.config(state="normal")
        self.log_txt.delete("1.0", "end")
        self.log_txt.config(state="disabled")


if __name__ == "__main__":
    App().mainloop()