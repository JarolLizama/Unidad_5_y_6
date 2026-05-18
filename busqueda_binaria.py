"""
Librería de Búsqueda Binaria
Autor: Asistente IA
Descripción: Implementación de búsqueda binaria en sus diferentes variantes
"""

from typing import List, Any, Optional, Union
from numbers import Number


class BusquedaBinaria:
    """
    Clase que contiene diferentes implementaciones del algoritmo de búsqueda binaria.
    Solo funciona con colecciones ORDENADAS.
    """
    
    @staticmethod
    def buscar_iterativo(arreglo: List[Any], objetivo: Any) -> Optional[int]:
        """
        Búsqueda binaria iterativa estándar.
        
        Args:
            arreglo: Lista ordenada de elementos
            objetivo: Elemento a buscar
            
        Returns:
            Índice del elemento encontrado, None si no existe
            
        Ejemplo:
            >>> BusquedaBinaria.buscar_iterativo([1, 3, 5, 7, 9], 5)
            2
        """
        izquierda = 0
        derecha = len(arreglo) - 1
        
        while izquierda <= derecha:
            medio = (izquierda + derecha) // 2
            
            if arreglo[medio] == objetivo:
                return medio
            elif arreglo[medio] < objetivo:
                izquierda = medio + 1
            else:
                derecha = medio - 1
        
        return None
    
    @staticmethod
    def buscar_recursivo(arreglo: List[Any], objetivo: Any, 
                         izquierda: int = 0, derecha: int = None) -> Optional[int]:
        """
        Búsqueda binaria recursiva.
        
        Args:
            arreglo: Lista ordenada de elementos
            objetivo: Elemento a buscar
            izquierda: Índice izquierdo del intervalo
            derecha: Índice derecho del intervalo
            
        Returns:
            Índice del elemento encontrado, None si no existe
        """
        if derecha is None:
            derecha = len(arreglo) - 1
        
        # Caso base: intervalo vacío
        if izquierda > derecha:
            return None
        
        medio = (izquierda + derecha) // 2
        
        if arreglo[medio] == objetivo:
            return medio
        elif arreglo[medio] < objetivo:
            return BusquedaBinaria.buscar_recursivo(arreglo, objetivo, medio + 1, derecha)
        else:
            return BusquedaBinaria.buscar_recursivo(arreglo, objetivo, izquierda, medio - 1)
    
    @staticmethod
    def buscar_todos(arreglo: List[Any], objetivo: Any) -> List[int]:
        """
        Encuentra todas las ocurrencias del elemento en el arreglo ordenado.
        
        Args:
            arreglo: Lista ordenada de elementos (puede tener duplicados)
            objetivo: Elemento a buscar
            
        Returns:
            Lista con todos los índices donde aparece el elemento
            
        Ejemplo:
            >>> BusquedaBinaria.buscar_todos([1, 2, 2, 2, 3, 4], 2)
            [1, 2, 3]
        """
        # Primero encontramos una ocurrencia
        indice = BusquedaBinaria.buscar_iterativo(arreglo, objetivo)
        if indice is None:
            return []
        
        # Buscar hacia la izquierda
        indices = [indice]
        i = indice - 1
        while i >= 0 and arreglo[i] == objetivo:
            indices.append(i)
            i -= 1
        
        # Buscar hacia la derecha
        i = indice + 1
        while i < len(arreglo) and arreglo[i] == objetivo:
            indices.append(i)
            i += 1
        
        return sorted(indices)
    
    @staticmethod
    def buscar_mas_cercano(arreglo: List[Number], objetivo: Number) -> Any:
        """
        Encuentra el elemento más cercano al objetivo cuando no existe exactamente.
        
        Args:
            arreglo: Lista ordenada de números
            objetivo: Número a buscar
            
        Returns:
            Elemento más cercano en el arreglo
            
        Ejemplo:
            >>> BusquedaBinaria.buscar_mas_cercano([1, 3, 5, 7, 9], 6)
            5  # o 7 dependiendo de la implementación
        """
        if not arreglo:
            return None
        
        izquierda = 0
        derecha = len(arreglo) - 1
        
        # Si el objetivo es menor que el primer elemento
        if objetivo <= arreglo[izquierda]:
            return arreglo[izquierda]
        
        # Si el objetivo es mayor que el último elemento
        if objetivo >= arreglo[derecha]:
            return arreglo[derecha]
        
        while izquierda <= derecha:
            medio = (izquierda + derecha) // 2
            
            if arreglo[medio] == objetivo:
                return arreglo[medio]
            elif arreglo[medio] < objetivo:
                izquierda = medio + 1
            else:
                derecha = medio - 1
        
        # Al salir, izquierda y derecha indican los vecinos más cercanos
        if abs(arreglo[izquierda] - objetivo) < abs(arreglo[derecha] - objetivo):
            return arreglo[izquierda]
        else:
            return arreglo[derecha]
    
    @staticmethod
    def buscar_en_rango(arreglo: List[Number], minimo: Number, maximo: Number) -> List[Number]:
        """
        Encuentra todos los elementos en un rango [minimo, maximo].
        
        Args:
            arreglo: Lista ordenada de números
            minimo: Límite inferior del rango
            maximo: Límite superior del rango
            
        Returns:
            Lista de elementos dentro del rango
        """
        # Encontrar el primer índice >= minimo
        izquierda = 0
        derecha = len(arreglo) - 1
        inicio = None
        
        while izquierda <= derecha:
            medio = (izquierda + derecha) // 2
            if arreglo[medio] >= minimo:
                inicio = medio
                derecha = medio - 1
            else:
                izquierda = medio + 1
        
        if inicio is None:
            return []
        
        # Encontrar el último índice <= maximo
        izquierda = inicio
        derecha = len(arreglo) - 1
        fin = None
        
        while izquierda <= derecha:
            medio = (izquierda + derecha) // 2
            if arreglo[medio] <= maximo:
                fin = medio
                izquierda = medio + 1
            else:
                derecha = medio - 1
        
        if fin is None:
            return []
        
        return arreglo[inicio:fin + 1]