# 🕷 Web Scraper

Aplicação desktop desenvolvida em Python que extrai dados de qualquer página da web, com interface gráfica e exportação para CSV.

## Funcionalidades

- Extração de dados de qualquer URL
- 6 modos de extração: títulos, links, imagens, tabelas, parágrafos e resumo geral
- Cards com contadores dos dados encontrados
- Resultados exibidos com formatação e cores
- Exportação dos dados extraídos para CSV
- Interface não trava durante o carregamento (uso de threading)
- Tratamento de erros de conexão e timeout

## Tecnologias

- **Python 3**
- **Tkinter** (interface gráfica)
- **Requests** (requisições HTTP)
- **BeautifulSoup4** (parsing HTML)
- **Threading** (execução assíncrona)

## Como executar

1. Instale as dependências:
```bash
pip install requests beautifulsoup4
```
2. Clone este repositório:
```bash
git clone https://github.com/SEU-USUARIO/web-scraper-python.git
```
3. Execute o arquivo:
```bash
python scraper.py
```

## Como usar

1. Digite a URL do site que deseja analisar
2. Escolha o tipo de extração no menu dropdown
3. Clique em "Extrair Dados"
4. Para salvar os dados, clique em "Exportar CSV"

## Captura de tela

*Em breve*

## Autor

Desenvolvido como projeto de portfólio durante a graduação em Engenharia da Computação.
