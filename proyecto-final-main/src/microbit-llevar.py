# Escribe tu código aquí :-)
import radio
import machine
from microbit import *

ID_MICROBIT = machine.unique_id()
PX_MINIMA = -50
ID_MOSTRADOR = b'f\xc3n\xb56rf6'
MESSAGE_ASOCIACION = "ASC"

def main():
    radio.on()
    radio.config(power=7, length=251, queue=50)
    id_mostrador_conectado = None
    contador = 0
    display.show(Image.TRIANGLE)
    while True:
        sleep(50)
        received = radio.receive_full()
        if received is not None:
            mensaje = received[0].decode('utf-8')
            px = received[1]
            msg = mensaje[3:].split(",")
            id = msg[0].strip()

            if msg[0] =="aviso" and msg[1] == str(ID_MICROBIT):
                while not button_a.was_pressed():
                    display.show(Image.PACMAN)
                    audio.play(Sound.HELLO)
                    sleep(250)

            elif id == str(ID_MOSTRADOR) and px >= PX_MINIMA:
                contador += 1
                #display.show(Image.HAPPY)
                if contador == 20 and id_mostrador_conectado is None:
                    id_mostrador_conectado = id
                    radio.send(MESSAGE_ASOCIACION + " " + str(ID_MICROBIT) + " " + str(ID_MOSTRADOR))
                    display.show(Image.HEART)
                    contador = 0
                elif id_mostrador_conectado is not None:
                    display.show(Image.HEART)

            elif id == str(ID_MOSTRADOR) and px < PX_MINIMA:
                contador = 0
                id_mostrador_conectado = None
                display.show(Image.TRIANGLE)




#Falta todavia meter como asociar este microbit con el mostrador para poder volver a utilzarlo

if __name__ == "__main__":
    main()
