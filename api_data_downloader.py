import json
import sys, os
from datasources_mapping.DataSourceMap import DataSourceMap
from InfoMap import InfoMap
import api_explorer as api


def main(argv):
    if len(argv) < 3:
        print("Error: Faltan argumentos")
        sys.exit(1)

    portafolio = argv[0]
    start_date = argv[1]
    end_date = argv[2]

    output_folder_path = os.path.join("data_output/", portafolio)

    if not os.path.exists(output_folder_path):   
        os.makedirs(output_folder_path) 

    plants = InfoMap[portafolio]["plants"]

    if portafolio == "AlsoEnergy":
        also_query_file_path = os.path.join(output_folder_path, "AlsoEnergyQuery.json")
        api.main(["-S", "--portafolio", portafolio, "-o", "AUTH"])

    for plant in plants.keys():
        plant_id = plants[plant]
        for table_name, field_dict in DataSourceMap[portafolio][plant].items():
            output_path = os.path.join(
                output_folder_path,
                plant + "_" + table_name + "_" + argv[1] + "_" + argv[2] + ".json")
            if portafolio == "GPM":
                fields = [field for field in field_dict if field != "act_energy"]
            elif portafolio == "AlsoEnergy":
                fields = [field for field in field_dict]
            table_data = []
            output_data = {}

            print(f"Descargando datos de {portafolio} para planta {plant} y tabla {table_name}")

            for i in range(0, len(fields), 10):
                queryset = fields[i:i+10]

                if portafolio == "GPM":
                    ids = [field_dict[field]["DataSourceId"] for field in queryset]
                    ids_str = ",".join(map(str, ids))
                    args = ["-S", "--portafolio", portafolio, "--plant-id", str(plant_id),
                            "--start-date", start_date, "--end-date", end_date, "--ids",
                            ids_str, "-o", "DATA", "--pipe", "--grouping", "minute",
                            "--granularity", str(15), "--aggregation", str(1), "-S"]

                    returned_data = api.main(args)
                    table_data.extend(returned_data)
                    
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
                                    output_data[item["timestamp"]] = {}
                                output_data[item["timestamp"]][field] = value

                    except json.JSONDecodeError as e:
                        print(f"\t\tPlanta: {plant} - Error en la descarga de datos de AlsoEnergy para tabla {table_name} y campos {queryset}")
                        continue


            if table_name == "Generation" and portafolio == "GPM":
                args = ["-S", "--portafolio", portafolio, "--plant-id", str(plant_id),
                        "--start-date", start_date, "--end-date", end_date, "--ids",
                        str(field_dict["act_energy"]["DataSourceId"]), "-o", "DATA",
                        "--pipe", "--grouping", "minute", "--granularity", str(15),
                        "--aggregation", str(28), "-S"]
                returned_energy_data = api.main(args)
            
            if portafolio == "GPM":
                for entry in table_data:
                    if entry["Date"] not in output_data.keys():
                        timestamp_data = [matched for matched in table_data if matched["Date"] == entry["Date"]]
                        # print(timestamp_data)
                        output_data[entry["Date"]] = {
                            field: next((entryy["Value"] for entryy in timestamp_data if entryy["DataSourceId"] == field_dict[field]["DataSourceId"]), None) for field in fields
                        }
                        if table_name == "Generation":
                            output_data[entry["Date"]]["act_energy"] = next((entryy["Value"] for entryy in returned_energy_data if entryy["Date"] == entry["Date"]), None)
                        
            with open(output_path, "w") as file:
                json.dump(output_data, file, indent=4)
    if portafolio == "AlsoEnergy":
        os.remove(also_query_file_path)
    return
                



if __name__ == '__main__':
    main(sys.argv[1:])