from flask import jsonify, request, url_for, abort
from app import db, log
from app.models import Author
from app.api import bp
from sqlalchemy.exc import IntegrityError


@bp.route('/authors/generate', methods=['GET'])
def generate_authors():
    log.debug(f"ENTER /authors/generate")
    db.session.add(Author(name="Osheter Alexey"))
    db.session.add(Author(name="Osheter Tatiana"))
    db.session.add(Author(name="Campisi-Pinto Saro"))
    db.session.add(Author(name="Ashkenazi Hen"))
    db.session.add(Author(name="Yotvat Meiron"))
    db.session.add(Author(name="Abramowitz Janna"))

    try:
        db.session.commit()
    except IntegrityError as e:
        if "duplicate" in str(e.orig).lower():
            return jsonify({"error": f"{e.params[0]} already exists in DB"})
        else:
            raise e

    return jsonify(Author.query.get_or_404(1).to_dict())


@bp.route('/authors/<int:id>', methods=['GET'])
def get_author(id):
    log.debug(f"ENTER /authors/id/{id}")
    return jsonify(Author.query.get_or_404(id).to_dict())


@bp.route('/authors', methods=['GET'])
def get_authors():
    log.debug(f"ENTER /authors")
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = Author.to_collection_dict(Author.query, page, per_page, 'api.get_authors')
    return jsonify(data)


@bp.route('/authors/<int:id>/experiments', methods=['GET'])
def get_author_experiments(id):
    log.debug(f"ENTER /authors/{id}/experiments")
    author = Author.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = Author.to_collection_dict(author.experiments, page, per_page, 'api.get_author_experiments', id=id)
    return jsonify(data)
