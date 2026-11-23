import argparse
import logging
import re
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

# Clase DataIngestion: contiene la lógica para transformar el archivo en un formato aceptable por BigQuery.
class DataIngestion:
    def parse_method(self, string_input):
        # Este método toma una línea de valores separados por comas y la traduce a un diccionario
        # que BigQuery puede cargar.
        values = re.split(",", re.sub('\r\n', '', re.sub('"', '', string_input)))
        row = dict(
            zip(('state', 'gender', 'year', 'name', 'number', 'created_date'),
                values))
        return row

# Función principal run(): crea el pipeline y lo ejecuta.
def run(argv=None):
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--input',
        dest='input',
        required=False,
        help='Archivo de entrada para leer. Puede ser un archivo local o '
        'un archivo en un depósito de Google Storage.',
        default='gs://spls/gsp290/data_files/head_usa_names.csv')

    parser.add_argument('--output',
                        dest='output',
                        required=False,
                        help='Tabla de BQ de salida para escribir los resultados.',
                        default='lake.usa_names')

    known_args, pipeline_args = parser.parse_known_args(argv)

    data_ingestion = DataIngestion()

    # Inicia el pipeline utilizando los argumentos de pipeline proporcionados desde la línea de comandos.
    p = beam.Pipeline(options=PipelineOptions(pipeline_args))

    (p
     # Lee el archivo. Esta es la fuente del pipeline. Todo el procesamiento posterior comienza con las líneas leídas desde el archivo.
     | 'Leer desde un archivo' >> beam.io.ReadFromText(known_args.input,
                                                       skip_header_lines=1)
     # Esta etapa del pipeline traduce desde un archivo CSV de una sola fila, que es una cadena, a un objeto diccionario consumible por BigQuery.
     | 'String a Row BigQuery' >>
     beam.Map(lambda s: data_ingestion.parse_method(s))
     | 'Escribir en BigQuery' >> beam.io.Write(
         beam.io.BigQuerySink(
             known_args.output,
             # Se especifica el esquema de BigQuery para la tabla de salida.
             schema='state:STRING,gender:STRING,year:STRING,name:STRING,'
             'number:STRING,created_date:STRING',
             # Crea la tabla en BigQuery si aún no existe.
             create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
             # Borra todos los datos en la tabla de BigQuery antes de escribir.
             write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE)))
    p.run().wait_until_finish()

# Esta línea ejecutará la función run() cuando se ejecute el script.
if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()

