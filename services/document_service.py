import os
import io
import fitz
from docx import Document
from PIL import Image
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Tentar importar pytesseract (opcional)
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("⚠️ pytesseract não instalado. Análise de imagens desabilitada.")

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
            
            # Se a página não tem texto, tentar OCR na imagem da página
            if not page_text.strip() and TESSERACT_AVAILABLE:
                try:
                    print(f"  Página {page_num + 1} sem texto, aplicando OCR...")
                    pix = page.get_pixmap(dpi=150)
                    img_bytes = pix.tobytes("png")
                    pil_img = Image.open(io.BytesIO(img_bytes))
                    ocr_text = pytesseract.image_to_string(pil_img, lang='por', config='--oem 3 --psm 6').strip()
                    if ocr_text:
                        full_text += f"[OCR]: {ocr_text}\n"
                        print(f"  ✓ OCR extraiu {len(ocr_text)} caracteres")
                except Exception as e:
                    print(f"  Erro no OCR página {page_num + 1}: {e}")
        
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
        {text_content[:15000]}
        """
        
        response = model.generate_content(
            prompt,
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        
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
    words = text.lower().split()
    
    stop_words = {
        'o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas', 'de', 'do', 'da', 'dos', 'das',
        'em', 'no', 'na', 'nos', 'nas', 'por', 'para', 'com', 'sem', 'sob', 'sobre',
        'e', 'ou', 'mas', 'se', 'que', 'quando', 'como', 'onde', 'porque', 'então',
        'ele', 'ela', 'eles', 'elas', 'eu', 'tu', 'você', 'nós', 'vós', 'vocês',
        'este', 'esta', 'estes', 'estas', 'esse', 'essa', 'esses', 'essas',
        'aquele', 'aquela', 'aqueles', 'aquelas', 'isto', 'isso', 'aquilo'
    }
    
    keywords = []
    word_count = {}
    
    for word in words:
        clean_word = ''.join(c for c in word if c.isalnum())
        if len(clean_word) > 3 and clean_word not in stop_words:
            word_count[clean_word] = word_count.get(clean_word, 0) + 1
    
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
        "resultados": results[:10]
    }


def extract_images_from_pdf(pdf_doc):
    """Extrai imagens de PDF"""
    images = []
    for page_num in range(len(pdf_doc)):
        page = pdf_doc.load_page(page_num)
        for img in page.get_images():
            try:
                xref = img[0]
                base_image = pdf_doc.extract_image(xref)
                image_bytes = base_image["image"]
                if len(image_bytes) > 5000:  # Filtrar ícones pequenos
                    pil_image = Image.open(io.BytesIO(image_bytes))
                    if pil_image.width > 100 and pil_image.height > 100:
                        images.append({'page': page_num + 1, 'image': pil_image})
            except:
                continue
    return images


def extract_images_from_docx(file_content):
    """Extrai imagens de DOCX"""
    doc = Document(io.BytesIO(file_content))
    images = []
    for rel in doc.part.rels.values():
        if "image" in rel.target_ref:
            try:
                image_bytes = rel.target_part.blob
                if len(image_bytes) > 5000:
                    pil_image = Image.open(io.BytesIO(image_bytes))
                    if pil_image.width > 100 and pil_image.height > 100:
                        images.append({'image': pil_image})
            except:
                continue
    return images


def analyze_image_with_ocr(pil_image, document_context="", page_num=None):
    """Extrai texto da imagem com OCR e analisa com Gemini usando contexto do documento"""
    if not TESSERACT_AVAILABLE:
        return None, ""
    
    try:
        # Debug: verificar se contexto está chegando
        print(f"  🔍 Contexto recebido: {len(document_context)} caracteres")
        
        # OCR
        texto_ocr = pytesseract.image_to_string(pil_image, lang='por', config='--oem 3 --psm 6').strip()
        if not texto_ocr or len(texto_ocr) < 10:
            print(f"  ⚠️ OCR muito curto ou vazio ({len(texto_ocr)} chars)")
            return None, ""
        
        print(f"  ✓ OCR extraiu {len(texto_ocr)} caracteres")
        
        # Análise com Gemini COM CONTEXTO
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Usar contexto mais amplo do documento (até 3000 caracteres)
        context_preview = document_context[:3000] if document_context else ""
        
        if context_preview:
            prompt = f"""Analise esta imagem que faz parte de um documento maior.

===== CONTEÚDO DO DOCUMENTO COMPLETO =====
{context_preview}
==========================================

===== TEXTO EXTRAÍDO DESTA IMAGEM (OCR) =====
{texto_ocr}
==============================================

Página: {page_num if page_num else 'N/A'}

Com base no CONTEÚDO COMPLETO DO DOCUMENTO acima, analise esta imagem e responda de forma ESPECÍFICA E PRECISA:
- Que tipo de elemento visual é (banner, gráfico, foto, logo, diagrama)?
- Qual é o conteúdo/mensagem principal desta imagem?
- Como esta imagem se relaciona com o tema e conteúdo do documento?

Seja específico e use informações do documento para contextualizar."""
        else:
            prompt = f"""Analise esta imagem:

TEXTO EXTRAÍDO (OCR):
{texto_ocr}

Descreva brevemente:
1. Tipo de elemento visual
2. Conteúdo/mensagem principal"""
        
        response = model.generate_content(prompt, safety_settings={
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        })
        return response.text.strip(), texto_ocr
    except Exception as e:
        print(f"Erro OCR: {e}")
        return None, ""


def process_document(file_content, file_name, file_type, gerar_resumo=True, analisar_imagens=True):
    """
    Processa documentos PDF e DOCX
    - PDFs: extração com PyMuPDF preservando estrutura
    - DOCX: extração com python-docx incluindo tabelas
    - Resumo: geração automática com Gemini AI (opcional)
    """
    try:
        is_pdf = 'pdf' in file_type.lower() or file_name.lower().endswith('.pdf')
        is_docx = ('word' in file_type.lower() or 
                   'document' in file_type.lower() or 
                   file_name.lower().endswith(('.docx', '.doc')))
        
        if not (is_pdf or is_docx):
            return {
                "erro": "Tipo de arquivo não suportado. Use PDF ou DOCX.",
                "tipos_aceitos": ["PDF", "DOCX"]
            }
        
        print(f"Processando {'PDF' if is_pdf else 'DOCX'}: {file_name}")
        
        if is_pdf:
            resultado = extract_text_from_pdf(file_content)
        else:
            resultado = extract_text_from_docx(file_content)
        
        if not resultado or 'erro' in resultado:
            return resultado or {"erro": "Erro ao processar documento"}
        
        # Processar imagens se solicitado
        if analisar_imagens and TESSERACT_AVAILABLE:
            print("📸 Analisando imagens...")
            if is_pdf:
                pdf_doc = fitz.open(stream=file_content, filetype="pdf")
                images = extract_images_from_pdf(pdf_doc)
                pdf_doc.close()
            else:
                images = extract_images_from_docx(file_content)
            
            if images:
                image_texts = []
                # Passar contexto do documento para análise
                doc_context = resultado.get('text_content', '')
                
                for idx, img_info in enumerate(images, 1):
                    page = img_info.get('page', 'N/A')
                    desc, ocr_text = analyze_image_with_ocr(
                        img_info['image'],
                        doc_context,  # ← CONTEXTO DO DOCUMENTO
                        page
                    )
                    if desc and ocr_text:
                        image_texts.append(f"\n[Imagem {idx}{f' - Pág.{page}' if page != 'N/A' else ''}]\n💬 Texto: {ocr_text[:200]}\n📝 {desc}")
                
                if image_texts:
                    resultado['text_content'] += "\n\n" + "="*60 + "\n📸 TEXTO DE IMAGENS (OCR)\n" + "="*60 + "".join(image_texts)
                    resultado['imagens_analisadas'] = len(image_texts)
        
        resultado['arquivo_info'] = {
            'nome': file_name,
            'tipo': file_type,
            'tamanho_bytes': len(file_content),
            'formato': 'PDF' if is_pdf else 'DOCX'
        }
        
        if gerar_resumo and resultado.get('text_content'):
            print("Gerando resumo com Gemini...")
            resumo_data = generate_document_summary(resultado['text_content'])
            
            if 'erro' not in resumo_data:
                resultado['resumo'] = resumo_data.get('resumo')
                resultado['palavras_chave'] = resumo_data.get('palavras_chave')
        
        print("Documento processado com sucesso!")
        return resultado
        
    except Exception as e:
        print(f"Erro: {str(e)}")
        return {"erro": f"Erro ao processar documento: {str(e)}"}
