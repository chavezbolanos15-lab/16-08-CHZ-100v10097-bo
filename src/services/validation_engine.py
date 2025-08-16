#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARQV30 Enhanced v2.0 - Validation Engine
Motor de validação científica para garantir qualidade dos dados
"""

import logging
import re
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ValidationEngine:
    """Motor de validação científica para análises"""
    
    def __init__(self):
        """Inicializa motor de validação"""
        self.quality_thresholds = {
            'min_drivers': 19,
            'min_provis': 5,
            'min_insights': 25,
            'min_density': 85.0,
            'min_cialdini_triggers': 3,
            'min_content_length': 5000
        }
        
        self.validation_rules = {
            'drivers_mentais': self._validate_mental_drivers,
            'provas_visuais': self._validate_visual_proofs,
            'sistema_anti_objecao': self._validate_anti_objection,
            'avatar_ultra_detalhado': self._validate_avatar,
            'metricas_forenses': self._validate_forensic_metrics
        }
        
        logger.info("🔬 Validation Engine inicializado")
    
    def validate_complete_analysis(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida análise completa com critérios científicos"""
        
        validation_result = {
            'overall_valid': False,
            'quality_score': 0.0,
            'component_validations': {},
            'critical_issues': [],
            'warnings': [],
            'recommendations': [],
            'scientific_compliance': False,
            'validated_at': datetime.now().isoformat()
        }
        
        total_score = 0.0
        max_score = 0.0
        
        # Valida cada componente
        for component_name, validator in self.validation_rules.items():
            try:
                component_data = analysis_data.get(component_name, {})
                component_validation = validator(component_data, analysis_data)
                
                validation_result['component_validations'][component_name] = component_validation
                
                # Calcula score ponderado
                weight = self._get_component_weight(component_name)
                total_score += component_validation['score'] * weight
                max_score += 100 * weight
                
                # Coleta issues críticos
                if component_validation['critical_issues']:
                    validation_result['critical_issues'].extend(component_validation['critical_issues'])
                
                # Coleta warnings
                if component_validation['warnings']:
                    validation_result['warnings'].extend(component_validation['warnings'])
                    
            except Exception as e:
                logger.error(f"❌ Erro ao validar {component_name}: {e}")
                validation_result['critical_issues'].append(f"Falha na validação de {component_name}: {str(e)}")
        
        # Calcula score geral
        validation_result['quality_score'] = (total_score / max_score * 100) if max_score > 0 else 0
        
        # Determina se é válido
        validation_result['overall_valid'] = (
            validation_result['quality_score'] >= 80.0 and
            len(validation_result['critical_issues']) == 0
        )
        
        # Verifica compliance científica
        validation_result['scientific_compliance'] = self._check_scientific_compliance(analysis_data)
        
        # Gera recomendações
        validation_result['recommendations'] = self._generate_recommendations(validation_result)
        
        logger.info(f"🔬 Validação concluída: Score {validation_result['quality_score']:.1f}%")
        
        return validation_result
    
    def _validate_mental_drivers(self, drivers_data: Dict[str, Any], full_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Valida drivers mentais"""
        
        validation = {
            'valid': False,
            'score': 0.0,
            'critical_issues': [],
            'warnings': [],
            'metrics': {}
        }
        
        try:
            drivers_list = drivers_data.get('drivers_customizados', [])
            
            if not drivers_list:
                validation['critical_issues'].append("Nenhum driver mental encontrado")
                return validation
            
            # Verifica quantidade
            driver_count = len(drivers_list)
            validation['metrics']['driver_count'] = driver_count
            
            if driver_count < 5:
                validation['critical_issues'].append(f"Drivers insuficientes: {driver_count} < 5 mínimo")
            elif driver_count < 19:
                validation['warnings'].append(f"Drivers abaixo do ideal: {driver_count} < 19 recomendado")
            
            # Verifica qualidade dos drivers
            valid_drivers = 0
            generic_drivers = 0
            
            for driver in drivers_list:
                if isinstance(driver, dict):
                    nome = driver.get('nome', '')
                    definicao = driver.get('definicao_visceral', '')
                    
                    if nome and definicao and len(definicao) > 50:
                        valid_drivers += 1
                    
                    # Verifica se é genérico
                    if any(generic in str(driver).lower() for generic in ['em desenvolvimento', 'customizado para', 'driver mental']):
                        generic_drivers += 1
            
            validation['metrics']['valid_drivers'] = valid_drivers
            validation['metrics']['generic_drivers'] = generic_drivers
            
            # Calcula score
            quality_ratio = valid_drivers / driver_count if driver_count > 0 else 0
            quantity_score = min(driver_count / 19 * 100, 100)
            quality_score = quality_ratio * 100
            
            validation['score'] = (quantity_score + quality_score) / 2
            validation['valid'] = validation['score'] >= 60.0 and len(validation['critical_issues']) == 0
            
        except Exception as e:
            validation['critical_issues'].append(f"Erro na validação de drivers: {str(e)}")
        
        return validation
    
    def _validate_visual_proofs(self, proofs_data: Dict[str, Any], full_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Valida provas visuais (PROVIs)"""
        
        validation = {
            'valid': False,
            'score': 0.0,
            'critical_issues': [],
            'warnings': [],
            'metrics': {}
        }
        
        try:
            # Busca PROVIs em diferentes locais
            provis_list = []
            
            if isinstance(proofs_data, list):
                provis_list = proofs_data
            elif isinstance(proofs_data, dict):
                provis_list = (
                    proofs_data.get('arsenal_provis_completo', []) or
                    proofs_data.get('provas_visuais', []) or
                    proofs_data.get('visual_proofs', [])
                )
            
            validation['metrics']['provis_count'] = len(provis_list)
            
            if not provis_list:
                validation['critical_issues'].append("Nenhuma PROVI encontrada")
                return validation
            
            # Verifica qualidade das PROVIs
            valid_provis = 0
            complete_provis = 0
            
            for provi in provis_list:
                if isinstance(provi, dict):
                    nome = provi.get('nome', '')
                    experimento = provi.get('experimento', '') or provi.get('experimento_escolhido', '')
                    
                    if nome and experimento:
                        valid_provis += 1
                        
                        # Verifica se tem roteiro completo
                        if provi.get('roteiro_completo') and provi.get('materiais'):
                            complete_provis += 1
            
            validation['metrics']['valid_provis'] = valid_provis
            validation['metrics']['complete_provis'] = complete_provis
            
            # Calcula score
            if len(provis_list) >= 5:
                quantity_score = 100
            elif len(provis_list) >= 3:
                quantity_score = 80
            else:
                quantity_score = len(provis_list) * 20
            
            quality_score = (valid_provis / len(provis_list) * 100) if provis_list else 0
            completeness_score = (complete_provis / len(provis_list) * 100) if provis_list else 0
            
            validation['score'] = (quantity_score + quality_score + completeness_score) / 3
            validation['valid'] = validation['score'] >= 70.0 and len(validation['critical_issues']) == 0
            
        except Exception as e:
            validation['critical_issues'].append(f"Erro na validação de PROVIs: {str(e)}")
        
        return validation
    
    def _validate_anti_objection(self, anti_obj_data: Dict[str, Any], full_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Valida sistema anti-objeção"""
        
        validation = {
            'valid': False,
            'score': 0.0,
            'critical_issues': [],
            'warnings': [],
            'metrics': {}
        }
        
        try:
            # Verifica objeções universais
            universais = anti_obj_data.get('objecoes_universais', {})
            validation['metrics']['universais_count'] = len(universais)
            
            required_universals = ['tempo', 'dinheiro', 'confianca']
            missing_universals = [req for req in required_universals if req not in universais]
            
            if missing_universals:
                validation['critical_issues'].append(f"Objeções universais ausentes: {missing_universals}")
            
            # Verifica scripts personalizados
            scripts = anti_obj_data.get('scripts_personalizados', {})
            validation['metrics']['scripts_count'] = len(scripts)
            
            if not scripts:
                validation['critical_issues'].append("Scripts personalizados ausentes")
            
            # Verifica arsenal de emergência
            arsenal = anti_obj_data.get('arsenal_emergencia', [])
            validation['metrics']['arsenal_count'] = len(arsenal)
            
            if len(arsenal) < 5:
                validation['warnings'].append(f"Arsenal de emergência limitado: {len(arsenal)} < 5")
            
            # Calcula score
            coverage_score = (len(universais) / 3 * 100) if len(universais) <= 3 else 100
            scripts_score = min(len(scripts) / 3 * 100, 100)
            arsenal_score = min(len(arsenal) / 8 * 100, 100)
            
            validation['score'] = (coverage_score + scripts_score + arsenal_score) / 3
            validation['valid'] = validation['score'] >= 70.0 and len(validation['critical_issues']) == 0
            
        except Exception as e:
            validation['critical_issues'].append(f"Erro na validação anti-objeção: {str(e)}")
        
        return validation
    
    def _validate_avatar(self, avatar_data: Dict[str, Any], full_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Valida avatar ultra-detalhado"""
        
        validation = {
            'valid': False,
            'score': 0.0,
            'critical_issues': [],
            'warnings': [],
            'metrics': {}
        }
        
        try:
            # Verifica dores viscerais
            dores = avatar_data.get('dores_viscerais', []) or avatar_data.get('feridas_abertas_inconfessaveis', [])
            validation['metrics']['dores_count'] = len(dores)
            
            if len(dores) < 5:
                validation['critical_issues'].append(f"Dores insuficientes: {len(dores)} < 5")
            
            # Verifica desejos
            desejos = avatar_data.get('desejos_secretos', []) or avatar_data.get('sonhos_proibidos_ardentes', [])
            validation['metrics']['desejos_count'] = len(desejos)
            
            if len(desejos) < 5:
                validation['critical_issues'].append(f"Desejos insuficientes: {len(desejos)} < 5")
            
            # Verifica perfil demográfico
            demografico = avatar_data.get('perfil_demografico', {})
            validation['metrics']['demografico_fields'] = len(demografico)
            
            if len(demografico) < 3:
                validation['warnings'].append("Perfil demográfico limitado")
            
            # Verifica perfil psicográfico
            psicografico = avatar_data.get('perfil_psicografico', {})
            validation['metrics']['psicografico_fields'] = len(psicografico)
            
            if len(psicografico) < 3:
                validation['warnings'].append("Perfil psicográfico limitado")
            
            # Calcula score
            dores_score = min(len(dores) / 15 * 100, 100)
            desejos_score = min(len(desejos) / 15 * 100, 100)
            demografico_score = min(len(demografico) / 7 * 100, 100)
            psicografico_score = min(len(psicografico) / 8 * 100, 100)
            
            validation['score'] = (dores_score + desejos_score + demografico_score + psicografico_score) / 4
            validation['valid'] = validation['score'] >= 70.0 and len(validation['critical_issues']) == 0
            
        except Exception as e:
            validation['critical_issues'].append(f"Erro na validação do avatar: {str(e)}")
        
        return validation
    
    def _validate_forensic_metrics(self, metrics_data: Dict[str, Any], full_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Valida métricas forenses"""
        
        validation = {
            'valid': False,
            'score': 0.0,
            'critical_issues': [],
            'warnings': [],
            'metrics': {}
        }
        
        try:
            # Verifica densidade persuasiva
            densidade = metrics_data.get('densidade_persuasiva', {})
            
            if not densidade:
                validation['critical_issues'].append("Densidade persuasiva ausente")
                return validation
            
            argumentos_totais = densidade.get('argumentos_totais', 0)
            validation['metrics']['argumentos_totais'] = argumentos_totais
            
            if argumentos_totais < 10:
                validation['critical_issues'].append(f"Argumentos insuficientes: {argumentos_totais} < 10")
            
            # Verifica gatilhos de Cialdini
            cialdini = densidade.get('gatilhos_cialdini', {})
            cialdini_ativados = sum(1 for count in cialdini.values() if count > 0)
            validation['metrics']['cialdini_ativados'] = cialdini_ativados
            
            if cialdini_ativados < 3:
                validation['critical_issues'].append(f"Gatilhos de Cialdini insuficientes: {cialdini_ativados} < 3")
            
            # Verifica intensidade emocional
            intensidade = metrics_data.get('intensidade_emocional', {})
            
            if intensidade:
                # Extrai valores numéricos
                emocoes_validas = 0
                for emocao, valor in intensidade.items():
                    try:
                        if '/' in str(valor):
                            num_valor = int(str(valor).split('/')[0])
                        else:
                            num_valor = int(valor)
                        
                        if num_valor >= 7:  # Intensidade mínima
                            emocoes_validas += 1
                    except:
                        continue
                
                validation['metrics']['emocoes_intensas'] = emocoes_validas
                
                if emocoes_validas < 2:
                    validation['warnings'].append(f"Intensidade emocional baixa: {emocoes_validas} emoções >= 7/10")
            
            # Calcula score
            argumentos_score = min(argumentos_totais / 20 * 100, 100)
            cialdini_score = min(cialdini_ativados / 6 * 100, 100)
            intensidade_score = min(validation['metrics'].get('emocoes_intensas', 0) / 4 * 100, 100)
            
            validation['score'] = (argumentos_score + cialdini_score + intensidade_score) / 3
            validation['valid'] = validation['score'] >= 60.0 and len(validation['critical_issues']) == 0
            
        except Exception as e:
            validation['critical_issues'].append(f"Erro na validação de métricas: {str(e)}")
        
        return validation
    
    def _get_component_weight(self, component_name: str) -> float:
        """Retorna peso do componente na validação"""
        weights = {
            'drivers_mentais': 0.25,
            'provas_visuais': 0.20,
            'sistema_anti_objecao': 0.20,
            'avatar_ultra_detalhado': 0.20,
            'metricas_forenses': 0.15
        }
        return weights.get(component_name, 0.1)
    
    def _check_scientific_compliance(self, analysis_data: Dict[str, Any]) -> bool:
        """Verifica compliance científica"""
        
        # Verifica se há fontes reais
        pesquisa_data = analysis_data.get('pesquisa_web_massiva', {})
        if not pesquisa_data or not pesquisa_data.get('search_results'):
            return False
        
        # Verifica se há dados quantitativos
        has_metrics = bool(analysis_data.get('metricas_forenses_detalhadas'))
        
        # Verifica se há validação de qualidade
        has_validation = bool(analysis_data.get('metadata', {}).get('quality_score'))
        
        return has_metrics and has_validation
    
    def _generate_recommendations(self, validation_result: Dict[str, Any]) -> List[str]:
        """Gera recomendações baseadas na validação"""
        
        recommendations = []
        
        if validation_result['quality_score'] < 80:
            recommendations.append("Melhore a qualidade geral da análise configurando mais APIs")
        
        if validation_result['critical_issues']:
            recommendations.append("Resolva os issues críticos identificados antes de usar a análise")
        
        if not validation_result['scientific_compliance']:
            recommendations.append("Adicione mais fontes científicas e dados quantitativos")
        
        # Recomendações específicas por componente
        for component, validation in validation_result['component_validations'].items():
            if validation['score'] < 70:
                recommendations.append(f"Melhore a qualidade do componente {component}")
        
        return recommendations
    
    def validate_data_sources(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida fontes de dados"""
        
        validation = {
            'real_data_percentage': 0.0,
            'verified_sources': 0,
            'total_sources': 0,
            'source_quality': 'unknown',
            'has_fallback_content': False
        }
        
        try:
            # Verifica pesquisa web
            pesquisa = analysis_data.get('pesquisa_web_massiva', {})
            
            if pesquisa:
                search_results = pesquisa.get('search_results', [])
                validation['total_sources'] = len(search_results)
                
                # Verifica qualidade das fontes
                verified_domains = [
                    'g1.globo.com', 'exame.com', 'valor.globo.com', 'estadao.com.br',
                    'folha.uol.com.br', 'ibge.gov.br', 'sebrae.com.br'
                ]
                
                for result in search_results:
                    url = result.get('url', '')
                    if any(domain in url for domain in verified_domains):
                        validation['verified_sources'] += 1
                
                # Calcula percentual de dados reais
                if validation['total_sources'] > 0:
                    validation['real_data_percentage'] = (validation['verified_sources'] / validation['total_sources']) * 100
            
            # Verifica se há conteúdo de fallback
            analysis_str = json.dumps(analysis_data, ensure_ascii=False).lower()
            fallback_indicators = ['fallback', 'simulado', 'em desenvolvimento', 'modo emergência']
            
            validation['has_fallback_content'] = any(indicator in analysis_str for indicator in fallback_indicators)
            
            # Determina qualidade das fontes
            if validation['real_data_percentage'] >= 80:
                validation['source_quality'] = 'excellent'
            elif validation['real_data_percentage'] >= 60:
                validation['source_quality'] = 'good'
            elif validation['real_data_percentage'] >= 40:
                validation['source_quality'] = 'fair'
            else:
                validation['source_quality'] = 'poor'
                
        except Exception as e:
            logger.error(f"❌ Erro na validação de fontes: {e}")
        
        return validation

# Instância global
validation_engine = ValidationEngine()