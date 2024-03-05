InfoMap = {
    "GPM": {
        "operations": ["AUTH", "PING", "PLANTS", "DATA"],
        "pipeline": {
            "ops": ["AUTH", "DATA"],
            "help": '''
            -a, --pipe              Ejecuta cadena de operaciones hasta obtener data final'''
        },
        "paths": {
            "BASE": "https://webapitrinasolar.horizon.greenpowermonitor.com/api/",
            "AUTH": "Account/Token/",
            "PING": "Account/Ping",
            "PLANTS": "Plant",
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