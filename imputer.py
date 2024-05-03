import json
import os,sys
import pandas as pd
from InfoMap import InfoMap
from datasources_mapping.DataSourceMap import DataSourceMap
from datetime import timedelta, datetime


def main(args):

    if len(args) < 2:
        if args[0] == "-h":
            print("Usage: python imputer.py <portafolio> <path_file>")
            sys.exit(1)
        print("Error: Faltan argumentos")
        sys.exit(1)



    if args[0] not in InfoMap.keys():
        print(f"Error: Portafolio no encontrado - {args[0]}")
        sys.exit(1)

    portafolio = args[0]
    path_file = args[1]
    file = path_file.split("/")[-1]

    if portafolio not in InfoMap.keys():
        print(f"Error: Portafolio no encontrado - {portafolio}")
        sys.exit(1)

    if not (os.path.exists(f"imputed/{portafolio}")):
        os.makedirs(f"imputed/{portafolio}")
    if not (os.path.exists(f"imputed/{portafolio}/incidents")):
        os.makedirs(f"imputed/{portafolio}/incidents")

    try:
        with open(path_file, "r") as f:
            data = json.load(f)
        data_length = len(data)

    except FileNotFoundError:
        print(f"Error: Archivo no encontrado - {file}")
        sys.exit(1)

    plant_name = file.split("-")[0]
    table_name = file.split("-")[1].split("_date=")[0]
    start_date = file.split("date=")[1].split("_")[0]
    end_date = file.split("date=")[1].split("_")[1].split(".")[0]

    if portafolio == 'GPM':
        start_date = datetime.fromisoformat(start_date) + timedelta(minutes=15)
        start_date = start_date.isoformat()


    plant_id = InfoMap[portafolio]["plants"][plant_name]

    output_imputed_path = f"imputed/{portafolio}/{plant_name}-{table_name}_{start_date}_{end_date}.json"
    output_incidents_path = f"imputed/{portafolio}/incidents/{plant_name}-{table_name}_{start_date}_{end_date}.json"

    ## Reemplazar valores negativos por 0
    for element in data:
        for key, value in element.items():
            if type(value) == float:
                if value < 0:
                    element[key] = 0

    date_range = pd.date_range(start=start_date, end=end_date, freq="15min")
    timestamps = [date.isoformat() for date in date_range]
    # timestamps = timestamps[:-1]

    datasourceMap = DataSourceMap[portafolio][plant_name][table_name]

    incidentes = []

    for timestamp in timestamps:
        found = False
        for entry in data:
            emptyFields = []
            if entry["timestamp"] == timestamp:
                found = True
                for key in datasourceMap.keys():
                    if key not in entry.keys() or entry[key] == "NaN" or entry[key] is None:
                        emptyFields.append(key)
                        entry[key] = 0.0
                if emptyFields:
                    incidentes.append({
                        "timestamp": timestamp,
                        "emptyFields": emptyFields
                    })
                break
        if not found:
            data.append({
                "timestamp": timestamp,
                **{key: 0.0 for key in datasourceMap.keys()}
            })
            incidentes.append({
                "timestamp": timestamp,
                "emptyFields": list(datasourceMap.keys())
            })
    
    data = sorted(data, key=lambda x: x["timestamp"])
    with open(output_imputed_path, "w") as f:
        json.dump(data, f, indent=4)
    
    with open(output_incidents_path, "w") as f:
        json.dump(incidentes, f, indent=4)

    print(f"Data imputada: {len(incidentes)} incidentes")
    print(f"Entradas iniciales: {data_length}, entradas finales: {len(data)}")
    print(f"Archivo imputado guardado en {output_imputed_path}")

    return



    





if __name__ == "__main__":
    main(sys.argv[1:])