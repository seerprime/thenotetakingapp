from flask import Flask
from flask_cors import CORS
import os
from .utils.config import config, Config
from .routes.transcribe import transcribe_bp
from .routes.summarize import summarize_bp
from .routes.query import query_bp

def create_app(config_name="default"):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Setup CORS
    CORS(app, resources={
        r"/*": {"origins": app.config['CORS_ORIGINS']}
    })
    
    # Register blueprints
    app.register_blueprint(transcribe_bp, url_prefix='/api')
    app.register_blueprint(summarize_bp, url_prefix='/api')
    app.register_blueprint(query_bp, url_prefix='/api')
    
    # Create required directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    @app.route('/health')
    def health_check():
        """Basic health check endpoint."""
        return {'status': 'healthy'}
    
    return app

def main():
    """Main entry point for running the application."""
    # Get configuration from environment
    config_name = os.getenv('FLASK_CONFIG', 'default')
    
    # Create app
    app = create_app(config_name)
    
    # Run app
    app.run(
        host=app.config.get('API_HOST', '0.0.0.0'),
        port=app.config.get('API_PORT', 5000),
        debug=app.config.get('DEBUG', False)
    )

if __name__ == '__main__':
    main()