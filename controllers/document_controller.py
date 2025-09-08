from flask import Blueprint, request, jsonify
from services.document_service import (
    extract_text_from_pdf, 
    extract_text_from_docx, 
    extract_text_from_image,
    generate_document_summary,
    search_text_in_document
)
from services.tts_service import text_to_speech, prepare_document_audio
import os

document_bp = Blueprint("document", __name__)

@document_bp.route("/processar-documento", methods=["POST"])
def processar_documento():
    """
    Processa documentos PDF, DOCX ou imagens escaneadas
    """
    if "arquivo" not in request.files:
        return jsonify({"erro": "Nenhum arquivo foi enviado"}), 400
    
    arquivo = request.files["arquivo"]
    filename = arquivo.filename.lower()
    
    incluir_resumo = request.form.get("incluir_resumo", "true").lower() == "true"
    extrair_estrutura = request.form.get("extrair_estrutura", "true").lower() == "true"
    
    try:
        # Lê conteúdo do arquivo
        file_content = arquivo.read()
        
        # Processa baseado no tipo de arquivo
        if filename.endswith('.pdf'):
            resultado = extract_text_from_pdf(file_content)
        elif filename.endswith('.docx'):
            resultado = extract_text_from_docx(file_content)
        elif filename.endswith(('.jpg', '.jpeg', '.png', '.tiff', '.bmp')):
            resultado = extract_text_from_image(file_content)
        else:
            return jsonify({"erro": "Formato de arquivo não suportado. Use PDF, DOCX ou imagens."}), 400
        
        if "erro" in resultado:
            return jsonify(resultado), 400
        
        # Adiciona informações extras
        response_data = {
            "arquivo": filename,
            "tipo": "pdf" if filename.endswith('.pdf') else "docx" if filename.endswith('.docx') else "imagem",
            "texto_extraido": resultado["text_content"],
            "total_caracteres": len(resultado["text_content"]),
            "total_palavras": len(resultado["text_content"].split())
        }
        
        if extrair_estrutura and "structure" in resultado:
            response_data["estrutura"] = resultado["structure"]
        
        if "metadata" in resultado:
            response_data["metadados"] = resultado["metadata"]
        
        if incluir_resumo and resultado["text_content"]:
            resumo = generate_document_summary(resultado["text_content"])
            if "erro" not in resumo:
                response_data["resumo"] = resumo
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({"erro": f"Erro no processamento: {str(e)}"}), 500

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
    
    # Configurações de voz opcionais
    voice_config = {
        "language_code": data.get("idioma", "pt-BR"),
        "voice_name": data.get("voz", "pt-BR-Wavenet-A"),
        "gender": data.get("genero", "FEMALE"),
        "speaking_rate": float(data.get("velocidade", 1.0)),
        "pitch": float(data.get("tom", 0.0))
    }
    
    # Opções de processamento
    options = {
        "add_pauses": data.get("adicionar_pausas", True),
        "emphasize_headings": data.get("enfatizar_titulos", True),
        "variable_speed": data.get("velocidade_variavel", False)
    }
    
    try:
        texto = data["texto"]
        
        # Para textos longos, usa processamento especial
        if len(texto) > 4000:
            resultado = prepare_document_audio(texto, options)
        else:
            # Prepara texto
            from services.tts_service import TTSService
            tts = TTSService()
            prepared = tts.prepare_text_for_speech(texto, options)
            
            # Gera áudio
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
    Lista vozes disponíveis para TTS
    """
    idioma = request.args.get("idioma", "pt-BR")
    
    try:
        from services.tts_service import TTSService
        tts = TTSService()
        resultado = tts.get_available_voices(idioma)
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({"erro": f"Erro ao listar vozes: {str(e)}"}), 500

@document_bp.route("/extrair-texto-imagem", methods=["POST"])
def extrair_texto_imagem():
    """
    OCR especializado para documentos em imagem
    """
    if "imagem" not in request.files:
        return jsonify({"erro": "Nenhuma imagem foi enviada"}), 400
    
    imagem = request.files["imagem"]
    
    try:
        content = imagem.read()
        resultado = extract_text_from_image(content)
        
        if "erro" in resultado:
            return jsonify(resultado), 400
        
        return jsonify({
            "texto_extraido": resultado["text_content"],
            "confianca_geral": resultado["confidence"],
            "estrutura": resultado["structure"],
            "total_palavras": len(resultado["structure"]["words"]),
            "palavras_baixa_confianca": [
                word for word in resultado["structure"]["words"] 
                if word["confidence"] < 0.7
            ]
        })
        
    except Exception as e:
        return jsonify({"erro": f"Erro no OCR: {str(e)}"}), 500
