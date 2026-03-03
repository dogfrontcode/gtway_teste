# Payment Gateway - Frontend

Interface web para o Payment Gateway (React + Vite + Tailwind).

## Executar

```bash
cd frontend
npm install
npm run dev
```

Acesse: http://localhost:5173

## Requisitos

- Backend rodando em http://localhost:5001
- O Vite faz proxy de `/api` para o backend automaticamente

## Credenciais de teste

- **Admin:** admin@gateway.com / admin123
- **Tenant:** user@samplestore.com / user123 (após `flask seed-db`)

## Build para produção

```bash
npm run build
```

Os arquivos ficam em `dist/`. Para servir junto com o Flask, copie para a pasta `static` do backend.
