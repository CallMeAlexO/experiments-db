#!/usr/bin/python3
import sys
import logging
import logging.handlers as handlers

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
sys.path.insert(0,"/var/www/FlaskApp/")

from server import app as application
application.logger = logging.getLogger("application")
