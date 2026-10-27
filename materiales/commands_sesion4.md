################### App Engine ###################

# app.yaml
runtime: python39

# main.py
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Mi primera API con flask'

if __name__ == '__main__':
    app.run()

# requirements.txt
Flask==3.0.0

# Editor de Cloud Shell
python -m venv venv_app_engine
source venv_app_engine/bin/activate
pip install -r requirements.txt
python main.py

gcloud app deploy
gcloud app services list
gcloud app versions list
gcloud app browse
# Hacer cambios en el archivo main.py, por ejemplo, modificar la cadena de texto
gcloud app deploy
gcloud app versions list
gcloud app browse --version id-de-tu-version-1
gcloud app browse --version id-de-tu-version-2
gcloud app services set-traffic --splits=id-de-tu-version-1=.5,id-de-tu-version-2=.5
gcloud app services set-traffic --splits=id-de-tu-version-1=.5,id-de-tu-version-2=.5 --split-by=random
gcloud app browse
watch curl url-de-tu-aplicacion

################### Cloud Functions ###################

# main.py
import functions_framework
import random

@functions_framework.http
def f_choose_physical_activity(request):

	request_json = request.get_json(silent=True)
    request_args = request.args

	random_activity = random.randint(0, 1)
    
	dict_activity = {0: 'sports', 1: 'fun'}
	random_number = random.randint(0, 3)
	activities = {'sports': ['futbol', 'running', 'surf', 'tenis'], 'fun': ['cine', 'restaurant', 'teatro', 'spa']}

	if request_args and 'activity' in request_args:
		return activities[request_args['activity']][random_number]
	elif request_json and 'activity' in request_json:
		return activities[request_json['activity']][random_number]
	else:
		return activities[dict_activity[random_activity]][random_number]


################### Cloud Run ###################

# main.py
import os

from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello_world():
    """Example Hello World route."""
    name = os.environ.get("NAME", "World")
    return f"Hello {name}!"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
	
# requirements.txt
Flask==3.0.3
gunicorn==22.0.0
Werkzeug==3.0.3

# terminal/loca/cmd
gcloud run deploy --source .
