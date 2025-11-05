"""
Script de teste para funcionalidade de histórico de análises
"""
import requests
import json
import os

# Configuração
BASE_URL = "http://localhost:5000"

# Você precisa obter um token válido do Firebase primeiro
# Use test_firebase.html para fazer login e copiar o token
TOKEN = input("Cole o token do Firebase aqui (obtenha em test_firebase.html): ").strip()

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

def test_image_analysis_with_history():
    """Testa análise de imagem com salvamento de histórico"""
    print("\n🖼️ Testando análise de imagem COM autenticação...")
    
    # Caminho para uma imagem de teste (crie uma ou use qualquer imagem)
    test_image_path = "test_image.jpg"
    
    if not os.path.exists(test_image_path):
        print(f"⚠️ Crie uma imagem de teste chamada '{test_image_path}' no diretório atual")
        return
    
    with open(test_image_path, 'rb') as img:
        files = {'imagem': (test_image_path, img, 'image/jpeg')}
        
        response = requests.post(
            f"{BASE_URL}/analisar",
            files=files,
            headers=headers
        )
    
    print(f"Status: {response.status_code}")
    print(f"Resposta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        print("✅ Análise realizada com sucesso! Histórico deve ter sido salvo.")
    else:
        print("❌ Erro na análise")


def test_get_image_history():
    """Testa busca de histórico de imagens"""
    print("\n📋 Buscando histórico de imagens...")
    
    response = requests.get(
        f"{BASE_URL}/historico/imagens",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    print(f"Resposta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get("sucesso"):
            historico = data.get("historico", [])
            print(f"✅ Histórico recuperado: {len(historico)} item(ns)")
            return historico
        else:
            print(f"❌ Erro: {data.get('erro')}")
    else:
        print("❌ Erro ao buscar histórico")
    
    return []


def test_get_full_history():
    """Testa busca de histórico completo (imagens + documentos)"""
    print("\n📚 Buscando histórico completo...")
    
    response = requests.get(
        f"{BASE_URL}/historico/completo",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    print(f"Resposta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_delete_history_item(tipo, doc_id):
    """Testa deleção de item do histórico"""
    print(f"\n🗑️ Deletando item {doc_id} do tipo {tipo}...")
    
    response = requests.delete(
        f"{BASE_URL}/historico/deletar/{tipo}/{doc_id}",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    print(f"Resposta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")


def test_anonymous_analysis():
    """Testa análise sem autenticação (não deve salvar histórico)"""
    print("\n👤 Testando análise anônima (sem token)...")
    
    test_image_path = "test_image.jpg"
    
    if not os.path.exists(test_image_path):
        print(f"⚠️ Crie uma imagem de teste chamada '{test_image_path}'")
        return
    
    with open(test_image_path, 'rb') as img:
        files = {'imagem': (test_image_path, img, 'image/jpeg')}
        
        response = requests.post(
            f"{BASE_URL}/analisar",
            files=files
            # SEM headers de autenticação
        )
    
    print(f"Status: {response.status_code}")
    print(f"Resposta: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code == 200:
        print("✅ Análise anônima funcionou (histórico NÃO foi salvo)")


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTE DE HISTÓRICO DE ANÁLISES - LUMINUS")
    print("=" * 60)
    
    if not TOKEN:
        print("❌ Token não fornecido. Use test_firebase.html para obter um token.")
        exit(1)
    
    # Menu de testes
    print("\nEscolha um teste:")
    print("1. Analisar imagem (com histórico)")
    print("2. Ver histórico de imagens")
    print("3. Ver histórico completo")
    print("4. Testar análise anônima")
    print("5. Deletar item do histórico")
    print("6. Executar todos os testes")
    
    opcao = input("\nOpção: ").strip()
    
    if opcao == "1":
        test_image_analysis_with_history()
    elif opcao == "2":
        test_get_image_history()
    elif opcao == "3":
        test_get_full_history()
    elif opcao == "4":
        test_anonymous_analysis()
    elif opcao == "5":
        tipo = input("Tipo (imagens/documentos): ").strip()
        doc_id = input("ID do documento: ").strip()
        test_delete_history_item(tipo, doc_id)
    elif opcao == "6":
        test_anonymous_analysis()
        test_image_analysis_with_history()
        historico = test_get_image_history()
        test_get_full_history()
        
        if historico:
            print("\n🔍 Deseja deletar algum item? (s/n)")
            if input().lower() == 's':
                test_delete_history_item("imagens", historico[0]["id"])
                test_get_image_history()  # Verificar que foi deletado
    else:
        print("❌ Opção inválida")
    
    print("\n" + "=" * 60)
    print("✅ Testes concluídos!")
    print("=" * 60)
