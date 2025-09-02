📊 Análises de Dados Disponíveis
1. 📈 Análise de Distribuição

Distribuição Geral

# Patrimônio Líquido
python main.py analyze distribuicao --variavel patrimonio_liquido

# Receita Líquida
python main.py analyze distribuicao --variavel receita_liquida

# Lucro Líquido
python main.py analyze distribuicao --variavel lucro_liquido

# EBITDA
python main.py analyze distribuicao --variavel ebitda

# ROE (Return on Equity)
python main.py analyze distribuicao --variavel roe

# ROA (Return on Assets)
python main.py analyze distribuicao --variavel roa

# Margem EBITDA
python main.py analyze distribuicao --variavel margem_ebitda

Distribuição por Segmento (Boxplot por Segmento)

# Boxplot do Patrimônio Líquido por Segmento
python main.py analyze distribuicao --variavel patrimonio_liquido --por-segmento

# Boxplot do ROE por Segmento
python main.py analyze distribuicao --variavel roe --por-segmento

# Boxplot da Margem EBITDA por Segmento
python main.py analyze distribuicao --variavel margem_ebitda --por-segmento

2. 🔍 Detecção de Outliers
Método IQR (Intervalo Interquartil)

# Outliers no Patrimônio Líquido
python main.py analyze outliers --variavel patrimonio_liquido --metodo iqr

# Outliers na Receita Líquida
python main.py analyze outliers --variavel receita_liquida --metodo iqr

# Outliers no Lucro Líquido
python main.py analyze outliers --variavel lucro_liquido --metodo iqr

# Outliers no ROE
python main.py analyze outliers --variavel roe --metodo iqr

Método Z-Score

# Outliers com Z-Score > 3
python main.py analyze outliers --variavel patrimonio_liquido --metodo zscore

# Outliers na Receita com Z-Score
python main.py analyze outliers --variavel receita_liquida --metodo zscore

# Outliers no EBITDA com Z-Score
python main.py analyze outliers --variavel ebitda --metodo zscore

Outliers por Segmento

# Outliers do ROE por Segmento
python main.py analyze outliers --variavel roe --por-segmento --metodo iqr

# Outliers da Margem por Segmento
python main.py analyze outliers --variavel margem_ebitda --por-segmento --metodo zscore

3. 📊 Análise de Correlação

Correlação Geral
# Matriz de correlação completa
python main.py analyze correlacao

# Correlação específica
python main.py analyze correlacao --variaveis patrimonio_liquido receita_liquida lucro_liquido

# Correlação com indicadores de rentabilidade
python main.py analyze correlacao --variaveis roe roa margem_ebitda

# Correlação patrimônio vs resultados
python main.py analyze correlacao --variaveis patrimonio_liquido ebitda lucro_liquido

Correlação por Segmento
# Correlação por segmento - Bancos
python main.py analyze correlacao --variaveis patrimonio_liquido receita_liquida --por-segmento

# Correlação por segmento - ROE vs ROA
python main.py analyze correlacao --variaveis roe roa --por-segmento

# Correlação por segmento - Margem vs Crescimento
python main.py analyze correlacao --variaveis margem_ebitda receita_liquida --por-segmento

4. 🏢 Análise Comparativa por Segmentos
# Comparação do Patrimônio Líquido
python main.py analyze segmentos --variavel patrimonio_liquido

# Comparação da Receita Líquida
python main.py analyze segmentos --variavel receita_liquida

# Comparação do ROE entre segmentos
python main.py analyze segmentos --variavel roe

# Comparação da Margem EBITDA
python main.py analyze segmentos --variavel margem_ebitda

# Comparação do Lucro Líquido
python main.py analyze segmentos --variavel lucro_liquido

# Comparação do ROA
python main.py analyze segmentos --variavel roa

5. 📦 Boxplots com Medidas Separatrizes
# Boxplot do Patrimônio Líquido com quartis
python main.py analyze distribuicao --variavel patrimonio_liquido --por-segmento

# Boxplot do ROE com outliers
python main.py analyze segmentos --variavel roe

# Boxplot da Margem EBITDA por segmento
python main.py analyze distribuicao --variavel margem_ebitda --por-segmento