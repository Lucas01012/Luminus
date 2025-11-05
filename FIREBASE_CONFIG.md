# 🔥 Configurações Firebase - Luminus

## ✅ Credenciais Configuradas

### Backend (Python - Firebase Admin SDK)
**Arquivo:** `firebase/firebase_config.py`

```python
PROJECT_ID: luminus-2d0bd
STORAGE_BUCKET: luminus-2d0bd.firebasestorage.app
```

### Frontend (JavaScript - Firebase SDK)
**Arquivo:** `test_firebase.html` (já configurado)

```javascript
const firebaseConfig = {
  apiKey: "AIzaSyAMBGzFbCLayN-xSFHWA24xDZBNsoXuZ3M",
  authDomain: "luminus-2d0bd.firebaseapp.com",
  projectId: "luminus-2d0bd",
  storageBucket: "luminus-2d0bd.firebasestorage.app",
  messagingSenderId: "149284157143",
  appId: "1:149284157143:web:6d402e44c241535e372292"
};
```

---

## 🧪 Como Testar AGORA

### Opção 1: Teste Interativo (Recomendado)

1. **Abra no navegador:**
   ```
   test_firebase.html
   ```

2. **Siga os passos:**
   - ✅ Clique em "Inicializar Firebase"
   - ✅ Cadastre um usuário ou faça login
   - ✅ Clique em "Testar Backend"

3. **Pronto!** Vai mostrar todos os resultados automaticamente 🎉

---

### Opção 2: Teste via Postman

1. **Crie um usuário no Firebase Console:**
   - https://console.firebase.google.com/project/luminus-2d0bd/authentication/users
   - Email: `teste@luminus.com`
   - Senha: `teste123`

2. **Pegue o token** usando `test_firebase.html`

3. **Teste os endpoints:**

```http
### Verificar Token
POST http://localhost:5000/auth/verificar-token
Authorization: Bearer SEU_TOKEN_AQUI

### Buscar Perfil
GET http://localhost:5000/auth/perfil
Authorization: Bearer SEU_TOKEN_AQUI

### Atualizar Perfil
PUT http://localhost:5000/auth/atualizar-perfil
Authorization: Bearer SEU_TOKEN_AQUI
Content-Type: application/json

{
  "nome": "João Silva",
  "telefone": "+55 11 98765-4321"
}
```

---

## 📊 Estrutura Firestore

### Coleção: `usuarios`
```
usuarios/
  └── {uid}/
      ├── email: string
      ├── nome: string (opcional)
      ├── telefone: string (opcional)
      ├── ultimo_acesso: timestamp
      └── data_cadastro: timestamp
```

### Coleção: `historico_imagens` (a criar)
```
historico_imagens/
  └── {doc_id}/
      ├── usuario_id: string
      ├── imagem_nome: string
      ├── objeto_detectado: string
      ├── confianca: number
      ├── processing_time: number
      └── timestamp: timestamp
```

### Coleção: `historico_documentos` (a criar)
```
historico_documentos/
  └── {doc_id}/
      ├── usuario_id: string
      ├── arquivo_nome: string
      ├── formato: string (PDF/DOCX)
      ├── tamanho_bytes: number
      ├── resumo: string
      ├── palavras_chave: array
      └── timestamp: timestamp
```

---

## 🔧 Comandos Úteis

### Iniciar servidor
```bash
cd C:\Projetos\Luminus\Luminus
python main.py
```

### Rodar testes
```bash
python test_auth.py
```

### Abrir teste HTML
```bash
start test_firebase.html
```

---

## 🎯 Status Atual

- ✅ Firebase Admin SDK instalado
- ✅ Credenciais configuradas
- ✅ Autenticação funcionando
- ✅ Endpoints de auth prontos
- ✅ Middleware de proteção pronto
- ✅ Teste HTML configurado
- ⏳ Histórico de imagens/documentos (próximo passo)

---

## 📝 Próximos Passos

1. **Testar autenticação completa** com `test_firebase.html`
2. **Adicionar histórico** de imagens e documentos
3. **Integrar frontend React Native** com Firebase Auth
4. **Adicionar regras de segurança** no Firestore

---

**Projeto:** luminus-2d0bd  
**Última Atualização:** 05/11/2025
