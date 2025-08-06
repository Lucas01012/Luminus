import hashlib
import time
from typing import Dict, Any, Optional

class ImageCache:
    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
    
    def _generate_key(self, image_content: bytes, mode: str) -> str:
        """Gera chave única baseada no conteúdo da imagem e modo"""
        hash_obj = hashlib.md5(image_content)
        return f"{mode}_{hash_obj.hexdigest()}"
    
    def get(self, image_content: bytes, mode: str) -> Optional[Dict[str, Any]]:
        """Busca resultado no cache"""
        key = self._generate_key(image_content, mode)
        
        if key in self.cache:
            cached_item = self.cache[key]
            
            # Verifica se não expirou
            if time.time() - cached_item["timestamp"] < self.ttl_seconds:
                print(f"Cache HIT para {mode}")
                return cached_item["result"]
            else:
                # Remove item expirado
                del self.cache[key]
                print(f"Cache EXPIRED para {mode}")
        
        print(f"Cache MISS para {mode}")
        return None
    
    def set(self, image_content: bytes, mode: str, result: Dict[str, Any]) -> None:
        """Armazena resultado no cache"""
        key = self._generate_key(image_content, mode)
        
        # Remove itens antigos se atingir limite
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), 
                           key=lambda k: self.cache[k]["timestamp"])
            del self.cache[oldest_key]
        
        self.cache[key] = {
            "result": result,
            "timestamp": time.time()
        }
        print(f"Cache SET para {mode}")
    
    def clear(self) -> None:
        """Limpa todo o cache"""
        self.cache.clear()
        print("Cache limpo")
    
    def stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        return {
            "total_items": len(self.cache),
            "max_size": self.max_size,
            "ttl_seconds": self.ttl_seconds
        }

# Instância global do cache
image_cache = ImageCache(max_size=50, ttl_seconds=1800)  # 30 minutos
