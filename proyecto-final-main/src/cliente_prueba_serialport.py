# Escribe tu código aquí :-)
import radio
from microbit import *

#Prueba de microbit cliente para llevar para probar puerto-serie, tanto aviso al cliente de pedido listo, como asociacio cliente-mesa

ID_MICROBIT = "M-002" #Cambiar identificador para flashear en otro microbit: Cambiar a M-001 por ejemplo

def main():
    radio.on()
    radio.config(length=64)
    radio.config(power=7)
    while True:
        display.show('2') #Cambar valor para identificar que micorbit es: M-001 = 1, M-002 = 2
        sleep(500)
        received = radio.receive()
        if received != None:
            msg = received.split(",")
            if msg[0] == "aviso" and msg[1] == ID_MICROBIT: #Verifica si el aviso es para ese microbit o no
                while not button_a.was_pressed(): #Envia aviso luminico y acustico al microbit. Cuando se pulse el boton A, el aviso deja de emitirse
                    display.show(Image.SQUARE_SMALL)
                    audio.play(Sound.TWINKLE)
                    sleep(500)
                    display.show(Image.SQUARE)
                    audio.stop()
                    sleep(500)
        if button_b.was_pressed(): #Simulacion de asociacion cliente-mesa (PRUEBA)
            radio.send('Asocia,2,' + ID_MICROBIT)
            display.show(Image.YES)
            sleep(500)
            display.clear()




	
if __name__ == "__main__":
    main()
