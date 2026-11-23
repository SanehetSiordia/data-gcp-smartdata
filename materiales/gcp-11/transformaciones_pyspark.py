from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, count, expr

bucket_name = 'ssm-gcolab-bucket-01'
project_id = 'applied-primacy-512618-h7'

# Crear la sesión de Spark
spark = SparkSession.builder.appName('txt_to_bq').getOrCreate()
sc = spark.sparkContext
sc.setLogLevel('WARN')
spark.conf.set('temporaryGcsBucket', bucket_name)

files_rdd_cmp = sc.textFile(f'gs://{bucket_name}/ingested/txt/campanas_*.txt')
splitted_rdd_cmp = files_rdd_cmp.map(lambda x: x.split("\t"))
selected_col_rdd_cmp = splitted_rdd_cmp.map(lambda x: (x[0], x[1], x[2], x[3]))
columns_cmp = ["nro_campania","costo","pais","fecha_hora"]
cmp_df = selected_col_rdd_cmp.toDF(columns_cmp)
cmp_df.write.format('bigquery').option('table', project_id+'.raw_layer.r_campanas').mode('append').save()


files_rdd_trx = sc.textFile(f'gs://{bucket_name}/ingested/txt/transacciones_*.txt')
splitted_rdd_trx = files_rdd_trx.map(lambda x: x.split("\t"))
selected_col_rdd_trx = splitted_rdd_trx.map(lambda x: (x[0], x[1], x[2], x[3]))
columns_trx = ["nro_transaccion","monto","pais","fecha_hora"]
trx_df = selected_col_rdd_trx.toDF(columns_trx)
trx_df.write.format('bigquery').option('table', project_id+'.raw_layer.r_transacciones').mode('append').save()

# Leer los datos de neural-truth-406011.raw_layer.r_transacciones
tranx = spark.read.format('bigquery').option('table', project_id+'.raw_layer.r_transacciones').load()

# Calcular fecha y hora
tranx = tranx.withColumn('fecha', tranx.fecha_hora.substr(1, 10))
tranx = tranx.withColumn('hora', tranx.fecha_hora.substr(12, 8))

# Calcular las métricas de transacciones
tranx_agg = tranx.groupBy('pais', 'fecha').agg(
    sum(col('monto').cast('float')).alias('income'),
    count('nro_transaccion').alias('cant_trx'),
    expr('0.00 as costo'),
    expr('0 as cant_cmp')
)

# Leer los datos de neural-truth-406011.raw_layer.r_campanas
campaigns = spark.read.format('bigquery').option('table', project_id+'.raw_layer.r_campanas').load()

# Calcular fecha y hora
campaigns = campaigns.withColumn('fecha', campaigns.fecha_hora.substr(1, 10))
campaigns = campaigns.withColumn('hora', campaigns.fecha_hora.substr(12, 8))

# Calcular las métricas de campañas
campaigns_agg = campaigns.groupBy('pais', 'fecha').agg(
    expr('0.00 as income'),
    expr('0 as cant_trx'),
    sum(col('costo').cast('float')).alias('costo'),
    count('nro_campania').alias('cant_cmp')
)

# Unir las métricas de transacciones y campañas
unionall = tranx_agg.unionAll(campaigns_agg)

# Calcular las métricas agregadas
unionall_agg = unionall.groupBy('pais', 'fecha').agg(
    sum('income').alias('income'),
    sum('cant_trx').alias('cant_trx'),
    sum('costo').alias('cost'),
    sum('cant_cmp').alias('cant_cmp')
)

# Calcular las métricas finales
result = unionall_agg.select(
    col('pais').alias('country'),
    col('cant_trx'),
    col('income'),
    col('cost'),
    (col('income') - col('cost')).alias('revenue'),
    col('cant_cmp'),
    col('fecha').alias('date')
)

# Mostrar el resultado
result.show(5,False)

result.write.format('bigquery').option('table', project_id+'.master_layer.m_performance_country').mode('append').save()