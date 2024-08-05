import json
import sys, os, getopt
from .datasources_mapping.DataSourceMap import DataSourceMap
from .InfoMap import InfoMap
from . import api_explorer as api
from datetime import datetime, timedelta
from requests import exceptions as req_exceptions
import pytz

from tqdm import tqdm


def validate_date(date_str):
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
        next_day = date + timedelta(days=1)
        return date.isoformat(), next_day.isoformat()
    except ValueError as e:
        print(e)
        print("Error: La fecha proporcionada no es válida. Debe estar en formato YYYY-MM-DD.")
        sys.exit(1)

help_message = """
Usage: api_data_downloader.py <portafolio> <start_date> <end_date> [options]

-p    --plants      Plantas separadas por comas. Si no se especifica,
                    se descargan datos de todas las plantas.
-d    --day         Fecha en formato YYYY-MM-DD. Descarga datos de un solo día.
                    No requiere start_date y end_date.
"""

def main(argv):
    short_options = "hp:d:"
    long_options = ["help", "plants=", "day="]

    try:
        options, args = getopt.gnu_getopt(argv, short_options, long_options)
    except getopt.GetoptError:
        print("Error: Argumentos no reconocidos")
        sys.exit(1)

    plants_arg = "all"

    ## mover la deficion de la timezone al mapa de plantas luego
    tz = "America/Santiago"
    # tz = None

    if not any(option in ("-h", "--help") for option, value in options):
        if not any(option in ("-d", "--day") for option, value in options):
            if len(args) < 3:
                print("Error: Faltan argumentos")
                sys.exit(1)
            start_date = args[1]
            end_date = args[2]
        elif len(args) < 1:
            print("Error: Faltan argumentos")
            sys.exit(1)

    for option, argument in options:
        if option in ("-h", "--help"):
            print(help_message)
            sys.exit(0)
        elif option in ("-p", "--plants"):
            plants_arg = argument.split(",")

        elif option in ("-d", "--day"):
            start_date, end_date = validate_date(argument)
            start_date = start_date.split("T")[0]
            end_date = end_date.split("T")[0]

    portafolio = args[0]
    output_folder_path = os.path.join("data_output/", portafolio)


    if not os.path.exists("data_output"):
        os.makedirs("data_output")

    if not os.path.exists(output_folder_path):   
        os.makedirs(output_folder_path) 

    if plants_arg == "all":
        plants = InfoMap[portafolio]["plants"]
    else:
        try:
            plants = {plant: InfoMap[portafolio]["plants"][plant] for plant in plants_arg}
        except KeyError as e:
            print(f"Error: Planta no encontrada - {e}")
            sys.exit(1)

    if portafolio == "AlsoEnergy":
        also_query_file_path = os.path.join(output_folder_path, "AlsoEnergyQuery.json")
        api.main(["-S", "--portafolio", portafolio, "-o", "AUTH"])
        start_query = start_date + "T00:15:00"
        if any(option in ("-d", "--day") for option, value in options):
            end_query = end_date + "T00:00:01"
        else:
            _, next_day = validate_date(end_date)
            end_query = next_day.split("T")[0] + "T00:00:01"

    elif portafolio == "GPM":
        start_query = start_date + "T00:00:00"
        if any(option in ("-d", "--day") for option, value in options):
            end_query = end_date + "T00:00:00"
        else:
            _, next_day = validate_date(end_date)
            end_query = next_day.split("T")[0] + "T00:00:00"

    if tz:
        timezone = pytz.timezone(tz)
        ## GPM guarda todo en UTC, aun cuando las mediciones parecen estar en America/Santiago
        ## por lo que descartamos utilizar la timezone en este caso
        ## AlsoEnergy guarda todo en America/Santiago, por lo que la timezone es necesaria
        ## De todas formas en este punto se decide trabajar con datetimes naives en todo el proyecto django
        # if portafolio == "GPM":
        #     start_date = timezone.localize(datetime.fromisoformat(start_date)).isoformat()
        #     end_date = timezone.localize(datetime.fromisoformat(end_date)).isoformat()

    gen_data_paths = []
    weather_data_paths = []

    for plant in plants.keys():
        plant_id = plants[plant]
        print(f"\tPlanta: {plant}")
        for table_name, field_dict in DataSourceMap[portafolio][plant].items():
            if any(option in ("-d", "--day") for option, value in options): 
                output_path = os.path.join(
                    output_folder_path,
                    plant + "-" + table_name + "_date=" + start_date + ".json")
            else:
                output_path = os.path.join(
                    output_folder_path,
                    plant + "-" + table_name + "_range=" + start_date + "_" + end_date + ".json")
                
            if table_name == "Generation":
                gen_data_paths.append(output_path)
            elif table_name == "Weather":
                weather_data_paths.append(output_path)
            if portafolio == "GPM":
                fields = [field for field in field_dict if field != "act_energy"]
            elif portafolio == "AlsoEnergy":
                fields = [field for field in field_dict]
            table_data = []

            output_data = {}

            for i in tqdm(range(0, len(fields), 10), desc="{:40}".format(f"Descargando datos de {table_name}")):
                queryset = fields[i:i+10]

                if portafolio == "GPM":
                    ids = [field_dict[field]["DataSourceId"] for field in queryset]
                    ids_str = ",".join(map(str, ids))
                    args = ["-S", "--portafolio", portafolio, "--plant-id", str(plant_id),
                            "--start-date", start_query, "--end-date", end_query, "--ids",
                            ids_str, "-o", "DATA", "--pipe", "--grouping", "minute",
                            "--granularity", str(15), "--aggregation", str(1)]
                    
                    try:
                        returned_data = api.main(args)
                        table_data.extend(returned_data)
                    except (json.JSONDecodeError, req_exceptions.HTTPError, req_exceptions.RequestException) as e:
                        print(f"\nPlanta: {plant} - Error en la descarga de datos de GPM para tabla {table_name} y campos {queryset}\n")
                        continue
                    
                    
                elif portafolio == "AlsoEnergy":
                    body = []
                    for field in queryset:
                        body.append({
                            "hardwareId": field_dict[field]["hardwareId"],
                            "siteId": plant_id,
                            "fieldName": field_dict[field]["fieldName"],
                            "function": "Avg" if field != "act_energy" else "Sum",
                        })

                    with open(also_query_file_path, "w") as file:
                        json.dump(body, file, indent=4)

                    args = ["-S", "--portafolio", portafolio, "--plant-id", str(plant_id),
                            "--start-date", start_query, "--end-date", end_query,
                            "--also-query-file", also_query_file_path, "--pipe",
                            "--bin-size", "Bin15Min", "-o", "DATA", "--tz", tz]

                    try:
                        returned_data = api.main(args)

                        for item in returned_data["items"]:
                            for field in queryset:
                                value = None
                                for index, info in enumerate(returned_data["info"]):
                                    if (field_dict[field]["fieldName"] == info["name"] and
                                        field_dict[field]["hardwareId"] == info["hardwareId"]):
                                        value = item["data"][index]
                                        break
                                if item["timestamp"] not in output_data:
                                    timestamp = datetime.fromisoformat(item["timestamp"]).replace(tzinfo=None)
                                    output_data[item["timestamp"]] = {"timestamp": timestamp.isoformat()}
                                output_data[item["timestamp"]][field] = value

                    except (json.JSONDecodeError, req_exceptions.HTTPError, req_exceptions.RequestException) as e:
                        print(f"Planta: {plant} - Error en la descarga de datos de AlsoEnergy para tabla {table_name} y campos {queryset}")
                        continue
            # with open('asd.json', 'w') as f:
            #     json.dump(table_data, f, indent=4)


            if table_name == "Generation" and portafolio == "GPM":
                args = ["-S", "--portafolio", portafolio, "--plant-id", str(plant_id),
                        "--start-date", start_query, "--end-date", end_query, "--ids",
                        str(field_dict["act_energy"]["DataSourceId"]), "-o", "DATA",
                        "--pipe", "--grouping", "minute", "--granularity", str(15),
                        "--aggregation", str(28)]
                try:
                    returned_energy_data = api.main(args)
                except (json.JSONDecodeError, req_exceptions.HTTPError, req_exceptions.RequestException) as e:
                    print(f"Planta: {plant} - Error en la descarga de datos de GPM para tabla {table_name} y campo act_energy")
                    returned_energy_data = None
            
            if portafolio == "GPM":
                for entry in table_data:
                    if entry["Date"] not in output_data.keys():
                        if table_name == "Generation":
                            if not returned_energy_data:
                                returned_energy_data = {"Date": entry["Date"], "Value": None}
                        timestamp_data = [matched for matched in table_data if matched["Date"] == entry["Date"]]

                        timestamp = datetime.fromisoformat(entry["Date"]).replace(tzinfo=None)
                        output_data[entry["Date"]] = {"timestamp": timestamp.isoformat()}
                        output_data[entry["Date"]].update({
                            field: next((entryy["Value"] for entryy in timestamp_data if entryy["DataSourceId"] == field_dict[field]["DataSourceId"]), None) for field in fields
                        })
                        try:
                            if table_name == "Generation":
                                output_data[entry["Date"]]["act_energy"] = next((entryy["Value"] for entryy in returned_energy_data if entryy["Date"] == entry["Date"]), None)
                        except TypeError:
                            print(returned_energy_data)
            output_data = sorted(list(output_data.values()), key=lambda x: x["timestamp"])

            with open(output_path, "w") as file:
                json.dump(output_data, file, indent=4)
    if portafolio == "AlsoEnergy":
        os.remove(also_query_file_path)
    return gen_data_paths, weather_data_paths



if __name__ == '__main__':
    main(sys.argv[1:])