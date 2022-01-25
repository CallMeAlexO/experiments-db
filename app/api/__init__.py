from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import experiments, materials, authors, batches