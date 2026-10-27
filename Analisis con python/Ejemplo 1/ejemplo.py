import csv

with open('datos.csv', mode='r', newline='', encoding='utf-8') as archivo:
    #lector = csv.reader(archivo)
    for fila in csv.reader(archivo):
        print(fila)