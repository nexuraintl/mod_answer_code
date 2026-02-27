from flask import Flask, jsonify
import os
from config import Config
from src.controllers.ask_controller import ask_bp
from src.models.errors import AppError

def create_app():
    """
    Factory para crear la app Flask blueprints.
    """
    
    # Validar configuración al inicio
    errors = []
    if not Config.AZURE_PAT:
        errors.append("AZURE_PAT no configurado")
    if not Config.AZURE_ORG_URL:
        errors.append("AZURE_ORG_URL no configurado")
    if not Config.AZURE_CORE_REPOS:
        errors.append("AZURE_CORE_REPOS no configurado o vacío")
    if not Config.GEMINI_API_KEY:
        errors.append("GEMINI_API_KEY no configurado")
    if errors:
        print("\n" + "=" * 80)
        print(" Errores de configuración detectados:")
        print("=" * 80)
        for err in errors:
            print(f"  • {err}")
        print("\n Verifica tu archivo .env")
        print("=" * 80 + "\n")

    
    app = Flask(__name__)
    app.register_blueprint(ask_bp, url_prefix="/preguntar")
    
    # Health check
    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({
            "ok": True,
            "service": "Nexura Code AI",
            "repos": len(Config.AZURE_CORE_REPOS),
            "config_valid": bool(Config.AZURE_PAT and Config.GEMINI_API_KEY and Config.AZURE_CORE_REPOS)
        })
    
    # Manejador de errores global
    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify({
            "ok": False,
            "code": error.code,
            "error": error.message
        }), error.status_code
    
    @app.errorhandler(Exception)
    def handle_generic_error(error):
        print(f" Error inesperado: {error}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "ok": False,
            "code": "INTERNAL_ERROR",
            "error": str(error)
        }), 500
    
    return app



app = create_app()
if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    
    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )