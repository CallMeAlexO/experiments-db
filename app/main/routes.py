from flask import render_template, request, url_for
from sqlalchemy import func
from werkzeug.utils import redirect

from app.api.experiments import add_experiments, get_experiments
from app.main import bp
from app.models import Author, Material, Batch, Experiment


@bp.route('/')
@bp.route('/index')
def index():
    return render_template("index.html")


@bp.route('/authors')
def authors_frontend():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    authors = Author.to_collection_dict(Author.query, page, per_page, 'api.get_authors')
    return render_template("authors.html", authors=authors["items"])


@bp.route('/materials')
def materials_frontend():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    materials = Material.to_collection_dict(Material.query, page, per_page, 'api.get_materials')
    # TODO: Replace this with materials.html....
    return render_template("authors.html", authors=materials["items"])


@bp.route('/batches')
def batches_frontend():
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    batches = Batch.to_collection_dict(Batch.query, page, per_page, 'main.batches_frontend')
    links = batches["_links"]
    for item in batches["items"]:
        batch = Batch.query.get(item["id"])
        item["experiments"] = batch.experiments.count()
    return render_template("batches.html", batches=batches["items"], prev=links["prev"], next=links["next"])


@bp.route('/experiments', methods=['GET', 'POST'])
def experiments_frontend():
    authors = Author.query.all()
    batches = Batch.query.all()
    materials = Material.query.all()
    part_of = ["nmr"]

    if len(request.args) == 0:
        request.args = request.form # Either user sent a request, or it came from the filter...

    # experiments = Experiment.to_collection_dict(Experiment.query, page, per_page, 'api.get_experiments')
    experiments = get_experiments('main.experiments_frontend').json

    return render_template("experiments.html", authors=authors, batches=batches, materials=materials, part_of=part_of,
                           experiments=experiments["items"])


@bp.route('/upload')
def upload_frontend():
    authors = Author.query.all()
    batches = Batch.query.all()
    materials = Material.query.all()
    return render_template("upload.html", authors=authors, batches=batches, materials=materials)


@bp.route('/upload', methods=['POST'])
def upload_post():
    request.args = request.form
    pp = add_experiments()
    if pp.status_code != 201:
        # TODO: Redirect to error page - explain the error
        redirect(url_for('main.authors'))
    # uploaded_file = request.files['file']
    # if uploaded_file.filename != '':
    #     uploaded_file.save(uploaded_file.filename)
    return redirect(url_for('main.index'))