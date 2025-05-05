from flask import Flask

app = Flask(__name__)

# Register the v1 API blueprint
from app.api.v1 import api_v1
app.register_blueprint(api_v1)

# Remove the old routes import
# from app import routes 