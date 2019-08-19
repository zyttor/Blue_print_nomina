import os
from functools import update_wrapper

from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, json, make_response, current_app
from flask_cors import CORS, cross_origin
from flaskext.mysql import MySQL
import time, datetime

from werkzeug.utils import secure_filename

from templates import usuario, catalogos, web_services

app = Flask(__name__)
# my sql connection
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '1390'
app.config['MYSQL_DATABASE_DB'] = 'vinos_final'

UPLOAD_FOLDER = 'c:/ni_idea'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
mysql = MySQL(app)

app.secret_key = 'clve'

cors = CORS(app, resources={r"/*": {"origins": "*"}})

#app.register_blueprint(usuario.bp)
#app.register_blueprint(catalogos.bp)
app.register_blueprint(web_services.bp)






@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000, debug=True)
