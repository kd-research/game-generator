from flask import Blueprint

# Define the blueprint for v1 API endpoints
api_v1 = Blueprint('api_v1', __name__, url_prefix='/v1')

# Import the routes to register them with the blueprint
# These imports need to be after the Blueprint definition
from . import generate_game, customize_game 