import base64
import zlib
from datetime import datetime

from flask import jsonify, request, url_for, abort, json
from app import db
from app.models import Experiment, Author, ExperimentData
from app.api import bp
from file_handler import handle_zip


@bp.route('/experiments/generate', methods=['GET'])
def generate_experiments():
    db.session.add(Experiment(material=3, author_id=6, result=1, rawdata=""))
    db.session.add(Experiment(material=3, author_id=6, result=7, rawdata=""))
    db.session.add(Experiment(material=3, author_id=6, result=6, rawdata=""))
    db.session.add(Experiment(material=3, author_id=6, result=2, rawdata=""))
    db.session.add(Experiment(material=3, author_id=6, result=2, rawdata=""))
    db.session.add(Experiment(material=3, author_id=6, result=5, rawdata=""))
    db.session.add(Experiment(material=3, author_id=6, result=9, rawdata=""))
    db.session.commit()
    return jsonify(Experiment.query.get_or_404(1).to_dict())


@bp.route('/experiments/<int:id>', methods=['GET'])
def get_experiment(id):
    return jsonify(Experiment.query.get_or_404(id).to_dict(include_rawdata=True))


@bp.route('/experiments/<int:id>/<string:type>', methods=['GET'])
def get_experiment_data(id, type):
    data = Experiment.query.get_or_404(id).get_type(type)
    if data is None: return abort(404)
    return data.to_dict()


@bp.route('/experiments', methods=['GET'])
def get_experiments():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)

    author = request.args.get('author', None, type=int)
    material = request.args.get('type', None, type=int)
    sort_by = request.args.get('sort_by', None, type=str)
    has_t1 = request.args.get('has_t1', None, type=bool)
    has_t2 = request.args.get('has_t2', None, type=bool)
    has_2d = request.args.get('has_2d', None, type=bool)

    query = Experiment.query
    if author:
        query = query.filter(Experiment.author_id == author)
    if material:
        query = query.filter(Experiment.material == material)
    if sort_by:
        try:
            col, order = sort_by.split("_")
        except ValueError as e:
            return jsonify({"error": "'sort_by' requires a parameter of format [field]_asc or [field]_desc"})

        if col == "material":
            if order == "asc":
                query = query.order_by(Experiment.id.asc())
            elif order == "desc":
                query = query.order_by(Experiment.id.desc())
            else:
                return jsonify({"error": "'sort_by' requires a parameter of format [field]_asc or [field]_desc"})
        if col == "timestamp":
            if order == "asc":
                query = query.order_by(Experiment.timestamp.asc())
            elif order == "desc":
                query = query.order_by(Experiment.timestamp.desc())
            else:
                return jsonify({"error": "'sort_by' requires a parameter of format [field]_asc or [field]_desc"})
        if col == "result":
            if order == "asc":
                query = query.order_by(Experiment.result.asc())
            elif order == "desc":
                query = query.order_by(Experiment.result.desc())
            else:
                return jsonify({"error": "'sort_by' requires a parameter of format [field]_asc or [field]_desc"})
    if has_t1:
        query = query.join(ExperimentData).filter(ExperimentData.vector == 1)
    if has_t2:
        query = query.join(ExperimentData).filter(ExperimentData.vector == 2)
    if has_2d:
        query = query.join(ExperimentData).filter(ExperimentData.vector == 3)

    data = Experiment.to_collection_dict(query, page, per_page, 'api.get_experiments')
    return jsonify(data)


@bp.route('/experiments', methods=['POST'])
def add_experiments():
    file = request.files.get("file")
    mimetype = file.content_type
    material = request.args.get("material", None)
    author_id = request.args.get("author", None)
    result = request.args.get("result", None)
    date = request.args.get("date", None)
    exp = {}

    if mimetype == "application/x-zip-compressed" or mimetype == "application/zip":
        exp = handle_zip(file)

    if date:
        try:
            date = datetime.strptime(date, '%yyyy-%mm-%dd %H:%M:%S')
        except ValueError as e:
            date = datetime.strptime(date, '%Y-%m-%d')

    try:
        author_id = int(author_id)
    except ValueError as e:
        author_id = Author.query.filter(Author.name.like(f"%{author_id}%")).first().id

    experiment = Experiment(material=int(material),
                            timestamp=date,
                            author_id=author_id,
                            result=int(result))

    db.session.add(experiment)
    db.session.commit()

    if "T1_excel" in exp:
        t1_excel = ExperimentData(experiment_id=experiment.id, data_type=1, vector=1, data=exp.get("T1_excel"))
        db.session.add(t1_excel)
    if "T2_excel" in exp:
        t2_excel = ExperimentData(experiment_id=experiment.id, data_type=1, vector=2, data=exp.get("T2_excel"))
        db.session.add(t2_excel)
    if "2D_txt" in exp:
        twod_txt = ExperimentData(experiment_id=experiment.id, data_type=2, vector=3, data=exp.get("2D_txt"))
        db.session.add(twod_txt)
    db.session.commit()

    response = jsonify(experiment.to_dict())
    response.status_code = 201
    response.headers['Location'] = url_for('api.get_experiment', id=experiment.id)
    return response
