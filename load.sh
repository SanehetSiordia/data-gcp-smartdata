#!/bin/bash

# Nombre del dataset en BigQuery. Solo para Mac.
# Tarea: traducir a Windows, en archivo .bat
dataset="babynames"

# Recorre los años desde 1880 hasta 2023
for year in {1880..2023}
do
    # Nombre del archivo .txt correspondiente al año
    filename="artifacts/names/yob${year}.txt"

    # Comando para cargar el archivo en BigQuery
    bq load ${dataset}.names${year} ${filename} name:string,gender:string,count:integer

    # Verifica el resultado del comando
    if [ $? -eq 0 ]; then
        echo "Archivo ${filename} cargado exitosamente en ${dataset}.names${year}"
    else
        echo "Error al cargar el archivo ${filename} en ${dataset}.names${year}"
    fi
done
