import datetime
from flask import url_for
from sqlalchemy import ForeignKey

from app import db


class PaginatedAPIMixin(object):
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False)
        data = {
            'items': [item.to_dict() for item in resources.items],
            '_meta': {
                'page': page,
                'per_page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page,
                                **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page,
                                **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page,
                                **kwargs) if resources.has_prev else None
            }
        }
        return data


class Experiment(PaginatedAPIMixin, db.Model):
    __tablename__ = 'experiments'

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))
    experiments = db.relationship('ExperimentData', backref='raw_experiment', lazy='dynamic')
    material_id = db.Column(db.Integer, ForeignKey('materials.id'))
    batch_id = db.Column(db.Integer, ForeignKey('batches.id'))
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now)
    part_of = db.Column(db.String(256), default=None)

    def __repr__(self):
        return '<Experiment {}>'.format(self.experiment_id)

    def to_dict(self, include_rawdata=False):
        data = {
            'id': self.id,
            'type': self.material_id,
            'timestamp': self.timestamp,
            'author': self.author_id,
            'batch': self.batch_id,
            'vectors': [x.get_vector_name() for x in self.experiments.all()]
        }
        if include_rawdata:
            pass
        return data

    def get_type(self, type):
        data_type, vector = type.split("_")
        data_type, vector = ExperimentData.str_to_data_type(data_type), ExperimentData.str_to_vector(vector)
        return self.experiments.filter_by(vector=vector, data_type=data_type).first()


class NmrExperiment(PaginatedAPIMixin, db.Model):
    __tablename__ = 'nmr-experiments'

    nmrexp_id = db.Column(db.Integer, db.ForeignKey('experiments.id'), primary_key=True)
    result = db.Column(db.Integer)

    def __repr__(self):
        return '<NmrExperiment {}>'.format(self.experiment_id)

    def to_dict(self, include_rawdata=False):
        data = {
            'id': self.experiment_id,
            'type': self.material_id,
            'timestamp': self.timestamp,
            'author': self.author_id,
            'result': self.result,
            'vectors': [x.get_vector_name() for x in self.experiments.all()]
        }
        if include_rawdata:
            pass
        return data

    def get_type(self, type):
        data_type, vector = type.split("_")
        data_type, vector = ExperimentData.str_to_data_type(data_type), ExperimentData.str_to_vector(vector)
        return self.experiments.filter_by(vector=vector, data_type=data_type).first()


class Author(PaginatedAPIMixin, db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    email = db.Column(db.String(120), index=True, unique=True)
    experiments = db.relationship('Experiment', backref='backref_author', lazy='dynamic')

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
        }
        return data


class Material(PaginatedAPIMixin, db.Model):
    __tablename__ = 'materials'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    experiments = db.relationship('Experiment', backref='backref_material', lazy='dynamic')

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
        }
        return data

class Batch(PaginatedAPIMixin, db.Model):
    __tablename__ = 'batches'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    experiments = db.relationship('Experiment', backref='backref_batch', lazy='dynamic')

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
        }
        return data

class ExperimentData(db.Model):
    __tablename__ = 'rawdata'

    id = db.Column(db.Integer, primary_key=True)
    experiment_id = db.Column(db.Integer, db.ForeignKey('experiments.id'))
    data_type = db.Column(db.Integer)  # Excel, TXT, RiDat, ...
    vector = db.Column(db.Integer)  # T1, T2, 2D
    data = db.Column(db.LargeBinary)

    def get_vector_name(self):
        name = ""
        if self.data_type == 1:
            name = "Excel"
        elif self.data_type == 2:
            name = "TXT"
        elif self.data_type == 3:
            name = "RiDat"
        name += "_"
        if self.vector == 1:
            name += "T1"
        elif self.vector == 2:
            name += "T2"
        elif self.vector == 3:
            name += "2D"
        return name

    def to_dict(self):
        return self.data

    @classmethod
    def str_to_vector(cls, vector):
        if vector == "T1": return 1
        if vector == "T2": return 2
        if vector == "2D": return 3

    @classmethod
    def str_to_data_type(cls, datatype):
        if datatype == "Excel": return 1
        if datatype == "TXT": return 2
        if datatype == "RiDat": return 3
