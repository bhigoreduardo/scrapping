import requests
from typing import Optional, Dict
from config.settings import settings
from src.utils.logger import logger


class ReceitaWSClient:
    def __init__(self):
        self.base_url = settings.RECEITAWS_BASE_URL

    def get_company_by_cnpj(self, cnpj: str) -> Optional[Dict]:
        """Busca dados da empresa na ReceitaWS"""
        try:
            formatted_cnpj = "".join(filter(str.isdigit, cnpj))
            url = f"{self.base_url}/cnpj/{formatted_cnpj}"

            response = requests.get(url, timeout=settings.REQUEST_TIMEOUT)
            response.raise_for_status()

            data = response.json()
            if data.get("status") == "ERROR":
                return None

            return data
        except Exception as e:
            logger.error(f"Erro ao buscar CNPJ na ReceitaWS: {e}")
            return None
