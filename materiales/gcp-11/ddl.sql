CREATE OR REPLACE TABLE `neural-cosmos-396523.raw_layer.r_campanas` (
nro_campania STRING,
costo STRING,
pais STRING,
fecha_hora STRING
);

CREATE OR REPLACE TABLE `neural-cosmos-396523.raw_layer.r_transacciones` (
nro_transaccion STRING,
monto STRING,
pais STRING,
fecha_hora STRING
);

CREATE OR REPLACE TABLE `neural-cosmos-396523.master_layer.m_performance_country` (
country STRING,
cant_trx INT,
income FLOAT64,
cost FLOAT64,
revenue FLOAT64,
cant_cmp INT,
date STRING
);