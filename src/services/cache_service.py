from typing import List, Dict
from src.utils.helpers import get_all_cached_data, combine_cache_data
from src.utils.logger import logger


class CacheService:
    def __init__(self):
        pass

    def list_cached_empresas(self) -> List[Dict]:
        """Lista todas as empresas em cache"""
        cached_data = get_all_cached_data()
        empresas = []

        for item in cached_data:
            if "data" in item and "razao_social" in item["data"]:
                empresas.append(
                    {
                        "cnpj": item.get("cnpj", ""),
                        "razao_social": item["data"]["razao_social"],
                        "timestamp": item.get("timestamp", ""),
                        "endpoint": item.get("endpoint", ""),
                    }
                )

        return empresas

    def export_cache(
        self, output_format: str = "json", output_file: str = None
    ) -> bool:
        """Exporta cache para o formato especificado"""
        logger.info(f"Exportando cache para formato {output_format}")
        return combine_cache_data(output_format, output_file)

    def clear_cache(self) -> bool:
        """Limpa todo o cache"""
        from config.settings import settings
        import shutil
        import os

        try:
            if os.path.exists(settings.CACHE_DIR):
                shutil.rmtree(settings.CACHE_DIR)
                os.makedirs(settings.CACHE_DIR)
                logger.info("Cache limpo com sucesso")
                return True
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {e}")
            return False

    def get_cache_stats(self) -> Dict:
        """Retorna estatísticas do cache"""
        cached_data = get_all_cached_data()

        return {
            "total_empresas": len(cached_data),
            "empresas_unicas": len(set(item.get("cnpj", "") for item in cached_data)),
            "periodo_cache": self._get_cache_period(cached_data),
        }

    def _get_cache_period(self, cached_data: List[Dict]) -> Dict:
        """Retorna o período do cache"""
        if not cached_data:
            return {"mais_antigo": None, "mais_recente": None}

        timestamps = [
            item.get("timestamp", "") for item in cached_data if item.get("timestamp")
        ]
        if not timestamps:
            return {"mais_antigo": None, "mais_recente": None}

        from datetime import datetime

        dates = [datetime.fromisoformat(ts) for ts in timestamps]

        return {
            "mais_antigo": min(dates).isoformat(),
            "mais_recente": max(dates).isoformat(),
        }
