import heapq
import itertools
from collections import deque
from typing import Dict, List, Any, Set, Tuple, Union, Optional


class Nodo:
    def __init__(self, id_nodo: Union[int, str], **kwargs: Any):
        self.id = id_nodo
        self.atributos: Dict[str, Any] = kwargs

    def __str__(self) -> str:
        return str(self.id)


class Arista:
    def __init__(self, fuente: Nodo, destino: Nodo, dirigido: bool = False, peso: float = 1.0):
        self.fuente = fuente
        self.destino = destino
        self.dirigido = dirigido
        self.peso = peso

    def __str__(self) -> str:
        conector = "->" if self.dirigido else "--"
        return f"{self.fuente.id} {conector} {self.destino.id} ({self.peso:.2f})"


class Grafo:
    def __init__(self, dirigido: bool = False):
        self.dirigido: bool = dirigido
        self.nodos: Dict[Union[int, str], Nodo] = {}
        self.aristas: Dict[Union[int, str], Dict[Union[int, str], Arista]] = {}
        self.peso_mst: float = 0.0

    def agregar_nodo(self, id_nodo: Union[int, str], **kwargs: Any) -> None:
        if id_nodo not in self.nodos:
            self.nodos[id_nodo] = Nodo(id_nodo, **kwargs)
            self.aristas[id_nodo] = {}

    def agregar_arista(self, id_fuente: Union[int, str], id_destino: Union[int, str], peso: float = 1.0) -> None:
        self.agregar_nodo(id_fuente)
        self.agregar_nodo(id_destino)

        if id_destino in self.aristas[id_fuente]:
            return

        nueva_arista = Arista(self.nodos[id_fuente], self.nodos[id_destino], self.dirigido, peso)
        self.aristas[id_fuente][id_destino] = nueva_arista

        if not self.dirigido:
            self.aristas[id_destino][id_fuente] = nueva_arista

    def eliminar_arista(self, id_fuente: Union[int, str], id_destino: Union[int, str]) -> None:
        if id_fuente in self.aristas and id_destino in self.aristas[id_fuente]:
            del self.aristas[id_fuente][id_destino]
        if not self.dirigido and id_destino in self.aristas and id_fuente in self.aristas[id_destino]:
            del self.aristas[id_destino][id_fuente]

    def obtener_todas_las_aristas(self) -> List[Arista]:
        todas: List[Arista] = []
        visitadas: Set[Tuple[str, str]] = set()

        for origen, conexiones in self.aristas.items():
            for destino, arista in conexiones.items():
                if not self.dirigido:
                    conexion = tuple(sorted([str(origen), str(destino)]))
                    if conexion not in visitadas:
                        todas.append(arista)
                        visitadas.add(conexion)
                else:
                    todas.append(arista)
        return todas

    def obtener_peso_total(self) -> float:
        return round(sum(a.peso for a in self.obtener_todas_las_aristas()), 2)

    def exportar_graphviz(self, nombre_archivo: str, mostrar_peso_arista: bool = True) -> None:
        tipo_grafo = "digraph" if self.dirigido else "graph"
        conector = "->" if self.dirigido else "--"

        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            f.write(f"{tipo_grafo} G {{\n")
            for id_nodo in self.nodos:
                f.write(f'  "{id_nodo}";\n')

            for arista in self.obtener_todas_las_aristas():
                if mostrar_peso_arista:
                    f.write(
                        f'  "{arista.fuente.id}" {conector} "{arista.destino.id}" '
                        f'[weight={arista.peso:.2f}, label="{arista.peso:.2f}"];\n'
                    )
                else:
                    f.write(f'  "{arista.fuente.id}" {conector} "{arista.destino.id}";\n')
            f.write("}\n")

    # ==========================================
    # ALGORITMOS DE BÚSQUEDA (ETAPA 2)
    # ==========================================

    def BFS(self, s: Union[int, str]) -> 'Grafo':
        if s not in self.nodos:
            raise ValueError(f"El nodo '{s}' no existe.")
        arbol = Grafo(dirigido=self.dirigido)
        visitados: Set[Union[int, str]] = {s}
        cola: deque = deque([s])
        arbol.agregar_nodo(s, **self.nodos[s].atributos)

        while cola:
            u = cola.popleft()
            for v, arista in self.aristas[u].items():
                if v not in visitados:
                    visitados.add(v)
                    arbol.agregar_nodo(v, **self.nodos[v].atributos)
                    arbol.agregar_arista(u, v, arista.peso)
                    cola.append(v)
        return arbol

    def DFS_R(self, s: Union[int, str]) -> 'Grafo':
        if s not in self.nodos:
            raise ValueError(f"El nodo '{s}' no existe.")
        arbol = Grafo(dirigido=self.dirigido)
        visitados: Set[Union[int, str]] = set()

        def _dfs(u: Union[int, str]) -> None:
            visitados.add(u)
            arbol.agregar_nodo(u, **self.nodos[u].atributos)
            for v, arista in self.aristas[u].items():
                if v not in visitados:
                    arbol.agregar_nodo(v, **self.nodos[v].atributos)
                    arbol.agregar_arista(u, v, arista.peso)
                    _dfs(v)

        _dfs(s)
        return arbol

    def DFS_I(self, s: Union[int, str]) -> 'Grafo':
        if s not in self.nodos:
            raise ValueError(f"El nodo '{s}' no existe.")
        arbol = Grafo(dirigido=self.dirigido)
        visitados: Set[Union[int, str]] = set()
        pila: List[Tuple[Optional[Union[int, str]], Union[int, str], float]] = [(None, s, 1.0)]

        while pila:
            padre, u, peso = pila.pop()
            if u not in visitados:
                visitados.add(u)
                arbol.agregar_nodo(u, **self.nodos[u].atributos)
                if padre is not None:
                    arbol.agregar_arista(padre, u, peso)
                for v, arista in self.aristas[u].items():
                    if v not in visitados:
                        pila.append((u, v, arista.peso))
        return arbol

    # ==========================================
    # CAMINOS MÁS CORTOS (ETAPA 3)
    # ==========================================

    def Dijkstra(self, s: Union[int, str]) -> 'Grafo':
        if s not in self.nodos:
            raise ValueError(f"El nodo '{s}' no existe.")

        distancias: Dict[Union[int, str], float] = {nodo: float('inf') for nodo in self.nodos}
        padres: Dict[Union[int, str], Optional[Union[int, str]]] = {s: None}
        peso_arista_padre: Dict[Union[int, str], float] = {}
        visitados: Set[Union[int, str]] = set()

        distancias[s] = 0.0
        contador = itertools.count()
        cola_prioridad: List[Tuple[float, int, Union[int, str]]] = [(0.0, next(contador), s)]

        while cola_prioridad:
            dist_u, _, u = heapq.heappop(cola_prioridad)
            if u in visitados:
                continue
            visitados.add(u)

            for v, arista in self.aristas[u].items():
                if v not in visitados:
                    nueva_dist = dist_u + arista.peso
                    if nueva_dist < distancias[v]:
                        distancias[v] = nueva_dist
                        padres[v] = u
                        peso_arista_padre[v] = arista.peso
                        heapq.heappush(cola_prioridad, (nueva_dist, next(contador), v))

        arbol = Grafo(dirigido=self.dirigido)
        mapa_etiquetas: Dict[Union[int, str], str] = {}

        for u in visitados:
            etiqueta = f"{u} ({distancias[u]:.2f})"
            mapa_etiquetas[u] = etiqueta
            arbol.agregar_nodo(etiqueta, distancia=round(distancias[u], 2), **self.nodos[u].atributos)

        for v in visitados:
            u_padre = padres.get(v)
            if u_padre is not None:
                arbol.agregar_arista(mapa_etiquetas[u_padre], mapa_etiquetas[v], peso=peso_arista_padre[v])

        return arbol

    # ==========================================
    # ÁRBOL DE EXPANSIÓN - MST (ETAPA 4)
    # ==========================================

    def KruskalD(self) -> 'Grafo':
        arbol = Grafo(dirigido=False)
        padre: Dict[Union[int, str], Union[int, str]] = {}
        rango: Dict[Union[int, str], int] = {}

        for id_nodo, obj_nodo in self.nodos.items():
            arbol.agregar_nodo(id_nodo, **obj_nodo.atributos)
            padre[id_nodo] = id_nodo
            rango[id_nodo] = 0

        def encontrar(nodo: Union[int, str]) -> Union[int, str]:
            raiz = nodo
            while padre[raiz] != raiz:
                raiz = padre[raiz]
            actual = nodo
            while actual != raiz:
                siguiente = padre[actual]
                padre[actual] = raiz
                actual = siguiente
            return raiz

        def unir(u: Union[int, str], v: Union[int, str]) -> bool:
            raiz_u = encontrar(u)
            raiz_v = encontrar(v)
            if raiz_u == raiz_v:
                return False
            if rango[raiz_u] < rango[raiz_v]:
                padre[raiz_u] = raiz_v
            elif rango[raiz_u] > rango[raiz_v]:
                padre[raiz_v] = raiz_u
            else:
                padre[raiz_v] = raiz_u
                rango[raiz_u] += 1
            return True

        aristas_ordenadas = sorted(
            self.obtener_todas_las_aristas(),
            key=lambda a: (a.peso, str(a.fuente.id), str(a.destino.id))
        )

        peso_total = 0.0
        for arista in aristas_ordenadas:
            u, v = arista.fuente.id, arista.destino.id
            if unir(u, v):
                arbol.agregar_arista(u, v, arista.peso)
                peso_total += arista.peso

        arbol.peso_mst = round(peso_total, 2)
        return arbol

    def KruskalI(self) -> 'Grafo':
        arbol = Grafo(dirigido=False)
        for id_nodo, obj_nodo in self.nodos.items():
            arbol.agregar_nodo(id_nodo, **obj_nodo.atributos)

        todas_las_aristas = self.obtener_todas_las_aristas()
        for arista in todas_las_aristas:
            arbol.agregar_arista(arista.fuente.id, arista.destino.id, arista.peso)

        aristas_ordenadas = sorted(
            todas_las_aristas,
            key=lambda a: (a.peso, str(a.fuente.id), str(a.destino.id)),
            reverse=True
        )

        def _estan_conectados(origen: Union[int, str], objetivo: Union[int, str]) -> bool:
            visitados: Set[Union[int, str]] = {origen}
            cola: deque = deque([origen])
            while cola:
                actual = cola.popleft()
                if actual == objetivo:
                    return True
                for vecino in arbol.aristas[actual]:
                    if vecino not in visitados:
                        visitados.add(vecino)
                        cola.append(vecino)
            return False

        for arista in aristas_ordenadas:
            u, v, peso = arista.fuente.id, arista.destino.id, arista.peso
            arbol.eliminar_arista(u, v)
            if not _estan_conectados(u, v):
                arbol.agregar_arista(u, v, peso)

        arbol.peso_mst = arbol.obtener_peso_total()
        return arbol

    def Prim(self) -> 'Grafo':
        arbol = Grafo(dirigido=False)
        for id_nodo, obj_nodo in self.nodos.items():
            arbol.agregar_nodo(id_nodo, **obj_nodo.atributos)

        if not self.nodos:
            return arbol

        visitados: Set[Union[int, str]] = set()
        contador = itertools.count()
        peso_total = 0.0

        for nodo_inicial in self.nodos:
            if nodo_inicial in visitados:
                continue

            visitados.add(nodo_inicial)
            cola_prioridad: List[Tuple[float, int, Union[int, str], Union[int, str]]] = []

            for vecino, arista in self.aristas[nodo_inicial].items():
                heapq.heappush(cola_prioridad, (arista.peso, next(contador), nodo_inicial, vecino))

            while cola_prioridad:
                peso, _, u, v = heapq.heappop(cola_prioridad)
                if v in visitados:
                    continue

                visitados.add(v)
                arbol.agregar_arista(u, v, peso)
                peso_total += peso

                for siguiente, arista_sig in self.aristas[v].items():
                    if siguiente not in visitados:
                        heapq.heappush(cola_prioridad, (arista_sig.peso, next(contador), v, siguiente))

        arbol.peso_mst = round(peso_total, 2)
        return arbol