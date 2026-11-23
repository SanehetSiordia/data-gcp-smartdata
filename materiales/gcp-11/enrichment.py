import argparse
import logging
import os
import csv
import apache_beam as beam
from apache_beam.io.gcp import bigquery
from apache_beam.io.gcp.bigquery import parse_table_schema_from_json
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.pvalue import AsDict

# Clase DataIngestion: Contiene la lógica para traducir el archivo en un formato aceptado por BigQuery.
class DataIngestion(object):
    def __init__(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.schema_str = ''
        # Este es el esquema de la tabla de destino en BigQuery.
        schema_file = os.path.join(dir_path, 'resources', 'usa_names_with_full_state_name.json')
        with open(schema_file) as f:
            data = f.read()
            # Envuelve el esquema en "fields", necesario para la API de BigQuery.
            self.schema_str = '{"fields": ' + data + '}'

    def parse_method(self, string_input):
        # Elimina caracteres de retorno y comillas.
        schema = bigquery.parse_table_schema_from_json(self.schema_str)

        field_map = [f for f in schema.fields]

        # Usa un lector de CSV que puede manejar cadenas entre comillas, etc.
        reader = csv.reader(string_input.split('\n'))
        for csv_row in reader:
            values = csv_row
            # Nuestros datos de origen solo contienen el año, así que el mes y el día se establecen en enero 1.
            month = '01'
            day = '01'
            # El año proviene de nuestros datos de origen.
            year = values[2]
            row = {}
            i = 0
            # Itera sobre los valores del archivo CSV, aplicando cualquier lógica de transformación.
            for value in values:
                # Si el esquema indica que este campo es de formato de fecha, debemos
                # transformar la fecha de los datos de origen en un formato que
                # BigQuery pueda entender.
                if field_map[i].type == 'DATE':
                    # Formatea la fecha al formato YYYY-MM-DD que acepta BigQuery.
                    value = '-'.join((year, month, day))

                row[field_map[i].name] = value
                i += 1

            return row

def run(argv=None):
    parser = argparse.ArgumentParser()
    # Agregamos argumentos de línea de comandos para el archivo de entrada y la tabla de salida.
    parser.add_argument(
        '--input', dest='input', required=False,
        help='Archivo de entrada para leer. Puede ser un archivo local o '
             'un archivo en un depósito de Google Storage.',
        default='gs://spls/gsp290/data_files/head_usa_names.csv')
    
    parser.add_argument('--output', dest='output', required=False,
                        help='Tabla de BQ de salida para escribir los resultados.',
                        default='lake.usa_names_enriched')

    # Analizamos los argumentos de la línea de comandos.
    known_args, pipeline_args = parser.parse_known_args(argv)

    # DataIngestion es una clase que creamos en este script para contener la lógica de transformación del archivo en una tabla de BigQuery.
    data_ingestion = DataIngestion()

    # Iniciamos el pipeline utilizando los argumentos del pipeline pasados desde la línea de comandos, que incluyen información sobre dónde almacenar archivos temporales y cuál es el ID del proyecto.
    p = beam.Pipeline(options=PipelineOptions(pipeline_args))
    schema = parse_table_schema_from_json(data_ingestion.schema_str)

    # Esta función agrega un nombre completo del estado buscándolo en el mapa de abreviaturas a nombres completos.
    def add_full_state_name(row, short_to_long_name_map):
        row['state_full_name'] = short_to_long_name_map[row['state']]
        return row

    # Esta es una segunda fuente de datos. La fuente proviene de BigQuery.
    # Esto ingresará en nuestro pipeline como una entrada secundaria.
    read_query = """
    SELECT
    name as state_name,
    abbreviation as state_abbreviation
    FROM
    `qwiklabs-resources.python_dataflow_example.state_abbreviations`"""

    state_abbreviations = (
        p
        | 'Leer desde BigQuery' >> beam.io.Read(
            beam.io.BigQuerySource(query=read_query, use_standard_sql=True))
        | 'Abreviatura a Nombre Completo' >> beam.Map(
            lambda row: (row['state_abbreviation'], row['state_name'])))

    (p
     # Etapa 1: Leer el archivo.
     # Esta es la fuente del pipeline. Todo el procesamiento comienza con las líneas leídas desde el archivo.
     | 'Leer Desde Texto' >> beam.io.ReadFromText(known_args.input,
                                                skip_header_lines=1)
     # Etapa 2: Traducir la cadena CSV a un diccionario BigQuery.
     # Esta etapa traduce una fila de un archivo CSV (cadena) a un objeto diccionario que BigQuery puede consumir.
     | 'Cadena a Fila BigQuery' >> beam.Map(lambda s:
                                            data_ingestion.parse_method(s))
     # Etapa 3: Unir datos.
     # En esta etapa, pasamos una entrada secundaria que contiene un mapa de estados a sus nombres completos.
     # Luego, agregamos el nombre completo del estado a cada fila de datos.
     | 'Unir Datos' >> beam.Map(add_full_state_name, AsDict(
        state_abbreviations))
     # Etapa 4: Escribir en BigQuery.
     # En esta etapa final, definimos el destino de los datos. En este caso, escribimos en BigQuery.
     | 'Escribir en BigQuery' >> beam.io.Write(
        beam.io.BigQuerySink(
            # El nombre de la tabla es un argumento requerido para el sink de BigQuery.
            # En este caso, usamos el valor pasado desde la línea de comandos.
            known_args.output,
            # Aquí usamos el esquema JSON leído desde un archivo JSON.
            # Especificar el esquema permite que la API cree la tabla correctamente si aún no existe.
            schema=schema,
            # Crea la tabla en BigQuery si aún no existe.
            create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
            # Borra todos los datos en la tabla de BigQuery antes de escribir.
            write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE)))
    # Ejecuta el pipeline y espera hasta que se complete.
    p.run().wait_until_finish()

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()


