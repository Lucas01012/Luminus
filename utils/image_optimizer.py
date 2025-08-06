from PIL import Image
import io
import os

class ImageOptimizer:
    @staticmethod
    def optimize_for_ai(image_file, max_size=(1024, 1024), quality=85):
        """
        Otimiza imagem para processamento de IA
        - Redimensiona para tamanho ideal
        - Comprime mantendo qualidade
        - Converte para formato eficiente
        """
        try:
            # Abre a imagem
            image = Image.open(image_file)
            
            # Converte para RGB se necessário
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            # Calcula novo tamanho mantendo proporção
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Salva otimizada em buffer
            output_buffer = io.BytesIO()
            image.save(output_buffer, format='JPEG', quality=quality, optimize=True)
            output_buffer.seek(0)
            
            # Estatísticas
            original_size = image_file.seek(0, 2)  # Vai para o final
            image_file.seek(0)  # Volta para o início
            optimized_size = len(output_buffer.getvalue())
            
            compression_ratio = (1 - optimized_size / original_size) * 100
            
            return {
                "success": True,
                "optimized_image": output_buffer,
                "original_size": original_size,
                "optimized_size": optimized_size,
                "compression_ratio": round(compression_ratio, 1),
                "new_dimensions": image.size
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def quick_resize(image_file, target_size=(512, 512)):
        """
        Redimensionamento rápido para análise preliminar
        """
        try:
            image = Image.open(image_file)
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            # Resize rápido
            image = image.resize(target_size, Image.Resampling.BILINEAR)
            
            output_buffer = io.BytesIO()
            image.save(output_buffer, format='JPEG', quality=70)
            output_buffer.seek(0)
            
            return output_buffer
            
        except Exception as e:
            return None
