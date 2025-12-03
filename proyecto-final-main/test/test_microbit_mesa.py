import pytest
import microbit_mesa

def test_microbit_mesa(mocker):
    accel_mock = mocker.patch('microbit_mesa.accelerometer')
    radio_mock = mocker.patch('microbit_mesa.radio')
        
    radio_mock.send('id de microbit mesa')    
    assert radio_mock.send()
    assert radio_mock.receive_full()
    

    # Para testeat el acelerometro asignamos valores aleatorios a cada eje del acelerómetro
    accel_mock.get_x.side_effect = [919, 910, 895, 900, 920, 946, 888, 901, 904, 908]
    accel_mock.get_y.side_effect = [-100, -140, -138, -123, -143, -123, -198, -167, -200]
    accel_mock.get_z.side_effect = [10, 12, 67, 34, 27, 18, 19, 25, 89, 54]

    
    radio_mock.send(accel_mock.get_x, accel_mock.get_y, accel_mock.get_z)
    assert radio_mock.send()
    assert radio_mock.receive_full()

