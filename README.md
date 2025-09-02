--variavel:
  [patrimonio_liquido]
  [receita_liquida]
  [lucro_liquido]
  [ebitda]
  [roe]
  [roa]
  [margem_ebitda]

📊 Análises de Dados Disponíveis

# Distribuição Geral

python main.py analyze distribuicao --variavel [patrimonio_liquido]

# Distribuição por Segmento (Boxplot por Segmento)

python main.py analyze distribuicao --variavel [patrimonio_liquido] --por-segmento

# Correlação Geral

python main.py analyze correlacao

# Correlação específica

python main.py analyze correlacao --variaveis [patrimonio_liquido] [receita_liquida] [lucro_liquido]

python main.py analyze correlacao --variaveis [roe] [roa] [margem_ebitda]

# Análise Comparativa por Segmentos

python main.py analyze segmentos --variavel [patrimonio_liquido]

# Boxplots com Medidas Separatrizes

python main.py analyze distribuicao --variavel [patrimonio_liquido] --por-segmento

# Database Off

python criar_dados_multisetor.py

# Database search

python main.py search [33000167000101]