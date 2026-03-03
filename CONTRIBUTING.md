# Contribuindo para o Payment Gateway

Obrigado por considerar contribuir para o Payment Gateway! Este documento fornece diretrizes para contribuições.

## Como Contribuir

### Reportando Bugs

Ao reportar bugs, inclua:

1. **Descrição clara**: O que aconteceu e o que você esperava
2. **Passos para reproduzir**: Como reproduzir o problema
3. **Ambiente**: Versão do Python, sistema operacional, etc.
4. **Logs**: Inclua mensagens de erro relevantes

### Sugerindo Melhorias

Para sugestões de features:

1. **Descrição**: Explique a feature detalhadamente
2. **Justificativa**: Por que essa feature é útil
3. **Exemplos**: Forneça exemplos de uso se possível

### Pull Requests

1. **Fork** o repositório
2. **Crie uma branch** para sua feature (`git checkout -b feature/MinhaFeature`)
3. **Siga o estilo de código** existente
4. **Escreva testes** para sua feature
5. **Atualize a documentação** se necessário
6. **Commit** suas mudanças com mensagens claras
7. **Push** para sua branch (`git push origin feature/MinhaFeature`)
8. **Abra um Pull Request**

### Padrões de Código

- Use **type hints** em Python
- Siga **PEP 8** para formatação
- Escreva **docstrings** para funções e classes
- Mantenha **cobertura de testes** acima de 80%
- Use **nomes descritivos** para variáveis e funções

### Estrutura de Commits

```
tipo(escopo): descrição curta

Descrição mais detalhada se necessário.

Relacionado a #issue-number
```

**Tipos:**
- `feat`: Nova feature
- `fix`: Correção de bug
- `docs`: Mudanças na documentação
- `style`: Formatação, sem mudança de código
- `refactor`: Refatoração de código
- `test`: Adição ou correção de testes
- `chore`: Tarefas de manutenção

### Testes

Antes de submeter:

```bash
# Execute os testes
pytest

# Verifique a cobertura
pytest --cov=app --cov-report=html

# Execute linting (se configurado)
flake8 app/
```

### Código de Conduta

- Seja respeitoso e inclusivo
- Aceite críticas construtivas
- Foque no melhor para o projeto
- Mostre empatia com outros membros

## Configuração do Ambiente de Desenvolvimento

```bash
# Clone o fork
git clone https://github.com/seu-usuario/payment-gateway.git
cd payment-gateway

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac

# Instale dependências de desenvolvimento
pip install -r requirements.txt

# Configure pre-commit hooks (se disponível)
pre-commit install

# Execute testes
pytest
```

## Dúvidas?

Se tiver dúvidas, sinta-se à vontade para:
- Abrir uma issue
- Entrar em contato com os mantenedores

Obrigado por contribuir! 🙏
