from db import get_db
import sqlite3
#import datetime

def get_pedidos():
    db = get_db()
    cursor = db.cursor()
    statement = """
SELECT 
    p.n_pedido,
    p.id_m_cliente,
    b.n_microbit,
    m.n_mesa,
    p.estado,
    datetime (p.fecha, 'localtime') AS fecha
FROM Pedido p
LEFT JOIN (
    -- Obtener la última asociación del cliente después de la fecha del pedido
    SELECT 
        a.id_m_cliente,
        a.id_mesa,
        MAX(a.fecha_asociacion) AS ultima_asociacion
    FROM Asocia_m_cliente_m_mesa a
    GROUP BY a.id_m_cliente
) AS ultimas_asociaciones
ON p.id_m_cliente = ultimas_asociaciones.id_m_cliente
LEFT JOIN M_mesa m
ON ultimas_asociaciones.id_mesa = m.id_microbit
LEFT JOIN M_cliente b
ON b.id_microbit = p.id_m_cliente
WHERE 
    p.estado = 'En curso'  
    OR (
        p.estado != 'En curso' 
        AND NOT EXISTS (
            -- Verificar si el cliente ha vuelto al mostrador "M" después del pedido
            SELECT 1
            FROM Asocia_m_cliente_m_mesa a2
            WHERE 
                a2.id_m_cliente = p.id_m_cliente 
                AND a2.id_mesa = (SELECT id_microbit FROM M_mesa WHERE n_mesa = 'M')
                AND a2.fecha_asociacion >= p.fecha
        )
    )
ORDER BY p.n_pedido;
"""
    cursor.execute(statement)
    results = cursor.fetchall()
    pedidos = []
    for result in results:
        pedidos.append({
        "n_pedido": result[0],
        "id_m_cliente": result[1],
        "n_m_cliente": result[2],
        "id_mesa": result[3],
        "estado": result[4],
        "fecha": result[5]
        })
    return pedidos


def insert_pedido(id_m_cliente, estado):
    try:
        db = get_db()
        cursor = db.cursor()
        statement = "INSERT INTO Pedido(id_m_cliente, estado) VALUES (?, ?)"
        cursor.execute(statement, [id_m_cliente, estado])
        db.commit()
    except sqlite3.IntegrityError:
        db.close()
        return False
    return True

def get_disponibilidad_mb():
    db = get_db()
    cursor = db.cursor()
    statement = """SELECT mc.id_microbit, mc.n_microbit
FROM M_cliente mc
LEFT JOIN Pedido p 
    ON mc.id_microbit = p.id_m_cliente AND p.estado = "En curso"
LEFT JOIN (
    -- Obtener la última asociación de cada cliente con una mesa
    SELECT id_m_cliente, id_mesa, MAX(fecha_asociacion) AS ultima_asociacion
    FROM Asocia_m_cliente_m_mesa
    GROUP BY id_m_cliente
) asoc 
    ON mc.id_microbit = asoc.id_m_cliente
LEFT JOIN M_mesa mm
    ON asoc.id_mesa = mm.id_microbit
LEFT JOIN (
    -- Obtener la última fecha de un pedido finalizado por cliente
    SELECT id_m_cliente, MAX(fecha) AS ultima_fecha_pedido_finalizado
    FROM Pedido
    WHERE estado = "Finalizado"
    GROUP BY id_m_cliente
) ult_pedido
    ON mc.id_microbit = ult_pedido.id_m_cliente
WHERE p.id_m_cliente IS NULL
AND mm.n_mesa = "M"  -- La última asociación debe ser con el mostrador
AND (
    ult_pedido.ultima_fecha_pedido_finalizado IS NULL  -- Si nunca ha tenido pedidos, lo incluimos
    OR asoc.ultima_asociacion > ult_pedido.ultima_fecha_pedido_finalizado
);
"""
    cursor.execute(statement)
    results = cursor.fetchall()
    mb = []
    for result in results:
        mb.append({"id_microbit": result[0],
                "n_microbit": result[1]})
    return mb

def get_n_pedido(n_pedido):
    db = get_db()
    cursor = db.cursor()
    statement = "SELECT id_m_cliente FROM Asocia_m_client_pedido WHERE n_pedido = ?"
    cursor.execute(statement, [n_pedido])
    return cursor.fetchone()

def update_pedido(n_pedido):
    db = get_db()
    cursor = db.cursor()
    statement = """UPDATE Pedido SET estado = "Finalizado", fecha = CURRENT_TIMESTAMP WHERE n_pedido = ?"""
    cursor.execute(statement, [n_pedido])
    db.commit()
    return True

def asocia(id_m_cliente, id_mesa):
    db = get_db()
    cursor = db.cursor()
    statement = "INSERT INTO Asocia_m_cliente_m_mesa(id_m_cliente, id_mesa) VALUES (?, ?)"
    cursor.execute(statement, [id_m_cliente, id_mesa])
    db.commit()
    return True

def delete_pedido(n_pedido):
    db = get_db()
    cursor = db.cursor()
    statement = "DELETE FROM Pedido WHERE n_pedido = ?"
    cursor.execute(statement, [n_pedido])
    db.commit()
    return cursor.rowcount > 0