from network import NetworkManager
from schemas import INITIAL_CONNECT_SCHEMA, MATCH_FOUND_RESPONSE_SCHEMA
from json_config import JSON_Manager  # Importa tu clase real


def main():
    net = NetworkManager()

    print("\n--- TRYING THE CONNECTION WITH SERVER ---")
    
    if not net.connect():
        return

    # ---------------------------------------------------------
    # ACTIVIDAD 1: Handshake (Con validación de Esquema)
    # ---------------------------------------------------------
    print("\n--- INITIATING ACTIVITY 1 (WITH SCHEMA) ---")

    data_join = JSON_Manager.get_datajoin("Player_Console")

    net.send_json(data_join, schema=INITIAL_CONNECT_SCHEMA)

    waiting = True
    while waiting:
        response = net.receive_json(schema=MATCH_FOUND_RESPONSE_SCHEMA)
        if response:
            print(f"Server Response: {response}")
            waiting = False

    # ---------------------------------------------------------
    # ACTIVIDAD 2: Compra de Unidades (Sin Esquema)
    # ---------------------------------------------------------
    print("\n--- INITIATING ACTIVITY 2 (NO SCHEMA) ---")

    data_buy = JSON_Manager.get_unit_recolectors()

    net.send_json(data_buy)

    waiting = True
    while waiting:
        response = net.receive_json()
        if response:
            print(f"Server Response: {response}")
            waiting = False


if __name__ == "__main__":
    main()
