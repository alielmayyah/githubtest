from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
import certifi

# Load environment variables from .env
load_dotenv()

def test_mongo_connection(app, client):
    try:
        client.admin.command("ping")
        print("Database connected successfully")  # Print statement for successful connection
        app.logger.info("Database connected successfully")
    except Exception as e:
        print(f"Database connection failed: {e}")  # Print statement for failed connection
        app.logger.critical("Database connection failed: %s", e)


# Define before_request handlers
def basic_authentication():
    if request.method.lower() == 'options':
        return Response()

def setup_cors():
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Credentials': 'true'
    }
    if request.method in ['OPTIONS', 'options']:
        return jsonify(headers), 200

def create_app():
    app = Flask(__name__)

    # Load MongoDB URI from .env and create MongoDB client
    uri = os.getenv('MONGO_URL')
    mongo_client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())

    # Configure the Flask app (if any additional configurations are needed)
    app.config['JWT_SECRET'] = os.getenv('JWT_SECRET')
    
    # Test MongoDB connection
    with app.app_context():
        # Test MongoDB connection inside an application context
        test_mongo_connection(app, mongo_client)

    # Initialize CORS with support for credentials
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
    
    # Register before_request handlers
    app.before_request(basic_authentication)
    app.before_request(setup_cors)

    # Import and register the blueprints
    from routes.AuthRoutes import auth_routes  # Adjust the import path as necessary
    app.register_blueprint(auth_routes)
    # Import and register the project_routes blueprint
    from routes.projectRoutes import project_routes
    app.register_blueprint(project_routes)
    # Import and register the contentPlan_routes blueprint
    from routes.contentPlanRoutes import contentPlan_routes
    app.register_blueprint(contentPlan_routes)
    # Import and register the profile_routes blueprint
    from routes.profileRoutes import profile_routes
    app.register_blueprint(profile_routes)
    @app.route('/')
    def index():
        return "Welcome To Flask App"
    
    # Optionally, store mongo_client reference in app for easy access across the app
    app.config['mongo_client'] = mongo_client
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
