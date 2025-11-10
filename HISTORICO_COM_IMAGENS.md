# 🖼️ Histórico com Armazenamento de Imagens

## ✨ Novo Recurso Implementado

Agora o histórico de análises **salva a imagem original** junto com a resposta da IA!

### Como funciona?

1. **Usuário faz upload da imagem** → `/analisar`
2. **IA analisa e retorna descrição** → Gemini AI
3. **Imagem é salva no Firebase Storage** → `gs://luminus-2d0bd/historico/{user_id}/{doc_id}.jpg`
4. **Dados são salvos no Firestore** → Collection `historico_imagens` com URL da imagem
5. **Frontend pode exibir histórico** → Imagem + Resposta da IA

---

## 📊 Estrutura de Dados

### Firestore: `historico_imagens`

```json
{
  "id": "abc123xyz",
  "usuario_id": "firebase-uid-do-usuario",
  "imagem_nome": "cachorro.jpg",
  "imagem_url": "https://storage.googleapis.com/luminus-2d0bd.../historico/uid/abc123xyz.jpg",
  "objeto_detectado": "Um cachorro dourado correndo em um parque ensolarado...",
  "confianca": null,
  "processing_time": 2.34,
  "timestamp": "2024-11-07T15:30:00Z",
  "tipo": "analise_imagem"
}
```

### Firebase Storage

```
gs://luminus-2d0bd.firebasestorage.app/
  └── historico/
      └── {usuario_id}/
          ├── abc123xyz.jpg
          ├── def456uvw.png
          └── ghi789rst.jpeg
```

**Estrutura organizada por usuário!** Cada pasta contém as imagens do histórico do usuário.

---

## 🎯 Endpoints da API

### 1. Analisar Imagem (salva no histórico)

```http
POST /analisar
Content-Type: multipart/form-data
Authorization: Bearer {firebase_token}

Body:
  imagem: [arquivo de imagem]
```

**Response:**
```json
{
  "objeto": "Um cachorro dourado correndo em um parque...",
  "confianca": null,
  "processing_time": 2.34
}
```

**O que acontece nos bastidores:**
1. ✅ Imagem é analisada pela IA
2. ✅ Imagem original é salva no Firebase Storage
3. ✅ URL da imagem + resultado são salvos no Firestore
4. ✅ Usuário recebe a resposta da análise

---

### 2. Buscar Histórico de Imagens

```http
GET /historico/imagens
Authorization: Bearer {firebase_token}
```

**Response:**
```json
{
  "sucesso": true,
  "total": 3,
  "historico": [
    {
      "id": "abc123",
      "imagem_nome": "cachorro.jpg",
      "imagem_url": "https://storage.googleapis.com/.../abc123.jpg",
      "objeto_detectado": "Um cachorro dourado...",
      "confianca": null,
      "processing_time": 2.34,
      "timestamp": "2024-11-07T15:30:00Z"
    },
    {
      "id": "def456",
      "imagem_nome": "gato.png",
      "imagem_url": "https://storage.googleapis.com/.../def456.png",
      "objeto_detectado": "Um gato preto dormindo...",
      "confianca": null,
      "processing_time": 1.87,
      "timestamp": "2024-11-07T14:20:00Z"
    }
  ]
}
```

**Agora o frontend pode:**
- ✅ Exibir a imagem original: `<img src="{imagem_url}" />`
- ✅ Mostrar a descrição da IA
- ✅ Exibir quando foi analisada
- ✅ Mostrar tempo de processamento

---

### 3. Buscar Histórico Completo

```http
GET /historico/completo
Authorization: Bearer {firebase_token}
```

**Response:** Combina histórico de imagens + documentos

---

### 4. Deletar Item do Histórico

```http
DELETE /historico/deletar/imagens/{doc_id}
Authorization: Bearer {firebase_token}
```

**O que acontece:**
1. ✅ Valida que o item pertence ao usuário
2. ✅ Deleta documento do Firestore
3. ⚠️ **Nota:** A imagem no Storage permanece (pode ser deletada depois para economizar)

---

## 🎨 Exemplo de Integração no Frontend

### React/Next.js

```jsx
function HistoricoImagens() {
  const [historico, setHistorico] = useState([]);
  
  useEffect(() => {
    async function buscarHistorico() {
      const token = await user.getIdToken();
      
      const response = await fetch('http://localhost:5000/historico/imagens', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      const data = await response.json();
      setHistorico(data.historico);
    }
    
    buscarHistorico();
  }, []);
  
  return (
    <div className="historico">
      <h2>Minhas Análises</h2>
      
      {historico.map(item => (
        <div key={item.id} className="historico-item">
          {/* Exibe a imagem original */}
          <img 
            src={item.imagem_url} 
            alt={item.imagem_nome}
            className="historico-imagem"
          />
          
          {/* Exibe a resposta da IA */}
          <div className="historico-info">
            <h3>{item.imagem_nome}</h3>
            <p>{item.objeto_detectado}</p>
            <small>
              Analisado em {new Date(item.timestamp).toLocaleString()}
              • {item.processing_time}s
            </small>
          </div>
        </div>
      ))}
    </div>
  );
}
```

### HTML + JavaScript

```html
<div id="historico"></div>

<script>
async function carregarHistorico() {
  const token = firebase.auth().currentUser.accessToken;
  
  const response = await fetch('http://localhost:5000/historico/imagens', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  const { historico } = await response.json();
  
  const container = document.getElementById('historico');
  
  historico.forEach(item => {
    container.innerHTML += `
      <div class="item">
        <img src="${item.imagem_url}" alt="${item.imagem_nome}">
        <div>
          <h3>${item.imagem_nome}</h3>
          <p>${item.objeto_detectado}</p>
          <small>${new Date(item.timestamp).toLocaleString()}</small>
        </div>
      </div>
    `;
  });
}

carregarHistorico();
</script>
```

---

## 🔒 Segurança e Privacidade

### ✅ O que está protegido:

1. **Autenticação obrigatória** para salvar e buscar histórico
2. **Isolamento de dados** - cada usuário só vê suas próprias imagens
3. **Validação de ownership** - só pode deletar próprios itens
4. **Imagens públicas** - URLs são públicas mas difíceis de adivinhar (UUIDs)

### ⚠️ Considerações:

- **As URLs das imagens são públicas** - qualquer pessoa com a URL pode ver
- **Não há autenticação nas URLs** - Firebase Storage precisa de regras para isso
- **Recomendação:** Configure Storage Rules para maior segurança

### 🛡️ Storage Rules Recomendadas

Adicione no Firebase Console → Storage → Rules:

```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    // Permite leitura pública das imagens (para URLs funcionarem)
    match /historico/{userId}/{imageId} {
      allow read: if true;  // Público
      allow write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

---

## 📦 O que mudou no código?

### `services/history_service.py`

**Antes:**
```python
def save_image_analysis(user_id, image_name, analysis_result):
    # Salvava só os dados no Firestore
```

**Depois:**
```python
def save_image_analysis(user_id, image_name, analysis_result, image_file=None):
    # 1. Faz upload da imagem para Firebase Storage
    # 2. Gera URL pública
    # 3. Salva dados + URL no Firestore
```

### `controllers/image_controller.py`

**Mudanças:**
1. ✅ Importou `io` para trabalhar com BytesIO
2. ✅ Cria cópia da imagem original antes de otimizar
3. ✅ Passa `image_file=imagem_original` para o HistoryService

---

## 🧪 Como Testar

### 1. Analise uma imagem autenticado

```bash
# Obtenha token em test_firebase.html
curl -X POST http://localhost:5000/analisar \
  -H "Authorization: Bearer SEU_TOKEN" \
  -F "imagem=@cachorro.jpg"
```

### 2. Verifique o histórico

```bash
curl http://localhost:5000/historico/imagens \
  -H "Authorization: Bearer SEU_TOKEN"
```

**Você verá:**
- ✅ Campo `imagem_url` com URL do Firebase Storage
- ✅ Pode abrir a URL no navegador e ver a imagem!

### 3. Verifique no Firebase Console

1. Acesse: https://console.firebase.google.com/
2. Projeto: **luminus-2d0bd**
3. **Storage** → Pasta `historico/{seu_user_id}/`
4. Veja as imagens salvas! 🎉
5. **Firestore** → Collection `historico_imagens`
6. Veja os documentos com `imagem_url`

---

## 💡 Melhorias Futuras (Opcional)

### 1. Deletar imagem do Storage ao remover do histórico

```python
def delete_history_item(user_id, doc_id, tipo='imagem'):
    # ... código atual ...
    
    # Deleta também do Storage
    if tipo == 'imagem' and data.get('imagem_url'):
        try:
            # Extrai path da URL
            blob = bucket.blob(f"historico/{user_id}/{doc_id}.jpg")
            blob.delete()
        except:
            pass  # Ignora se já foi deletado
    
    doc_ref.delete()
```

### 2. Miniatura (thumbnail) para carregar mais rápido

```python
# Salva versão otimizada para listagem
thumbnail = ImageOptimizer.optimize_for_ai(image_file, max_size=(200, 200))
blob_thumb = bucket.blob(f"historico/{user_id}/thumb_{doc_id}.jpg")
blob_thumb.upload_from_string(thumbnail.getvalue())
```

### 3. Limite de armazenamento por usuário

```python
# Conta total de imagens do usuário
count = db.collection('historico_imagens')\
          .where('usuario_id', '==', user_id)\
          .count().get()

if count > 100:
    return {"erro": "Limite de 100 imagens atingido"}
```

### 4. Compressão automática antes do upload

```python
# Já temos ImageOptimizer, podemos usar:
compressed = ImageOptimizer.optimize_for_ai(
    image_file, 
    max_size=(1024, 1024), 
    quality=85
)
# Salva versão comprimida (economiza storage)
```

---

## ✅ Checklist de Validação

- [ ] Analisar imagem COM autenticação salva no histórico
- [ ] GET `/historico/imagens` retorna `imagem_url`
- [ ] Abrir `imagem_url` no navegador exibe a imagem
- [ ] Firebase Storage tem pasta `historico/{user_id}/`
- [ ] Firestore tem documentos com campo `imagem_url`
- [ ] Usuário A não vê histórico do usuário B
- [ ] Deletar item remove do Firestore (Storage opcional)

---

**🎉 Sistema de histórico com imagens implementado!**

Agora o frontend pode exibir uma galeria completa das análises anteriores! 📸
