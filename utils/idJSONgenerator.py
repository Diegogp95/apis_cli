import openpyxl
import os
import json

dir = os.getcwd()

path = os.path.join(dir, 'AE_plantsid.xlsx')

wb_obj = openpyxl.load_workbook(path)

hoja = wb_obj.active

datos = {}
for fila in hoja.iter_rows(min_row=2, values_only=True):
    siteName = fila[2].replace(" ", "_")
    siteId = fila[1]
    datos[siteName] = siteId

wb_obj.close()

with open(os.path.join(dir,'plantIds.json'), 'w', encoding='utf-8') as archivo:
    json.dump(datos, archivo, indent=2, ensure_ascii=False)
