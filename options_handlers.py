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

def set_portafolio(portafolio, config_file_path):
    # Cargar datos existentes desde el archivo (o un diccionario vacío si el archivo está vacío o no existe)
    try:
        with open(config_file_path, 'r') as config_file:
            data = json.load(config_file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    data["portafolio"] = portafolio

    # Escribir el diccionario actualizado
    with open(config_file_path, 'w') as config_file:
        json.dump(data, config_file, indent=2)

    # Imprimir
    with open(config_file_path, 'r') as config_file:
        updated_data = json.load(config_file)
        for key, value in updated_data.items():
            print(f'{key}: {value}')

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

    # Cargar datos existentes desde el archivo (o un diccionario vacío si el archivo está vacío o no existe)
    try:
        with open(config_file_path, 'r') as config_file:
            data = json.load(config_file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    # Actualizar el diccionario con las nuevas fechas
    data["start_date"] = start_date
    data["end_date"] = end_date

    # Escribir el diccionario actualizado al archivo
    with open(config_file_path, 'w') as config_file:
        json.dump(data, config_file, indent=2)

    # Imprimir el contenido actualizado para verificar
    with open(config_file_path, 'r') as config_file:
        updated_data = json.load(config_file)
        for key, value in updated_data.items():
            print(f'{key}: {value}')

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
            for key, value in data.items():
                print(f'\t{key}: {value}')
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

    