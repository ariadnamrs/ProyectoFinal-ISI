import restaurante_controller, sqlite3
from flask import request, jsonify
import pytest
from main import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_get_pedidos(client, mocker):
    # Mockear la función del controlador
    mock_get_pedidos = mocker.patch("restaurante_controller.get_pedidos", return_value=[{"n_pedido": 1}, {"n_pedido": 2}])

    # Realizar una solicitud GET
    response = client.get("/pedidos")

    # Verificar la respuesta
    assert response.status_code == 200
    assert response.json == [{"n_pedido": 1}, {"n_pedido": 2}]

    # Asegurarse de que el mock fue llamado
    mock_get_pedidos.assert_called_once()


def test_insert_pedido_success(client, mocker):
    # Mockear la función insert_pedido para simular el comportamiento de la base de datos
    mock_insert_pedido = mocker.patch("restaurante_controller.insert_pedido", return_value=True)

    # Realizar la solicitud POST con un número de pedido válido
    content = {"n_pedido": "5", "id_m_cliente": "6", "Estado": "En curso"}
    response = client.post("/pedidos", json=content)

    # Verificar la respuesta
    assert response.status_code == 200
    assert response.json == True

    # Verificar que la función insert_pedido fue llamada con el valor correcto
    mock_insert_pedido.assert_called_once_with("5", "6", "En curso")

def test_insert_pedido_key_error(client):
    # Realizar la solicitud POST con cuerpo incompleto
    content = {"n_pedido": 3}  # Ponemos solo el n_pedido sin el id del microbit
    response = client.post("/pedidos", json=content)

    # Verificar la respuesta
    assert response.status_code == 400
    assert response.json == "Datos del pedido incompletos"

def test_insert_pedido_integrity_error(client, mocker):
    # Simular una excepción de integridad desde el controlador, dada por las FOREIGN KEY
    mocker.patch(
        "restaurante_controller.insert_pedido", return_value=False
    )

    # Datos válidos para enviar
    data = {"n_pedido": 1, "id_m_cliente": 2}

    # Realizar la solicitud POST
    response = client.post("/pedidos", json=data)

    # Verificar la respuesta
    assert response.status_code == 400
    assert response.json == "Valor incorrecto, pedido o micorbit no registrado"

def test_get_n_pedido_found(client, mocker):
    mock_get_n_pedidos = mocker.patch("restaurante_controller.get_n_pedido", return_value=[{"n_pedido": 1, "id_m_cliente": 2}])

     # Realizar una solicitud GET
    response = client.get("/pedidos/1")

    # Verificar la respuesta
    assert response.status_code == 200
    assert response.json == [{"n_pedido": 1, "id_m_cliente": 2}]

    # Asegurarse de que el mock fue llamado
    mock_get_n_pedidos.assert_called_once()

def test_invalid_get_n_pedido(client):
    # Realizar una solicitud GET
    response = client.get("/pedidos/hello")

    # Verificar la respuesta
    assert response.status_code == 404
    assert response.json == "Valor de pedido invalido"

def test_get_n_pedido_not_found(client, mocker):
    #Mockamos una consulta de un pedido que no se encuentra en la base de datos
    mock_get_n_pedidos = mocker.patch("restaurante_controller.get_n_pedido", return_value=None)

    #Realizamos la peticion get a ese pedido que no existe
    response = client.get("pedidos/999")

    #Respuesta del servidor
    assert response.status_code == 404
    assert response.json == "Pedido no encontrado"

    #Nos aseguramos que se llame al mock al menos una vez
    mock_get_n_pedidos.assert_called_once()

def test_asocia_cliente_mesa(client, mocker):
    # Mockear la función asocia baliza mesa con baliza cliente para simular el comportamiento de la base de datos
    mock_asocia = mocker.patch("restaurante_controller.asocia", return_value=True)

    # Realizar la solicitud POST con un número de pedido válido
    content = {"id_m_cliente": "2", "id_mesa": "8"}
    response = client.post("/asocia", json=content)

    # Verificar la respuesta
    assert response.status_code == 200
    assert response.json == True

def test_asocia_cliente_mesa_key_error(client):
    # Mockear la función asocia baliza mesa con baliza cliente para simular el comportamiento de la base de dato
    # Realizar la solicitud POST con un número de pedido válido
    content = {"id_mesa": "8"}
    response = client.post("/asocia", json=content)

    # Verificar la respuesta
    assert response.status_code == 400
    assert response.json == "Datos de la asociacion incompletos"

def test_asocia_cliente_mesa_key_error(client, mocker):
    # Mockear la función asocia baliza mesa con baliza cliente para simular el comportamiento de la base de datos
    mocker.patch(
        "restaurante_controller.asocia", side_effect=sqlite3.IntegrityError
    )
    # Realizar la solicitud POST con un número de pedido válido
    content = {"id_mesa": "8", "id_m_cliente": "3"}
    response = client.post("/asocia", json=content)

    # Verificar la respuesta
    assert response.status_code == 400
    assert response.json == "Valores incorrectos, mesa o microbit no encontrados"

def test_delete_pedido(client, mocker):
    #Mockeamos que se borra un pedido de la base de datos correctamente
    mock_delete_n_pedido = mocker.patch("restaurante_controller.delete_pedido", return_value=True)

    response = client.delete("pedidos/1")

    assert response.status_code == 200
    assert response.json is True
    
    mock_delete_n_pedido.assert_called_once_with("1")

def test_update_pedido(client, mocker):
    mock_update_pedido = mocker.patch("restaurante_controller.update_pedido", return_value=True)
    response = client.put("pedidos/1")

    assert response.status_code == 200
    assert response.json is True
    
    mock_update_pedido.assert_called_once_with(1)

def test_update_pedido_not_found(client, mocker):
    mock_update_pedido = mocker.patch("restaurante_controller.update_pedido", return_value=None)
    response = client.put("pedidos/1")

    assert response.status_code == 404
    assert response.json == "Pedido no encontrado"
    
    mock_update_pedido.assert_called_once_with(1)





