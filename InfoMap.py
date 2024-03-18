InfoMap = {
    "GPM": {
        "operations": ["AUTH", "PING", "PLANTS", "ELEMENTS", "ALLDATASOURCES", "DATASOURCE", "DATA"],
        "plants": {
            "Mandinga": 46,
            "La_Foresta": 45,
            "Villa_Prat": 40,
            "Quillay": 37,
            "San_Ramiro": 39,
            "Lirio_de_Campo": 38,
            "Los_Lagos": 42,
            "Las_Cabras": 43,
            "El_Castano": 44,
        },
        "paths": {
            "BASE": "https://webapitrinasolar.horizon.greenpowermonitor.com/api/",
            "AUTH": "Account/Token/",
            "PING": "Account/Ping",
            "PLANTS": "Plant",
            "ELEMENTS": "Plant/{plant_id}/Element",
            "ALLDATASOURCES": "Plant/{plant_id}/DataSource",
            "DATASOURCE": "Plant/{plant_id}/Element/{element_id}/DataSource",
            "DATA": "DataList/v2/"
        },
        "headers": {
            "Content-Type": "application/json"
        }
    },
    "AlsoEnergy": {
        "operations": ["AUTH", "SITES", "HARDWARE", "COMPONENTS", "DATA", "DATAV2"],
        "plants": {
            "Guanaco_Solar_I": 54937,
            "Margarita": 58333,
            "Escorial": 60009,
            "Gabardo": 60010,
            "Portezuelos": 60011,
            "Rexner": 60012,
            "Monte": 60013,
            "Plomo": 60014,
            "Idahue_Solar": 60015,
            "Nazarino": 60078,
            "Guanaco_Solar_II": 60384,
            "Duqueco_Solar": 61819,
            "Patricia_Solar": 63572,
            "Loma_Tendida_Solar": 63573,
            "San_Eugenio_Solar": 63574,
            "Lo_Chacon_Solar": 63575,
            "Avellano_Solar": 63576,
            "Las_Palmas_Solar": 63577,
            "Anunuca_Solar": 63579,
            "Rio_Peuco_Solar": 63580
        },
        "paths": {
            "BASE": "https://api.alsoenergy.com/",
            "AUTH": "Auth/token/",
            "SITES": "Sites/",
            "HARDWARE": "Sites/{siteId}/Hardware/",
            "COMPONENTS": "Hardware/{hardwareId}/",
            "DATA": "v2/Data/BinData",
        },
        "headers-auth": {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        "headers": {
            "Content-Type": "application/json"
        }
    }
}