# 🔧 Solução: Problema de Login

## ✅ Status

- ✅ Backend rodando: porta 5001
- ✅ Frontend rodando: porta 5173
- ✅ Usuário existe no banco
- ✅ Senha está correta
- ✅ Endpoint `/api/v1/auth/login` funciona

## ❌ Problema

Você recriou o banco com `make db-reset`, mas o navegador tem **tokens antigos** no cache.

## ✅ Solução Rápida

### Opção 1: Limpar Cache do Navegador

1. Abra http://localhost:5173
2. Pressione **F12** (abre DevTools)
3. Vá para **Application** (ou **Armazenamento**)
4. Clique em **Local Storage** → `http://localhost:5173`
5. **Delete** tudo (clique direito → Clear)
6. Feche o DevTools
7. **Recarregue a página** (Ctrl+R ou Cmd+R)
8. Faça login novamente: `user@samplestore.com` / `user123`
9. ✅ Deve funcionar!

### Opção 2: Modo Anônimo

1. Abra uma **janela anônima/privada** do navegador
2. Acesse http://localhost:5173
3. Login: `user@samplestore.com` / `user123`
4. ✅ Deve funcionar!

### Opção 3: Reiniciar Tudo

```bash
# Mate os processos
pkill -f "python.*run.py"
pkill -f "vite"

# Reinicie
make dev
```

Depois:
1. Abra http://localhost:5173
2. **Limpe o localStorage** (F12 → Application → Local Storage → Clear)
3. Recarregue a página
4. Login: `user@samplestore.com` / `user123`

---

## 🧪 Teste Via API (Terminal)

Para confirmar que funciona:

```bash
# Teste direto no backend
curl -X POST http://localhost:5001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@samplestore.com","password":"user123"}'
```

Se isso funcionar (retorna `access_token`), o problema é só o cache do navegador.

---

## 🎯 Por Que Isso Acontece?

Quando você faz `make db-reset`:
1. ✅ Banco é recriado
2. ✅ Novos usuários são criados
3. ✅ Novos IDs são gerados
4. ❌ Mas o navegador ainda tem **tokens antigos** no localStorage

**Solução**: Limpar o localStorage do navegador

---

## ✅ Credenciais Corretas

Após `make db-reset`:

**Admin**:
- Email: `admin@gateway.com`
- Senha: `admin123`

**Tenant (Sample Store)**:
- Email: `user@samplestore.com`
- Senha: `user123`

---

## 🚀 Fluxo Recomendado

1. `make db-reset` (quando resetar banco)
2. Limpar localStorage do navegador (F12 → Application → Clear)
3. Recarregar página
4. Fazer login
5. ✅ Funciona!

---

## 💡 Dica para o Futuro

Adicione um botão "Limpar Cache" no frontend ou faça logout automático quando o token é inválido.

Exemplo no `api.js`:

```javascript
async function request(url, options = {}) {
  const res = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers: { ...getHeaders(options.auth !== false), ...options.headers },
  });
  
  // Se token inválido, limpar localStorage
  if (res.status === 401) {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login';
  }
  
  const data = res.ok ? await res.json().catch(() => ({})) : await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || data.details || `HTTP ${res.status}`);
  return data;
}
```

---

## ✅ Resumo

O problema **NÃO** é com seu código. É apenas cache do navegador.

**Solução**: Limpar localStorage (F12 → Application → Local Storage → Clear)

Depois disso, o login funcionará perfeitamente! 🎉
