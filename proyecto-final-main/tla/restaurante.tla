---- MODULE restaurante ----
EXTENDS Sequences,FiniteSets, Integers

CONSTANT 
    MAX_M_MESA,       \* maximo numero de mesas
    MAX_M_CLIENTE,    \* maximo numero de balizas
    MICRO_MESA,       \* conjunto de las mesas
    MICRO_CLIENT      \* conjunto de las balizas  

ASSUME MAX_M_MESA >= Cardinality(MICRO_MESA) 
ASSUME MAX_M_CLIENTE >= Cardinality(MICRO_CLIENT)

(*--algorithm RestauranteMicro {
variables 
    pedidos = [cliente \in MICRO_CLIENT |-> ""],
    mesas = [m_mesas \in MICRO_MESA |-> {}],
    pendientes = <<>>,
    llevar = 0,
    aqui = 0

define {

    (* Propiedad de tipo Safety                                               *)
    (* Compueba que la cantidad de mesas no sea superior al número de balizas *)
    NoMasMesasQueClient == Cardinality(MICRO_MESA) =< Cardinality(MICRO_CLIENT)
    
    (* Propiedad de tipo Safety                                               *)
    (* Cada baliza solo puede ser asociada a un pedido                        *)
    UnSoloPedidoPorClient == \A client \in MICRO_CLIENT : 
                            pedidos[client] /= "" => \E m \in MICRO_MESA: pedidos[client] = m \/ pedidos[client] = "Llevar"
    
    (* Propiedad de tipo Safety                                               *)
    (* El mismo cliente no puede estar asociado a dos balizas                 *)
    NoDuplicadoClient == \A client \in MICRO_CLIENT : \E m1,m2 \in MICRO_MESA : m1 /= m2 =>
                            \/ /\ mesas[m1] = client
                               /\ mesas[m2] /= client
                            \/ /\ mesas[m1] /= client
                               /\ mesas[m2] = client
    
    (* Propiedad de tipo Liveness                                               *)
    (* Por siempre, de manera eventual, cuando haya pedidos pendientes, estos   *)
    (* seran atendidos, no necesariamente todos de golpe                        *)
    PendientesEventualVacio == []<>(Len(pendientes) > 0 ~>  (Len(pendientes) = 0))

    (* Propiedad de tipo Liveness                                               *)
    (* Para todos las balizas se cumple que cuando haya un pedido asociado a    *)
    (* ella, de manera eventual, no necesaria en un paso, esa baliza quedará    *)
    (* libre para ser usado.                                                    *)
    SeEntregaPedido == \A client \in MICRO_CLIENT: (pedidos[client] /= "" ~>  pedidos[client] = "")

    (* Propiedad de tipo Liveness                                               *)
    (* Para todos las mesas se cumple que cuando haya una mesa ocupada implica, *)
    (* que de forma eventual, esa mesa se quedará libre                         *)
    SeVaciaMesa == \A mesa \in MICRO_MESA: mesas[mesa] /= {} => <> (mesas[mesa] = {})
}

(* Proceso Realizar Pedido, se ejecuta siempre que la suma de pedidos para      *)
(* llevar y aquí sea menor que 5.                                               *)
(* Con cualquier baliza, cuando no haya un pedido asociada a ella, pueden       *)
(* ocurrir dos cosas, que el pedido sea para llevar o que sea para comer        *)
(* en el restaurante. En ambos añadidmos el pedido a pendientes y               *)
(* actualizamos el pedido de la baliza, en el caso de comer aquí, actualizamos  *)
(* la asociacion entre la mesa y la baliza                                      *)

fair process (RealizarPedido = "realizarpedido")
{   RealizarPedido:
    while (llevar + aqui < 5 ) {
        with (client \in MICRO_CLIENT) { 
            when(pedidos[client] = "");  
            either{ 
                pedidos[client] := "Llevar";
                pendientes := Append(pendientes,<<client>>)
            }
            or{
                with ( mesa \in MICRO_MESA){
                    pedidos[client] := mesa;
                    mesas[mesa] := mesas[mesa] \cup {client}; 
                    pendientes := Append(pendientes,<<client,mesa>>)
                }
            }
        }
    }
}

(* Proceso Cambio de mesa, se ejecuta siempre que la suma de pedidos para      *)
(* llevar y aquí sea menor que 5.                                               *)
(* Con cualquier baliza, cuando haya un pedido asociada a ella y además,        *)
(* no sea para llevar. Con cualquier mesa, siempre que no sea la mesa en        *)
(* la que ya está sentado, se podrá realizar el cambio.                         *)
(* Para ello, actualizamos la funcion mesas cambiando unicamente el valor de    *)
(* la antigua mesa, la nueva mesa y la informacion del pedido.                  *)

fair process (CambioMesa = "cambiomesa"){
    CambioMesa:
    while(llevar + aqui < 5){
        with(client \in MICRO_CLIENT){
            when(pedidos[client] /= "" /\ pedidos[client] /= "Llevar");
            with(mesa_nueva \in MICRO_MESA){
                when(mesa_nueva /= pedidos[client]);
                mesas := [mesas EXCEPT ![pedidos[client]] = mesas[pedidos[client]] \ {client},
                                       ![mesa_nueva] = mesas[mesa_nueva] \cup {client}];
                pedidos := [pedidos EXCEPT ![client] = mesa_nueva];
            }
        }
    }
}


(* Proceso Manejar pedido, se ejecuta siempre que la suma de pedidos para       *)
(* llevar y aquí sea menor que 5.                                               *)
(* Cuando la longitud de los pedidos pendientes sea distinto de 0,              *)
(* me quedo con el primer pedido, actualizando los pedidos pendientes.          *)
(* Cuando el primer pedido tenga una logitud mayor a 0, pueden ocurrir dos      *)
(* cosas, o que sea un pedido para llevar, en cuyo caso la longitud del pedido  *)
(* debe de ser uno, o que sea para comer aqui, en cuyo caso la longituf será    *)
(* dos. En ambos actualizo las funciones pertinentes.                           *)

fair process (ManejarPedido = "manejarpedido")
    variable pedido = <<>>;
{   ManejarPedido:
    while (llevar + aqui < 5) {
        when(Len(pendientes) /= 0);
        pedido := Head(pendientes);
        pendientes := Tail(pendientes);
        when(Len(pedido) > 0);
        either{
            when(Len(pedido) = 2 /\ pedido[2] /= "");
            mesas := [mesas EXCEPT ![pedido[2]] = mesas[pedido[2]] \ {pedido[1]}];
            aqui := aqui + 1;
            pedidos := [pedidos EXCEPT ![pedido[1]] = ""];
        }or{
            when(Len(pedido) = 1);
            pedidos := [pedidos EXCEPT ![pedido[1]] = ""];
            llevar := llevar + 1;
        }
    }}

(* Proceso Entregar pedidos finales.                                            *)
(* Cuando  la suma de pedidos llevar y aquí sea mayor o igual                   *)
(* a 5 y aun queden pedidos pendientes.                                         *)
(* Siguiendo la misma lógica que el proceso Manejar pedido, acaba de entregar   *)
(* aquellos pedidos que no se entregaron debido a la restricion de 5 pedidos.   *)
fair process (EntregarPedidosFinales = "entregarpedidosfinales")
    variable pedido = <<>>;
{
    EntregarPedidosFinales:
    while(TRUE){
        when(llevar + aqui >= 5 /\ Len(pendientes) /= 0);
        when(Len(pendientes) /= 0);
        pedido := Head(pendientes);
        pendientes := Tail(pendientes);
        when(Len(pedido) > 0);
        either{
            when(Len(pedido) = 2 /\ pedido[2] /= "");
            mesas := [mesas EXCEPT ![pedido[2]] = mesas[pedido[2]] \ {pedido[1]}];
            aqui := aqui + 1;
            pedidos := [pedidos EXCEPT ![pedido[1]] = ""];
        }or{
            when(Len(pedido) = 1);
            pedidos := [pedidos EXCEPT ![pedido[1]] = ""];
            llevar := llevar + 1;
        }
    }
}
}
*)
\* BEGIN TRANSLATION (chksum(pcal) = "47d7aba" /\ chksum(tla) = "e22ae2e1")
\* Label RealizarPedido of process RealizarPedido at line 55 col 5 changed to RealizarPedido_
\* Label CambioMesa of process CambioMesa at line 75 col 5 changed to CambioMesa_
\* Label ManejarPedido of process ManejarPedido at line 91 col 5 changed to ManejarPedido_
\* Label EntregarPedidosFinales of process EntregarPedidosFinales at line 112 col 5 changed to EntregarPedidosFinales_
\* Process variable pedido of process ManejarPedido at line 89 col 14 changed to pedido_
VARIABLES pc, pedidos, mesas, pendientes, llevar, aqui

(* define statement *)
NoMasMesasQueClient == Cardinality(MICRO_MESA) =< Cardinality(MICRO_CLIENT)



UnSoloPedidoPorClient == \A client \in MICRO_CLIENT :
                        pedidos[client] /= "" => \E m \in MICRO_MESA: pedidos[client] = m \/ pedidos[client] = "Llevar"



NoDuplicadoClient == \A client \in MICRO_CLIENT : \E m1,m2 \in MICRO_MESA : m1 /= m2 =>
                        \/ /\ mesas[m1] = client
                           /\ mesas[m2] /= client
                        \/ /\ mesas[m1] /= client
                           /\ mesas[m2] = client




PendientesEventualVacio == []<>(Len(pendientes) > 0 ~>  (Len(pendientes) = 0))




SeEntregaPedido == \A client \in MICRO_CLIENT: (pedidos[client] /= "" ~>  pedidos[client] = "")

SeVaciaMesa == \A mesa \in MICRO_MESA: mesas[mesa] /= {} => <> (mesas[mesa] = {})

VARIABLES pedido_, pedido

vars == << pc, pedidos, mesas, pendientes, llevar, aqui, pedido_, pedido >>

ProcSet == {"realizarpedido"} \cup {"cambiomesa"} \cup {"manejarpedido"} \cup {"entregarpedidosfinales"}

Init == (* Global variables *)
        /\ pedidos = [cliente \in MICRO_CLIENT |-> ""]
        /\ mesas = [m_mesas \in MICRO_MESA |-> {}]
        /\ pendientes = <<>>
        /\ llevar = 0
        /\ aqui = 0
        (* Process ManejarPedido *)
        /\ pedido_ = <<>>
        (* Process EntregarPedidosFinales *)
        /\ pedido = <<>>
        /\ pc = [self \in ProcSet |-> CASE self = "realizarpedido" -> "RealizarPedido_"
                                        [] self = "cambiomesa" -> "CambioMesa_"
                                        [] self = "manejarpedido" -> "ManejarPedido_"
                                        [] self = "entregarpedidosfinales" -> "EntregarPedidosFinales_"]

RealizarPedido_ == /\ pc["realizarpedido"] = "RealizarPedido_"
                   /\ IF llevar + aqui < 5
                         THEN /\ \E client \in MICRO_CLIENT:
                                   /\ (pedidos[client] = "")
                                   /\ \/ /\ pedidos' = [pedidos EXCEPT ![client] = "Llevar"]
                                         /\ pendientes' = Append(pendientes,<<client>>)
                                         /\ mesas' = mesas
                                      \/ /\ \E mesa \in MICRO_MESA:
                                              /\ pedidos' = [pedidos EXCEPT ![client] = mesa]
                                              /\ mesas' = [mesas EXCEPT ![mesa] = mesas[mesa] \cup {client}]
                                              /\ pendientes' = Append(pendientes,<<client,mesa>>)
                              /\ pc' = [pc EXCEPT !["realizarpedido"] = "RealizarPedido_"]
                         ELSE /\ pc' = [pc EXCEPT !["realizarpedido"] = "Done"]
                              /\ UNCHANGED << pedidos, mesas, pendientes >>
                   /\ UNCHANGED << llevar, aqui, pedido_, pedido >>

RealizarPedido == RealizarPedido_

CambioMesa_ == /\ pc["cambiomesa"] = "CambioMesa_"
               /\ IF llevar + aqui < 5
                     THEN /\ \E client \in MICRO_CLIENT:
                               /\ (pedidos[client] /= "" /\ pedidos[client] /= "Llevar")
                               /\ \E mesa_nueva \in MICRO_MESA:
                                    /\ (mesa_nueva /= pedidos[client])
                                    /\ mesas' = [mesas EXCEPT ![pedidos[client]] = mesas[pedidos[client]] \ {client},
                                                              ![mesa_nueva] = mesas[mesa_nueva] \cup {client}]
                                    /\ pedidos' = [pedidos EXCEPT ![client] = mesa_nueva]
                          /\ pc' = [pc EXCEPT !["cambiomesa"] = "CambioMesa_"]
                     ELSE /\ pc' = [pc EXCEPT !["cambiomesa"] = "Done"]
                          /\ UNCHANGED << pedidos, mesas >>
               /\ UNCHANGED << pendientes, llevar, aqui, pedido_, pedido >>

CambioMesa == CambioMesa_

ManejarPedido_ == /\ pc["manejarpedido"] = "ManejarPedido_"
                  /\ IF llevar + aqui < 5
                        THEN /\ (Len(pendientes) /= 0)
                             /\ pedido_' = Head(pendientes)
                             /\ pendientes' = Tail(pendientes)
                             /\ (Len(pedido_') > 0)
                             /\ \/ /\ (Len(pedido_') = 2 /\ pedido_'[2] /= "")
                                   /\ mesas' = [mesas EXCEPT ![pedido_'[2]] = mesas[pedido_'[2]] \ {pedido_'[1]}]
                                   /\ aqui' = aqui + 1
                                   /\ pedidos' = [pedidos EXCEPT ![pedido_'[1]] = ""]
                                   /\ UNCHANGED llevar
                                \/ /\ (Len(pedido_') = 1)
                                   /\ pedidos' = [pedidos EXCEPT ![pedido_'[1]] = ""]
                                   /\ llevar' = llevar + 1
                                   /\ UNCHANGED <<mesas, aqui>>
                             /\ pc' = [pc EXCEPT !["manejarpedido"] = "ManejarPedido_"]
                        ELSE /\ pc' = [pc EXCEPT !["manejarpedido"] = "Done"]
                             /\ UNCHANGED << pedidos, mesas, pendientes, 
                                             llevar, aqui, pedido_ >>
                  /\ UNCHANGED pedido

ManejarPedido == ManejarPedido_

EntregarPedidosFinales_ == /\ pc["entregarpedidosfinales"] = "EntregarPedidosFinales_"
                           /\ (llevar + aqui >= 5 /\ Len(pendientes) /= 0)
                           /\ (Len(pendientes) /= 0)
                           /\ pedido' = Head(pendientes)
                           /\ pendientes' = Tail(pendientes)
                           /\ (Len(pedido') > 0)
                           /\ \/ /\ (Len(pedido') = 2 /\ pedido'[2] /= "")
                                 /\ mesas' = [mesas EXCEPT ![pedido'[2]] = mesas[pedido'[2]] \ {pedido'[1]}]
                                 /\ aqui' = aqui + 1
                                 /\ pedidos' = [pedidos EXCEPT ![pedido'[1]] = ""]
                                 /\ UNCHANGED llevar
                              \/ /\ (Len(pedido') = 1)
                                 /\ pedidos' = [pedidos EXCEPT ![pedido'[1]] = ""]
                                 /\ llevar' = llevar + 1
                                 /\ UNCHANGED <<mesas, aqui>>
                           /\ pc' = [pc EXCEPT !["entregarpedidosfinales"] = "EntregarPedidosFinales_"]
                           /\ UNCHANGED pedido_

EntregarPedidosFinales == EntregarPedidosFinales_

Next == RealizarPedido \/ CambioMesa \/ ManejarPedido
           \/ EntregarPedidosFinales

Spec == /\ Init /\ [][Next]_vars
        /\ WF_vars(RealizarPedido)
        /\ WF_vars(CambioMesa)
        /\ WF_vars(ManejarPedido)
        /\ WF_vars(EntregarPedidosFinales)

\* END TRANSLATION 
====
