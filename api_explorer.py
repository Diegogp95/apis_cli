from datetime import datetime
import sys, getopt, os
import json
from operations import *
from options_handlers import *
from InfoMap import InfoMap


helpmessage = '''python api_download.py [opciones]

Opciones:
    -h, --help              Muestra este mensaje
    -n, --portafolio        Nombre del portafolio
    -P, -N, --portafolios   Muestra los portafolios disponibles
    -a, --pipe              Retorna la data final, sin salida a archivo
    -s, --start_date        Fecha de inicio, uso: YYYY-MM-DD o ISO 8601
    -e, --end_date          Fecha de fin, uso: YYYY-MM-DD o ISO 8601
    -o, --operation         Operacion a realizar, uso: [token, data, hardware, pipe, ...]
    -O, --show-operations   Muestra las operaciones disponibles para el portafolio.
    -d, --set-date          Establece la fecha de inicio y fin para la operacion en el archivo de configuracion
    -D, --show-date         Muestra la fecha de inicio y fin actuales del archivo de configuracion
    -p, --set-portafolio    Establece el portafolio de trabajo en el archivo de configuracion
    -c, --config            Muestra el archivo de configuracion
    -r, --reset             Elimina el archivo de configuracion
    -i, --interactive       Modo interactivo, excluyente con otras opciones, en desarrollo
    -S, --silent            No muestra mensajes de progreso
    --params                Muestra los parametros disponibles para las operaciones
    --plant-id              ID de la planta para operaciones especificas
    --set-plant-id          Establece el ID de la planta en el archivo de configuracion
    --element-id            ID del elemento para operaciones especificas
    --set-element-id        Establece el ID del elemento en el archivo de configuracion
    --grouping              Formato de agrupamiento de datos, uso: [raw, minute, hour, day, month, year]
    --set-grouping          Establece el agrupamiento de datos en el archivo de configuracion
    --granularity           Formato de granularidad de datos
    --set-granularity       Establece la granularidad de datos en el archivo de configuracion
    --aggregation           Formato de agregacion de datos. uso: 0-28
    --set-aggregation       Establece la agregacion de datos en el archivo de configuracion
    --ids                   IDs de las fuentes de data
    --set-ids               Establece los IDs de las fuentes de data en el archivo de configuracion
    --field                 Campo a seleccionar de un Hardware
    --set-field             Establece el campo a seleccionar de un Hardware en el archivo de configuracion
    --function              Funcion a aplicar a un campo
    --set-function          Establece la funcion a aplicar a un campo en el archivo de configuracion
    --bin-size              Tamaño de la ventana de tiempo
    --set-bin-size          Establece el tamaño de la ventana de tiempo en el archivo de configuracion
    --tz                    Zona horaria en base de datos iana
    --set-tz                Establece la zona horaria en base de datos iana en el archivo de configuracion
    --also-query-file       Archivo con query para AlsoEnergy


Cualquier operacion (-o -O) requiere el nombre del portafolio, debe configurarse previamente con -p o proveerse
con -n. Si no se especifica una fecha de inicio y fin, se usaran las fechas guardades en archivo de configuracion,
si no se encuentra la informacion el programa terminara.
-d y -D excluyen cualquier otra opcion. -dD es equivalente a -d.
-o acepta concatenacion de operaciones separadas por coma, ejemplo: -o OP1,OP2,OP3
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

options="ihn:PNas:e:o:Od:Dp:crS"
long_options=["interactive", "help", "portafolio=", "portafolios",
              "pipe", "start-date=", "end-date=", "operation=",
              "show-operations", "set-date=", "show-date", "set-portafolio=",
              "config", "reset", "plant-id=", "set-plant-id=", "element-id=",
              "set-element-id=", "grouping=", "set-grouping=", "granularity=",
              "set-granularity=", "aggregation=", "set-aggregation=", "ids=",
              "set-ids=", "field=", "set-field=", "function=", "set-function=",
              "bin-size=", "set-bin-size=", "tz=", "set-tz=", "also-query-file=",
              "--silent", "--params"]


Portafolios = ["GPM", "AlsoEnergy"]

params_msg = f'''Parametros:
\t\tComunes:
\t\t\t\tstart_date: Fecha de inicio, uso: YYYY-MM-DD o ISO 8601
\t\t\t\tend_date: Fecha de fin, uso: YYYY-MM-DD o ISO 8601
\t\t\t\tportafolio: Nombre del portafolio {Portafolios}
\t\t\t\tplant_id: ID de la planta, equivalente a siteId para AlsoEnergy
\t\t\t\telement_id: ID del elemento, equivalente a hardwareId para AlsoEnergy

\t\tGPM:
\t\t\t\tgrouping: Formato de agrupamiento de datos, uso: [raw, minute, hour, day, month, year]
\t\t\t\tgranularity: Formato de granularidad de datos (int). Ver --info-granularity
\t\t\t\taggregation: Formato de agregacion de datos. uso: 0-28. Ver --info-aggregation
\t\t\t\tids: IDs de las fuentes de data, uso id1,id2,id3,... Maximo 10 IDs

\t\tAlsoEnergy:
\t\t\t\tfield: Campo a seleccionar de un Hardware, uso: field
\t\t\t\tfunction: Funcion a aplicar a un campo, ver --info-function:
\t\t\t\t\tAvg           - Weighted average over time (i.e. volts)
\t\t\t\t\tLast          - Last value (i.e. KWH)
\t\t\t\t\tMin           - Minumum (first KWH reading for the day) NOTE: Only works when all data is &gt; 0
\t\t\t\t\tMax           - Maximum (i.e. wind speed)               NOTE: Only works when all data is &gt; 0
\t\t\t\t\tDiff          - Last value - first value (KWH)
\t\t\t\t\tSum           - Sumation of the data
\t\t\t\t\tIntegral      - Integral of the data
\t\t\t\t\tDiffNonZero   - MIN() - MAX(), excluding zeros (see ArchiveDB.LoadJoinData)
\t\t\t\tbin_size: Tamaño de la ventana de tiempo, BinUnkown, BinRaw, Bin5Min, Bin15Min, BinHour, BinDay, BinMonth, BinYear
\t\t\t\ttz: Zona horaria en base de datos iana.
'''


# Portafolios y operaciones disponibles




def main(argv):
    os.makedirs("output", exist_ok=True)

    toPerform = []
    also_query_file = None
    mode = 'static'
    silent = False

    # archivo de configuracion
    config_file = "config.json"
    config_file_path = os.path.join(os.path.dirname(__file__), config_file)

    if not os.path.exists(config_file_path):
        init_config(config_file_path)

    with open(config_file_path, 'r') as config_file:
        try:
            data = json.load(config_file)
            portafolio = data.get("portafolio")
            start_date = data.get("start_date")
            end_date = data.get("end_date")
            plant_id = data.get("plant_id")
            element_id = data.get("element_id")
            grouping = data.get("grouping")
            granularity = data.get("granularity")
            aggregation = data.get("aggregation")
            ids = data.get("ids")
            field = data.get("field")
            func = data.get("function")
            bin_size = data.get("bin_size")
            tz = data.get("tz")
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

        if opt in ("-i", "--interactive"):
            print('''
                  Modo interactivo en desarrollo.
                  ''')
            sys.exit(0)

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

        elif opt in ("-S", "--silent"):
            silent = True

        # elegir fecha de inicio
        elif opt in ("-s", "--start-date"):
            try:
                try:
                    start_date = datetime.strptime(arg, "%Y-%m-%dT%H:%M:%S").isoformat()
                except ValueError:
                    start_date = datetime.fromisoformat(arg).isoformat()
            except ValueError:
                print("Error: La fecha debe estar en el formato 'YYYY-mm-ddTHH:MM:SS', formato ISO 8601.")
                sys.exit(1)
            if not silent:
                print(f"Fecha de inicio: {start_date}")

        # elegir fecha de fin
        elif opt in ("-e", "--end-date"):
            try:
                try:
                    end_date = datetime.strptime(arg, "%Y-%m-%dT%H:%M:%S").isoformat()
                except ValueError:
                    end_date = datetime.fromisoformat(arg).isoformat()
                    print(f"Fecha de fin: {end_date}")
            except ValueError:
                print("Error: La fecha debe estar en el formato 'YYYY-mm-ddTHH:MM:SS', formato ISO 8601.")
                sys.exit(1)
            if not silent:
                print(f"Fecha de fin: {end_date}")
            
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

        elif opt in ("--params"):
            print(params_msg)
            sys.exit(0)

        # elegir ID de planta
        elif opt in ("--plant-id"):
            plant_id = arg
            if not silent:
                print(f"ID de planta: {plant_id}")

        # elegir ID de elemento
        elif opt in ("--element-id"):
            element_id = arg
            if not silent:
                print(f"ID de elemento: {element_id}")
        
        # elegir formato de agrupamiento
        elif opt in ("--grouping"):
            grouping = arg
            if not silent:
                print(f"Agrupamiento: {grouping}")

        # elegir formato de granularidad
        elif opt in ("--granularity"):
            granularity = arg
            if not silent:
                print(f"Granularidad: {granularity}")

        # elegir formato de agregacion
        elif opt in ("--aggregation"):
            aggregation = arg
            if not silent:
                print(f"Agregacion: {aggregation}")
        
        # elegir IDs de fuentes de data
        elif opt in ("--ids"):
            try:
                ids = [int(id) for id in arg.split(',')]
            except ValueError:
                print("Error: Los IDs deben ser numeros enteros.")
                sys.exit(1)
            if not silent:
                print(f"IDs de fuentes de data: {ids}")

        elif opt in ("--field"):
            field = arg
            if not silent:
                print(f"Campo: {field}")

        elif opt in ("--function"):
            func = arg
            if not silent:
                print(f"Funcion: {func}")

        elif opt in ("--bin-size"):
            bin_size = arg
            if not silent:
                print(f"Tamaño de ventana de tiempo: {bin_size}")

        elif opt in ("--tz"):
            tz = arg
            if not silent:
                print(f"Zona horaria: {tz}")

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
            mode = 'pipe'

        # operaciones especificas
        elif opt in ("-o", "--operation"):
            if portafolio == "":
                print(exceptName)
                sys.exit(2)

            # arg subtring de operaciones y cada operacion existe en el portafolio
            elif all(op in InfoMap[portafolio]["operations"] for op in arg.split(',')):
                toPerform.extend(arg.split(','))
                if not silent:
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

        # setear fechas de inicio y fin en archivo de configuracion            
        elif opt in ("-d", "--set-date"):
            print("Seteando fechas")
            set_date(arg, config_file_path)
            # sys.exit(0)

        # setear ID de planta en archivo de configuracion
        elif opt in ("--set-plant-id"):
            print("Seteando ID de planta")
            set_plant_id(arg, config_file_path)
            # sys.exit(0)

        # setear ID de elemento en archivo de configuracion
        elif opt in ("--set-element-id"):
            print("Seteando ID de elemento")
            set_element_id(arg, config_file_path)
            # sys.exit(0)

        # setear formato de agrupamiento en archivo de configuracion
        elif opt in ("--set-grouping"):
            print("Seteando formato de agrupamiento")
            set_grouping(arg, config_file_path)
            # sys.exit(0)
        
        # setear formato de granularidad en archivo de configuracion
        elif opt in ("--set-granularity"):
            print("Seteando formato de granularidad")
            set_granularity(int(arg), grouping, config_file_path)
            # sys.exit(0)
        
        # setear formato de agregacion en archivo de configuracion
        elif opt in ("--set-aggregation"):
            print("Seteando formato de agregacion")
            set_aggregation(int(arg), config_file_path)
            # sys.exit(0)

        # setear IDs de fuentes de data en archivo de configuracion
        elif opt in ("--set-ids"):
            print("Seteando IDs de fuentes de data")
            ids = [int(id) for id in arg.split(',')]
            set_ids(ids, config_file_path)
            # sys.exit(0)

        elif opt in ("--set-field"):
            print("Seteando campos")
            field = arg
            set_field(field, config_file_path)
            # sys.exit(0)

        elif opt in ("--set-function"):
            print("Seteando funcion")
            set_function(arg, config_file_path)
            # sys.exit(0)
        
        elif opt in ("--set-bin-size"):
            print("Seteando tamaño de ventana de tiempo")
            set_bin_size(arg, config_file_path)
            # sys.exit(0)
    
        elif opt in ("--set-tz"):
            print("Seteando zona horaria")
            set_tz(arg, config_file_path)
            # sys.exit(0)

        elif opt in ("--also-query-file"):
            also_query_file = arg
            if not silent:
                print("Archivo de query para AlsoEnergy")

    # si llega hasta aca es porque se realizaran operaciones

    try:
        # Verificar que ambas fechas se han especificado juntas
        if (start_date is None and end_date is not None) or (start_date is not None and end_date is None):
            print("Error: Debes especificar ambas fechas de inicio y fin.")
            sys.exit(1)
        # Verificar que la fecha de fin sea posterior a la fecha de inicio
        if start_date and end_date and end_date < start_date:
            print("Error: La fecha de fin debe ser posterior a la fecha de inicio.")
            print(f"Fecha de inicio: {start_date}\t\tFecha de fin: {end_date}")
            sys.exit(1)
    except Exception as e:
        print(f"Error inesperado: {e}")
        sys.exit(1)

    if len(toPerform) == 0:
        sys.exit(0)

    # ejecutar operaciones
    if portafolio == "":
        print(exceptName)
        sys.exit(2)

    authed = False

    if "AUTH" in toPerform:
        token = auth(portafolio, config_file_path)
        if token is None:
            print("Error: Autenticacion fallida.")
            sys.exit(1)
        else:
            authed = True

    if "PING" in toPerform:
        if ping(portafolio, config_file_path):
            print("Ping exitoso.")
            authed = True
        else:
            print("Ping fallido.")
            sys.exit(1)

    if portafolio == "GPM" and not authed:
        authed = check_gpm_login(portafolio, config_file_path)

    if "PLANTS" in toPerform or "SITES" in toPerform:
        plants(portafolio, config_file_path)

    if "ELEMENTS" in toPerform or "HARDWARE" in toPerform:
        elements(portafolio, config_file_path, plant_id)

    if "ALLDATASOURCES" in toPerform:
        all_datasources(portafolio, config_file_path, plant_id)

    if "DATASOURCE" in toPerform or "COMPONENTS" in toPerform:
        datasource(portafolio, config_file_path, plant_id, element_id)

    if "DATA" in toPerform:
        if portafolio == "GPM":
            if mode == 'pipe':
                return get_data(portafolio, config_file_path, start_date, end_date,
                        datasource_ids=ids, grouping=grouping, granularity=granularity,
                        aggregation=aggregation, mode=mode)
            else:
                get_data(portafolio, config_file_path, start_date, end_date,
                        datasource_ids=ids, grouping=grouping, granularity=granularity,
                        aggregation=aggregation)
            
        elif portafolio == "AlsoEnergy":
            if mode == 'pipe':
                return get_data(portafolio, config_file_path, start_date, end_date,
                        site_id=plant_id, also_query_file=also_query_file,
                        bin_size=bin_size, tz=tz, mode=mode)
            else:
                get_data(portafolio, config_file_path, start_date, end_date,
                    site_id=plant_id, hardware_id=element_id, field=field,
                    func=func, bin_size=bin_size, tz=tz)

if __name__ == "__main__":
    main(sys.argv[1:])