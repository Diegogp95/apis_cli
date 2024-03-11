InfoMap = {
    "GPM": {
        "operations": ["AUTH", "PING", "PLANTS", "ELEMENTS", "ALLDATASOURCES", "DATASOURCE", "DATA"],
        "pipeline": {
            "ops": ["AUTH", "DATA"],
            "help": '''
            -a, --pipe              Ejecuta cadena de operaciones hasta obtener data final'''
        },
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
            "ELEMENTS": "Plant/{}/Element",
            "ALLDATASOURCES": "Plant/{}/DataSource",
            "DATASOURCE": "Plant/{}/Element/{}/DataSource",
            "DATA": "DataList/v2/"
        },
        "headers": {
            "Content-Type": "application/json"
        }
    },
    "AlsoEnergy": {
        "operations": ["AUTH", "HARDWARE", "COMPONENTS", "DATA", "DATAV2"],
        "pipeline": {
            "ops": ["AUTH", "HARDWARE", "COMPONENTS", "DATA"],
            "help": '''
            -a, --pipe              Ejecuta cadena de operaciones hasta obtener data final'''
        },
        "paths": {
            "BASE": "https://api.alsoenergy.com/",
            "AUTH": "Auth/token/",
            "HARDWARE": "Sites/{siteId}/Hardware/",
            "COMPONENTS": "Hardware/{hardwareId}/",
            "DATA": "Data/BindData/",
            "DATAV2": "v2/Data/BindData/",
        },
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded"
        }
    }
}