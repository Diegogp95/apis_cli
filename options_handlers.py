import json
import sys
from datetime import datetime
import os

def init_config(config_file):
    config = {
        "portafolio": "",
        "token": "",
        "start_date": "",
        "end_date": "",
    }
    try:
        with open(config_file, "w") as json_file:
            json.dump(config, json_file, indent=2)
    except:
        print("Error al iniciar archivo de configuracion.")
        sys.exit(2)
    return

def update_config(new_entries, config_file_path):
    try:
        with open(config_file_path, 'r') as config_file:
            data = json.load(config_file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    for key, value in new_entries.items():
        data[key] = value

    with open(config_file_path, 'w') as config_file:
        json.dump(data, config_file, indent=2)

    show_config(config_file_path)

def set_portafolio(portafolio, config_file_path):
    update_config({"portafolio": portafolio}, config_file_path)

def set_date(arg, config_file_path):
    try:
        start_date, end_date = arg.split(',')
        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d-%H:%M:%S").isoformat()
        except ValueError:
            start_date = datetime.fromisoformat(start_date).isoformat()
        try:
            end_date = datetime.strptime(end_date, "%Y-%m-%d-%H:%M:%S").isoformat()
        except ValueError:
            end_date = datetime.fromisoformat(end_date).isoformat()
    except ValueError:
        print("Error: La fecha debe estar en el formato 'YYYY-mm-dd-HH:MM:SS' o en el formato ISO 8601")
        sys.exit(1)
    if start_date and end_date and end_date < start_date:
        print("Error: La fecha de fin debe ser posterior a la fecha de inicio.")
        sys.exit(1)
    update_config({"start_date": start_date, "end_date": end_date}, config_file_path)


def load_saved_dates(config_file_path):
    try:
        with open(config_file_path, 'r') as config_file:
            data = json.load(config_file)
            start_date = data["start_date"]
            end_date = data["end_date"]
            return start_date, end_date
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise e
    
def show_dates(config_file_path):
    try:
        with open(config_file_path, 'r') as config_file:
            data = json.load(config_file)
            print(f"Fecha de inicio: {data['start_date']}")
            print(f"Fecha de fin: {data['end_date']}")
    except (FileNotFoundError, json.JSONDecodeError):
        print("No se encontraron fechas guardadas.")
        sys.exit()

def show_config(config_file_path):
    try:
        with open(config_file_path, 'r') as config_file:
            data = json.load(config_file)
            print("\n\tConfiguracion actual:\n\n")

            for key, value in data.items():
                if key == "token":
                    print("{:<20} {:<20}".format(key, "*" * 10))
                else:
                    print("{:<20} {:<20}".format(key, str(value).strip('[]')
                                                 if isinstance(value, list) else value))
    except (FileNotFoundError, json.JSONDecodeError):
        print("No se encontraron datos guardados.")
        sys.exit()

def reset_config(config_file_path):
    try:
        os.remove(config_file_path)
        print("Archivo de configuracion eliminado.")
    except FileNotFoundError:
        print("No se encontro el archivo de configuracion.")
    sys.exit()

def set_plant_id(plant_id, config_file_path):
    update_config({"plant_id": plant_id}, config_file_path)

def set_element_id(element_id, config_file_path):
    update_config({"element_id": element_id}, config_file_path)

def set_grouping(grouping, config_file_path):
    if grouping not in ["raw", "minute", "hour", "day", "month", "year"]:
        print("Error: El agrupamiento debe ser 'hour', 'day' o 'month'")
        sys.exit(1)
    update_config({"grouping": grouping}, config_file_path)

def set_granularity(granularity, grouping, config_file_path):
    if grouping == "minute" and granularity not in range(1, 61):
        print("Error: La granularidad debe ser un entero entre 1 y 60")
        sys.exit(1)
    if grouping == "hour" and granularity not in range(1, 24):
        print("Error: La granularidad debe ser un entero entre 1 y 23")
        sys.exit(1)
    if grouping == "day" and granularity not in range(1, 32):
        print("Error: La granularidad debe ser un entero entre 1 y 31")
        sys.exit(1)
    if grouping == "month" and granularity not in range(1, 13):
        print("Error: La granularidad debe ser un entero entre 1 y 12")
        sys.exit(1)
    if grouping == "year" and granularity < 1:
        print("Error: La granularidad debe ser un entero mayor a 0")
        sys.exit(1)
    update_config({"granularity": granularity}, config_file_path)

def set_aggregation(agregation, config_file_path):
    if agregation not in range(0, 29):
        print("Error: La agregacion debe ser un entero entre 0 y 28")
        sys.exit(1)
    update_config({"agregation": agregation}, config_file_path)

def set_ids(ids, config_file_path):
    update_config({"ids": ids}, config_file_path)