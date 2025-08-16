#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Analysis Routes com Controles de Sessão
Rotas para análise de mercado com pausar/continuar/salvar
"""

import logging
from flask import Blueprint, request, jsonify, render_template
from datetime import datetime
import json
import os
from services.ultra_detailed_analysis_engine import ultra_detailed_analysis_engine
from services.auto_save_manager import auto_save_manager, salvar_etapa, salvar_erro
from services.super_orchestrator import super_orchestrator
from services.comprehensive_report_generator import comprehensive_report_generator
from services.tavily_mcp_client import tavily_mcp_client

logger = logging.getLogger(__name__)

analysis_bp = Blueprint('analysis', __name__)

# Instancia o Super Orchestrator
orchestrator = super_orchestrator

# Armazena sessões ativas
active_sessions = {}

@analysis_bp.route('/')
def index():
    """Interface principal"""
    return render_template('unified_interface.html')

@analysis_bp.route('/analyze', methods=['POST'])
@analysis_bp.route('/api/analyze', methods=['POST'])
def analyze():
    """Inicia análise de mercado com controle de sessão"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400

        logger.info("🚀 Iniciando análise de mercado ultra-detalhada")

        # Cria sessão única
        session_id = auto_save_manager.iniciar_sessao()

        # Salva dados da requisição
        salvar_etapa("requisicao_analise", data, categoria="analise_completa")

        segmento_negocio = data.get('segmento')
        produto_servico = data.get('produto')
        publico_alvo = data.get('publico_alvo', '')
        objetivos_estrategicos = data.get('objetivos_estrategicos', '')
        contexto_adicional = data.get('contexto_adicional', '')

        logger.info(f"📊 Dados recebidos: Segmento={segmento_negocio}, Produto={produto_servico}")

        # Prepara query de pesquisa
        query = data.get('query', f"mercado de {produto_servico or segmento_negocio} no brasil desde 2022")
        logger.info(f"🔍 Query de pesquisa: {query}")

        # Salva query
        salvar_etapa("query_preparada", {"query": query}, categoria="pesquisa_web")

        # Registra sessão como ativa
        active_sessions[session_id] = {
            'status': 'running',
            'data': data,
            'started_at': datetime.now().isoformat(),
            'paused_at': None
        }

        # Função para enviar atualizações de progresso
        def send_progress_update(session_id, step, message):
            logger.info(f"Progress {session_id}: Step {step} - {message}")
            salvar_etapa("progresso", {
                "step": step,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }, categoria="logs")

        # Executa análise COMPLETA com todos os serviços
        logger.info("🚀 Executando análise COMPLETA com todos os serviços...")

        analysis_data = {
            'segmento': segmento_negocio,
            'produto': produto_servico,
            'publico': publico_alvo,
            'objetivos': objetivos_estrategicos,
            'contexto': contexto_adicional,
            'query': query
        }

        resultado = super_orchestrator.execute_synchronized_analysis(
            data=analysis_data,
            session_id=session_id,
            progress_callback=lambda step, msg: send_progress_update(session_id, step, msg)
        )

        # Atualiza status da sessão
        active_sessions[session_id]['status'] = 'completed'
        active_sessions[session_id]['completed_at'] = datetime.now().isoformat()

        # Gera relatório final limpo
        try:
            clean_report = comprehensive_report_generator.generate_clean_report(resultado, session_id)
            resultado['relatorio_final_limpo'] = clean_report
            logger.info("✅ Relatório final limpo gerado")
        except Exception as e:
            logger.error(f"❌ Erro ao gerar relatório limpo: {e}")

        # Resposta final
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'Análise COMPLETA concluída com sucesso!',
            'processing_time': resultado.get('metadata', {}).get('processing_time_formatted', 'N/A'),
            'data': resultado,
            'engine': 'ARQV30 Enhanced v3.0 - ULTRA CLEAN',
            'clean_report_available': 'relatorio_final_limpo' in resultado
        })

    except Exception as e:
        logger.error(f"❌ Erro na análise: {str(e)}")
        if 'session_id' in locals() and session_id:
            active_sessions[session_id]['status'] = 'error'
            active_sessions[session_id]['error'] = str(e)
            active_sessions[session_id]['error_at'] = datetime.now().isoformat()
            salvar_erro("erro_analise", e, {"session_id": session_id})
        else:
            salvar_erro("erro_geral_analise", e)
        return jsonify({
            'success': False,
            'session_id': locals().get('session_id'), # Try to get session_id if it was created
            'error': str(e),
            'message': 'Erro na análise. Dados intermediários foram salvos.'
        }), 500


@analysis_bp.route('/sessions', methods=['GET'])
def list_sessions():
    """Lista todas as sessões salvas"""
    try:
        # Lista sessões do auto_save_manager
        try:
            saved_sessions_ids = auto_save_manager.listar_sessoes()
        except AttributeError:
            # Fallback se método não existe
            import os
            base_path = 'relatorios_intermediarios/logs'
            saved_sessions_ids = []
            if os.path.exists(base_path):
                for item in os.listdir(base_path):
                    if item.startswith('session_'):
                        saved_sessions_ids.append(item.replace('session_', '').split('.')[0]) # Extract session ID
            else:
                saved_sessions_ids = []

        sessions_list = []
        for session_id in saved_sessions_ids:
            session_data = active_sessions.get(session_id, {})
            session_info = auto_save_manager.obter_info_sessao(session_id)

            sessions_list.append({
                'session_id': session_id,
                'status': session_data.get('status', 'saved'), # Default to 'saved' if not active
                'segmento': session_data.get('data', {}).get('segmento', 'N/A'),
                'produto': session_data.get('data', {}).get('produto', 'N/A'), # Corrected variable name here
                'started_at': session_data.get('started_at'),
                'completed_at': session_data.get('completed_at'),
                'paused_at': session_data.get('paused_at'),
                'error': session_data.get('error'),
                'etapas_salvas': len(session_info.get('etapas', {})) if session_info else 0
            })

        return jsonify({
            'success': True,
            'sessions': sessions_list,
            'total': len(sessions_list)
        })

    except Exception as e:
        logger.error(f"❌ Erro ao listar sessões: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/sessions/<session_id>/pause', methods=['POST'])
def pause_session(session_id):
    """Pausa uma sessão ativa"""
    try:
        if session_id not in active_sessions:
            return jsonify({'error': 'Sessão não encontrada'}), 404

        session = active_sessions[session_id]
        if session['status'] != 'running':
            return jsonify({'error': 'Sessão não está em execução'}), 400

        # Atualiza status
        session['status'] = 'paused'
        session['paused_at'] = datetime.now().isoformat()

        # Salva estado de pausa
        salvar_etapa("sessao_pausada", {
            "session_id": session_id,
            "paused_at": session['paused_at'],
            "reason": "User requested pause"
        }, categoria="logs")

        logger.info(f"⏸️ Sessão {session_id} pausada pelo usuário")

        return jsonify({
            'success': True,
            'message': 'Sessão pausada com sucesso',
            'session_id': session_id,
            'status': 'paused'
        })

    except Exception as e:
        logger.error(f"❌ Erro ao pausar sessão: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/sessions/<session_id>/resume', methods=['POST'])
def resume_session(session_id):
    """Resume uma sessão pausada"""
    try:
        if session_id not in active_sessions:
            return jsonify({'error': 'Sessão não encontrada'}), 404

        session = active_sessions[session_id]
        if session['status'] != 'paused':
            return jsonify({'error': 'Sessão não está pausada'}), 400

        # Atualiza status
        session['status'] = 'running'
        session['resumed_at'] = datetime.now().isoformat()
        session['paused_at'] = None

        # Salva estado de resume
        salvar_etapa("sessao_resumida", {
            "session_id": session_id,
            "resumed_at": session['resumed_at'],
            "reason": "User requested resume"
        }, categoria="logs")

        logger.info(f"▶️ Sessão {session_id} resumida pelo usuário")

        return jsonify({
            'success': True,
            'message': 'Sessão resumida com sucesso',
            'session_id': session_id,
            'status': 'running'
        })

    except Exception as e:
        logger.error(f"❌ Erro ao resumir sessão: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/sessions/<session_id>/continue', methods=['POST'])
def continue_session(session_id):
    """Continua uma sessão salva"""
    try:
        # Recupera dados da sessão
        session_info = auto_save_manager.obter_info_sessao(session_id)

        if not session_info:
            return jsonify({'error': 'Sessão não encontrada'}), 404

        # Recupera dados originais
        original_data = None
        for etapa_nome, etapa_data in session_info.get('etapas', {}).items():
            if 'requisicao_analise' in etapa_nome:
                original_data = etapa_data.get('dados', {})
                break

        if not original_data:
            return jsonify({'error': 'Dados originais não encontrados'}), 400

        # Registra como sessão ativa
        active_sessions[session_id] = {
            'status': 'running',
            'data': original_data,
            'continued_at': datetime.now().isoformat(),
            'original_session': True
        }

        # Continua a análise
        def progress_callback(step, message):
            logger.info(f"Continue Progress {session_id}: Step {step} - {message}")
            salvar_etapa("progresso_continuacao", {
                "step": step,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }, categoria="logs")

        logger.info(f"🔄Continuando análise da sessão {session_id}...")

        # Use o Super Orchestrator para continuar a análise
        analysis_data = {
            'segmento': original_data.get('segmento'),
            'produto': original_data.get('produto'),
            'publico': original_data.get('publico_alvo', ''),
            'objetivos': original_data.get('objetivos_estrategicos', ''),
            'contexto': original_data.get('contexto_adicional', ''),
            'query': original_data.get('query', f"mercado de {original_data.get('produto') or original_data.get('segmento')} no brasil desde 2022")
        }

        resultado = super_orchestrator.execute_synchronized_analysis(
            data=analysis_data,
            session_id=session_id,
            progress_callback=progress_callback,
            continue_from_saved=True # Indicate that we are continuing a saved session
        )

        active_sessions[session_id]['status'] = 'completed'
        active_sessions[session_id]['completed_at'] = datetime.now().isoformat()

        # Gera relatório final limpo
        try:
            clean_report = comprehensive_report_generator.generate_clean_report(resultado, session_id)
            resultado['relatorio_final_limpo'] = clean_report
            logger.info("✅ Relatório final limpo gerado")
        except Exception as e:
            logger.error(f"❌ Erro ao gerar relatório limpo: {e}")

        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'Análise continuada e concluída com sucesso!',
            'data': resultado,
            'engine': 'ARQV30 Enhanced v3.0 - ULTRA CLEAN',
            'clean_report_available': 'relatorio_final_limpo' in resultado
        })

    except Exception as e:
        logger.error(f"❌ Erro geral ao continuar sessão: {str(e)}")
        if 'session_id' in locals() and session_id:
            active_sessions[session_id]['status'] = 'error'
            active_sessions[session_id]['error'] = str(e)
            active_sessions[session_id]['error_at'] = datetime.now().isoformat()
            salvar_erro("erro_continuacao_sessao", e, {"session_id": session_id})
        else:
            salvar_erro("erro_geral_continuacao_sessao", e)
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/sessions/<session_id>/save', methods=['POST'])
def save_session(session_id):
    """Salva explicitamente uma sessão"""
    try:
        if session_id not in active_sessions:
            return jsonify({'error': 'Sessão não encontrada'}), 404

        session = active_sessions[session_id]

        # Salva estado completo da sessão
        salvar_etapa("sessao_salva_explicitamente", {
            "session_id": session_id,
            "saved_at": datetime.now().isoformat(),
            "session_data": session,
            "reason": "User explicitly saved session"
        }, categoria="logs")

        logger.info(f"💾 Sessão {session_id} salva explicitamente pelo usuário")

        return jsonify({
            'success': True,
            'message': 'Sessão salva com sucesso',
            'session_id': session_id
        })

    except Exception as e:
        logger.error(f"❌ Erro ao salvar sessão: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/sessions/<session_id>/status', methods=['GET'])
@analysis_bp.route('/api/sessions/<session_id>/status', methods=['GET'])
def get_session_status(session_id):
    """Obtém status de uma sessão"""
    try:
        session = active_sessions.get(session_id)
        session_info = auto_save_manager.obter_info_sessao(session_id)

        if not session and not session_info:
            return jsonify({'error': 'Sessão não encontrada'}), 404

        status_data = {
            'session_id': session_id,
            'status': session.get('status', 'saved') if session else 'saved', # Default to 'saved' if not active
            'active': session is not None,
            'saved': session_info is not None,
            'etapas_salvas': len(session_info.get('etapas', {})) if session_info else 0
        }

        if session:
            status_data.update({
                'started_at': session.get('started_at'),
                'paused_at': session.get('paused_at'),
                'completed_at': session.get('completed_at'),
                'error': session.get('error'),
                'segmento': session.get('data', {}).get('segmento'),
                'produto': session.get('data', {}).get('produto')
            })

        return jsonify({
            'success': True,
            'session': status_data
        })

    except Exception as e:
        logger.error(f"❌ Erro ao obter status da sessão: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/api/sessions', methods=['GET'])
def api_list_sessions():
    """API endpoint para listar sessões"""
    return list_sessions()

@analysis_bp.route('/api/progress/<session_id>', methods=['GET'])
def api_get_progress(session_id):
    """API endpoint para obter progresso"""
    try:
        session = active_sessions.get(session_id)
        session_info = auto_save_manager.obter_info_sessao(session_id)

        if not session and not session_info:
            return jsonify({'error': 'Sessão não encontrada'}), 404

        if session and session['status'] == 'error':
            return jsonify({
                'success': False,
                'completed': False,
                'percentage': 0,
                'current_step': f"Erro: {session.get('error')}",
                'total_steps': 13,
                'estimated_time': 'N/A'
            })

        if session and session['status'] == 'completed':
            return jsonify({
                'success': True,
                'completed': True,
                'percentage': 100,
                'current_step': 'Análise concluída',
                'total_steps': 13,
                'estimated_time': '0m'
            })
        elif session and session['status'] == 'running':
            # Tenta obter progresso do Super Orchestrator se disponível
            progress_data = super_orchestrator.get_session_progress(session_id)
            if progress_data:
                return jsonify({
                    'success': True,
                    'completed': progress_data.get('completed', False),
                    'percentage': progress_data.get('percentage', 0),
                    'current_step': progress_data.get('current_step', 'Processando...'),
                    'total_steps': progress_data.get('total_steps', 13),
                    'estimated_time': progress_data.get('estimated_time', 'N/A')
                })
            else:
                # Fallback para cálculo de progresso baseado no tempo
                start_time = datetime.fromisoformat(session['started_at'])
                elapsed = (datetime.now() - start_time).total_seconds()
                progress = min(elapsed / 600 * 100, 95)  # 10 minutos = 100% (ajustar conforme necessário)

                return jsonify({
                    'success': True,
                    'completed': False,
                    'percentage': progress,
                    'current_step': f'Processando... ({progress:.0f}%)',
                    'total_steps': 13,
                    'estimated_time': f'{max(0, 10 - elapsed/60):.0f}m' # Estimativa de 10 minutos totais
                })
        else: # Paused or unknown status
            return jsonify({
                'success': True,
                'completed': False,
                'percentage': 0,
                'current_step': 'Pausado' if session and session['status'] == 'paused' else 'Aguardando',
                'total_steps': 13,
                'estimated_time': 'N/A'
            })

    except Exception as e:
        logger.error(f"❌ Erro ao obter progresso: {str(e)}")
        return jsonify({'error': str(e)}), 500