import base64
import sys
import zlib

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
import datetime
from sqlalchemy.dialects.mysql.types import TINYTEXT
from sqlalchemy import ForeignKey
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from werkzeug.utils import secure_filename
import re
from file_handler import handle_zip
import json
import os
url = os.environ.get('CLEARDB_DATABASE_URL', "").split("?")[0]

app = Flask(__name__)
c = CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_size' : 100, 'pool_recycle' : 280}

db = SQLAlchemy(app)
ma = Marshmallow(app)



UPLOAD_FOLDER = "./uploads"

class Articles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    body = db.Column(db.Text())
    date = db.Column(db.DateTime, default=datetime.datetime.now)

    def __init__(self, title, body):
        self.title = title
        self.body = body

class Sample_Types(db.Model):
    __tablename__ = 'sample_types'

    types_id = db.Column(db.Integer, primary_key=True)
    types_name = db.Column(db.String(100))

    def __init__(self, name):
        self.types_name = name

class Experiments(db.Model):
    __tablename__ = 'experiments'

    experiment_id = db.Column(db.Integer, primary_key=True)
    experiment_type = db.Column(db.Integer, ForeignKey('sample_types.types_id'))
    experiment_date = db.Column(db.DateTime, default=datetime.datetime.now)
    experiment_author = db.Column(db.Text)
    experiment_result = db.Column(db.Integer)
    experiment_rawdata = db.Column(db.Text)

    def __init__(self, experiment):
        # Mandatory parameters:
        if experiment.get("type", None) is None: raise ValueError("Missing mandatory parameter: type")
        if experiment.get("raw_data", None) is None: raise ValueError("Missing mandatory parameter: raw_data")
        self.experiment_type = experiment["type"]
        self.experiment_rawdata = experiment["raw_data"]

        # optional parameters
        if experiment.get("date", None): self.experiment_date = experiment["date"]
        if experiment.get("author", None): self.experiment_author = experiment["author"]
        if experiment.get("result", None): self.experiment_result = experiment["result"]


class ArticleSchema(ma.Schema):
    class Meta:
        fields = ("id", "title", "body", "date")


class ExperimentSchema(ma.Schema):
    class Meta:
        fields = ("experiment_id", "experiment_type", "experiment_date", "experiment_author", "experiment_result", "experiment_rawdata")


article_schema = ArticleSchema()
articles_schema = ArticleSchema(many=True)
experiment_schema = ExperimentSchema()

@app.route("/")
def index():
    return "Hello World!"


def api_error(e):
    if "orig" in dir(e):
        err_num = e.orig.args[0]
        if err_num == 1452:
            m = re.search("CONSTRAINT `(.*)` FOREIGN KEY", e.orig.args[1])
            return jsonify({"success": False, "error": f"Incorrect value for field {m.group(1)}"})
    return jsonify({"success": False, "error": e.__cause__})


@app.route("/upload", methods=["POST"])
def add_experiment():

    file = request.files.get("file")
    mimetype = file.content_type
    type = request.args.get("type", None)
    author = request.args.get("author", None)
    result = request.args.get("result", None)
    date = request.args.get("date", None)


    if mimetype == "application/x-zip-compressed" or mimetype == "application/zip":
        # Get raw data
        experiment = handle_zip(file)
        if type: experiment.update({"type": int(type)})
        if author: experiment.update({"author": author})
        if result: experiment.update({"result": result})
        if date: experiment.update({"date": date})
        compressed = zlib.compress(json.dumps(experiment["raw_data"]).encode("utf-8"))
        experiment.update({"raw_data": base64.b64encode(compressed)})
        try:
            exp = Experiments(experiment)
        except ValueError as e:
            return api_error(e)

        try:
            db.session.add(exp)
            db.session.commit()
        except ValueError as e:
            return api_error(e)
        except Exception as g:
            return api_error(g)


        payload = {"author": exp.experiment_author,
                   "type": exp.experiment_type,
                   "result": exp.experiment_result,
                   "date": exp.experiment_date,
                   "id": exp.experiment_id
                   }
        return jsonify({"success": True, "data": payload})
    else:
        return "TODO: Implement your mimetype"


@app.route("/get/<experiment_id>", methods = ['GET'])
def files(experiment_id):
    exp = Experiments.query.get(experiment_id)
    results = experiment_schema.dump(exp)
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)