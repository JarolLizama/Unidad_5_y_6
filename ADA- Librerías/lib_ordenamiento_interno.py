"""
╔══════════════════════════════════════════════════════════════════╗
║         lib_ordenamiento_interno.py                             ║
║  Librería de Métodos de Ordenamiento Interno                    ║
║                                                                  ║
║  Métodos incluidos:                                              ║
║    1. Burbuja      (Bubble Sort)                                ║
║    2. Inserción    (Insertion Sort)                             ║
║    3. Selección    (Selection Sort)                             ║
║    4. Shell Sort                                                 ║
║    5. Quick Sort                                                 ║
║    6. Merge Sort                                                 ║
║    7. Heap Sort                                                  ║
║                                                                  ║
║  Cada algoritmo es un generador que produce pasos:             ║
║    yield (array_snapshot, highlights_dict, mensaje)            ║
╚══════════════════════════════════════════════════════════════════╝
"""

import random

METODOS_INTERNOS = [
    "Burbuja",
    "Inserción",
    "Selección",
    "Shell Sort",
    "Quick Sort",
    "Merge Sort",
    "Heap Sort",
]

# Colores semánticos
C_CMP  = "#00d4ff"   # comparando
C_SWP  = "#ff6b6b"   # intercambiando
C_AUX  = "#a78bfa"   # auxiliar / pivote
C_DONE = "#22c55e"   # ordenado
C_READ = "#f59e0b"   # lectura


def generar_datos(n, min_val=1, max_val=None):
    if max_val is None:
        max_val = n * 10
    return random.choices(range(min_val, max_val + 1), k=n)


# ══════════════════════════════════════════════════════════════════
#  1. BURBUJA
# ══════════════════════════════════════════════════════════════════

def burbuja(arr):
    """
    Burbuja (Bubble Sort).
    Complejidad: O(n²) promedio y peor caso, O(n) mejor caso.
    """
    a = arr[:]
    n = len(a)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            hi = {j: C_CMP, j + 1: C_CMP}
            hi.update({k: C_DONE for k in range(n - i, n)})
            yield a[:], hi, f"Comparando a[{j}]={a[j]} con a[{j+1}]={a[j+1]}"
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
                hi2 = {j: C_SWP, j + 1: C_SWP}
                hi2.update({k: C_DONE for k in range(n - i, n)})
                yield a[:], hi2, f"Intercambio: a[{j}]↔a[{j+1}]"
        if not swapped:
            break
    yield a[:], {i: C_DONE for i in range(n)}, "¡Ordenado!"


# ══════════════════════════════════════════════════════════════════
#  2. INSERCIÓN
# ══════════════════════════════════════════════════════════════════

def insercion(arr):
    """
    Inserción (Insertion Sort).
    Complejidad: O(n²) promedio y peor caso, O(n) mejor caso.
    """
    a = arr[:]
    n = len(a)
    yield a[:], {0: C_DONE}, "Inicio: primer elemento ya ordenado"
    for i in range(1, n):
        key = a[i]
        j = i - 1
        yield a[:], {i: C_AUX, **{k: C_DONE for k in range(i)}}, \
              f"Insertando a[{i}]={key}"
        while j >= 0 and a[j] > key:
            yield a[:], {j: C_CMP, j + 1: C_SWP}, \
                  f"Moviendo a[{j}]={a[j]} → derecha"
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
        yield a[:], {**{k: C_DONE for k in range(i + 1)}, j + 1: C_SWP}, \
              f"Colocando {key} en posición {j+1}"
    yield a[:], {i: C_DONE for i in range(n)}, "¡Ordenado!"


# ══════════════════════════════════════════════════════════════════
#  3. SELECCIÓN
# ══════════════════════════════════════════════════════════════════

def seleccion(arr):
    """
    Selección (Selection Sort).
    Complejidad: O(n²) en todos los casos.
    """
    a = arr[:]
    n = len(a)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            hi = {j: C_CMP, min_idx: C_AUX}
            hi.update({k: C_DONE for k in range(i)})
            yield a[:], hi, f"Mínimo actual: a[{min_idx}]={a[min_idx]}, comparando con a[{j}]={a[j]}"
            if a[j] < a[min_idx]:
                min_idx = j
        if min_idx != i:
            a[i], a[min_idx] = a[min_idx], a[i]
            hi2 = {i: C_SWP, min_idx: C_SWP}
            hi2.update({k: C_DONE for k in range(i)})
            yield a[:], hi2, f"Intercambio: a[{i}]↔a[{min_idx}]"
        hi3 = {k: C_DONE for k in range(i + 1)}
        yield a[:], hi3, f"Posición {i} fijada con {a[i]}"
    yield a[:], {i: C_DONE for i in range(n)}, "¡Ordenado!"


# ══════════════════════════════════════════════════════════════════
#  4. SHELL SORT
# ══════════════════════════════════════════════════════════════════

def shell_sort(arr):
    """
    Shell Sort (secuencia de Knuth: 1, 4, 13, 40...).
    Complejidad: O(n log² n) con secuencia de Knuth.
    """
    a = arr[:]
    n = len(a)
    gap = 1
    while gap < n // 3:
        gap = gap * 3 + 1
    while gap >= 1:
        yield a[:], {}, f"Gap = {gap}"
        for i in range(gap, n):
            temp = a[i]
            j = i
            yield a[:], {i: C_AUX}, f"Insertando a[{i}]={temp} con gap={gap}"
            while j >= gap and a[j - gap] > temp:
                yield a[:], {j: C_SWP, j - gap: C_CMP}, \
                      f"Moviendo a[{j-gap}]={a[j-gap]}"
                a[j] = a[j - gap]
                j -= gap
            a[j] = temp
            yield a[:], {j: C_DONE}, f"Colocado {temp} en posición {j}"
        gap //= 3
    yield a[:], {i: C_DONE for i in range(n)}, "¡Ordenado!"


# ══════════════════════════════════════════════════════════════════
#  5. QUICK SORT
# ══════════════════════════════════════════════════════════════════

def quick_sort(arr):
    """
    Quick Sort (pivote: elemento medio).
    Complejidad: O(n log n) promedio, O(n²) peor caso.
    """
    a = arr[:]
    pasos = []

    def _partition(lo, hi):
        mid = (lo + hi) // 2
        pivot = a[mid]
        pasos.append((a[:], {mid: C_AUX}, f"Pivote={pivot} en [{lo}..{hi}]"))
        a[mid], a[hi] = a[hi], a[mid]
        store = lo
        for k in range(lo, hi):
            pasos.append((a[:], {k: C_CMP, hi: C_AUX},
                          f"Comparando a[{k}]={a[k]} con pivote={pivot}"))
            if a[k] <= pivot:
                a[k], a[store] = a[store], a[k]
                pasos.append((a[:], {k: C_SWP, store: C_SWP},
                              f"Intercambio a[{k}]↔a[{store}]"))
                store += 1
        a[store], a[hi] = a[hi], a[store]
        pasos.append((a[:], {store: C_DONE},
                      f"Pivote {pivot} en posición final {store}"))
        return store

    def _quick(lo, hi):
        if lo < hi:
            p = _partition(lo, hi)
            _quick(lo, p - 1)
            _quick(p + 1, hi)

    _quick(0, len(a) - 1)
    pasos.append((a[:], {i: C_DONE for i in range(len(a))}, "¡Ordenado!"))
    yield from pasos


# ══════════════════════════════════════════════════════════════════
#  6. MERGE SORT
# ══════════════════════════════════════════════════════════════════

def merge_sort(arr):
    """
    Merge Sort (Bottom-Up iterativo).
    Complejidad: O(n log n) en todos los casos.
    """
    a = arr[:]
    n = len(a)
    size = 1
    while size < n:
        yield a[:], {}, f"Fusionando bloques de tamaño {size}"
        for lo in range(0, n, size * 2):
            mid = min(lo + size, n)
            hi  = min(lo + size * 2, n)
            left  = a[lo:mid]
            right = a[mid:hi]
            i = j = 0; k = lo
            while i < len(left) and j < len(right):
                yield a[:], {lo + i: C_CMP, mid + j: C_CMP}, \
                      f"Comparando {left[i]} con {right[j]}"
                if left[i] <= right[j]:
                    a[k] = left[i]; i += 1
                else:
                    a[k] = right[j]; j += 1
                yield a[:], {k: C_SWP}, f"Colocando {a[k]} en posición {k}"
                k += 1
            while i < len(left):
                a[k] = left[i]; i += 1; k += 1
            while j < len(right):
                a[k] = right[j]; j += 1; k += 1
            yield a[:], {p: C_DONE for p in range(lo, hi)}, \
                  f"Bloque [{lo}..{hi-1}] fusionado"
        size *= 2
    yield a[:], {i: C_DONE for i in range(n)}, "¡Ordenado!"


# ══════════════════════════════════════════════════════════════════
#  7. HEAP SORT
# ══════════════════════════════════════════════════════════════════

def heap_sort(arr):
    """
    Heap Sort (Max-Heap).
    Complejidad: O(n log n) en todos los casos.
    """
    a = arr[:]
    n = len(a)
    pasos = []

    def heapify(size, root):
        largest = root
        l = 2 * root + 1
        r = 2 * root + 2
        pasos.append((a[:], {root: C_AUX,
                              **({l: C_CMP} if l < size else {}),
                              **({r: C_CMP} if r < size else {})},
                      f"Heapify en raíz={root}"))
        if l < size and a[l] > a[largest]:
            largest = l
        if r < size and a[r] > a[largest]:
            largest = r
        if largest != root:
            a[root], a[largest] = a[largest], a[root]
            pasos.append((a[:], {root: C_SWP, largest: C_SWP},
                          f"Intercambio a[{root}]↔a[{largest}]"))
            heapify(size, largest)

    for i in range(n // 2 - 1, -1, -1):
        heapify(n, i)

    for i in range(n - 1, 0, -1):
        a[0], a[i] = a[i], a[0]
        pasos.append((a[:], {0: C_SWP, i: C_DONE},
                      f"Raíz máxima {a[i]} → posición {i}"))
        heapify(i, 0)

    pasos.append((a[:], {i: C_DONE for i in range(n)}, "¡Ordenado!"))
    yield from pasos


# ══════════════════════════════════════════════════════════════════
#  REGISTRO
# ══════════════════════════════════════════════════════════════════

CLASES_INTERNAS = {
    "Burbuja":    burbuja,
    "Inserción":  insercion,
    "Selección":  seleccion,
    "Shell Sort": shell_sort,
    "Quick Sort": quick_sort,
    "Merge Sort": merge_sort,
    "Heap Sort":  heap_sort,
}


def ordenar_interno(nombre_metodo: str, n_elem: int) -> list:
    """Ejecuta el método interno y retorna la lista ordenada."""
    if nombre_metodo not in CLASES_INTERNAS:
        raise ValueError(f"Método desconocido: {nombre_metodo}")
    datos = generar_datos(n_elem)
    gen = CLASES_INTERNAS[nombre_metodo](datos)
    snap = datos[:]
    for snap, _, _ in gen:
        pass
    return snap


if __name__ == "__main__":
    for nombre in METODOS_INTERNOS:
        res = ordenar_interno(nombre, 10)
        print(f"{nombre:<12}: {res}")