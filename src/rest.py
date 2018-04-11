from flask import Flask, render_template, jsonify, request, url_for, Response
import json
import os
import sys
from lexer_parser.parser import *
from tree.tree import *
# Define a aplicacao
app = Flask(__name__)

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]

# Ponto de entrada para a pagina web, carregando o template padrao
@app.route("/")
def index():
    return render_template('index.html')

# Ponto de entrada para traducao de codigo, devolvendo a arvore para visualizacao
@app.route("/translateCode", methods=['POST'])
def translateCode():
    try:
		dataDict = json.loads(request.data.decode())
		parser.parse(dataDict['code'])
		treeDict = change(namesOut)
		return Response(json.dumps({'tree':treeDict}), status=200)
    except:
		return Response(str(sys.exc_info()[0]), status=500)

# Gera um novo token a cada request para prevenir cache de paginas no browser
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path, endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

if __name__ == "__main__":
    app.run(port=8080)
