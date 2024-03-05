from datetime import datetime
import sys, getopt, os
import json
from operations import *
from options_handlers import *
from InfoMap import InfoMap


helpmessage = '''python api_download.py -n <portafolio> [-a -s <start_date> -e <end_date>]
Opciones:
    -h, --help              Muestra este mensaje
    -n, --portafolio        Nombre del portafolio
    -P, -N, --portafolios   Muestra los portafolios disponibles
    -a, --pipe              Ejecuta cadena de operaciones hasta obtener data final
    -s, --start_date        Fecha de inicio, uso: YYYY-MM-DD o ISO 8601
    -e, --end_date          Fecha de fin, uso: YYYY-MM-DD o ISO 8601
    -o, --operation         Operacion a realizar, uso: [token, data, hardware, pipe, ...]
    -O, --show-operations   Muestra las operaciones disponibles para el portafolio.
    -d, --set-date          Establece la fecha de inicio y fin para la operacion en el archivo de configuracion
    -D, --show-date         Muestra la fecha de inicio y fin actuales del archivo de configuracion
    -p, --set-portafolio    Establece el portafolio de trabajo en el archivo de configuracion
    -c, --config            Muestra el archivo de configuracion
    -r, --reset             Elimina el archivo de configuracion

Cualquier operacion (-o -O -a) requiere el nombre del portafolio, debe configurarse previamente con -p o proveerse
con -n. Si no se especifica una fecha de inicio y fin, se usaran las fechas guardades en archivo de configuracion,
si no se encuentra la informacion el programa terminara.
-d y -D excluyen cualquier otra opcion. -dD es equivalente a -d.
-a y -o pipe son equivalentes.
-o acepta concatenacion de operaciones separadas por coma, ejemplo: -o token,data,hardware
Las operaciones de autenticacion guardan el token en archivo de configuracion.
Si se especifica la operacion autenticacion o se ejecuta pipe, primero se busca un token guardado,
si no se encuentra se ejecuta la operacion de autenticacion, si el token guardado falla termina el programa,
y se requiere reautenticar.
'''


# Mensajes de error

exceptMessage = '''Uso incorrecto, para mas informacion ejecute:
python api_download.py -h
'''

exceptName = '''-a -o -O requieren el nombre del portafolio, para mas informacion ejecute:
python api_download.py -h
'''

# Opciones y argumentos

options="hn:PNas:e:o:Od:Dp:cr"
long_options=["help", "portafolio=", "portafolios", "pipe", "start-date=", "end-date=", "operation=",
              "show-operations", "set-date=", "show-date", "set-portafolio=", "config", "reset"]



# Portafolios y operaciones disponibles

Portafolios = ["GPM", "AlsoEnergy"]


def main(argv):
    portafolio = ""
    toPerform = []
    start_date = None
    end_date = None

    # archivo de configuracion
    config_file = "config.json"
    config_file_path = os.path.join(os.path.dirname(__file__), config_file)

    if not os.path.exists(config_file_path):
        init_config(config_file_path)

    else:
        with open(config_file_path, 'r') as config_file:
            try:
                data = json.load(config_file)
                portafolio = data["portafolio"]
                start_date = data["start_date"]
                end_date = data["end_date"]
            except json.JSONDecodeError:
                print("Error: Archivo de configuracion vacio o corrupto.")
                sys.exit(1)

    # tratar argumentos y opciones
    try:
        opts, args = getopt.getopt(argv, options, long_options)
    except getopt.GetoptError:
        print(exceptMessage)
        sys.exit(2)
    for opt, arg in opts:
        # Ayuda
        if opt in ("-h", "--help"):
            print(helpmessage)
            sys.exit(0)

        # nombre del portafolio, requerido para otras opciones
        elif opt in ("-n", "--portafolio"):
            if arg not in Portafolios:
                print(f"Portafolio {arg} no encontrado.")
                sys.exit(2)
            portafolio = arg

        # elegir fecha de inicio
        elif opt in ("-s", "--start-date"):
            try:
                try:
                    start_date = datetime.strptime(arg, "%Y-%m-%d-%H:%M:%S").isoformat()
                except ValueError:
                    start_date = datetime.fromisoformat(arg).isoformat()
            except ValueError:
                print("Error: La fecha debe estar en el formato 'YYYY-mm-dd-HH:MM:SS' o en el formato ISO 8601")
                sys.exit(1)
            print(f"Fecha de inicio: {start_date}")

        # elegir fecha de fin
        elif opt in ("-e", "--end-date"):
            try:
                try:
                    end_date = datetime.strptime(arg, "%Y-%m-%d-%H:%M:%S").isoformat()
                except ValueError:
                    end_date = datetime.fromisoformat(arg).isoformat()
                    print(f"Fecha de fin: {end_date}")
            except ValueError:
                print("Error: La fecha debe estar en el formato 'YYYY-mm-dd-HH:MM:SS' o en el formato ISO 8601")
                sys.exit(1)
            print(f"Fecha de fin: {end_date}")


        # setear fechas de inicio y fin en archivo de configuracion            
        elif opt in ("-d", "--set-date"):
            print("Seteando fechas")
            set_date(arg, config_file_path)
            sys.exit(0)
        
        # mostrar fechas de inicio y fin guardadas en archivo de configuracion
        elif opt in ("-D", "--show-date"):
            show_dates(config_file_path)
            sys.exit(0)

        # mostrar portafolios disponibles
        elif opt in ("-N", "-P", "--portafolios"):
            print("Portafolios disponibles:")
            for p in Portafolios:
                print(f"\t{p}")
            sys.exit(0)

        # ejecutar todas las operaciones del portafolio en pipeline
        elif opt in ("-a", "--pipe"):
            if portafolio == "":
                print(exceptMessage)
                sys.exit(2)
            toPerform.extend(InfoMap[portafolio]["pipeline"]["ops"])
            print(f"pipeline: {toPerform} para {portafolio}")
            sys.exit(1)

        # operaciones especificas
        elif opt in ("-o", "--operation"):
            if portafolio == "":
                print(exceptName)
                sys.exit(2)
            if arg == "pipe":
                toPerform.extend(InfoMap[portafolio]["pipeline"]["ops"])
                print(f"pipeline: {toPerform} para {portafolio}")
                sys.exit(0)

            # arg subtring de operaciones y cada operacion existe en el portafolio
            elif all(op in InfoMap[portafolio]["operations"] for op in arg.split(',')):
                toPerform.extend(arg.split(','))
                print(f"operaciones: {toPerform} contenidas en {InfoMap[portafolio]['operations']} para {portafolio}")
            else:
                print(f"Operacion(es) {arg} no disponible(s) para {portafolio}")
                sys.exit(2)

        # mostrar operaciones disponibles para el portafolio
        elif opt in ("-O", "--show-operations"):
            if portafolio == "":
                print(exceptName)
                sys.exit(2)
            print(f"Operaciones disponibles para {portafolio}:")
            ops = []
            for op in InfoMap[portafolio]["operations"]:
                ops.append(op)
                print(f"\t{op}")
            sys.exit(0)
        
        # mostrar archivo de configuracion
        elif opt in ("-c", "--config"):
            show_config(config_file_path)
            sys.exit(0)
        
        # resetear archivo de configuracion
        elif opt in ("-r", "--reset"):
            reset_config(config_file_path)
            sys.exit(0)
        
        # setear portafolio de trabajo en archivo de configuracion
        elif opt in ("-p", "--set-portafolio"):
            print("Seteando portafolio")
            try:
                if arg not in Portafolios:
                    print(f"Portafolio {arg} no encontrado.")
                    sys.exit(2)
                set_portafolio(arg, config_file_path)
            except ValueError:
                print("Error: Portafolio no encontrado.")
                sys.exit(1)
            sys.exit(0)

    print("Paso comprobacion de argumentos y opciones.")
    # si llega hasta aca es porque se realizaran operaciones
    # verificar fechas de inicio y fin
    try:
        # si no se especificaron fechas cargar las guardadas en el archivo de configuracion
        if (start_date is None and end_date is None):
            start_date, end_date = load_saved_dates(config_file_path)
            print(f"Fechas cargadas desde archivo de configuracion: {start_date} - {end_date}")
    except (FileNotFoundError, json.JSONDecodeError):
        print("Debe especificar fechas o configurarlas previamente.")
        sys.exit(1)
    try:
        # Verificar que ambas fechas se han especificado juntas
        if (start_date is None and end_date is not None) or (start_date is not None and end_date is None):
            print("Error: Debes especificar ambas fechas de inicio y fin.")
            sys.exit(1)
        # Verificar que la fecha de fin sea posterior a la fecha de inicio
        if start_date and end_date and end_date < start_date:
            print("Error: La fecha de fin debe ser posterior a la fecha de inicio.")
            sys.exit(1)
    except Exception as e:
        print(f"Error inesperado: {e}")
        sys.exit(1)

    # ejecutar operaciones
    if portafolio == "":
        print(exceptName)
        sys.exit(2)

    authed = False

    for op in toPerform:
        if op == "AUTH":
            token = auth(portafolio, config_file_path)
            if token is None:
                print("Error: Autenticacion fallida.")
                sys.exit(1)
        if op == "PING":
            if ping(portafolio, config_file_path):
                print("Ping exitoso.")
            else:
                if len(toPerform) > 1:
                    print("Ping fallido, autenticando...")
                    token = auth(portafolio, config_file_path)
                else:
                    print("Ping fallido.")
                    sys.exit(1)
        if op == "PLANTS":
            if not authed:
                if ping(portafolio, config_file_path):
                    authed = True
                else:
                    print("Ping fallido, autenticando...")
                    token = auth(portafolio, config_file_path)
                    if token:
                        authed = True
                    else:
                        print("Error: Autenticacion fallida.")
                        sys.exit(1)
            plants(portafolio, config_file_path)


if __name__ == "__main__":
    main(sys.argv[1:])