import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from google.cloud import bigquery

# Definición de una clase personalizada que extiende DoFn (Do Function) de Apache Beam.
class QueryToCSV(beam.DoFn):
    def __init__(self, query):
        self.query = query
    
    # El método process se llama para cada elemento en la tubería.
    def process(self, element):        
        # Crea una instancia del cliente BigQuery.
        client = bigquery.Client()
        
        # Ejecuta la consulta definida en el constructor.
        query_job = client.query(self.query)
        
        # Obtiene los resultados de la consulta.
        results = query_job.result()
        
        # Itera sobre los resultados y los devuelve como una cadena CSV.
        for row in results:
            yield ','.join(str(value) for value in row.values())

# Función principal que ejecuta el pipeline de Apache Beam.
def run():
    # Definición de la consulta SQL que se ejecutará en BigQuery.
    query = "SELECT * FROM bigquery-public-data.baseball.games_wide LIMIT 5000"
    
    # Especifica la ubicación de salida en Google Cloud Storage (GCS).
    output_bucket = "gs://sd-gcolab-bucket-2/output/"  # Asegúrate de que el camino termine con un directorio
    
    # Configura las opciones del pipeline.
    pipeline_options = PipelineOptions()
    
    # Crea un pipeline de Apache Beam.
    with beam.Pipeline(options=pipeline_options) as p:
        (
            # Crea un elemento nulo (no se usa, solo para iniciar el pipeline).
            p | 'Create' >> beam.Create([None])
              # Aplica la transformación QueryToCSV que ejecuta la consulta en BigQuery y genera CSV.
              | 'QueryToCSV' >> beam.ParDo(QueryToCSV(query))
              # Escribe los resultados en un archivo CSV en GCS.
              | 'WriteToText' >> beam.io.WriteToText(output_bucket, file_name_suffix='.csv')
        )

# La siguiente línea ejecutará la función run() cuando se ejecute el script.
if __name__ == '__main__':
    run()
