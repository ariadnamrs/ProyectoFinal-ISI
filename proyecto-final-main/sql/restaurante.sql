CREATE TABLE M_mesa
(
	id_microbit INT PRIMARY KEY,
    n_mesa INT
);

CREATE TABLE M_cliente
(
	id_microbit INT PRIMARY KEY,
	n_microbit INT NOT NULL
);

CREATE TABLE M_camarero
(
	id_microbit INT PRIMARY KEY
);

CREATE TABLE Asocia_m_cliente_m_mesa
(
	id_m_cliente INT,
    id_mesa INT,
    fecha_asociacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_m_cliente, id_mesa, fecha_asociacion),
    FOREIGN KEY (id_m_cliente) REFERENCES M_cliente (id_microbit),
    FOREIGN KEY (id_mesa) REFERENCES M_mesa (id_microbit)
    
);

CREATE TABLE Pedido
(
	n_pedido INTEGER PRIMARY KEY AUTOINCREMENT,
    Estado VARCHAR(20) NOT NULL,
    id_m_cliente INT,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_m_cliente) REFERENCES M_cliente (id_microbit)
		ON DELETE CASCADE
);


CREATE TABLE Cliente
(
	n_cliente INT PRIMARY KEY
);

CREATE TABLE Pide
(
	n_pedido INT,
    n_cliente INT,
	PRIMARY KEY (n_cliente, n_pedido),
	FOREIGN KEY (n_cliente) REFERENCES Cliente,
    FOREIGN KEY (n_pedido) REFERENCES Pedido
);

CREATE TABLE Camarero
(
	nif VARCHAR(10) PRIMARY KEY,
    nombre VARCHAR(20)
);

CREATE TABLE Sirve
(
	nif VARCHAR(10),
    n_pedido INT NOT NULL,
    PRIMARY KEY(nif,n_pedido),
    FOREIGN KEY (n_pedido) REFERENCES Pedido,
    FOREIGN KEY (nif) REFERENCES Camarero
    
);

CREATE TABLE Asocia_camarero_m_camarero
(
	id_m_camarero INT,
    nif VARCHAR(10),
    PRIMARY KEY(nif,id_m_camarero),
	FOREIGN KEY (id_m_camarero) REFERENCES M_camarero (id_microbit),
    FOREIGN KEY (nif) REFERENCES Camarero
);

/*Clientes*/

INSERT INTO "main"."M_cliente" ("id_microbit", "n_microbit") VALUES ('b''\xf6\xd5}\xa3Ny\xbb!''', 'M-001');
INSERT INTO "main"."M_cliente" ("id_microbit", "n_microbit") VALUES ('b''}\xf7\x1a\x1fE<\xed\x0c''', 'M-002');
INSERT INTO "main"."M_cliente" ("id_microbit", "n_microbit") VALUES ('b"''x\xb4\x19F\xc5\xc9\xd6"', 'O-001');

/*Mesas*/
INSERT INTO "main"."M_mesa" ("id_microbit", "n_mesa") VALUES ('b''\xf9\x9e\xf02\x18\xccX\x17''', '1');
INSERT INTO "main"."M_mesa" ("id_microbit", "n_mesa") VALUES ('b''\x13\xaf\xe8J=o\x1b`''', '2');
INSERT INTO "main"."M_mesa" ("id_microbit", "n_mesa") VALUES ('b''m\xe7\x7f\xf8g^X\xed''', '3');
INSERT INTO "main"."M_mesa" ("id_microbit", "n_mesa") VALUES ('b''f\xc3n\xb56rf6''', 'M');

/*Camareros*/
INSERT INTO "main"."M_camarero" ("id_microbit") VALUES ('b''hz\xb9\x8bT+4\xb6''');



