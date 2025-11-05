# 🎯 Guia de Teste - Histórico de Análises

## O que foi implementado?

✅ **HistoryService** - Serviço que gerencia o histórico no Firestore
- Salva análises de imagens na coleção `historico_imagens`
- Salva processamento de documentos na coleção `historico_documentos`
- Permite buscar, listar e deletar histórico

✅ **history_controller** - Endpoints REST para histórico
- `GET /historico/imagens` - Lista histórico de imagens do usuário
- `GET /historico/documentos` - Lista histórico de documentos
- `GET /historico/completo` - Lista histórico completo (imagens + docs)
- `DELETE /historico/deletar/<tipo>/<doc_id>` - Deleta item do histórico

✅ **Integração com image_controller**
- Todas as 3 rotas de análise agora salvam histórico automaticamente
- `/analisar` - Análise normal
- `/analisar-rapido` - Análise rápida
- `/analisar-ultra` - Análise ultra-rápida
- Usa `@optional_auth` - funciona com ou sem autenticação
- Se autenticado → salva histórico
- Se anônimo → funciona normalmente, sem salvar

---

## 📋 Estrutura dos Dados no Firestore

### Collection: `historico_imagens`

```json
{
  "usuario_id": "firebase-uid-123",
  "imagem_nome": "foto.jpg",
  "objeto_detectado": "Cachorro",
  "confianca": 0.95,
  "descricao": "Um cachorro dourado...",
  "processing_time": 2.34,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Collection: `historico_documentos`

```json
{
  "usuario_id": "firebase-uid-123",
  "arquivo_nome": "documento.pdf",
  "formato": "pdf",
  "tamanho_bytes": 54321,
  "preview_texto": "Primeiros 500 caracteres...",
  "resumo": "Resumo gerado pelo Gemini",
  "palavras_chave": ["palavra1", "palavra2"],
  "total_paginas": 5,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## 🧪 Como Testar

### 1️⃣ Certifique-se que o servidor está rodando

```powershell
cd c:\Projetos\Luminus\Luminus
python main.py
```

Deve exibir: `Running on http://0.0.0.0:5000`

---

### 2️⃣ Obtenha um Token do Firebase

Abra no navegador: `test_firebase.html`

1. Clique em **"Registrar Novo Usuário"** ou **"Fazer Login"**
2. Após login bem-sucedido, copie o **Token** exibido
3. Guarde esse token para os próximos passos

---

### 3️⃣ Teste com Script Python

```powershell
python test_history.py
```

Quando pedir, cole o token obtido no passo 2.

**Menu de testes disponíveis:**
- **Opção 1** - Analisar imagem (cria histórico)
- **Opção 2** - Ver histórico de imagens
- **Opção 3** - Ver histórico completo
- **Opção 4** - Testar análise anônima (sem histórico)
- **Opção 5** - Deletar item específico
- **Opção 6** - Executar todos os testes em sequência

⚠️ **Atenção:** Você precisa ter uma imagem chamada `test_image.jpg` na pasta do projeto para a opção 1 funcionar.

---

### 4️⃣ Teste Manual com Postman/Insomnia

#### 📤 Analisar Imagem (COM autenticação)

**Request:**
```
POST http://localhost:5000/analisar
Headers:
  Authorization: Bearer SEU_TOKEN_AQUI
Body (form-data):
  imagem: [selecione arquivo]
```

**Response esperado:**
```json
{
  "objeto": "Cachorro",
  "confianca": 0.95,
  "descricao": "Um cachorro dourado...",
  "processing_time": 2.34
}
```

✅ **Histórico salvo automaticamente no Firestore!**

---

#### 📤 Analisar Imagem (SEM autenticação)

**Request:**
```
POST http://localhost:5000/analisar
Body (form-data):
  imagem: [selecione arquivo]
```

**Response esperado:**
```json
{
  "objeto": "Cachorro",
  "confianca": 0.95,
  "descricao": "Um cachorro dourado...",
  "processing_time": 2.34
}
```

✅ **Funciona normalmente, mas não salva histórico**

---

#### 📥 Buscar Histórico de Imagens

**Request:**
```
GET http://localhost:5000/historico/imagens
Headers:
  Authorization: Bearer SEU_TOKEN_AQUI
```

**Response esperado:**
```json
{
  "sucesso": true,
  "historico": [
    {
      "id": "abc123",
      "imagem_nome": "foto.jpg",
      "objeto_detectado": "Cachorro",
      "confianca": 0.95,
      "descricao": "Um cachorro dourado...",
      "processing_time": 2.34,
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

#### 📥 Buscar Histórico Completo

**Request:**
```
GET http://localhost:5000/historico/completo
Headers:
  Authorization: Bearer SEU_TOKEN_AQUI
```

**Response esperado:**
```json
{
  "sucesso": true,
  "historico": [
    {
      "tipo": "imagem",
      "id": "abc123",
      "imagem_nome": "foto.jpg",
      "objeto_detectado": "Cachorro",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    {
      "tipo": "documento",
      "id": "def456",
      "arquivo_nome": "doc.pdf",
      "formato": "pdf",
      "timestamp": "2024-01-15T09:15:00Z"
    }
  ]
}
```

---

#### 🗑️ Deletar Item do Histórico

**Request:**
```
DELETE http://localhost:5000/historico/deletar/imagens/abc123
Headers:
  Authorization: Bearer SEU_TOKEN_AQUI
```

**Response esperado:**
```json
{
  "sucesso": true,
  "mensagem": "Histórico deletado com sucesso"
}
```

---

## 🔍 Verificar no Firestore Console

1. Acesse: https://console.firebase.google.com/
2. Selecione o projeto **luminus-2d0bd**
3. Vá em **Firestore Database**
4. Procure pelas collections:
   - `historico_imagens`
   - `historico_documentos`

Você verá os documentos salvos com os dados das análises!

---

## ⚙️ Comportamento Esperado

### ✅ Cenário 1: Usuário Autenticado
- Analisa imagem → **Salva no histórico automaticamente**
- Busca histórico → **Retorna apenas dados do próprio usuário**
- Deleta histórico → **Só consegue deletar próprios dados**

### ✅ Cenário 2: Usuário Anônimo
- Analisa imagem → **Funciona normalmente**
- Histórico não é salvo (não tem user_id)
- Endpoints de histórico retornam 401 (não autenticado)

### ✅ Cenário 3: Token Inválido/Expirado
- Endpoints protegidos retornam 401
- Análise de imagem funciona (usa `@optional_auth`)

---

## 🐛 Troubleshooting

### Erro: "Nenhuma imagem foi enviada"
- Certifique-se de enviar o campo `imagem` no form-data
- Formato aceito: JPEG, PNG, etc.

### Erro: "Token inválido"
- Obtenha um novo token em `test_firebase.html`
- Verifique se o formato é: `Bearer SEU_TOKEN`

### Histórico não aparece
- Verifique se analisou imagem COM token válido
- Verifique no Firestore Console se o documento foi criado
- Logs no terminal mostram: `✅ Histórico salvo para usuário...`

### Erro 401 ao buscar histórico
- Você precisa estar autenticado
- Use o header `Authorization: Bearer TOKEN`

---

## 📚 Próximos Passos (Futuro)

- [ ] Implementar histórico para documentos (document_controller)
- [ ] Adicionar paginação no histórico (limit/offset)
- [ ] Permitir filtrar histórico por data
- [ ] Adicionar estatísticas (total de análises, objetos mais detectados)
- [ ] Upload de imagem para Firebase Storage (opcional)

---

## ✅ Checklist de Validação

Antes de considerar completo, verifique:

- [ ] Servidor Flask rodando sem erros
- [ ] Login no Firebase funciona (test_firebase.html)
- [ ] Análise de imagem COM token salva no histórico
- [ ] Análise de imagem SEM token funciona (mas não salva)
- [ ] GET /historico/imagens retorna dados corretos
- [ ] GET /historico/completo combina imagens e documentos
- [ ] DELETE remove item e valida ownership
- [ ] Firestore Console mostra collections e documentos

---

**🎉 Sistema de histórico implementado com sucesso!**
