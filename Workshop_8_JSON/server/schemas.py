# Esquema para el request de la Actividad 1 (Tu INITIAL_CONNECT)
INITIAL_CONNECT_SCHEMA = {
    "type": "object",
    "properties": {
        "type": {"type": "string", "enum": ["INITIAL_CONNECT"]},
        "payload": {
            "type": "object",
            "properties": {
                "player_id": {"type": "string", "minLength": 1},
                "client_version": {"type": "string"},
                "is_ready": {"type": "boolean"},
            },
            "required": ["player_id", "client_version", "is_ready"],
        },
    },
    "required": ["type", "payload"],
}

# Schema for the Response (Server -> Client)
MATCH_FOUND_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "type": {"type": "string"},
        "payload": {
            "type": "object",
            "properties": {
                "you": {"type": "string"},
                "opponent": {"type": "string"},
                "session_id": {"type": "string"},
                "global_player_id": {"type": "integer"},
            },
            "required": ["you", "session_id", "global_player_id"],
        },
    },
    "required": ["type", "payload"],
}