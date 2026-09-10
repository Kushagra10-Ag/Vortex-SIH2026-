from flask import jsonify
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from app.db import db
from app.utils.logger import logger

def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"success": False, "error": "Bad Request", "details": str(e)}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": "Endpoint or resource not found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"success": False, "error": "Method Not Allowed"}), 405

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        return jsonify({
            "success": False,
            "error": e.description or e.name,
            "code": e.code
        }), e.code

    @app.errorhandler(SQLAlchemyError)
    def handle_db_error(e):
        db.session.rollback()
        logger.error(f"Database error occurred: {str(e)}")
        return jsonify({
            "success": False,
            "error": "A database error occurred. Changes were rolled back.",
            "details": str(e) if app.debug else None
        }), 500

    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        logger.exception(f"Unhandled exception: {str(e)}")
        return jsonify({
            "success": False,
            "error": "An internal server error occurred.",
            "details": str(e) if app.debug else None
        }), 500

