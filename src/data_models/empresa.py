from dataclasses import dataclass
from typing import Optional, List, Dict
from datetime import datetime


@dataclass
class BalancoPatrimonial:
    periodo: str
    patrimonio_liquido: Optional[float]
    ativo_total: Optional[float]
    passivo_total: Optional[float]
    divida_bruta: Optional[float]
    divida_liquida: Optional[float]
    receita_liquida: Optional[float]
    ebitda: Optional[float]
    lucro_liquido: Optional[float]
    margem_ebitda: Optional[float]
    roe: Optional[float]  # Return on Equity
    roa: Optional[float]  # Return on Assets


@dataclass
class Empresa:
    cnpj: str
    razao_social: str
    nome_fantasia: Optional[str]
    segmento: Optional[str]
    setor: Optional[str]
    subsetor: Optional[str]
    atividade_principal: Optional[str]
    situacao_cadastral: Optional[str]
    data_abertura: Optional[str]
    capital_social: Optional[float]
    endereco: Optional[Dict]
    telefone: Optional[str]
    email: Optional[str]
    ticker: Optional[str]
    bolsa: Optional[str]
    balanco_patrimonial: List[BalancoPatrimonial]

    def to_dict(self) -> Dict:
        return {
            "cnpj": self.cnpj,
            "razao_social": self.razao_social,
            "nome_fantasia": self.nome_fantasia,
            "segmento": self.segmento,
            "setor": self.setor,
            "subsetor": self.subsetor,
            "atividade_principal": self.atividade_principal,
            "situacao_cadastral": self.situacao_cadastral,
            "data_abertura": self.data_abertura,
            "capital_social": self.capital_social,
            "endereco": self.endereco,
            "telefone": self.telefone,
            "email": self.email,
            "ticker": self.ticker,
            "bolsa": self.bolsa,
            "balanco_patrimonial": [
                {
                    "periodo": bp.periodo,
                    "patrimonio_liquido": bp.patrimonio_liquido,
                    "ativo_total": bp.ativo_total,
                    "passivo_total": bp.passivo_total,
                    "divida_bruta": bp.divida_bruta,
                    "divida_liquida": bp.divida_liquida,
                    "receita_liquida": bp.receita_liquida,
                    "ebitda": bp.ebitda,
                    "lucro_liquido": bp.lucro_liquido,
                    "margem_ebitda": bp.margem_ebitda,
                    "roe": bp.roe,
                    "roa": bp.roa,
                }
                for bp in self.balanco_patrimonial
            ],
        }

    def calcular_indicadores(self):
        """Calcula indicadores financeiros automaticamente"""
        for balanco in self.balanco_patrimonial:
            # Margem EBITDA
            if (
                balanco.ebitda is not None
                and balanco.receita_liquida is not None
                and balanco.receita_liquida > 0
            ):
                balanco.margem_ebitda = (balanco.ebitda / balanco.receita_liquida) * 100

            # ROE (Return on Equity)
            if (
                balanco.lucro_liquido is not None
                and balanco.patrimonio_liquido is not None
                and balanco.patrimonio_liquido > 0
            ):
                balanco.roe = (balanco.lucro_liquido / balanco.patrimonio_liquido) * 100

            # ROA (Return on Assets)
            if (
                balanco.lucro_liquido is not None
                and balanco.ativo_total is not None
                and balanco.ativo_total > 0
            ):
                balanco.roa = (balanco.lucro_liquido / balanco.ativo_total) * 100
