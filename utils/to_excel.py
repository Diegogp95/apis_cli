import pandas as pd
import argparse,os

def json_to_excel(input_path, output_name):
    # Verificar que el archivo de entrada existe
    if not os.path.isfile(input_path):
        print(f"Error: El archivo {input_path} no existe.")
        return
    
    # Leer el archivo json
    data = pd.read_json(input_path)

    # Si la columna "timestamp" existe y es de tipo datetime, eliminar la información de la zona horaria
    if 'timestamp' in data.columns and pd.api.types.is_datetime64_any_dtype(data['timestamp']):
        data['timestamp'] = data['timestamp'].dt.tz_localize(None)

    # Convertir a Excel
    data.to_excel(output_name, index=False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert a JSON file to Excel.')
    parser.add_argument('input_path', type=str, help='The path to the input JSON file.')
    parser.add_argument('output_name', type=str, help='The name of the output Excel file.')

    args = parser.parse_args()

    json_to_excel(args.input_path, args.output_name)