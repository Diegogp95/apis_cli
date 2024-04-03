import json
import sys, os, getopt
from datasources_mapping.DataSourceMap import DataSourceMap
from InfoMap import InfoMap
import api_explorer as api
from datetime import datetime, timedelta



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

    portafolio = args[0]
    output_folder_path = os.path.join("data_output/", portafolio)

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

    for plant in plants.keys():
        plant_id = plants[plant]
        for table_name, field_dict in DataSourceMap[portafolio][plant].items():
            output_path = os.path.join(
                output_folder_path,
                plant + "_" + table_name + "_" + start_date + "_" + end_date + ".json")
            if portafolio == "GPM":
                fields = [field for field in field_dict if field != "act_energy"]
            elif portafolio == "AlsoEnergy":
                fields = [field for field in field_dict]
            table_data = []

            print(f"Descargando datos de {portafolio} para planta {plant} y tabla {table_name}")

            output_data = {}

            for i in range(0, len(fields), 10):
                queryset = fields[i:i+10]

                if portafolio == "GPM":
                    ids = [field_dict[field]["DataSourceId"] for field in queryset]
                    ids_str = ",".join(map(str, ids))
                    args = ["-S", "--portafolio", portafolio, "--plant-id", str(plant_id),
                            "--start-date", start_date, "--end-date", end_date, "--ids",
                            ids_str, "-o", "DATA", "--pipe", "--grouping", "minute",
                            "--granularity", str(15), "--aggregation", str(1)]
                    
                    try:
                        returned_data = api.main(args)
                        table_data.extend(returned_data)
                    except json.JSONDecodeError as e:
                        print(f"\t\tPlanta: {plant} - Error en la descarga de datos de GPM para tabla {table_name} y campos {queryset}")
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
                            "--start-date", start_date, "--end-date", end_date,
                            "--also-query-file", also_query_file_path, "--pipe",
                            "--bin-size", "Bin15Min", "-o", "DATA"]

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
                                    output_data[item["timestamp"]] = {"timestamp": item["timestamp"]}
                                output_data[item["timestamp"]][field] = value

                    except json.JSONDecodeError as e:
                        print(f"\t\tPlanta: {plant} - Error en la descarga de datos de AlsoEnergy para tabla {table_name} y campos {queryset}")
                        continue


            if table_name == "Generation" and portafolio == "GPM":
                args = ["-S", "--portafolio", portafolio, "--plant-id", str(plant_id),
                        "--start-date", start_date, "--end-date", end_date, "--ids",
                        str(field_dict["act_energy"]["DataSourceId"]), "-o", "DATA",
                        "--pipe", "--grouping", "minute", "--granularity", str(15),
                        "--aggregation", str(28)]
                try:
                    returned_energy_data = api.main(args)
                except json.JSONDecodeError as e:
                    print(f"\t\tPlanta: {plant} - Error en la descarga de datos de GPM para tabla {table_name} y campo act_energy")
                    returned_energy_data = None
            
            if portafolio == "GPM":
                for entry in table_data:
                    if entry["Date"] not in output_data.keys():
                        if table_name == "Generation":
                            if not returned_energy_data:
                                returned_energy_data = {"Date": entry["Date"], "Value": None}
                        timestamp_data = [matched for matched in table_data if matched["Date"] == entry["Date"]]
                        output_data[entry["Date"]] = {"timestamp": entry["Date"]}
                        output_data[entry["Date"]].update({
                            field: next((entryy["Value"] for entryy in timestamp_data if entryy["DataSourceId"] == field_dict[field]["DataSourceId"]), None) for field in fields
                        })
                        if table_name == "Generation":
                            output_data[entry["Date"]]["act_energy"] = next((entryy["Value"] for entryy in returned_energy_data if entryy["Date"] == entry["Date"]), None)

            output_data = list(output_data.values())

            with open(output_path, "w") as file:
                json.dump(output_data, file, indent=4)
    if portafolio == "AlsoEnergy":
        os.remove(also_query_file_path)
    return
                



if __name__ == '__main__':
    main(sys.argv[1:])