import requests
from typing import Optional, Dict
from config.settings import settings
from src.utils.logger import logger
from src.utils.helpers import format_cnpj


class BrasilAPIClient:
    def __init__(self):
        self.base_url = settings.BRASIL_API_BASE_URL

    def get_company_by_cnpj(self, cnpj: str) -> Optional[Dict]:
        """Busca dados básicos da empresa por CNPJ"""
        try:
            formatted_cnpj = "".join(filter(str.isdigit, cnpj))
            url = f"{self.base_url}/cnpj/v1/{formatted_cnpj}"

            response = requests.get(url, timeout=settings.REQUEST_TIMEOUT)
            response.raise_for_status()

            return response.json()
        except Exception as e:
            logger.error(f"Erro ao buscar CNPJ na BrasilAPI: {e}")
            return None
