# This code runs on the micro:bit

from microbit import *
import radio
import machine

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
    uart.init(baudrate=115200)
    radio.on()
    id_mesa = machine.unique_id()
    mensaje_mesa = str(id_mesa) + " "
    MESSAGE_CLIENTE = "Accelerometer" # Pido el acelerometro
    MESSAGE_ASOCIACION = "ASC"
    radio.config(power=7, length=251, queue=50)
    print(mensaje_mesa)
    while True:
        sleep(100)
        # Has the server sent any bytes?
        msg = uart.read()
        if (msg != None):
            #display.show(str(msg, 'UTF-8'))
            # Sends a msg replying to the one received
            print(msg)
            radio.send(msg)
        else:
            display.clear()

        radio.send(mensaje_mesa) #Envio mensaje de mostrador
        received = radio.receive_full()
        if received != None:
            mensaje = received[0]
            dBm = received[1]
            contenido = str(mensaje[3:], 'utf-8')
            x = contenido.find(" ")
            id = contenido[:x]
            msg = contenido[x+1:]
            # print("Mensaje: " + id + " -> " + msg)
            if msg == MESSAGE_CLIENTE: #Si el mensaje recibido es Give me the accelerometer
                accel = collect_accel_data()
                datos = str(id_mesa) + " " + str(accel)
                radio.send(datos)

            elif msg.startswith(MESSAGE_ASOCIACION):
                print(contenido)





if __name__ == "__main__":
    main()

