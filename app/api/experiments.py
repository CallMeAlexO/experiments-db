import base64
import zlib
from datetime import datetime

from flask import jsonify, request, url_for, abort, json
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import NmrExperiment, Author, ExperimentData, Experiment, Batch
from app.api import bp
from file_handler import handle_zip


@bp.route('/experiments/generate', methods=['GET'])
def generate_experiments():
    db.session.add(NmrExperiment(material=3, author_id=6, result=1))
    db.session.add(NmrExperiment(material=3, author_id=6, result=7))
    db.session.add(NmrExperiment(material=3, author_id=6, result=6))
    db.session.add(NmrExperiment(material=3, author_id=6, result=2))
    db.session.add(NmrExperiment(material=3, author_id=6, result=2))
    db.session.add(NmrExperiment(material=3, author_id=6, result=5))
    db.session.add(NmrExperiment(material=3, author_id=6, result=9))
    db.session.commit()
    return jsonify(NmrExperiment.query.get_or_404(1).to_dict())


@bp.route('/experiments/<int:id>', methods=['GET'])
def get_experiment(id):
    return jsonify(NmrExperiment.query.get_or_404(id).to_dict(include_rawdata=True))


@bp.route('/experiments/<int:id>/<string:type>', methods=['GET'])
def get_experiment_data(id, type):
    data = NmrExperiment.query.get_or_404(id).get_type(type)
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
        query = query.filter(NmrExperiment.author_id == author)
    if material:
        query = query.filter(NmrExperiment.material_id == material)
    if sort_by:
        try:
            col, order = sort_by.split("_")
        except ValueError as e:
            return jsonify({"error": "'sort_by' requires a parameter of format [field]_asc or [field]_desc"})

        if col == "material":
            if order == "asc":
                query = query.order_by(NmrExperiment.experiment_id.asc())
            elif order == "desc":
                query = query.order_by(NmrExperiment.experiment_id.desc())
            else:
                return jsonify({"error": "'sort_by' requires a parameter of format [field]_asc or [field]_desc"})
        if col == "timestamp":
            if order == "asc":
                query = query.order_by(NmrExperiment.timestamp.asc())
            elif order == "desc":
                query = query.order_by(NmrExperiment.timestamp.desc())
            else:
                return jsonify({"error": "'sort_by' requires a parameter of format [field]_asc or [field]_desc"})
        if col == "result":
            if order == "asc":
                query = query.order_by(NmrExperiment.result.asc())
            elif order == "desc":
                query = query.order_by(NmrExperiment.result.desc())
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
    part_of = request.args.get("part_of", None)
    batch_id = request.args.get("batch", None)
    exp = {}

    allowed_types = ["nmr"]

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

    if batch_id:
        try:
            batch_id = int(batch_id)
        except ValueError as e:
            batch_id = Batch.query.filter(Batch.name.like(f"%{batch_id}%")).first().id

    # This is validated in the program, not the DB because the program is the one that handles the various types.
    if part_of is None or part_of not in allowed_types:
        if part_of is None:
            response = jsonify({"error": f"Field `part_of` cannot be empty"})
        else:
            response = jsonify({"error": f"Field `part_of` {part_of} not allowed"})
        response.status_code = 400
        return response

    experiment = Experiment(material_id=int(material), timestamp=date, author_id=author_id, batch_id=batch_id, part_of=part_of)
    db.session.add(experiment)
    try:
        db.session.flush()
    except IntegrityError as e:
        error = e.orig.args[1].lower()
        response = jsonify({"error": error})
        response.status_code = 500
        if e.orig.args[0] == 1452:
            response.status_code = 400 # User error
            if "batch" in error:
                response = jsonify({"error": f"batch id {batch_id} does not exist"})
            elif "author" in error:
                response = jsonify({"error": f"author id {author_id} does not exist"})
            elif "material" in error:
                response = jsonify({"error": f"material id {material} does not exist"})
        return response

    if part_of == "nmr":
        specific_experiment = NmrExperiment(nmrexp_id=experiment.id, result=result)
        db.session.add(specific_experiment)
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
