#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Aplicação Principal
Servidor Flask para análise de mercado ultra-detalhada
"""

import os
import sys
import time
import logging
from typing import Dict, List, Any, Optional
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from datetime import datetime
from logging.handlers import RotatingFileHandler

# Adiciona src ao path se necessário
if 'src' not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configuração de logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/arqv30.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

def create_app():
    """Cria e configura a aplicação Flask"""

    # Carrega variáveis de ambiente
    from services.environment_loader import environment_loader

    app = Flask(__name__)
    
    # CONFIGURAÇÃO CRÍTICA DE PRODUÇÃO
    # Força ambiente de produção - NUNCA debug em produção
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    debug = False  # SEMPRE False em produção
    app.config['DEBUG'] = debug
    app.config['TESTING'] = False

    # Configuração de logging para produção
    if FLASK_ENV == 'production':
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(name)s %(message)s'
        )
    else:
        logging.basicConfig(level=logging.DEBUG)

    # Configuração CORS para produção
    cors_origins = os.getenv('CORS_ORIGINS', '*')
    if FLASK_ENV == 'production' and cors_origins == '*':
        # Em produção, CORS deve ser restritivo
        cors_origins = ['https://yourdomain.com']  # Configurar domínio real

    CORS(app, resources={
        r"/api/*": {
            "origins": cors_origins.split(',') if isinstance(cors_origins, str) else cors_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # Chave secreta segura carregada do ambiente
    app.secret_key = os.getenv('SECRET_KEY', 'arqv30-enhanced-ultra-secure-key-2024')
    if not os.getenv('SECRET_KEY') and FLASK_ENV == 'production':
        raise ValueError("SECRET_KEY deve ser definida em produção")

    # Registra blueprints
    from routes.analysis import analysis_bp
    from routes.enhanced_analysis import enhanced_analysis_bp
    from routes.progress import progress_bp
    from routes.user import user_bp
    from routes.files import files_bp
    from routes.pdf_generator import pdf_bp
    from routes.monitoring import monitoring_bp
    from routes.forensic_analysis import forensic_bp

    app.register_blueprint(analysis_bp, url_prefix='/api')
    app.register_blueprint(enhanced_analysis_bp, url_prefix='/api')
    app.register_blueprint(progress_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(files_bp, url_prefix='/api')
    app.register_blueprint(pdf_bp, url_prefix='/api')
    app.register_blueprint(monitoring_bp, url_prefix='/api')
    app.register_blueprint(forensic_bp, url_prefix='/api/forensic')

    @app.route('/')
    def index():
        """Página principal"""
        return render_template('enhanced_index.html')

    @app.route('/archaeological')
    def archaeological():
        """Interface arqueológica"""
        return render_template('enhanced_interface.html')

    @app.route('/forensic')
    def forensic():
        """Interface forense"""
        return render_template('forensic_interface.html')

    @app.route('/unified')
    def unified():
        """Interface unificada"""
        return render_template('unified_interface.html')

    @app.route('/api/app_status')
    def app_status():
        """Status da aplicação"""
        try:
            from services.ai_manager import ai_manager
            from services.production_search_manager import production_search_manager
            from database import db_manager

            ai_status = ai_manager.get_provider_status()
            search_status = production_search_manager.get_provider_status()
            db_status = db_manager.test_connection()

            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '2.0.0',
                'services': {
                    'ai_providers': {
                        'available': len([p for p in ai_status.values() if p['available']]),
                        'total': len(ai_status),
                        'providers': ai_status
                    },
                    'search_providers': {
                        'available': len([p for p in search_status.values() if p['available']]),
                        'total': len(search_status),
                        'providers': search_status
                    },
                    'database': {
                        'connected': db_status
                    }
                }
            })
        except Exception as e:
            logger.error(f"Error in app_status: {e}")
            return jsonify({
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint não encontrado'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

    return app

def main():
    """Função principal"""

    print("🚀 ARQV30 Enhanced v2.0 - Iniciando aplicação...")

    try:
        # Cria aplicação
        app = create_app()

        # Configurações do servidor
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', 5000))
        debug = os.getenv('FLASK_ENV', 'production') == 'development' # This line is kept for clarity in main, but app.config['DEBUG'] is set in create_app

        print(f"🌐 Servidor: http://{host}:{port}")
        print(f"🔧 Modo: {'Desenvolvimento' if debug else 'Produção'}")
        print(f"📊 Interface: Análise Ultra-Detalhada de Mercado")
        print(f"🤖 IA: Gemini 2.5 Pro + Groq + Fallbacks")
        print(f"🔍 Pesquisa: WebSailor + Google + Múltiplos Engines")
        print(f"💾 Banco: Supabase + Arquivos Locais")
        print(f"🛡️ Sistema: Ultra-Robusto com Salvamento Automático")

        print("\n" + "=" * 60)
        print("✅ ARQV30 Enhanced v2.0 PRONTO!")
        print("=" * 60)
        print("Pressione Ctrl+C para parar o servidor")
        print("=" * 60)

        # Inicia servidor
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )

    except KeyboardInterrupt:
        print("\n\n✅ Servidor encerrado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro ao iniciar servidor: {e}")
        logger.critical(f"Critical error during server startup: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()