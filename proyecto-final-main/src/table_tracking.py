from queue import Queue
import time
from threading import Thread
import requests
from graphics import *
import sys
from datetime import datetime, timedelta


API_BASE_URL = "http://127.0.0.1:5000"
TIEMPO_AVISO = 1 #Minutos

class TableTracker:
    def __init__(self, n_pedido, id_m_cliente, n_m_cliente, id_mesa, fecha, estado):
        self.n_pedido = n_pedido
        self.id_m_cliente = id_m_cliente
        self.n_m_cliente = n_m_cliente
        self.id_mesa = id_mesa
        self.estado = estado
        self.fecha = fecha
        self.start_time = time.time()
    
    def get_elapsed_time(self):
        return int(time.time() - self.start_time)
    
    def reset_timer(self):
        self.start_time = time.time()

class BalizaTracker:
    def __init__(self, id_microbit, n_microbit):
        self.id_microbit = id_microbit
        self.n_microbit = n_microbit


def draw_table(win, x, y, width, height, table):
    rect = Rectangle(Point(x, y), Point(x + width, y + height))
    tiempo = datetime.now().replace(microsecond=0) - datetime.strptime(table.fecha, "%Y-%m-%d %H:%M:%S")
    if table.estado == "En curso":
        rect.setFill("lightblue")
    elif table.estado == "Finalizado" and tiempo < timedelta(minutes=1):
        rect.setFill("yellow")
    elif table.estado == "Finalizado" and tiempo >= timedelta(minutes=1):
        rect.setFill("red")

    rect.draw(win)

    pedido_text = Text(Point(x + width / 2, y + 20), f"Pedido: {table.n_pedido}")
    pedido_text.setSize(12)
    pedido_text.draw(win)
    
    cliente_text = Text(Point(x + width / 2, y + 40), f"Cliente: {table.n_m_cliente}")
    cliente_text.setSize(12)
    cliente_text.draw(win)
    
    if table.n_m_cliente.startswith("M-"):
        mesa_text = Text(Point(x + width / 2, y + 60), f"Mesa: {table.id_mesa}")
    else:
        mesa_text = Text(Point(x + width / 2, y + 60), f"Llevar")
    mesa_text.setSize(12)
    mesa_text.draw(win)
    
    time_text = Text(Point(x + width / 2, y + 80), f"Tiempo: {tiempo}")
    time_text.setSize(12)
    time_text.draw(win)
    
    return rect, pedido_text, cliente_text, mesa_text, time_text

def draw_baliza(win, x, y, width, height, balizas):
    rect = Rectangle(Point(x, y), Point(x + width, y + height))
    rect.setFill("lightgreen")
    rect.draw(win)

    baliza_text = Text(Point(x + width / 2, y + height / 2), f"Baliza: {balizas.n_microbit}")
    baliza_text.setSize(12)
    baliza_text.draw(win)

    return rect, baliza_text



def update_table_color(rect, elapsed_time):
    if elapsed_time >= 10:
        rect.setFill("red")
    elif elapsed_time >= 5:
        rect.setFill("yellow")
    else:
        rect.setFill("lightblue")

def obtener_pedidos():
    try:
        response = requests.get(f"{API_BASE_URL}/pedidos")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener pedidos: {e}")
        return []

def obtener_balizas():
    try:
        response = requests.get(f"{API_BASE_URL}/balizas")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener pedidos: {e}")
        return []

def actualizar_pedidos(queue):
    """
    Hilo secundario: obtiene los pedidos periódicamente y los pone en la cola.
    """
    pedidos = []
    while True:
        pedidos_actuales = obtener_pedidos()
        if pedidos_actuales != pedidos:
            pedidos = pedidos_actuales
            queue.put(pedidos)
        time.sleep(2)

def actualizar_balizas(queue_balizas):
    balizas = []
    while True:
        balizas_actuales = obtener_balizas()
        if balizas_actuales != balizas:
            balizas = balizas_actuales
            queue_balizas.put(balizas)
        time.sleep(2)

def main():
    try:
        win = GraphWin("Gestión de Pedidos", 1200, 800)
        win.setBackground("white")
        
        table_width = 150
        table_height = 100
        baliza_width = 120
        baliza_height = 50

        tables = []
        balizas = []
        table_elements = []
        baliza_elements = []
        time_texts = []

        # Colas para la comunicación entre hilos
        queue_pedidos = Queue()
        queue_balizas = Queue()

        # Iniciar hilos para actualizar pedidos y balizas
        update_pedidos_thread = Thread(target=actualizar_pedidos, args=(queue_pedidos,))
        update_balizas_thread = Thread(target=actualizar_balizas, args=(queue_balizas,))
        update_pedidos_thread.start()
        update_balizas_thread.start()

        while True:
            # Verificar si hay datos nuevos en la cola de pedidos
            if not queue_pedidos.empty():
                pedidos = queue_pedidos.get()  # Obtener los datos nuevos
                tables.clear()
                for pedido in pedidos:
                    table = TableTracker(
                        n_pedido=pedido["n_pedido"],
                        id_m_cliente=pedido["id_m_cliente"],
                        n_m_cliente=pedido["n_m_cliente"],
                        id_mesa=pedido["id_mesa"],
                        estado=pedido["estado"],
                        fecha=pedido["fecha"]
                    )
                    tables.append(table)

                # Redibujar las mesas
                for rect, pedido_text, cliente_text, mesa_text, time_text in table_elements:
                    rect.undraw()
                    pedido_text.undraw()
                    cliente_text.undraw()
                    mesa_text.undraw()
                    time_text.undraw()
                table_elements.clear()
                time_texts.clear()

                for idx, table in enumerate(tables):
                    x = (idx % 4) * (table_width + 20) + 20
                    y = (idx // 4) * (table_height + 20) + 20

                    rect, pedido_text, cliente_text, mesa_text, time_text = draw_table(
                        win, x, y, table_width, table_height, table)
                    table_elements.append((rect, pedido_text, cliente_text, mesa_text, time_text))
                    time_texts.append(time_text)  # Guardamos el texto del tiempo para actualizarlo luego

            # **Actualizar el tiempo transcurrido en cada iteración sin necesidad de recibir nuevos pedidos**
            for idx, table in enumerate(tables):
                tiempo_transcurrido = datetime.now().replace(microsecond=0) - datetime.strptime(table.fecha, "%Y-%m-%d %H:%M:%S")
                if tiempo_transcurrido >= timedelta(minutes=TIEMPO_AVISO) and table.estado == "Finalizado":
                    rect = table_elements[idx][0]
                    rect.setFill("red")
                if tiempo_transcurrido == timedelta(minutes=TIEMPO_AVISO) and table.estado == "Finalizado" and table.n_m_cliente.startswith("M-"):
                    response = requests.post(f"http://localhost:5000/envia", json={"msg": f"MFT {table.id_mesa}"})
                    if response.status_code == 200:
                        print("Camareros avisados de microbit olividado")
                time_texts[idx].setText(f"Tiempo: {tiempo_transcurrido}")

            # Verificar si hay datos nuevos en la cola de balizas
            if not queue_balizas.empty():
                mb_clientes = queue_balizas.get()
                balizas.clear()
                for mb in mb_clientes:
                    baliza = BalizaTracker(
                        id_microbit=mb["id_microbit"],
                        n_microbit=mb["n_microbit"]
                    )
                    balizas.append(baliza)
                # Obtener los datos nuevos

                # Redibujar las balizas
                for bal, baliza_text in baliza_elements:
                    bal.undraw()
                    baliza_text.undraw()
                baliza_elements.clear()

                for idx, baliza in enumerate(balizas):
                    x = (idx % 6) * (baliza_width + 10) + 20
                    y = 600  # Fija la posición vertical de las balizas en la parte inferior

                    bal, baliza_text = draw_baliza(
                        win, x, y, baliza_width, baliza_height, baliza)
                    baliza_elements.append((bal, baliza_text))

            # Manejo de clics
            point = win.checkMouse()
            if point:
                # Verificar clics en mesas
                for idx, (rect, pedido_text, cliente_text, mesa_text, time_text) in enumerate(table_elements):
                    if rect.getP1().getX() <= point.getX() <= rect.getP2().getX() and rect.getP1().getY() <= point.getY() <= rect.getP2().getY():
                        if tables[idx].estado == "En curso":
                            print(f"Pedido {tables[idx].n_pedido} seleccionado, Mesa: {tables[idx].id_mesa}, Mb: {tables[idx].n_m_cliente}")
                            response = requests.post(f"http://localhost:5000/envia", json={"id_m_cliente": tables[idx].id_m_cliente})  # Enviar aviso al cliente
                            if response.status_code == 200:
                                requests.put(f"{API_BASE_URL}/pedidos/{tables[idx].n_pedido}")
                                print(f"Pedido {tables[idx].n_pedido} actualizado a 'finalizado'")
                            else:
                                print(f"Error al actualizar el pedido: Codigo {response.status_code}")
                        else:
                            print(f"Pedido {tables[idx].n_pedido} ya esta finalizado")
                        break

                # Verificar clics en balizas
                for idx, (rect, baliza_text) in enumerate(baliza_elements):
                    if rect.getP1().getX() <= point.getX() <= rect.getP2().getX() and rect.getP1().getY() <= point.getY() <= rect.getP2().getY():
                        print(f"Baliza {balizas[idx].id_microbit} seleccionada")
                        requests.post(f"http://localhost:5000/pedidos", json={"id_m_cliente": str(balizas[idx].id_microbit)})
                        break

            time.sleep(1)
            
    except KeyboardInterrupt:
        print("Cerrando programa...")
        win.close()
        sys.exit()

        

if __name__ == "__main__":
    main()



