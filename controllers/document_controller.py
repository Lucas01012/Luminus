from flask import Blueprint, request, jsonify
from services.document_service import (
    process_document,
    search_text_in_document
)
from services.tts_service import TTSService, prepare_document_audio

document_bp = Blueprint("document", __name__)

@document_bp.route("/processar", methods=["POST"])
def processar_documento():
    """
    Endpoint unificado para processar documentos PDF e DOCX
    
    Aceita:
    - arquivo: PDF ou DOCX
    - gerar_resumo: true/false (opcional, padrão: true)
    - analisar_imagens: true/false (opcional, padrão: true)
    
    Retorna:
    - text_content: texto completo extraído + descrição de imagens
    - structure: estrutura do documento (títulos, parágrafos, tabelas)
    - arquivo_info: metadados do arquivo
    - resumo: resumo gerado por IA (se solicitado)
    - palavras_chave: palavras-chave principais
    - imagens_analisadas: número de imagens processadas
    """
    if "arquivo" not in request.files:
        return jsonify({"erro": "Nenhum arquivo enviado no campo 'arquivo'"}), 400
    
    arquivo = request.files["arquivo"]
    gerar_resumo = request.form.get("gerar_resumo", "true").lower() == "true"
    analisar_imagens = request.form.get("analisar_imagens", "true").lower() == "true"
    
    try:
        file_content = arquivo.read()
        file_type = arquivo.content_type or ""
        file_name = arquivo.filename or "documento"
        
        resultado = process_document(file_content, file_name, file_type, gerar_resumo, analisar_imagens)
        
        if "erro" in resultado:
            return jsonify(resultado), 400
        
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({"erro": f"Erro ao processar documento: {str(e)}"}), 500

@document_bp.route("/buscar-no-documento", methods=["POST"])
def buscar_no_documento():
    """
    Busca termos específicos no texto do documento
    """
    data = request.get_json()
    
    if not data or "texto_documento" not in data or "termo_busca" not in data:
        return jsonify({"erro": "Campos 'texto_documento' e 'termo_busca' são obrigatórios"}), 400
    
    try:
        resultado = search_text_in_document(data["texto_documento"], data["termo_busca"])
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({"erro": f"Erro na busca: {str(e)}"}), 500

@document_bp.route("/gerar-audio-documento", methods=["POST"])
def gerar_audio_documento():
    """
    Converte texto do documento em áudio (TTS)
    """
    data = request.get_json()
    
    if not data or "texto" not in data:
        return jsonify({"erro": "Campo 'texto' é obrigatório"}), 400
    
    voice_config = {
        "language_code": data.get("idioma", "pt-BR"),
        "voice_name": data.get("voz", "pt-BR-Wavenet-A"),
        "gender": data.get("genero", "FEMALE"),
        "speaking_rate": float(data.get("velocidade", 1.0)),
        "pitch": float(data.get("tom", 0.0))
    }
    
    options = {
        "add_pauses": data.get("adicionar_pausas", True),
        "emphasize_headings": data.get("enfatizar_titulos", True),
        "variable_speed": data.get("velocidade_variavel", False)
    }
    
    try:
        texto = data["texto"]
        
        if len(texto) > 4000:
            resultado = prepare_document_audio(texto, options)
        else:
            from services.tts_service import TTSService
            tts = TTSService()
            prepared = tts.prepare_text_for_speech(texto, options)
            
            if prepared["type"] == "ssml":
                resultado = tts.generate_ssml_audio(prepared["text"], voice_config)
            else:
                resultado = tts.generate_audio(prepared["text"], voice_config)
        
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({"erro": f"Erro na geração de áudio: {str(e)}"}), 500

@document_bp.route("/vozes-disponiveis", methods=["GET"])
def listar_vozes():
    """
    Lista vozes disponíveis para TTS (Text-to-Speech)
    
    Query params:
    - idioma: código do idioma (opcional, padrão: pt-BR)
    """
    idioma = request.args.get("idioma", "pt-BR")
    
    try:
        tts = TTSService()
        resultado = tts.get_available_voices(idioma)
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({"erro": f"Erro ao listar vozes: {str(e)}"}), 500
