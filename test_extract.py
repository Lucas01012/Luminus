import sys
sys.path.insert(0, 'c:/Users/Lucas/Desktop/Lumis/Luminus-backend/Luminus')

from services.document_service import extract_text_from_pdf
import io

# Teste com um PDF de exemplo
with open('test.pdf', 'rb') as f:
    content = f.read()
    
resultado = extract_text_from_pdf(content)

print("=" * 60)
print("TEXTO EXTRAÍDO:")
print("=" * 60)
print(resultado.get('text_content', 'VAZIO!')[:1000])
print("\n")
print("=" * 60)
print(f"Total de caracteres: {len(resultado.get('text_content', ''))}")
print("=" * 60)
