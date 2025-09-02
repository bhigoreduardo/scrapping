#!/usr/bin/env python3
"""
Script para criar dados de exemplo para Bancos, Mineração e Energia
"""

import json
import os
import hashlib
from datetime import datetime
import numpy as np
from config.settings import settings


def criar_dados_multisetor():
    """Cria dados de exemplo para 3 segmentos diferentes"""

    os.makedirs(settings.CACHE_DIR, exist_ok=True)

    # Dados realistas por segmento
    segmentos = {
        "Bancos": [
            {
                "cnpj": "60746948000112",
                "nome": "BRADESCO S.A.",
                "patrimonio": 198700,
                "receita": 312800,
                "lucro": 68900,
                "roe": 18.5,
            },
            {
                "cnpj": "60872504000123",
                "nome": "ITAU UNIBANCO S.A.",
                "patrimonio": 235000,
                "receita": 345600,
                "lucro": 75200,
                "roe": 19.2,
            },
            {
                "cnpj": "33603457000190",
                "nome": "SANTANDER BRASIL S.A.",
                "patrimonio": 167800,
                "receita": 289400,
                "lucro": 52300,
                "roe": 17.8,
            },
            {
                "cnpj": "59285411000113",
                "nome": "BANCO DO BRASIL S.A.",
                "patrimonio": 275400,
                "receita": 398700,
                "lucro": 68400,
                "roe": 16.2,
            },
            {
                "cnpj": "34111187000166",
                "nome": "XP INVESTIMENTOS CCTVM S.A.",
                "patrimonio": 45600,
                "receita": 123400,
                "lucro": 28700,
                "roe": 22.1,
            },
        ],
        "Mineração": [
            {
                "cnpj": "33592510000154",
                "nome": "VALE S.A.",
                "patrimonio": 287500,
                "receita": 389600,
                "lucro": 87300,
                "roe": 22.4,
            },
            {
                "cnpj": "76535764000100",
                "nome": "CSN MINERAÇÃO S.A.",
                "patrimonio": 156200,
                "receita": 234500,
                "lucro": 45600,
                "roe": 18.7,
            },
            {
                "cnpj": "07683085000100",
                "nome": "ANGLO AMERICAN BRASIL",
                "patrimonio": 189400,
                "receita": 267800,
                "lucro": 51200,
                "roe": 20.1,
            },
            {
                "cnpj": "02581102000106",
                "nome": "GERDAU S.A.",
                "patrimonio": 123600,
                "receita": 198700,
                "lucro": 23400,
                "roe": 15.8,
            },
            {
                "cnpj": "92757637000190",
                "nome": "USIMINAS S.A.",
                "patrimonio": 87600,
                "receita": 145600,
                "lucro": 12300,
                "roe": 12.5,
            },
        ],
        "Energia": [
            {
                "cnpj": "00001118000134",
                "nome": "ELETROBRAS S.A.",
                "patrimonio": 156800,
                "receita": 287400,
                "lucro": 42300,
                "roe": 15.8,
            },
            {
                "cnpj": "02474103000119",
                "nome": "ENGIE BRASIL ENERGIA S.A.",
                "patrimonio": 87600,
                "receita": 154200,
                "lucro": 28700,
                "roe": 19.6,
            },
            {
                "cnpj": "76484013000119",
                "nome": "CPFL ENERGIA S.A.",
                "patrimonio": 123400,
                "receita": 198700,
                "lucro": 34500,
                "roe": 17.2,
            },
            {
                "cnpj": "61584144000147",
                "nome": "NEOENERGIA S.A.",
                "patrimonio": 98700,
                "receita": 167800,
                "lucro": 27800,
                "roe": 18.9,
            },
            {
                "cnpj": "07883140000109",
                "nome": "CEMIG S.A.",
                "patrimonio": 145600,
                "receita": 234500,
                "lucro": 38900,
                "roe": 16.7,
            },
        ],
    }

    total_empresas = 0

    for segmento, empresas in segmentos.items():
        print(f"\n📊 Criando dados para {segmento}:")
        print("=" * 40)

        for empresa in empresas:
            # Adiciona variação realista nos dados
            variacao = np.random.uniform(0.9, 1.1)

            balanco = {
                "periodo": "2023",
                "patrimonio_liquido": round(empresa["patrimonio"] * variacao),
                "ativo_total": round(empresa["patrimonio"] * 2.5 * variacao),
                "passivo_total": round(empresa["patrimonio"] * 1.5 * variacao),
                "divida_liquida": round(empresa["patrimonio"] * 0.6 * variacao),
                "receita_liquida": round(empresa["receita"] * variacao),
                "lucro_liquido": round(empresa["lucro"] * variacao),
                "ebitda": round(empresa["receita"] * 0.25 * variacao),
                "margem_ebitda": round(25.0 * variacao, 1),
                "roe": round(empresa["roe"] * variacao, 1),
                "roa": round(empresa["roe"] * 0.7 * variacao, 1),
            }

            dados_empresa = {
                "cnpj": empresa["cnpj"],
                "razao_social": empresa["nome"],
                "nome_fantasia": empresa["nome"].split("S.A.")[0].strip(),
                "segmento": segmento,
                "setor": segmento,
                "subsetor": segmento,
                "atividade_principal": f"Atividade principal em {segmento}",
                "situacao_cadastral": "ATIVA",
                "data_abertura": "1990-01-01",
                "capital_social": round(empresa["patrimonio"] * 0.8),
                "endereco": {
                    "logradouro": "Av. Paulista",
                    "numero": "1000",
                    "bairro": "Bela Vista",
                    "cep": "01310-100",
                    "municipio": "São Paulo",
                    "uf": "SP",
                },
                "telefone": "(11) 3000-1000",
                "email": f'contato@{empresa["nome"].split()[0].lower()}.com.br',
                "ticker": "TICK3",
                "bolsa": "B3",
                "balanco_patrimonial": [balanco],
            }

            # Salva no cache
            cache_key = hashlib.md5(
                f"{empresa['cnpj']}_empresa_completa".encode()
            ).hexdigest()
            cache_path = os.path.join(settings.CACHE_DIR, f"{cache_key}.json")

            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "cnpj": empresa["cnpj"],
                        "endpoint": "empresa_completa",
                        "data": dados_empresa,
                    },
                    f,
                    ensure_ascii=False,
                    indent=2,
                )

            print(f"✅ {empresa['nome']}")
            total_empresas += 1

    print(
        f"\n🎯 Dados criados: {total_empresas} empresas (5 Bancos, 5 Mineração, 5 Energia)"
    )


if __name__ == "__main__":
    criar_dados_multisetor()
