from app import create_app, db
from app.models import Experiment, Author, Material

application = create_app()


@application.shell_context_processor
def make_shell_context():
    return {'db': db, 'Author': Author, 'Experiment': Experiment, 'Material': Material}


if __name__ == "__main__":
    application.run(debug=True)
