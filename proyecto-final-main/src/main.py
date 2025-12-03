from flask import Flask, jsonify, request, abort
import restaurante_controller
import sqlite3
import serial_server
from threading import Thread
#from serial_server import microbit_blueprint

app = Flask(__name__)
#app.register_blueprint(microbit_blueprint)

@app.route("/pedidos", methods=["GET"])
def get_pedidos():
    result = restaurante_controller.get_pedidos()
    return jsonify(result)

@app.route("/pedidos", methods=["POST"])
def insert_pedido():
    try:
        pedido = request.get_json()
        id_m_cliente = pedido["id_m_cliente"]
        estado = "En curso"
        disponibilidad_mb = restaurante_controller.get_disponibilidad_mb()
        id_microbits = [item['id_microbit'] for item in disponibilidad_mb]
        if id_m_cliente in id_microbits:
            result = restaurante_controller.insert_pedido(id_m_cliente, estado)
            if result:
                print(f"Pedido asociado a {id_m_cliente} guardado")
                return jsonify(result)
            else:
                response = jsonify("Valor incorrecto, pedido o micorbit no registrado")
                response.status_code = 400

                return response
        else:
            response = jsonify("Microbit no disponible, ya en uso")
            response.status_code = 400
            return response
    except KeyError:
        response = jsonify("Datos del pedido incompletos")
        response.status_code = 400
        return response


@app.route("/pedidos/<n_pedido>", methods=["GET"])
def get_n_pedido(n_pedido):
    try:
        n_pedido = int(n_pedido)
    except ValueError:
        response = jsonify("Valor de pedido invalido")
        response.status_code = 404
        return response

    result = restaurante_controller.get_n_pedido(n_pedido)
    if result is None:
        response = jsonify("Pedido no encontrado")
        response.status_code = 404
        return response

    return jsonify(result)

@app.route("/pedidos/<n_pedido>", methods=["PUT"])
def update_pedido(n_pedido):
    try:
        n_pedido = int(n_pedido)
        result = restaurante_controller.update_pedido(n_pedido)
        if result is None:
            response = jsonify("Pedido no encontrado")
            response.status_code = 404
            return response
    except ValueError:
        response = jsonify("Valor de pedido invalido")
        response.status_code = 404
        return response


    return jsonify(result)

@app.route("/asocia", methods=["POST"])
def asocia_mesa_baliza():
    try:
        asocia = request.get_json()
        id_mesa = asocia["id_mesa"]
        id_m_cliente = asocia["id_m_cliente"]
        result = restaurante_controller.asocia(id_m_cliente, id_mesa)
        print(f"Mesa {id_mesa} asociada a cliente {id_m_cliente}: Guardado")
        return jsonify(result)
    except sqlite3.IntegrityError:
        response = jsonify("Valores incorrectos, mesa o microbit no encontrados")
        print(response)
        response.status_code = 400
        return response

@app.route("/pedidos/<n_pedido>", methods=["DELETE"])
def delete_pedido(n_pedido):
    result = restaurante_controller.delete_pedido(n_pedido)
    return jsonify(result)

@app.route("/balizas", methods=["GET"])
def get_balizas():
    result = restaurante_controller.get_disponibilidad_mb()
    return jsonify(result)

@app.route("/envia", methods=["POST"])
def enviar_aviso():
    data = request.get_json()
    id_cliente = data.get("id_m_cliente")
    msg = data.get("msg")
    if id_cliente:
        serial_server.enviar_aviso_microbit_cliente(id_cliente)
        response = jsonify(f"Aviso enviado al micro:bit para el cliente {id_cliente}")
        response.status_code = 200
    elif msg:
        serial_server.aviso_microbit_camarero(msg)
        response = jsonify(f"Aviso a camareros")
        response.status_code = 200
    return response


if __name__ == "__main__":
    serial_server.main()
    app.run(host='0.0.0.0', port=5000, debug=False)
    
    
