Laboratorio BigQuery 01
bq show bigquery-public-data:samples.shakespeare

bq query --use_legacy_sql=false \
'SELECT
   word,
   SUM(word_count) AS count
 FROM
   `bigquery-public-data`.samples.shakespeare
 WHERE
   word LIKE "%raisin%"
 GROUP BY
   word'
   
bq help
bq mk sd_local_dataset_1
bq ls
bq ls -n 10 bigquery-public-data:
bq mk babynames
curl -LO http://www.ssa.gov/OACT/babynames/names.zip
ls
unzip names.zip # solo Mac. En Windows, descomprimir manualmente
bq load babynames.names2010 yob2010.txt name:string,gender:string,count:integer
bq ls babynames
bq show babynames.names2010
bq query "SELECT name,count FROM babynames.names2010 WHERE gender = 'F' ORDER BY count DESC LIMIT 5"
bq rm -t smart-data-c:babynames.names2010

Crear un archivo load.sh con el siguiente contenido
#!/bin/bash

# Nombre del dataset en BigQuery. Solo para Mac.
# Tarea: traducir a Windows, en archivo .bat
dataset="babynames"

# Recorre los años desde 1880 hasta 2023
for year in {1880..2023}
do
    # Nombre del archivo .txt correspondiente al año
    filename="yob${year}.txt"

    # Comando para cargar el archivo en BigQuery
    bq load ${dataset}.names${year} ${filename} name:string,gender:string,count:integer

    # Verifica el resultado del comando
    if [ $? -eq 0 ]; then
        echo "Archivo ${filename} cargado exitosamente en ${dataset}.names${year}"
    else
        echo "Error al cargar el archivo ${filename} en ${dataset}.names${year}"
    fi
done


bq ls babynames
bq rm -r babynames

Laboratorio Bigtable 01
echo project = `gcloud config get-value project` > ~/.cbtrc
echo instance = sd-consola-bigtable-1 >> ~/.cbtrc
cat ~/.cbtrc
cbt createtable my-table
cbt ls
cbt createfamily my-table cf1
cbt ls my-table
cbt set my-table r1 cf1:c1=test-value
cbt set my-table r2 cf1:c1=test-value2
cbt set my-table r2 cf1:c1=test-value1
cbt deletetable my-table


cbt createtable test-sessions
cbt createfamily test-sessions Interactions
cbt createfamily test-sessions Sales
cbt ls test-sessions
cbt set test-sessions green1939#1638940844260 Interactions:red_hat=seen
cbt set test-sessions blue2737#1638940844260 Sales:sale=blue_dress#blue_jacket

# Ejemplo 1
cbt set test-sessions blue2737#1638940844260 Interactions:red_skirt=seen
cbt set test-sessions blue2737#1638940844260 Interactions:red_hat=seen
cbt set test-sessions blue2737#1638940844260 Interactions:orange_shoes=
cbt set test-sessions blue2737#1638940844260 Sales:sale=blue_dress#blue_jacket

# Ejemplo 2
cbt set test-sessions 1638940844261 Interactions:blue_shirt=clicked
cbt set test-sessions green4567#1638940844261 Interactions:green_hat=seen
cbt set test-sessions green4567#1638940844261 Interactions:yellow_shoes=
cbt set test-sessions green4567#1638940844261 Sales:sale=green_dress#green_jacket

# Ejemplo 3
cbt set test-sessions red7890#1638940844262 Interactions:yellow_pants=clicked
cbt set test-sessions red7890#1638940844262 Interactions:red_socks=seen
cbt set test-sessions red7890#1638940844262 Interactions:green_scarf=
cbt set test-sessions red7890#1638940844262 Sales:sale=red_coat#blue_hat

# Ejemplo 4
cbt set test-sessions yellow1234#1638940844263 Interactions:blue_shoes=clicked
cbt set test-sessions yellow1234#1638940844263 Interactions:yellow_hat=seen
cbt set test-sessions yellow1234#1638940844263 Interactions:red_scarf=
cbt set test-sessions yellow1234#1638940844263 Sales:sale=yellow_dress#yellow_jacket

# Ejemplo 5
cbt set test-sessions blue5678#1638940844264 Interactions:red_pants=clicked
cbt set test-sessions blue5678#1638940844264 Interactions:blue_socks=seen
cbt set test-sessions blue5678#1638940844264 Interactions:green_hat=
cbt set test-sessions blue5678#1638940844264 Sales:sale=blue_coat#green_hat

# Ejemplo 6
cbt set test-sessions green1234#1638940844265 Interactions:orange_pants=clicked
cbt set test-sessions green1234#1638940844265 Interactions:green_socks=seen
cbt set test-sessions green1234#1638940844265 Interactions:blue_scarf=
cbt set test-sessions green1234#1638940844265 Sales:sale=green_suit#blue_shoes

# Ejemplo 7
cbt set test-sessions red5678#1638940844266 Interactions:red_pants=clicked
cbt set test-sessions red5678#1638940844266 Interactions:blue_socks=seen
cbt set test-sessions red5678#1638940844266 Interactions:yellow_hat=
cbt set test-sessions red5678#1638940844266 Sales:sale=red_shirt#yellow_shoes

# Ejemplo 8
cbt set test-sessions yellow1234#1638940844267 Interactions:orange_pants=clicked
cbt set test-sessions yellow1234#1638940844267 Interactions:red_socks=seen
cbt set test-sessions yellow1234#1638940844267 Interactions:green_scarf=
cbt set test-sessions yellow1234#1638940844267 Sales:sale=yellow_suit#green_shoes

# Ejemplo 9
cbt set test-sessions blue5678#1638940844268 Interactions:green_pants=clicked
cbt set test-sessions blue5678#1638940844268 Interactions:blue_socks=seen
cbt set test-sessions blue5678#1638940844268 Interactions:red_hat=
cbt set test-sessions blue5678#1638940844268 Sales:sale=blue_skirt#red_shoes

# Ejemplo 10
cbt set test-sessions green1234#1638940844269 Interactions:yellow_pants=clicked
cbt set test-sessions green1234#1638940844269 Interactions:green_socks=seen
cbt set test-sessions green1234#1638940844269 Interactions:orange_hat=
cbt set test-sessions green1234#1638940844269 Sales:sale=green_blouse#orange_pants

# Ejemplo 11
cbt set test-sessions red5678#1638940844270 Interactions:blue_pants=clicked
cbt set test-sessions red5678#1638940844270 Interactions:red_socks=seen
cbt set test-sessions red5678#1638940844270 Interactions:green_hat=
cbt set test-sessions red5678#1638940844270 Sales:sale=red_coat#blue_hat

# Ejemplo 12
cbt set test-sessions yellow1234#1638940844271 Interactions:red_pants=clicked
cbt set test-sessions yellow1234#1638940844271 Interactions:yellow_socks=seen
cbt set test-sessions yellow1234#1638940844271 Interactions:green_scarf=
cbt set test-sessions yellow1234#1638940844271 Sales:sale=yellow_dress#yellow_jacket

# Ejemplo 13
cbt set test-sessions blue5678#1638940844272 Interactions:orange_pants=clicked
cbt set test-sessions blue5678#1638940844272 Interactions:red_socks=seen
cbt set test-sessions blue5678#1638940844272 Interactions:green_hat=
cbt set test-sessions blue5678#1638940844272 Sales:sale=blue_suit#green_shoes

# Ejemplo 14
cbt set test-sessions green1234#1638940844273 Interactions:red_pants=clicked
cbt set test-sessions green1234#1638940844273 Interactions:green_socks=seen
cbt set test-sessions green1234#1638940844273 Interactions:yellow_hat=
cbt set test-sessions green1234#1638940844273 Sales:sale=green_skirt#yellow_shoes

# Ejemplo 15
cbt set test-sessions red5678#1638940844274 Interactions:blue_pants=clicked
cbt set test-sessions red5678#1638940844274 Interactions:red_socks=seen
cbt set test-sessions red5678#1638940844274 Interactions:green_scarf=
cbt set test-sessions red5678#1638940844274 Sales:sale=red_blouse#blue_pants


cbt read test-sessions \
    prefix=yellow \
    count=10
	
cbt read test-sessions \
    start=yellow1234#1638940844270 \
    end=yellow1235#1638940844271

cbt lookup test-sessions \
    yellow1234#1638940844267
	
cbt read test-sessions count=5 \
    columns="Interactions:.*"

cbt read test-sessions count=5 \
    columns="Interactions:red_socks"

cbt read test-sessions count=5 \
    columns="Sales:sale"


