# yadro_tech

![CI](https://github.com/solomonalfred/yadro_tech/actions/workflows/ci.yml/badge.svg)

API сервис для работы с ориентированными ациклическими графами

- /api/graph/
Ручка для создания графа, принимает граф в виде списка вершин и списка ребер.
```json
{
  "nodes": [
    { "name": "A" },
    { "name": "B" },
    { "name": "C" }
  ],
  "edges": [
    { "source": "A", "target": "B" },
    { "source": "B", "target": "C" }
  ]
}
```

- /api/graph/{graph_id}/

Ручка для чтения графа в виде списка вершин и списка ребер.

- /api/graph/{graph_id}/adjacency_list

Ручка для чтения графа в виде списка смежности.\nСписок смежности представлен в виде пар ключ - значение, где\n- ключ - имя вершины графа,\n- значение - список имен всех смежных вершин (всех потомков ключа).

- /api/graph/{graph_id}/reverse_adjacency_list

Ручка для чтения транспонированного графа в виде списка смежности.\nСписок смежности представлен в виде пар ключ - значение, где\n- ключ - имя вершины графа,\n- значение - список имен всех смежных вершин (всех предков ключа в исходном графе).

- /api/graph/{graph_id}/node/{node_name}

Ручка для удаления вершины из графа по ее имени.

- Запуск контейнера
    1) 
```docker
docker-compose up -d --build
```

    2) 
```makefile
make up
```

Остановить
    1)
```docker
docker-compose stop
```

    2)
```makefile
make stop
```


Запуск тестов
```python
pytest -q
```
