# LAB 01
```bash
sudo su
apt update 
apt install apache2
ls /var/www/html
echo "Aprendiendo Compute Engine con GCP"
echo "Aprendiendo Compute Engine con GCP" > /var/www/html/index.html
echo $(hostname)
echo $(hostname -i)
echo "Aprendiendo Compute Engine con GCP desde mi VM:$(hostname)"
echo "Aprendiendo Compute Engine con GCP desde mi VM:$(hostname) ip:$(hostname -i)"
echo "Aprendiendo Compute Engine con GCP desde mi VM:$(hostname) ip:$(hostname -i)" > /var/www/html/index.html
sudo service apache2 start
```


# LAB 02
```bash
#!/bin/bash
apt update 
apt -y install apache2
echo "Aprendiendo Compute Engine con GCP desde mi VM:$(hostname) ip:$(hostname -i)" > /var/www/html/index.html
```

# LAB 03
Puede mostrar el nombre de la cuenta activa con este comando:
-    gcloud auth list

Puede mostrar el ID del proyecto con este comando::
-    gcloud config list project

Establezca la región:
-    gcloud config set compute/region us-central1

Para ver la configuración de la región del proyecto, ejecute el siguiente comando:
-    gcloud config get-value compute/region    

Establezca la zona:
-    gcloud config set compute/zone us-central1-f

Para ver la configuración de la zona del proyecto, ejecute el siguiente comando:
-    gcloud config get-value compute/zone

En Cloud Shell, ejecute el siguiente comando de gcloud para ver el ID de su proyecto:
-    gcloud config get-value project

En Cloud Shell, ejecute el siguiente comando de gcloud para ver los detalles del proyecto:
-    gcloud compute project-info describe --project $(gcloud config get-value project)

Cree una variable de entorno para almacenar su ID de proyecto:
-    export PROJECT_ID=$(gcloud config get-value project)

Cree una variable de entorno para almacenar su Zona:
-    export ZONE=$(gcloud config get-value compute/zone)

Para verificar si las variables se establecieron correctamente, ejecute los siguientes comandos:   
-    echo -e "PROJECT ID: $PROJECT_ID\nZONE: $ZONE"

## -> CREACION DE COMPUTE ENGINE <-

Para abrir la ayuda del comando create, ejecute lo siguiente:
-    gcloud compute instances create --help

Para crear la VM, ejecute el siguiente comando:
-    gcloud compute instances create sd-local-vm-01 --machine-type e2-medium --zone us-central1-f

## -> EXPLORE LOS COMANDOS DE GCLOUD <-
Ejecute el siguiente comando:
```bash
    gcloud -h
    gcloud config --help    
    gcloud help config
```

Visualice la lista de parámetros de configuración en su entorno:
-    gcloud config list

Visualice todas las propiedades y sus parámetros de configuración:
-    gcloud config list --all

Obtenga una lista de sus componentes:
-    gcloud components list     

## -> FILTRE EL RESULTADO DE LA LÍNEA DE COMANDOS <-
Enumere las instancias de procesamiento disponibles en el proyecto:
-    gcloud compute instances list

Enumere la máquina virtual:    
-    gcloud compute instances list --filter="name=('ronny-vm-cloud-shell')"

Enumere las reglas de firewall en el proyecto.:
-    gcloud compute firewall-rules list

Enumere las reglas de firewall de la red predeterminada.:
-    gcloud compute firewall-rules list --filter="network='default'"

Enumere las reglas del firewall de la red predeterminada donde la regla de permiso coincide con una regla ICMP.
-    gcloud compute firewall-rules list --filter="NETWORK:'default' AND ALLOW:'icmp'"

## -> CONÉCTESE A LA INSTANCIA DE VM <-
Para conectarse a su VM con SSH, ejecute el siguiente comando:
-    gcloud compute ssh ronny-vm-cloud-shell --zone $ZONE

Si sale una pregunta para confirmar, escriba Y.

Para dejar la frase de contraseña vacía, presione INTRO dos veces.

Instale el servidor web nginx en la máquina virtual:
-    sudo apt install -y nginx

Como no debe realizar ninguna acción aquí, ejecute el siguiente comando para desconectarse de SSH y salir de la shell remota:
-    exit

## -> ACTUALICE EL FIREWALL <-
Enumere las reglas de firewall del proyecto:
-    gcloud compute firewall-rules list

Agregue una etiqueta a la máquina virtual:
-    gcloud compute instances add-tags ronny-vm-cloud-shell --tags http-server,https-server

Actualice la regla de firewall para permitir la conexión.:
-    gcloud compute firewall-rules create ronny-allow-http --direction=INGRESS --priority=1000 --network=default --action=ALLOW --rules=tcp:80 --source-ranges=0.0.0.0/0 --target-tags=http-server

Enumere las reglas de firewall del proyecto:
-    gcloud compute firewall-rules list --filter=ALLOW:'80'

Verifique que la comunicación de http a la máquina virtual sea posible:
-    curl http://$(gcloud compute instances list --filter=name:ronny-vm-cloud-shell --format='value(EXTERNAL_IP)')

# -> VISUALICE LOS LOGS DEL SISTEMA <-
Visualice los registros disponibles en el sistema:
-    gcloud logging logs list

Consulte los registros de procesamiento:
-    gcloud logging logs list --filter="compute"

Lea los registros relacionados con el tipo de recurso de gce_instance:
-    gcloud logging read "resource.type=gce_instance" --limit 5

Lea los registros de una máquina virtual específica:
-    gcloud logging read "resource.type=gce_instance AND labels.instance_name=ronny-vm-cloud-shell" --limit 5


# LAB 06

## Crear instancia

### A ejecutar dentro de la instancia

```bash
sudo su
apt update
apt install docker.io -y

sudo docker run --name bd-postgres \
-e POSTGRES_USER=dyanez \
-e POSTGRES_PASSWORD=1234 \
-e POSTGRES_DB=mi_bd_prueba \
-d -p 5432:5432 postgres
```

### A ejecutar en terminal local
```bash
gcloud compute firewall-rules create allow-postgres --allow=tcp:5432
```