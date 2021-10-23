from flask import Flask
from flask import request, make_response
import os
from werkzeug.utils import secure_filename
import glob
import json
from flask import send_file

app = Flask(__name__)

UPLOAD_FOLDER = "./uploads"

@app.route("/")
def index():
    return "Hello World!"
    
@app.route("/upload", methods = ['POST', 'OPTIONS'])
def upload():
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_preflight_response()
    elif request.method == "POST": # The actual request following the preflight
        file = request.files.get("file")
        mimetype = file.content_type
        filename = secure_filename(file.filename)
        response = make_response()
        if "image/jpeg" in str(mimetype):
            response.response = "jpg not allowed"
        else:
            response.response = "OK!"
            file.save(UPLOAD_FOLDER +"/"+ filename)
        return _corsify_actual_response(response)

    return str(request.form)

@app.route("/files", methods = ['GET', 'OPTIONS'])
def files():
    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_preflight_response()
    elif request.method == "GET": # The actual request following the preflight
        response = make_response()
        my_files = glob.glob(UPLOAD_FOLDER+"/*")
        my_files_list = []
        for f in my_files:
            filename = f[len(UPLOAD_FOLDER):]
            my_files_list.append({"name" : filename[1:], "url": request.base_url+filename})
        response.response = json.dumps(my_files_list)
        return _corsify_actual_response(response)

    return str(request.form)
    
@app.route("/files/<filename>", methods = ['GET', 'OPTIONS'])
def files_file(filename):

    if request.method == "OPTIONS": # CORS preflight
        return _build_cors_preflight_response()
    else:
        try:
            response = send_file(UPLOAD_FOLDER +"/"+ filename, attachment_filename=filename)
            return _corsify_actual_response(response)
        except Exception as e:
            return str(e)

def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response