from flask import jsonify, request, url_for, abort
from app import db, log
from app.models import Author, Batch
from app.api import bp
from sqlalchemy.exc import IntegrityError


@bp.route('/batches/generate', methods=['GET'])
def generate_batches():
    log.debug(f"ENTER /batches/generate")
    for i in range(300):
        b = Batch(name="TEST_BATCH"+str(i))
        db.session.add(b)

    try:
        db.session.commit()
    except IntegrityError as e:
        if "duplicate" in str(e.orig).lower():
            return jsonify({"error": f"{e.params[0]} already exists in DB"})
        else:
            raise e

    return jsonify(b.to_dict())


@bp.route('/batches/<int:id>', methods=['GET'])
def get_batch(id):
    log.debug(f"ENTER /batches/id/{id}")
    return jsonify(Batch.query.get_or_404(id).to_dict())


@bp.route('/batches', methods=['GET'])
def get_batches():
    log.debug(f"ENTER /batches")
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = Batch.to_collection_dict(Batch.query, page, per_page, 'api.get_batches')
    return jsonify(data)


@bp.route('/batches/<int:id>/experiments', methods=['GET'])
def get_batch_experiments(id):
    log.debug(f"ENTER /batches/{id}/experiments")
    batch = Batch.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = Batch.to_collection_dict(batch.experiments, page, per_page, 'api.get_batch_experiments', id=id)
    return jsonify(data)
