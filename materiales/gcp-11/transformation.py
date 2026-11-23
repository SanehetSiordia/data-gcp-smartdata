import argparse
import logging
import os
import csv
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.io.gcp.bigquery_tools import parse_table_schema_from_json

# Este script se utiliza para leer un archivo y escribir su contenido en una tabla de BigQuery.
# También realiza una transformación en los datos de fecha para que coincidan con el formato esperado por BigQuery.

class DataTransformation:
    def __init__(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.schema_str = ''
        # Aquí leemos el esquema de salida desde un archivo JSON.
        # Esto se utiliza para especificar los tipos de datos que estamos escribiendo en BigQuery.
        schema_file = os.path.join(dir_path, 'resources', 'usa_names_year_as_date.json')
        with open(schema_file) as f:
            data = f.read()
            # Envuelve el esquema en 'fields', necesario para la API de BigQuery.
            self.schema_str = '{"fields": ' + data + '}'

    def parse_method(self, string_input):
        # Este método traduce una línea de valores separados por comas en un diccionario
        # que BigQuery puede cargar.

        # Elimina caracteres de retorno y comillas.
        schema = parse_table_schema_from_json(self.schema_str)
        field_map = [f for f in schema.fields]

        # Utiliza un lector de CSV que maneja cadenas entre comillas, etc.
        reader = csv.reader(string_input.split('\n'))
        for csv_row in reader:
            # Nuestros datos de origen solo contienen el año, por lo que asumimos el 1 de enero como el mes y día.
            month = '01'
            day = '01'
            # El año proviene de nuestros datos de origen.
            year = csv_row[2]

            row = {}
            i = 0
            # Itera sobre los valores del archivo CSV, aplicando cualquier lógica de transformación.
            for value in csv_row:
                if field_map[i].type == 'DATE':
                    # Formatea la fecha como YYYY-MM-DD, que BigQuery acepta.
                    value = '-'.join((year, month, day))

                row[field_map[i].name] = value
                i += 1

            return row

def run(argv=None):
    parser = argparse.ArgumentParser()
    
    # Argumentos de línea de comandos para especificar el archivo de entrada y la tabla de salida.
    parser.add_argument(
        '--input', dest='input', required=False,
        help='Archivo de entrada para leer. Puede ser un archivo local o '
             'un archivo en un depósito de Google Storage.',
        default='gs://spls/gsp290/data_files/head_usa_names.csv')
    
    parser.add_argument('--output', dest='output', required=False,
                        help='Tabla de BQ de salida para escribir los resultados.',
                        default='lake.usa_names_transformed')

    # Analiza los argumentos de la línea de comandos.
    known_args, pipeline_args = parser.parse_known_args(argv)
    
    # Clase DataTransformation se utiliza para contener la lógica de transformación de datos.
    data_ingestion = DataTransformation()

    # Inicia el pipeline usando los argumentos del pipeline pasados desde la línea de comandos.
    p = beam.Pipeline(options=PipelineOptions(pipeline_args))
    schema = parse_table_schema_from_json(data_ingestion.schema_str)

    (p
     # Lee el archivo. Esta es la fuente del pipeline. Todo el procesamiento posterior comienza con las líneas leídas desde el archivo.
     | 'Leer Desde Texto' >> beam.io.ReadFromText(known_args.input,
                                                  skip_header_lines=1)
     # Esta etapa del pipeline traduce desde un archivo CSV de una sola fila
     # a una fila de diccionario que BigQuery puede consumir.
     # Refiere a una función que hemos escrito. Esta función se ejecutará en paralelo en diferentes trabajadores utilizando la entrada de la etapa anterior del pipeline.
     | 'Cadena a Fila BigQuery' >> beam.Map(lambda s: data_ingestion.parse_method(s))
     | 'Escribir en BigQuery' >> beam.io.Write(
        beam.io.BigQuerySink(
            # El nombre de la tabla es un argumento obligatorio para el sink de BigQuery.
            # En este caso, utilizamos el valor pasado desde la línea de comandos.
            known_args.output,
            # Aquí utilizamos el esquema JSON leído desde un archivo JSON.
            # Especificar el esquema permite que la API cree la tabla correctamente si aún no existe.
            schema=schema,
            # Crea la tabla en BigQuery si aún no existe.
            create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
            # Borra todos los datos en la tabla de BigQuery antes de escribir.
            write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE)))
    p.run().wait_until_finish()

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()


