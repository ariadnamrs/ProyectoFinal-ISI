import restaurante_controller
import pytest

# Test de la función get_pedidos
def test_get_pedidos(mocker):
    # Mockear la base de datos y el cursor
    mock_db = mocker.Mock()
    mock_cursor = mocker.Mock()
    
    # Configurar los valores de retorno de los mocks
    mock_db.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [            
        (1, "M-001", 12),  # Simula un pedido con mesa asociada
        (2, "M-002", None)] #Simula pedido sin mesa
    
    # Mockear la función get_db para que devuelva el mock de la base de datos
    mocker.patch('restaurante_controller.get_db', return_value=mock_db)
    
    # Llamar a la función a probar
    result = restaurante_controller.get_pedidos()
    
    # Verificar los resultados
    assert result == [            
        {"n_pedido": 1, "id_m_cliente": "M-001", "id_mesa": 12},
        {"n_pedido": 2, "id_m_cliente": "M-002", "id_mesa": None}]

    mock_cursor.execute.assert_called_once_with("""
                SELECT n_pedido, Pedido.id_m_cliente, Asocia_m_cliente_m_mesa.id_mesa FROM Pedido
                LEFT JOIN Asocia_m_cliente_m_mesa
                ON Pedido.id_m_cliente = Asocia_m_cliente_m_mesa.id_m_cliente
                WHERE Pedido.estado = "En curso"
                GROUP BY n_pedido
                """)

def test_get_n_pedido(mocker):
    # Resultado esperado del mock
    mock_result = {12}

    # Mockear la base de datos y el cursor
    mock_db = mocker.Mock()
    mock_cursor = mocker.Mock()

    # Configurar los valores de retorno de los mocks
    mock_db.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = mock_result

    # Mockear la función get_db para que devuelva el mock de la base de datos
    mocker.patch('restaurante_controller.get_db', return_value=mock_db)

    # Llamar a la función a probar
    result = restaurante_controller.get_n_pedido(1)

    # Verificar los resultados
    assert result == mock_result

    # Verificar que se llamó a la consulta con el parámetro correcto
    mock_cursor.execute.assert_called_once_with(
        "SELECT id_m_cliente FROM Asocia_m_client_pedido WHERE n_pedido = ?", [1]
    )


def test_get_n_pedido_not_db(mocker):

    #Resultado del mock
    mock_result = None
        # Mockear la base de datos y el cursor
    mock_db = mocker.Mock()
    mock_cursor = mocker.Mock()
    
    # Configurar los valores de retorno de los mocks
    mock_db.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = mock_result
    
    # Mockear la función get_db para que devuelva el mock de la base de datos
    mocker.patch('restaurante_controller.get_db', return_value=mock_db)
    
    # Llamar a la función a probar
    result = restaurante_controller.get_n_pedido(1)
    
    # Verificar los resultados
    assert result == mock_result
    # Verificar que se llamó a la consulta con el parámetro correcto
    mock_cursor.execute.assert_called_once_with(
        "SELECT id_m_cliente FROM Asocia_m_client_pedido WHERE n_pedido = ?", [1]
    )

# Test de la función insert_pedido
def test_insert_correct_pedido(mocker):
    # Mockear la base de datos y el cursor
    mock_db = mocker.Mock()
    mock_cursor = mocker.Mock()
    
    # Configurar los valores de retorno de los mocks
    mock_db.cursor.return_value = mock_cursor
    
    # Mockear la función get_db para que devuelva el mock de la base de datos
    mocker.patch('restaurante_controller.get_db', return_value=mock_db)
    
    # Llamar a la función a probar
    n_pedido = 1
    id_m_cliente = 2
    estado = "En curso"
    result = restaurante_controller.insert_pedido(n_pedido, id_m_cliente,estado)
    
    # Verificar los resultados
    assert result is True
    mock_cursor.execute.assert_called_once_with("INSERT INTO Pedido(id_m_cliente, n_pedido, estado) VALUES (?, ?, ?)", [id_m_cliente, n_pedido, estado])
    mock_db.commit.assert_called_once()

def test_asocia_mesa_cliente(mocker):
    # Mockear la base de datos y el cursor
    mock_db = mocker.Mock()
    mock_cursor = mocker.Mock()
    
    # Configurar los valores de retorno de los mocks
    mock_db.cursor.return_value = mock_cursor
    
    # Mockear la función get_db para que devuelva el mock de la base de datos
    mocker.patch('restaurante_controller.get_db', return_value=mock_db)
    id_m_cliente = 3
    id_mesa = 12

    result = restaurante_controller.asocia(id_m_cliente, id_mesa)
    assert result is True
    mock_cursor.execute.assert_called_once_with("INSERT INTO Asocia_m_cliente_m_mesa(id_m_cliente, id_mesa) VALUES (?, ?)", [id_m_cliente, id_mesa])
    mock_db.commit.assert_called_once()

def test_update_pedido(mocker):
    # Mockear la base de datos y el cursor
    mock_db = mocker.Mock()
    mock_cursor = mocker.Mock()
    
    # Configurar los valores de retorno de los mocks
    mock_db.cursor.return_value = mock_cursor
    
    # Mockear la función get_db para que devuelva el mock de la base de datos
    mocker.patch('restaurante_controller.get_db', return_value=mock_db)
    n_pedido = 1
    result = restaurante_controller.update_pedido(n_pedido)
    assert result == True
    mock_cursor.execute.assert_called_once_with("""UPDATE Pedido SET estado = "Finalizado" WHERE n_pedido = ?""", [n_pedido])
    mock_db.commit.assert_called_once()

