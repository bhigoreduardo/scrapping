from typing import Optional, List
from src.api_clients.brasil_api_client import BrasilAPIClient
from src.api_clients.receitaws_client import ReceitaWSClient
from src.api_clients.b3_client import B3Client
from src.data_models.empresa import Empresa, BalancoPatrimonial
from src.utils.helpers import load_from_cache, save_to_cache, format_cnpj
from src.utils.logger import logger


class EmpresaService:
    def __init__(self):
        self.brasil_api = BrasilAPIClient()
        self.receitaws = ReceitaWSClient()
        self.b3_client = B3Client()

    def buscar_empresa_por_cnpj(self, cnpj: str) -> Optional[Empresa]:
        """Busca dados completos de uma empresa por CNPJ"""
        logger.info(f"Buscando dados para CNPJ: {format_cnpj(cnpj)}")

        # Tenta carregar do cache primeiro
        cached_data = load_from_cache(cnpj, "empresa_completa")
        if cached_data:
            logger.info("Dados encontrados em cache")
            return Empresa(**cached_data)

        # Busca dados das APIs
        dados_basicos = self._buscar_dados_basicos(cnpj)
        if not dados_basicos:
            logger.error("Não foi possível encontrar dados básicos da empresa")
            return None

        dados_financeiros = self._buscar_dados_financeiros(cnpj)

        # Constrói o objeto Empresa
        empresa = self._construir_empresa(dados_basicos, dados_financeiros)

        # Calcula indicadores automaticamente
        empresa.calcular_indicadores()

        # Salva no cache
        save_to_cache(cnpj, "empresa_completa", empresa.to_dict())

        return empresa

    def _buscar_dados_basicos(self, cnpj: str) -> Optional[dict]:
        """Busca dados básicos da empresa"""
        # Tenta BrasilAPI primeiro
        dados = self.brasil_api.get_company_by_cnpj(cnpj)
        if dados:
            return dados

        # Fallback para ReceitaWS
        dados = self.receitaws.get_company_by_cnpj(cnpj)
        return dados

    def _buscar_dados_financeiros(self, cnpj: str) -> Optional[dict]:
        """Busca dados financeiros da empresa"""
        return self.b3_client.get_company_financials(cnpj)

    def _construir_empresa(
        self, dados_basicos: dict, dados_financeiros: dict
    ) -> Empresa:
        """Constrói objeto Empresa a partir dos dados brutos"""
        # Converte dados da BrasilAPI/ReceitaWS para formato padrão
        if "razao_social" in dados_basicos:
            # Formato BrasilAPI
            endereco = {
                "logradouro": dados_basicos.get("logradouro"),
                "numero": dados_basicos.get("numero"),
                "complemento": dados_basicos.get("complemento"),
                "bairro": dados_basicos.get("bairro"),
                "cep": dados_basicos.get("cep"),
                "municipio": dados_basicos.get("municipio"),
                "uf": dados_basicos.get("uf"),
            }
            telefone = dados_basicos.get("telefone")
            email = dados_basicos.get("email")
            capital_social = (
                float(dados_basicos.get("capital_social", 0))
                if dados_basicos.get("capital_social")
                else None
            )
        else:
            # Formato ReceitaWS
            endereco = {
                "logradouro": dados_basicos.get("logradouro"),
                "numero": dados_basicos.get("numero"),
                "complemento": dados_basicos.get("complemento"),
                "bairro": dados_basicos.get("bairro"),
                "cep": dados_basicos.get("cep"),
                "municipio": dados_basicos.get("municipio"),
                "uf": dados_basicos.get("uf"),
            }
            telefone = dados_basicos.get("telefone")
            email = dados_basicos.get("email")
            capital_social = (
                float(dados_basicos.get("capital_social", 0))
                if dados_basicos.get("capital_social")
                else None
            )

        # Prepara informações de segmento dos dados financeiros
        segmento_info = dados_financeiros or {}

        # Prepara balanço patrimonial com valores padrão para campos opcionais
        balanco_patrimonial = []
        if dados_financeiros and "financials" in dados_financeiros:
            financials = dados_financeiros["financials"]
            balanco = BalancoPatrimonial(
                periodo="2023",
                patrimonio_liquido=financials.get("patrimonio_liquido"),
                ativo_total=financials.get("ativo_total"),
                passivo_total=financials.get("passivo_total"),
                divida_bruta=financials.get(
                    "divida_liquida"
                ),  # Usando divida_liquida como proxy
                divida_liquida=financials.get("divida_liquida"),
                receita_liquida=financials.get("receita_liquida"),
                ebitda=financials.get("ebitda"),
                lucro_liquido=financials.get("lucro_liquido"),
                margem_ebitda=None,  # Será calculado depois
                roe=None,  # Será calculado depois
                roa=None,  # Será calculado depois
            )
            balanco_patrimonial.append(balanco)

        return Empresa(
            cnpj=dados_basicos.get("cnpj", ""),
            razao_social=dados_basicos.get("razao_social", "")
            or dados_basicos.get("nome", ""),
            nome_fantasia=dados_basicos.get("nome_fantasia"),
            segmento=segmento_info.get("segmento"),
            setor=segmento_info.get("setor"),
            subsetor=segmento_info.get("subsetor"),
            atividade_principal=dados_basicos.get("atividade_principal"),
            situacao_cadastral=dados_basicos.get("situacao"),
            data_abertura=dados_basicos.get("data_inicio_atividade")
            or dados_basicos.get("abertura"),
            capital_social=capital_social,
            endereco=endereco,
            telefone=telefone,
            email=email,
            ticker=segmento_info.get("ticker") if segmento_info else None,
            bolsa="B3" if segmento_info else None,
            balanco_patrimonial=balanco_patrimonial,
        )
