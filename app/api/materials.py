from flask import jsonify, request, url_for, abort
from app import db
from app.models import Material
from app.api import bp


@bp.route('/materials/generate', methods=['GET'])
def generate_materials():
    db.session.add(Material(name="LINSEED"))
    db.session.add(Material(name="CANOLA"))
    db.session.add(Material(name="SOYBEAN"))
    db.session.add(Material(name="LINSEED_EMULSION"))
    db.session.add(Material(name="MUSTARD"))
    db.session.add(Material(name="POMEGRANATE"))
    db.session.add(Material(name="RED_MICROALGEA"))
    db.session.add(Material(name="COCONUT_OIL"))
    db.session.add(Material(name="PEANUT_OIL"))
    db.session.commit()
    return jsonify(Material.query.get_or_404(3).to_dict())


@bp.route('/materials/<int:id>', methods=['GET'])
def get_material(id):
    return jsonify(Material.query.get_or_404(id).to_dict())


@bp.route('/materials', methods=['GET'])
def get_materials():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = Material.to_collection_dict(Material.query, page, per_page, 'api.get_materials')
    return jsonify(data)