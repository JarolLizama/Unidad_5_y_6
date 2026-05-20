"""
busqueda_secuencial.py
----------------------
Librería para realizar búsqueda secuencial (lineal) sobre listas.
"""


def buscar(lista, objetivo):
    """
    Busca un elemento en la lista y retorna el índice de su primera aparición.

    Args:
        lista (list): La lista donde se realizará la búsqueda.
        objetivo: El valor a buscar.

    Returns:
        int: Índice del elemento si se encuentra, -1 si no existe.
    """
    for i, elemento in enumerate(lista):
        if elemento == objetivo:
            return i
    return -1


def buscar_todos(lista, objetivo):
    """
    Busca todas las apariciones de un elemento en la lista.

    Args:
        lista (list): La lista donde se realizará la búsqueda.
        objetivo: El valor a buscar.

    Returns:
        list[int]: Lista con todos los índices donde aparece el elemento.
                   Lista vacía si no se encuentra.
    """
    return [i for i, elemento in enumerate(lista) if elemento == objetivo]


def buscar_con_condicion(lista, condicion):
    """
    Busca el primer elemento que cumpla una condición dada.

    Args:
        lista (list): La lista donde se realizará la búsqueda.
        condicion (callable): Función que recibe un elemento y retorna True/False.

    Returns:
        tuple: (índice, elemento) si se encuentra, (-1, None) si no.

    Ejemplo:
        buscar_con_condicion([1, 5, 3, 8], lambda x: x > 4)
        → (1, 5)
    """
    for i, elemento in enumerate(lista):
        if condicion(elemento):
            return (i, elemento)
    return (-1, None)


def contiene(lista, objetivo):
    """
    Verifica si un elemento existe en la lista.

    Args:
        lista (list): La lista a revisar.
        objetivo: El valor a buscar.

    Returns:
        bool: True si el elemento existe, False si no.
    """
    return buscar(lista, objetivo) != -1


def buscar_rango(lista, objetivo, inicio=0, fin=None):
    """
    Busca un elemento dentro de un rango específico de la lista.

    Args:
        lista (list): La lista donde se realizará la búsqueda.
        objetivo: El valor a buscar.
        inicio (int): Índice de inicio del rango (inclusivo). Por defecto 0.
        fin (int): Índice de fin del rango (exclusivo). Por defecto len(lista).

    Returns:
        int: Índice del elemento si se encuentra, -1 si no existe.
    """
    if fin is None:
        fin = len(lista)

    for i in range(inicio, fin):
        if lista[i] == objetivo:
            return i
    return -1
