import requests
import json
from typing import Optional, Dict, List
from config.settings import settings
from src.utils.logger import logger


class B3Client:
    def __init__(self):
        self.base_url = settings.B3_API_BASE_URL
        self.segmentos_map = self._load_segmentos_map()

    def _load_segmentos_map(self) -> Dict:
        """Mapeamento de tickers para segmentos"""
        return {
            "PETR4": {
                "segmento": "Petróleo e Gás",
                "setor": "Energia",
                "subsetor": "Exploração e Produção",
            },
            "VALE3": {
                "segmento": "Mineração",
                "setor": "Materiais Básicos",
                "subsetor": "Mineração",
            },
            "ITUB4": {
                "segmento": "Bancos",
                "setor": "Financeiro",
                "subsetor": "Bancos",
            },
            "BBDC4": {
                "segmento": "Bancos",
                "setor": "Financeiro",
                "subsetor": "Bancos",
            },
            "ABEV3": {
                "segmento": "Bebidas",
                "setor": "Consumo Não-Cíclico",
                "subsetor": "Bebidas",
            },
            "WEGE3": {
                "segmento": "Equipamentos",
                "setor": "Bens Industriais",
                "subsetor": "Máquinas e Equipamentos",
            },
            "MGLU3": {
                "segmento": "Varejo",
                "setor": "Consumo Cíclico",
                "subsetor": "Comércio",
            },
            "B3SA3": {
                "segmento": "Serviços Financeiros",
                "setor": "Financeiro",
                "subsetor": "Serviços Financeiros",
            },
            "JBSS3": {
                "segmento": "Alimentos",
                "setor": "Consumo Não-Cíclico",
                "subsetor": "Carnes e Derivados",
            },
            "VIIA3": {
                "segmento": "Varejo",
                "setor": "Consumo Cíclico",
                "subsetor": "Comércio",
            },
            "ELET3": {
                "segmento": "Energia Elétrica",
                "setor": "Utilidade Pública",
                "subsetor": "Energia Elétrica",
            },
            "TIMS3": {
                "segmento": "Telecomunicações",
                "setor": "Comunicações",
                "subsetor": "Telecomunicações",
            },
            "VIVT3": {
                "segmento": "Telecomunicações",
                "setor": "Comunicações",
                "subsetor": "Telecomunicações",
            },
            "RENT3": {
                "segmento": "Locação de Veículos",
                "setor": "Consumo Cíclico",
                "subsetor": "Serviços",
            },
            "RADL3": {
                "segmento": "Farmácias",
                "setor": "Consumo Não-Cíclico",
                "subsetor": "Comércio e Distribuição",
            },
            "SUZB3": {
                "segmento": "Papel e Celulose",
                "setor": "Materiais Básicos",
                "subsetor": "Papel e Celulose",
            },
            "KLBN11": {
                "segmento": "Papel e Celulose",
                "setor": "Materiais Básicos",
                "subsetor": "Papel e Celulose",
            },
            "EGIE3": {
                "segmento": "Energia Elétrica",
                "setor": "Utilidade Pública",
                "subsetor": "Energia Elétrica",
            },
            "CCRO3": {
                "segmento": "Infraestrutura",
                "setor": "Bens Industriais",
                "subsetor": "Transporte",
            },
            "RAIL3": {
                "segmento": "Logística",
                "setor": "Bens Industriais",
                "subsetor": "Transporte",
            },
        }

    def get_company_financials(self, cnpj: str) -> Optional[Dict]:
        """Busca dados financeiros de empresas listadas na B3"""
        try:
            # Primeiro busca o ticker pelo CNPJ
            ticker_info = self._find_ticker_by_cnpj(cnpj)
            if not ticker_info:
                return None

            # Busca dados financeiros
            financial_data = self._get_financial_data(ticker_info["ticker"])
            if financial_data:
                financial_data.update(ticker_info)

            return financial_data

        except Exception as e:
            logger.error(f"Erro ao buscar dados B3: {e}")
            return None

    def _find_ticker_by_cnpj(self, cnpj: str) -> Optional[Dict]:
        """Encontra o ticker na B3 pelo CNPJ"""
        try:
            # Lista de empresas listadas - exemplo simplificado
            companies = [
                {"cnpj": "33000167000101", "ticker": "PETR4", "name": "PETROBRAS"},
                {"cnpj": "33592510000154", "ticker": "VALE3", "name": "VALE S.A."},
                {"cnpj": "60872504000123", "ticker": "ITUB4", "name": "ITAUUNIBANCO"},
                {"cnpj": "60746948000112", "ticker": "BBDC4", "name": "BRADESCO"},
                {"cnpj": "07526557000100", "ticker": "ABEV3", "name": "AMBEV S.A."},
                {"cnpj": "84429695000111", "ticker": "WEGE3", "name": "WEG S.A."},
                {"cnpj": "09346601000125", "ticker": "MGLU3", "name": "MAGAZINE LUIZA"},
                {"cnpj": "09346611000113", "ticker": "B3SA3", "name": "B3 S.A."},
                {"cnpj": "02916265000160", "ticker": "JBSS3", "name": "JBS S.A."},
                {"cnpj": "33112555000149", "ticker": "VIIA3", "name": "VIA S.A."},
                {"cnpj": "00001118000134", "ticker": "ELET3", "name": "ELETROBRAS"},
                {"cnpj": "02421403000140", "ticker": "TIMS3", "name": "TIM S.A."},
                {
                    "cnpj": "02558157000162",
                    "ticker": "VIVT3",
                    "name": "TELEFÔNICA BRASIL",
                },
                {"cnpj": "17184037000150", "ticker": "RENT3", "name": "LOCALIZA"},
                {"cnpj": "61585865000151", "ticker": "RADL3", "name": "RAIADROGASIL"},
                {"cnpj": "16404287000155", "ticker": "SUZB3", "name": "SUZANO S.A."},
                {"cnpj": "89637490000105", "ticker": "KLBN11", "name": "KLABIN S.A."},
                {"cnpj": "02474103000119", "ticker": "EGIE3", "name": "ENGIE BRASIL"},
                {"cnpj": "02998611000109", "ticker": "CCRO3", "name": "CCR S.A."},
                {"cnpj": "02387241000160", "ticker": "RAIL3", "name": "RUMO S.A."},
            ]

            formatted_cnpj = "".join(filter(str.isdigit, cnpj))

            for company in companies:
                company_cnpj = "".join(filter(str.isdigit, company.get("cnpj", "")))
                if company_cnpj == formatted_cnpj:
                    ticker = company.get("ticker")
                    segmento_info = self.segmentos_map.get(ticker, {})
                    return {
                        "ticker": ticker,
                        "nome": company.get("name"),
                        "segmento": segmento_info.get("segmento"),
                        "setor": segmento_info.get("setor"),
                        "subsetor": segmento_info.get("subsetor"),
                    }

            return None
        except Exception as e:
            logger.error(f"Erro ao buscar ticker: {e}")
            return None

    def _get_financial_data(self, ticker: str) -> Optional[Dict]:
        """Busca dados financeiros pelo ticker - implementação simplificada"""
        try:
            # Dados de exemplo - valores em milhões de R$
            financials_data = {
                "PETR4": {
                    "patrimonio_liquido": 452100,
                    "divida_liquida": 185300,
                    "receita_liquida": 511200,
                    "lucro_liquido": 124800,
                    "ebitda": 218700,
                    "ativo_total": 987600,
                    "passivo_total": 535500,
                },
                "VALE3": {
                    "patrimonio_liquido": 287500,
                    "divida_liquida": 98200,
                    "receita_liquida": 389600,
                    "lucro_liquido": 87300,
                    "ebitda": 156400,
                    "ativo_total": 654300,
                    "passivo_total": 366800,
                },
                "ITUB4": {
                    "patrimonio_liquido": 198700,
                    "divida_liquida": 45600,
                    "receita_liquida": 312800,
                    "lucro_liquido": 68900,
                    "ebitda": 102300,
                    "ativo_total": 2456700,
                    "passivo_total": 2258000,
                },
                "MGLU3": {
                    "patrimonio_liquido": 15200,
                    "divida_liquida": 8700,
                    "receita_liquida": 42600,
                    "lucro_liquido": -3200,
                    "ebitda": 1800,
                    "ativo_total": 38900,
                    "passivo_total": 23700,
                },
            }

            if ticker in financials_data:
                return {"ticker": ticker, "financials": financials_data[ticker]}

            return None
        except Exception as e:
            logger.error(f"Erro ao buscar dados financeiros: {e}")
            return None
