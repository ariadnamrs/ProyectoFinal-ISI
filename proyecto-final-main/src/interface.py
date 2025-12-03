from graphics import *
import requests

# Función para registrar el pedido
def registrar_pedido():
    n_pedido = entry_n_pedido.getText()
    id_m_cliente = entry_id_m_cliente.getText()
    
    # Validar campos
    if not n_pedido or not id_m_cliente:
        message.setText("Error: Ambos campos son obligatorios")
        return

    try:
        # Convertir a enteros
        n_pedido = int(n_pedido)

        # Enviar la solicitud POST
        response = requests.post(
            "http://localhost:5000/pedidos",
            json={"n_pedido": n_pedido, "id_m_cliente": id_m_cliente}
        )

        if response.status_code == 200:
            message.setText("¡Pedido registrado exitosamente!")
        else:
            message.setText(f"Error: {response.json()}")

    except ValueError:
        message.setText("Error: Los valores deben ser numéricos")
    except Exception as e:
        message.setText(f"Error al conectar: {e}")

# Crear ventana principal
win = GraphWin("Registrar Pedido", 400, 300)
win.setBackground("lightgrey")

# Etiquetas y campos de texto
Text(Point(150, 50), "Número de Pedido:").draw(win)
entry_n_pedido = Entry(Point(300, 50), 10)
entry_n_pedido.draw(win)

Text(Point(150, 100), "ID Microbit Cliente:").draw(win)
entry_id_m_cliente = Entry(Point(300, 100), 10)
entry_id_m_cliente.draw(win)

# Botón
button = Rectangle(Point(150, 150), Point(250, 200))
button.setFill("blue")
button.draw(win)
Text(Point(200, 175), "Registrar").draw(win)

# Mensaje de estado
message = Text(Point(200, 250), "")
message.setSize(10)
message.setFill("red")
message.draw(win)

def main():
# Esperar eventos
    while True:
        click = win.getMouse()

        # Si se hace clic en el botón
        if 150 <= click.x <= 250 and 150 <= click.y <= 200:
            registrar_pedido()

    win.close()

if __name__ == "__main__":
    main()
