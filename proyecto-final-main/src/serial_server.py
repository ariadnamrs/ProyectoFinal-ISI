import time
import serial
import serial.tools.list_ports as list_ports
import requests, json
from threading import Thread

PID_MICROBIT = 516
VID_MICROBIT = 3368
TIMEOUT = 0.1

# Look for serial port where micro:bit is connected
def find_comport(pid, vid, baud):
    ''' return a serial port '''
    ser_port = serial.Serial(timeout=TIMEOUT)
    ser_port.baudrate = baud
    ports = list(list_ports.comports())
    print('scanning ports')
    for p in ports:
        print('port: {}'.format(p))
        try:
            print('pid: {} vid: {}'.format(p.pid, p.vid))
        except AttributeError:
            continue
        if (p.pid == pid) and (p.vid == vid):
            print('found target device pid: {} vid: {} port: {}'.format(
                p.pid, p.vid, p.device))
            ser_port.port = str(p.device)
            return ser_port
    return None

def recibir_mandar_msg(ser_micro):
    while True:
        time.sleep(0.01)

        # Has the micro:bit sent any bytes?
        line = ser_micro.readline().decode('utf-8')
        if line:
            new_line = line.strip()
            #print(new_line)
            # Divide el mensaje en partes
            msg = new_line.split(" ")
            print(msg)
            if "ASC" in msg:
                print("Asociando: ", line)
                # Convierte las partes en un diccionario
                datos = {
                    "id_mesa": msg[2],
                    "id_m_cliente": msg[0] 
                }
                # Convierte a JSON
                response = requests.post("http://localhost:5000/asocia", json=datos)
    ser_micro.close()


def enviar_aviso_microbit_cliente(id_cliente):
    mensaje = 'aviso,' + id_cliente
    if ser_micro and ser_micro.is_open:
        ser_micro.write(mensaje.encode('utf-8'))
        print(f"Aviso enviado al micro:bit para el cliente {id_cliente}")

def aviso_microbit_camarero(mensaje):
    print(mensaje)
    ser_micro.write(mensaje.encode('utf-8'))
    print("Mensaje enviado a los camareros")

def main():
    detected = False

    try:
        while not detected:
            global ser_micro  # Declara ser_micro como global
            ser_micro = find_comport(PID_MICROBIT, VID_MICROBIT, 115200)
            if (ser_micro == None):
                print("Conecta el serial port al ordenador")
                time.sleep(10)
            else:
                detected = True
                print("opening and monitoring microbit port")
                ser_micro.open()
                t = Thread(target=recibir_mandar_msg, args=[ser_micro])
                t.start()

    except AttributeError:
        print("Conecta microbit puerto serie para arrancar el servidor")


