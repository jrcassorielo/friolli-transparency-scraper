# LexOffice AI

Plataforma inovadora para gestão completa de escritórios de advocacia. O objetivo é centralizar o relacionamento com clientes, o ciclo de vida de processos, atividades jurídicas e rotinas de backoffice em um único hub inteligente com automações e insights preditivos.

## Principais recursos

- **Gestão de clientes**: cadastro enriquecido com histórico e anotações.
- **Gestão de casos**: acompanhamento por área de atuação, etapa processual e nível de risco.
- **Tarefas com priorização inteligente**: cálculo dinâmico de prioridade que considera urgência, esforço e atrasos.
- **Agenda de audiências**: vínculo direto com o caso para montar uma timeline unificada.
- **Painel de insights**: recomendações automáticas sobre riscos, gargalos e oportunidades de automação.

## Arquitetura

- **API**: [FastAPI](https://fastapi.tiangolo.com/) com SQLModel e SQLite.
- **Banco de dados**: SQLite embarcado (pode ser trocado por PostgreSQL ajustando a URL em `app/database.py`).
- **Serviço de insights**: heurísticas baseadas em prazos, riscos e automações registradas.

```
app/
├── main.py              # Ponto de entrada da API
├── database.py          # Engine e factory de sessões
├── models.py            # Modelos SQLModel
├── schemas.py           # Schemas Pydantic para entrada/saída
├── routers/             # Rotas organizadas por domínio
└── services/insights.py # Motor de priorização e recomendações
```

## Como executar

1. Instale as dependências (recomendado criar um virtualenv):

   ```bash
   pip install -e .[dev]
   ```

2. Inicie a API:

   ```bash
   uvicorn app.main:app --reload
   ```

3. Acesse a documentação interativa em `http://localhost:8000/docs`.

## Testes automatizados

```bash
pytest
```

## Próximos passos sugeridos

- Integração com provedores de agenda (Google/Outlook) para sincronizar audiências.
- Mecanismo de automação com templates para petições e notificações.
- Conectores com tribunais para ingestão automática de andamentos.
- Dashboard analítico em tempo real com indicadores financeiros e de produtividade.
