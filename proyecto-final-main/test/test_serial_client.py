import pytest
import requests
from serial import Serial
from serial.tools import list_ports
import serial_client

def test_receieve_msg_radio(mocker):
    m_radio = mocker.patch("microbit.radio")
    m_uart = mocker.patch("microbit.uart")

    m_radio.receive.return_value = "Hola"
    m_uart.read.return_value = None

    response = serial_client.receieve_msg_radio()

    assert response == "Hola"
    m_radio.receive.assert_called_once()

def test_send_msg(mocker):
    m_radio = mocker.patch("microbit.radio")
    m_uart = mocker.patch("microbit.uart")

    m_uart.read.return_value = b"hola"

    serial_client.main()

    m_radio.send.assert_called_once_with(b"hola")

def test_no_msg(mocker):
    m_radio = mocker.patch("microbit.radio")
    m_uart = mocker.patch("microbit.uart")

    m_radio.receive.return_value = None
    m_uart.read.return_value = None

    serial_client.main()

    m_radio.send.assert_not_called()

