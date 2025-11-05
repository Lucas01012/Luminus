import os
import io
import base64
import tempfile
import uuid
from google.cloud import texttospeech
class TTSService:
    def __init__(self):
        self.client = texttospeech.TextToSpeechClient()
        
    def generate_audio(self, text, voice_config=None):
        """
        Converte texto em áudio com configurações personalizáveis
        """
        try:
            default_config = {
                "language_code": "pt-BR",
                "voice_name": "pt-BR-Wavenet-A",
                "gender": "FEMALE",
                "speaking_rate": 1.0,
                "pitch": 0.0,
                "volume_gain_db": 0.0
            }
            
            if voice_config:
                default_config.update(voice_config)
            
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            voice = texttospeech.VoiceSelectionParams(
                language_code=default_config["language_code"],
                name=default_config["voice_name"],
                ssml_gender=getattr(texttospeech.SsmlVoiceGender, default_config["gender"])
            )
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=default_config["speaking_rate"],
                pitch=default_config["pitch"],
                volume_gain_db=default_config["volume_gain_db"]
            )
            
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            audio_id = str(uuid.uuid4())
            
            temp_dir = tempfile.gettempdir()
            audio_path = os.path.join(temp_dir, f"temp_audio_{audio_id}.mp3")
            
            with open(audio_path, "wb") as audio_file:
                audio_file.write(response.audio_content)
            
            audio_base64 = base64.b64encode(response.audio_content).decode('utf-8')
            
            return {
                "sucesso": True,
                "audio_id": audio_id,
                "audio_base64": audio_base64,
                "audio_path": audio_path,
                "duracao_estimada": self._estimate_duration(text, default_config["speaking_rate"]),
                "configuracao_usada": default_config,
                "tamanho_arquivo": len(response.audio_content)
            }
            
        except Exception as e:
            return {
                "sucesso": False,
                "erro": f"Erro ao gerar áudio: {str(e)}"
            }
    
    def generate_ssml_audio(self, ssml_text, voice_config=None):
        """
        Gera áudio usando SSML para controle avançado de prosódia
        """
        try:
            default_config = {
                "language_code": "pt-BR",
                "voice_name": "pt-BR-Wavenet-A",
                "gender": "FEMALE"
            }
            
            if voice_config:
                default_config.update(voice_config)
            
            synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)
            
            voice = texttospeech.VoiceSelectionParams(
                language_code=default_config["language_code"],
                name=default_config["voice_name"],
                ssml_gender=getattr(texttospeech.SsmlVoiceGender, default_config["gender"])
            )
            
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )
            
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            audio_id = str(uuid.uuid4())
            audio_base64 = base64.b64encode(response.audio_content).decode('utf-8')
            
            return {
                "sucesso": True,
                "audio_id": audio_id,
                "audio_base64": audio_base64,
                "tipo": "ssml",
                "tamanho_arquivo": len(response.audio_content)
            }
            
        except Exception as e:
            return {
                "sucesso": False,
                "erro": f"Erro ao gerar áudio SSML: {str(e)}"
            }
    
    def prepare_text_for_speech(self, text, options=None):
        """
        Prepara texto para síntese de voz com pausas inteligentes e formatação
        """
        if not options:
            options = {}
        
        cleaned_text = text.replace('\n\n', '. ')
        cleaned_text = cleaned_text.replace('\n', ' ')
        
        if options.get("add_pauses", True):
            cleaned_text = cleaned_text.replace('.', '. <break time="0.5s"/>')
            cleaned_text = cleaned_text.replace('!', '! <break time="0.5s"/>')
            cleaned_text = cleaned_text.replace('?', '? <break time="0.5s"/>')
            cleaned_text = cleaned_text.replace(',', ', <break time="0.2s"/>')
            cleaned_text = cleaned_text.replace(';', '; <break time="0.3s"/>')
            cleaned_text = cleaned_text.replace(':', ': <break time="0.3s"/>')
        
        if options.get("emphasize_headings", True):
            lines = text.split('\n')
            for i, line in enumerate(lines):
                if len(line) < 100 and line.isupper():
                    cleaned_text = cleaned_text.replace(line, f'<emphasis level="strong">{line}</emphasis>')
        
        if options.get("variable_speed", False):
            cleaned_text = cleaned_text.replace('<emphasis level="strong">', '<emphasis level="strong"><prosody rate="0.8">')
            cleaned_text = cleaned_text.replace('</emphasis>', '</prosody></emphasis>')
        
        if '<break' in cleaned_text or '<emphasis' in cleaned_text or '<prosody' in cleaned_text:
            ssml_text = f'''
            <speak>
                {cleaned_text}
            </speak>
            '''
            return {"text": ssml_text, "type": "ssml"}
        
        return {"text": cleaned_text, "type": "plain"}
    
    def split_long_text(self, text, max_chars=4000):
        """
        Divide texto longo em chunks para processamento TTS
        """
        if len(text) <= max_chars:
            return [text]
        
        chunks = []
        sentences = text.split('. ')
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk + sentence + '. ') <= max_chars:
                current_chunk += sentence + '. '
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + '. '
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def get_available_voices(self, language_code="pt-BR"):
        """
        Lista vozes disponíveis para um idioma
        """
        try:
            voices_response = self.client.list_voices(language_code=language_code)
            
            voices = []
            for voice in voices_response.voices:
                if voice.language_codes[0] == language_code:
                    voices.append({
                        "name": voice.name,
                        "gender": voice.ssml_gender.name,
                        "natural": "Wavenet" in voice.name or "Neural2" in voice.name
                    })
            
            return {
                "sucesso": True,
                "idioma": language_code,
                "vozes": voices
            }
            
        except Exception as e:
            return {
                "sucesso": False,
                "erro": f"Erro ao listar vozes: {str(e)}"
            }
    
    def _estimate_duration(self, text, speaking_rate=1.0):
        """
        Estima duração do áudio baseado no texto
        """
        words = len(text.split())
        base_duration = (words / 150) * 60
        adjusted_duration = base_duration / speaking_rate
        
        return round(adjusted_duration, 1)

def text_to_speech(text, voice_config=None):
    """
    Função helper para conversão rápida de texto em áudio
    """
    tts = TTSService()
    return tts.generate_audio(text, voice_config)

def prepare_document_audio(document_text, options=None):
    """
    Prepara documento completo para síntese de voz
    """
    tts = TTSService()
    
    prepared = tts.prepare_text_for_speech(document_text, options)
    
    chunks = tts.split_long_text(prepared["text"])
    
    audio_parts = []
    total_duration = 0
    
    for i, chunk in enumerate(chunks):
        if prepared["type"] == "ssml":
            result = tts.generate_ssml_audio(chunk)
        else:
            result = tts.generate_audio(chunk)
        
        if result["sucesso"]:
            audio_parts.append({
                "parte": i + 1,
                "audio_id": result["audio_id"],
                "audio_base64": result["audio_base64"],
                "duracao": result.get("duracao_estimada", 0)
            })
            total_duration += result.get("duracao_estimada", 0)
    
    return {
        "sucesso": True,
        "total_partes": len(audio_parts),
        "duracao_total": total_duration,
        "partes": audio_parts
    }
