from firebase.firebase_config import db
from firebase_admin import firestore
from datetime import datetime

class HistoryService:
    """
    Serviço para gerenciar histórico de análises de imagens e documentos
    """
    
    @staticmethod
    def save_image_analysis(user_id, image_name, analysis_result):
        """
        Salva histórico de análise de imagem no Firestore
        
        Args:
            user_id: UID do usuário
            image_name: Nome do arquivo de imagem
            analysis_result: Resultado da análise (dict com objeto, confianca, etc)
            
        Returns:
            dict com sucesso e id do documento ou erro
        """
        try:
            doc_ref = db.collection("historico_imagens").document()
            
            data = {
                "usuario_id": user_id,
                "imagem_nome": image_name,
                "objeto_detectado": analysis_result.get('objeto', ''),
                "confianca": analysis_result.get('confianca'),
                "processing_time": analysis_result.get('processing_time'),
                "timestamp": firestore.SERVER_TIMESTAMP,
                "tipo": "analise_imagem"
            }
            
            doc_ref.set(data)
            
            return {
                "sucesso": True,
                "doc_id": doc_ref.id,
                "mensagem": "Análise salva no histórico"
            }
            
        except Exception as e:
            print(f"Erro ao salvar histórico de imagem: {str(e)}")
            return {
                "sucesso": False,
                "erro": f"Erro ao salvar histórico: {str(e)}"
            }
    
    @staticmethod
    def get_user_image_history(user_id, limit=20):
        """
        Retorna histórico de análises de imagens do usuário
        
        Args:
            user_id: UID do usuário
            limit: Número máximo de resultados (padrão: 20)
            
        Returns:
            lista de análises ou dict com erro
        """
        try:
            docs = db.collection("historico_imagens")\
                     .where("usuario_id", "==", user_id)\
                     .order_by("timestamp", direction=firestore.Query.DESCENDING)\
                     .limit(limit)\
                     .stream()
            
            historico = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                
                # Converte timestamp para ISO string
                if data.get('timestamp'):
                    data['timestamp'] = data['timestamp'].isoformat()
                
                historico.append(data)
            
            return {
                "sucesso": True,
                "total": len(historico),
                "historico": historico
            }
            
        except Exception as e:
            print(f"Erro ao buscar histórico de imagens: {str(e)}")
            return {
                "sucesso": False,
                "erro": f"Erro ao buscar histórico: {str(e)}"
            }
    
    @staticmethod
    def save_document_analysis(user_id, file_name, document_result):
        """
        Salva histórico de processamento de documento no Firestore
        
        Args:
            user_id: UID do usuário
            file_name: Nome do arquivo
            document_result: Resultado do processamento
            
        Returns:
            dict com sucesso e id do documento ou erro
        """
        try:
            doc_ref = db.collection("historico_documentos").document()
            
            # Limita preview do texto para 500 caracteres
            preview_texto = document_result.get('text_content', '')[:500]
            
            data = {
                "usuario_id": user_id,
                "arquivo_nome": file_name,
                "formato": document_result.get('arquivo_info', {}).get('formato', ''),
                "tamanho_bytes": document_result.get('arquivo_info', {}).get('tamanho_bytes', 0),
                "preview_texto": preview_texto,
                "resumo": document_result.get('resumo', ''),
                "palavras_chave": document_result.get('palavras_chave', []),
                "total_paginas": document_result.get('metadata', {}).get('total_pages'),
                "total_caracteres": len(document_result.get('text_content', '')),
                "timestamp": firestore.SERVER_TIMESTAMP,
                "tipo": "documento"
            }
            
            doc_ref.set(data)
            
            return {
                "sucesso": True,
                "doc_id": doc_ref.id,
                "mensagem": "Documento salvo no histórico"
            }
            
        except Exception as e:
            print(f"Erro ao salvar histórico de documento: {str(e)}")
            return {
                "sucesso": False,
                "erro": f"Erro ao salvar histórico: {str(e)}"
            }
    
    @staticmethod
    def get_user_document_history(user_id, limit=20):
        """
        Retorna histórico de documentos processados do usuário
        
        Args:
            user_id: UID do usuário
            limit: Número máximo de resultados (padrão: 20)
            
        Returns:
            lista de documentos ou dict com erro
        """
        try:
            docs = db.collection("historico_documentos")\
                     .where("usuario_id", "==", user_id)\
                     .order_by("timestamp", direction=firestore.Query.DESCENDING)\
                     .limit(limit)\
                     .stream()
            
            historico = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                
                # Converte timestamp para ISO string
                if data.get('timestamp'):
                    data['timestamp'] = data['timestamp'].isoformat()
                
                historico.append(data)
            
            return {
                "sucesso": True,
                "total": len(historico),
                "historico": historico
            }
            
        except Exception as e:
            print(f"Erro ao buscar histórico de documentos: {str(e)}")
            return {
                "sucesso": False,
                "erro": f"Erro ao buscar histórico: {str(e)}"
            }
    
    @staticmethod
    def get_user_full_history(user_id, limit=30):
        """
        Retorna histórico completo (imagens + documentos) do usuário
        
        Args:
            user_id: UID do usuário
            limit: Número máximo de resultados (padrão: 30)
            
        Returns:
            lista combinada ordenada por timestamp
        """
        try:
            # Busca imagens
            imagens_result = HistoryService.get_user_image_history(user_id, limit // 2)
            documentos_result = HistoryService.get_user_document_history(user_id, limit // 2)
            
            if not imagens_result['sucesso'] or not documentos_result['sucesso']:
                return {
                    "sucesso": False,
                    "erro": "Erro ao buscar histórico completo"
                }
            
            # Combina e ordena por timestamp
            historico_completo = imagens_result['historico'] + documentos_result['historico']
            historico_completo.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            return {
                "sucesso": True,
                "total": len(historico_completo[:limit]),
                "historico": historico_completo[:limit],
                "total_imagens": len(imagens_result['historico']),
                "total_documentos": len(documentos_result['historico'])
            }
            
        except Exception as e:
            print(f"Erro ao buscar histórico completo: {str(e)}")
            return {
                "sucesso": False,
                "erro": f"Erro ao buscar histórico: {str(e)}"
            }
    
    @staticmethod
    def delete_history_item(user_id, doc_id, tipo='imagem'):
        """
        Deleta um item do histórico
        
        Args:
            user_id: UID do usuário (para validação)
            doc_id: ID do documento no Firestore
            tipo: 'imagem' ou 'documento'
            
        Returns:
            dict com sucesso ou erro
        """
        try:
            collection = "historico_imagens" if tipo == 'imagem' else "historico_documentos"
            doc_ref = db.collection(collection).document(doc_id)
            
            # Verifica se documento existe e pertence ao usuário
            doc = doc_ref.get()
            if not doc.exists:
                return {
                    "sucesso": False,
                    "erro": "Item não encontrado"
                }
            
            if doc.to_dict().get('usuario_id') != user_id:
                return {
                    "sucesso": False,
                    "erro": "Não autorizado a deletar este item"
                }
            
            doc_ref.delete()
            
            return {
                "sucesso": True,
                "mensagem": "Item deletado com sucesso"
            }
            
        except Exception as e:
            print(f"Erro ao deletar item do histórico: {str(e)}")
            return {
                "sucesso": False,
                "erro": f"Erro ao deletar: {str(e)}"
            }
