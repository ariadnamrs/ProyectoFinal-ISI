import radio
import machine

from microbit import *

# Id de mesa 3 -> b'm\xe7\x7f\xf8g^X\xed'

def collect_accel_data():

    data = []
    for _ in range(10):
        x = accelerometer.get_x()
        y = accelerometer.get_y()
        z = accelerometer.get_z()
        data.append(x)
        data.append(y)
        data.append(z)
        sleep(10)

    return data


def main():
    radio.on()
    id_mesa = machine.unique_id()
    print(id_mesa)
    mensaje_mesa = str(id_mesa) + " "
    MESSAGE_CLIENTE = "Accelerometer"
    MESSAGE_ASOCIACION = "ASC"

    radio.config(power=7, length=251)
    while True:
        sleep(1000)
        display.show("3")
        radio.send(mensaje_mesa)

        received = radio.receive_full() #Recibo mensajes
        while received:
            if received != None:
                mensaje = received[0]
                dBm = received[1]
                contenido = str(mensaje[3:], 'utf-8')
                x = contenido.find(" ")
                id = contenido[:x]
                msg = contenido[x+1:]
                if msg == MESSAGE_CLIENTE:
                    accel = collect_accel_data()
                    datos = str(id_mesa) + " " + str(accel)
                    radio.send(datos)

            received = radio.receive_full() #Recibo mensajes

if __name__ == "__main__":
    main()
