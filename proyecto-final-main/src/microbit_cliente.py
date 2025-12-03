# El microbit del cliente es el que recibe

import radio
import machine
from microbit import *


# b'\xf9\x9e\xf02\x18\xccX\x17' microbit que está conectado al externo

PX_MINIMA = -50
MESSAGE_CLIENTE = "Accelerometer"
MESSAGE_ASOCIACION = "ASC"

# Implementación DTW
def dtw_restringido_puro(secuencia_1, secuencia_2, w):  # Usar para comparar los acelerometros en cada eje de los microbits
    n = len(secuencia_1)
    m = len(secuencia_2)
    w = max(w, abs(n - m))  # Asegurar que la banda cubra la diferencia mínima

    # Crear matriz de costos inicializada en infinito
    dtw_matrix = [[float('inf') for _ in range(m + 1)] for _ in range(n + 1)]
    dtw_matrix[0][0] = 0

    # Llenar la matriz dentro de la banda
    for i in range(1, n + 1):
        for j in range(max(1, i - w), min(m + 1, i + w + 1)):
            cost = abs(secuencia_1[i - 1] - secuencia_2[j - 1])
            dtw_matrix[i][j] = cost + min(
                dtw_matrix[i - 1][j],     # Inserción
                dtw_matrix[i][j - 1],     # Eliminación
                dtw_matrix[i - 1][j - 1]  # Sustitución
            )

    # La distancia DTW está en la esquina inferior derecha
    distancia = dtw_matrix[n][m]

    return distancia, dtw_matrix

# Recolectar datos del acelerómetro
def collect_accel_data():
    """
    Recopila datos del acelerómetro durante un tiempo determinado.
    :return: Lista de tuplas (x, y, z).
    """
    dataX = []
    dataY = []
    dataZ = []
    for _ in range(10):
        x = accelerometer.get_x()
        y = accelerometer.get_y()
        z = accelerometer.get_z()
        dataX.append(x)
        dataY.append(y)
        dataZ.append(z)
        sleep(10)

    return dataX, dataY, dataZ


def main():
    radio.on()
    posible_mesa = []
    posible_asociacion = {}
    id_mesa_conectado = None
    contador = 0
    MESSAGE_ACCELEROMETER = "Accelerometer"
    id_cliente = machine.unique_id()

    radio.config(power=7, length=251, queue=50)
    display.show(Image.TRIANGLE)
    while True:
        sleep(10)
        contador += 10
        received = radio.receive_full()

        while received != None:
            mensaje = received[0]
            dBm = received[1]
            contenido = str(mensaje[3:], 'utf-8')
            x = contenido.find(" ")
            id = contenido[:x]
            msg = contenido[x+1:]
            print(id_mesa_conectado)
            if id == id_mesa_conectado and dBm < PX_MINIMA: # Si recibo un mensaje de la mesa a la que estaba conectada por debajo del umbral de potencia me desconecto
                id_mesa_conectado = None
                display.show(Image.TRIANGLE)
                contador = 0
            elif dBm > PX_MINIMA and msg.find("ASC") == -1 and msg.find("Accelerometer") == -1 and msg.find("MFT") == -1 and id_mesa_conectado == None:
                if id not in posible_mesa:
                    posible_mesa.append(id)
                elif len(msg) != 0:  # Aquí entramos cuando ya hemos pedido los acelerómetros y queremos compararlos con el nuestro
                    clean = msg.strip("[]")
                    print("Aqui peta: ", clean)
                    accelMesa = list(map(int, clean.split(",")))
                    i = 0
                    accelMesaX = []
                    accelMesaY = []
                    accelMesaZ = []
                    while i <= len(accelMesa)-1:
                        accelMesaX.append(accelMesa[i])
                        accelMesaY.append(accelMesa[i+1])
                        accelMesaZ.append(accelMesa[i+2])
                        i += 3
                    accelClienteX, accelClienteY, accelClienteZ = collect_accel_data()

                    distanciaX = 0
                    distanciaY = 0
                    distanciaZ = 0
                    distancia_total = 0
                    matrizX = []
                    matrizY = []
                    matrizZ = []
                    distanciaX, matrizX = dtw_restringido_puro(accelMesaX, accelClienteX, 2)
                    distanciaY, matrizY = dtw_restringido_puro(accelMesaY, accelClienteY, 2)
                    distanciaZ, matrizZ = dtw_restringido_puro(accelMesaZ, accelClienteZ, 2)
                    distancia_total = distanciaX + distanciaY + distanciaZ
                    posible_asociacion[id] = distancia_total

                    if len(posible_mesa) == len(posible_asociacion) and contador >= 5000:
                        print(posible_mesa)
                        min_distancia = min(posible_asociacion.values())  # Lo pilla bien
                        clave = None
                        for key, value in posible_asociacion.items():
                            if value == min_distancia:
                                id_mesa_conectado = key
                                break

                        print("-----------------------------")
                        print("Conectado a mesa: " + str(id_mesa_conectado))
                        print("-----------------------------")
                        display.show(Image.HEART)
                        msg_asociacion = str(id_cliente) + " " + MESSAGE_ASOCIACION + " " + str(id_mesa_conectado)
                        radio.send(msg_asociacion)
                        posible_mesa.clear()
                        posible_asociacion.clear()
                        contador = 0


            received = radio.receive_full()

        if contador == 5000:
            for id_mesa in posible_mesa:
                mensaje = id_mesa + " " + MESSAGE_ACCELEROMETER
                radio.send(mensaje)
        elif contador == 10000:
            reset()

if __name__ == "__main__":
    main()

