from microbit import *
import radio

  #Funcionalidad del Microbit-Camarero:
  # El camarero del restaurante cuando un pedido esta listo, se encarga de coger dicho pedido
  # y entregarlo al usuario correspondiente. Para ello, a traves de la interfaz obtiene la informacion
  # necesaria para entregar el pedido. Una vez entregado, recoge el microbit del usuario y lo devuelve al mostrador, si
  # se le olvida recoger el microbit del cliente, se tiene que mandar un mensaje a todos los camareros para que uno de ellos
  # recoga el microbit del cliente

  def main():
      MESSAGE_WARNING = "MFT" #Mensaje de microbit olvidado: microbit forgotten
      radio.on()
      while True:
          sleep(10)
          received = radio.receive_full() # Bucle para recibir mensajes

          if received is not None:  #Si lo recibido es distinto de None
              message = received[0]
              msg = str(message[3:], 'utf-8')
              mesa = str(msg[3:], 'utf-8')
              print("Mensaje recibido: " + mesa) #Depurar
              if msg.find(MESSAGE_WARNING) != -1: #Si el mensaje es que se ha olvidado un microbit
                  display.show(mesa)
                  sleep(100)
                  display.show(Image.ANGRY)
                  audio.play(Sound.MYSTERIOUS)#Cara de enfado

          display.clear() #Si el mensaje no es MFT, entonces, limpiamos la pantalla y mostramos un cara sonriente para indicar que todo va bien
          display.show(Image.HAPPY)


  if __name__ == "__main__":
      main()




