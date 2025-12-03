import pytest
import requests
from serial import Serial
from serial.tools import list_ports
from serial_server import find_comport, recibir_mandar_msg


def test_encontrar_comport_true(mocker):
    m_puerto = pytest.Mock()
    m_puerto.pid =  111
    m_puerto.vid = 2222
    m_puerto.device = "COM5"

    mocker.patch("serial.tools.list_ports.comports",return_value=[m_puerto])
    m_serial = mocker.patch("serial.Serial",return_value=Serial(timeout=1,baudrate=115200))
    puerto = find_comport(111,2222,115200)

    assert puerto is not None
    assert puerto.port == "COM5"
    assert puerto.baudrate == 115200
    m_serial.assert_called_once()


def test_encontrar_comport_false(mocker):
    m_puerto = pytest.Mock()
    m_puerto.pid =  111
    m_puerto.vid = 2222
    m_puerto.device = "COM5"

    mocker.patch("serial.tools.list_ports.comports",return_value=[m_puerto])
    m_serial = mocker.patch("serial.Serial",return_value=Serial(timeout=1,baudrate=115200))
    puerto = find_comport(222,1111,115200)

    assert puerto is None
    m_serial.assert_called_once()

def test_recibir_mandar_mensaje(mocker):
    m_serial = pytest.Mock()
    m_serial.readline.return_value = b'{"id_mesa": "1","id_m_cliente":"M-001"}\n'
    m_serial.is_open = True

    m_post = mocker.patch("requests.post")
    m_post.return_value.status_code = 200
    m_post.return_value.text = 'OK'

    respuesta = recibir_mandar_msg(m_serial)

    assert respuesta == {"status_code":200,"response":"OK"}

    url = "http://localhost:5000/asocia"
    datos = '{"id_mesa": "1","id_m_cliente":"M-001"}'

    m_post.assert_called_once_with(url,json=json.loads(datos))

def test_recibir_mandar_mensaje_vacio(mocker):
    m_serial = pytest.Mock()
    m_serial.readline.return_value = b''
    m_serial.is_open = True

    respuesta = recibir_mandar_msg(m_serial)

    assert respuesta == {"error":"No se recibió mensaje"}

def test_recibir_mandar_error_post(mocker):
    m_serial = pytest.Mock()
    m_serial.readline.return_value = b'{"id_mesa": "1","id_m_cliente":"M-001"}\n'
    m_serial.is_open = True

    m_post = mocker.patch("requests.post", side_effect=Exception('Error al enviar'))

    respuesta = recibir_mandar_msg(m_serial)

    assert respuesta == {"error":"Error al enviar"}

    url = "http://localhost:5000/asocia"
    datos = '{"id_mesa": "1","id_m_cliente":"M-001"}'

    m_post.assert_called_once_with(url,json=json.loads(datos))
