from flask import jsonify, request, url_for, abort
from app import db
from app.models import Author
from app.api import bp


@bp.route('/authors/generate', methods=['GET'])
def generate_authors():
    db.session.add(Author(name="Osheter Alexey"))
    db.session.add(Author(name="Osheter Tatiana"))
    db.session.add(Author(name="Campisi-Pinto Saro"))
    db.session.add(Author(name="Ashkenazi Hen"))
    db.session.add(Author(name="Yotvat Meiron"))
    db.session.add(Author(name="Abramowitz Janna"))
    db.session.commit()
    return jsonify(Author.query.get_or_404(1).to_dict())


@bp.route('/authors/<int:id>', methods=['GET'])
def get_author(id):
    return jsonify(Author.query.get_or_404(id).to_dict())


@bp.route('/authors', methods=['GET'])
def get_authors():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = Author.to_collection_dict(Author.query, page, per_page, 'api.get_authors')
    return jsonify(data)


@bp.route('/authors/<int:id>/experiments', methods=['GET'])
def get_author_experiments(id):
    author = Author.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = Author.to_collection_dict(author.experiments, page, per_page,
                                   'api.get_author_experiments', id=id)
    return jsonify(data)
