import os
import io
import fitz  # PyMuPDF
from docx import Document
from PIL import Image
import google.generativeai as genai
from google.cloud import vision
import base64
from google.cloud import texttospeech
def extract_text_from_pdf(file_content):
    """
    Extrai texto de PDF com estrutura preservada
    """
    try:
        pdf_doc = fitz.open(stream=file_content, filetype="pdf")
        extracted_data = {
            "text_content": "",
            "structure": {
                "pages": [],
                "headings": [],
                "paragraphs": [],
                "tables": []
            },
            "metadata": {
                "total_pages": len(pdf_doc),
                "title": pdf_doc.metadata.get("title", ""),
                "author": pdf_doc.metadata.get("author", "")
            }
        }
        
        full_text = ""
        
        for page_num in range(len(pdf_doc)):
            page = pdf_doc.load_page(page_num)
            
            # Extrai texto estruturado
            blocks = page.get_text("dict")
            page_text = ""
            page_structure = {
                "page_number": page_num + 1,
                "headings": [],
                "paragraphs": [],
                "images": []
            }
            
            for block in blocks["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        line_text = ""
                        font_size = 0
                        
                        for span in line["spans"]:
                            line_text += span["text"]
                            font_size = max(font_size, span["size"])
                        
                        if line_text.strip():
                            # Identifica títulos por tamanho da fonte
                            if font_size > 14:
                                page_structure["headings"].append({
                                    "text": line_text.strip(),
                                    "level": 1 if font_size > 18 else 2,
                                    "page": page_num + 1
                                })
                                extracted_data["structure"]["headings"].append({
                                    "text": line_text.strip(),
                                    "level": 1 if font_size > 18 else 2,
                                    "page": page_num + 1
                                })
                            else:
                                page_structure["paragraphs"].append(line_text.strip())
                                extracted_data["structure"]["paragraphs"].append({
                                    "text": line_text.strip(),
                                    "page": page_num + 1
                                })
                            
                            page_text += line_text + "\n"
            
            extracted_data["structure"]["pages"].append(page_structure)
            full_text += f"\n--- Página {page_num + 1} ---\n" + page_text
        
        pdf_doc.close()
        extracted_data["text_content"] = full_text
        return extracted_data
        
    except Exception as e:
        return {"erro": f"Erro ao processar PDF: {str(e)}"}

def extract_text_from_docx(file_content):
    """
    Extrai texto de DOCX preservando estrutura
    """
    try:
        doc = Document(io.BytesIO(file_content))
        
        extracted_data = {
            "text_content": "",
            "structure": {
                "headings": [],
                "paragraphs": [],
                "tables": []
            }
        }
        
        full_text = ""
        
        for para in doc.paragraphs:
            if para.text.strip():
                # Verifica se é um título
                if para.style.name.startswith('Heading'):
                    level = int(para.style.name.split()[-1]) if para.style.name.split()[-1].isdigit() else 1
                    extracted_data["structure"]["headings"].append({
                        "text": para.text.strip(),
                        "level": level
                    })
                else:
                    extracted_data["structure"]["paragraphs"].append({
                        "text": para.text.strip()
                    })
                
                full_text += para.text + "\n"
        
        # Processa tabelas
        for table in doc.tables:
            table_data = []
            for row in table.rows:
                row_data = []
                for cell in row.cells:
                    row_data.append(cell.text.strip())
                table_data.append(row_data)
            
            extracted_data["structure"]["tables"].append({
                "data": table_data,
                "rows": len(table_data),
                "columns": len(table_data[0]) if table_data else 0
            })
        
        extracted_data["text_content"] = full_text
        return extracted_data
        
    except Exception as e:
        return {"erro": f"Erro ao processar DOCX: {str(e)}"}

def extract_text_from_image(image_content):
    """
    OCR avançado para extrair texto de imagens/documentos escaneados
    """
    try:
        client = vision.ImageAnnotatorClient()
        image = vision.Image(content=image_content)
        
        # OCR com detecção de estrutura de documento
        response = client.document_text_detection(image=image)
        document = response.full_text_annotation
        
        if not document.text:
            return {"erro": "Nenhum texto detectado na imagem"}
        
        extracted_data = {
            "text_content": document.text,
            "structure": {
                "blocks": [],
                "paragraphs": [],
                "words": []
            },
            "confidence": 0
        }
        
        # Processa blocos de texto estruturados
        for page in document.pages:
            for block in page.blocks:
                block_text = ""
                block_confidence = 0
                
                for paragraph in block.paragraphs:
                    para_text = ""
                    para_confidence = 0
                    
                    for word in paragraph.words:
                        word_text = ''.join([symbol.text for symbol in word.symbols])
                        word_confidence = sum([symbol.confidence for symbol in word.symbols]) / len(word.symbols)
                        
                        para_text += word_text + " "
                        para_confidence += word_confidence
                        
                        extracted_data["structure"]["words"].append({
                            "text": word_text,
                            "confidence": round(word_confidence, 2)
                        })
                    
                    if para_text.strip():
                        extracted_data["structure"]["paragraphs"].append({
                            "text": para_text.strip(),
                            "confidence": round(para_confidence / len(paragraph.words), 2)
                        })
                        block_text += para_text + "\n"
                
                if block_text.strip():
                    extracted_data["structure"]["blocks"].append({
                        "text": block_text.strip(),
                        "confidence": round(block_confidence, 2)
                    })
        
        # Calcula confiança geral
        word_confidences = [word["confidence"] for word in extracted_data["structure"]["words"]]
        extracted_data["confidence"] = round(sum(word_confidences) / len(word_confidences), 2) if word_confidences else 0
        
        return extracted_data
        
    except Exception as e:
        return {"erro": f"Erro no OCR da imagem: {str(e)}"}

def generate_document_summary(text_content):
    """
    Gera resumo automático do documento usando Gemini
    """
    try:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel(model_name="gemini-2.5-flash")
        
        prompt = f"""
        Analise o seguinte texto e gere um resumo estruturado e acessível:
        
        1. Resumo principal (2-3 frases)
        2. Pontos-chave (máximo 5 tópicos)
        3. Estrutura do documento (tipo de documento, seções principais)
        
        Texto para resumir:
        {text_content[:4000]}  # Limita para não exceder token limit
        """
        
        response = model.generate_content(prompt)
        
        return {
            "resumo": response.text.strip(),
            "palavras_chave": extract_keywords_from_text(text_content)
        }
        
    except Exception as e:
        return {"erro": f"Erro ao gerar resumo: {str(e)}"}

def extract_keywords_from_text(text):
    """
    Extrai palavras-chave importantes do texto
    """
    # Implementação simples - pode ser melhorada com NLP mais avançado
    words = text.lower().split()
    
    # Remove palavras comuns (stop words)
    stop_words = {
        'o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas', 'de', 'do', 'da', 'dos', 'das',
        'em', 'no', 'na', 'nos', 'nas', 'por', 'para', 'com', 'sem', 'sob', 'sobre',
        'e', 'ou', 'mas', 'se', 'que', 'quando', 'como', 'onde', 'porque', 'então',
        'ele', 'ela', 'eles', 'elas', 'eu', 'tu', 'você', 'nós', 'vós', 'vocês',
        'este', 'esta', 'estes', 'estas', 'esse', 'essa', 'esses', 'essas',
        'aquele', 'aquela', 'aqueles', 'aquelas', 'isto', 'isso', 'aquilo'
    }
    
    # Filtra palavras significativas
    keywords = []
    word_count = {}
    
    for word in words:
        clean_word = ''.join(c for c in word if c.isalnum())
        if len(clean_word) > 3 and clean_word not in stop_words:
            word_count[clean_word] = word_count.get(clean_word, 0) + 1
    
    # Ordena por frequência e pega as top 10
    sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
    keywords = [word for word, count in sorted_words[:10]]
    
    return keywords

def search_text_in_document(text_content, search_term):
    """
    Busca palavras-chave no documento e retorna contexto
    """
    lines = text_content.split('\n')
    results = []
    
    for i, line in enumerate(lines):
        if search_term.lower() in line.lower():
            # Contexto: linha anterior, atual e próxima
            context_start = max(0, i - 1)
            context_end = min(len(lines), i + 2)
            context = '\n'.join(lines[context_start:context_end])
            
            results.append({
                "linha": i + 1,
                "texto": line.strip(),
                "contexto": context,
                "posicao": line.lower().find(search_term.lower())
            })
    
    return {
        "termo_busca": search_term,
        "total_ocorrencias": len(results),
        "resultados": results[:10]  # Limita a 10 resultados
    }
