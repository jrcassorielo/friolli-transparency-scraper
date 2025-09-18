# Friolli Transparency Scraper

## Objetivo do Projeto

Este projeto é uma ferramenta de web scraping desenvolvida para extrair dados de transparência do portal da Prefeitura de Frioli. O scraper automatiza a coleta de informações públicas como licitações, contratos, despesas e outras informações de transparência pública.

## Funcionalidades

- Extração automatizada de dados de transparência
- Login automático no portal (quando necessário)
- Exportação dos dados em formato CSV
- Tratamento de erros e logs detalhados
- Interface de linha de comando
- Geração de executável standalone

## Como Usar

### Instalação

1. Clone este repositório:
```bash
git clone https://github.com/jrcassorielo/friolli-transparency-scraper.git
cd friolli-transparency-scraper
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

### Execução

```bash
python scraper_friolli.py [opções]
```

#### Opções disponíveis:
- `--output`: Nome do arquivo de saída (padrão: dados_transparencia.csv)
- `--headless`: Executar em modo headless (sem interface gráfica)
- `--verbose`: Modo verboso para logs detalhados
- `--help`: Exibe ajuda e opções disponíveis

#### Exemplo de uso:
```bash
python scraper_friolli.py --output relatorio_2024.csv --headless --verbose
```

### Gerando Executável

Para gerar um executável standalone:
```bash
pyinstaller --onefile scraper_friolli.py
```

O executável será criado na pasta `dist/`.

## Dependências

- **selenium**: Automação do navegador web
- **beautifulsoup4**: Parsing e extração de dados HTML
- **pandas**: Manipulação e análise de dados
- **pyinstaller**: Geração de executáveis standalone

Versões específicas estão listadas no arquivo `requirements.txt`.

## Estrutura do Projeto

```
friolli-transparency-scraper/
├── README.md
├── requirements.txt
├── scraper_friolli.py
└── dados_transparencia.csv (gerado após execução)
```

## Requisitos do Sistema

- Python 3.7+
- Chrome ou Firefox instalado
- Conexão com a internet

## Contribuição

Contribuições são bem-vindas! Por favor:

1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## Avisos Legais

- Este scraper foi desenvolvido para acessar apenas informações públicas
- Respeite os termos de uso do portal
- Use com responsabilidade e ética
- Não sobrecarregue os servidores com muitas requisições simultâneas
