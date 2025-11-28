import asyncio
import concurrent.futures
from services.image_service import process_image_vision, process_image_gemini
from utils.cache import image_cache
import time

class AsyncImageProcessor:
    def __init__(self, max_workers: int = 3):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
    
    async def process_vision_async(self, image_file):
        """Processa Vision API de forma assíncrona"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, process_image_vision, image_file)
    
    async def process_gemini_async(self, image_file):
        """Processa Gemini de forma assíncrona"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, process_image_gemini, image_file)
    
    async def process_with_cache(self, image_file, mode: str):
        """Processa com cache para evitar reprocessamento"""
        content = image_file.read()
        image_file.seek(0)
        
        cached_result = image_cache.get(content, mode)
        if cached_result:
            return cached_result
        
        start_time = time.time()
        
        if mode == "vision":
            result = await self.process_vision_async(image_file)
        elif mode == "gemini":
            result = await self.process_gemini_async(image_file)
        else:
            raise ValueError(f"Modo inválido: {mode}")
        
        processing_time = time.time() - start_time
        print(f"Processamento {mode}: {processing_time:.2f}s")
        
        image_cache.set(content, mode, result)
        
        return result
    
    async def process_parallel(self, image_file, modes: list):
        """Processa múltiplos modos em paralelo"""
        tasks = []
        
        for mode in modes:
            image_file.seek(0)
            content = image_file.read()
            image_copy = type(image_file)(content)
            
            task = self.process_with_cache(image_copy, mode)
            tasks.append((mode, task))
        
        results = {}
        for mode, task in tasks:
            try:
                results[mode] = await task
            except Exception as e:
                results[mode] = {"erro": str(e)}
        
        return results

async_processor = AsyncImageProcessor(max_workers=2)
