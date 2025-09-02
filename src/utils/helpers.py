import os
import json
import hashlib
from datetime import datetime
from typing import Any, Dict, List
import csv
from config.settings import settings


def ensure_directories():
    """Garante que todos os diretórios necessários existam"""
    os.makedirs(settings.DATA_DIR, exist_ok=True)
    os.makedirs(settings.CACHE_DIR, exist_ok=True)
    os.makedirs(os.path.join(settings.DATA_DIR, "raw"), exist_ok=True)
    os.makedirs(os.path.join(settings.DATA_DIR, "processed"), exist_ok=True)


def get_cache_key(cnpj: str, endpoint: str) -> str:
    """Gera uma chave única para cache"""
    key = f"{cnpj}_{endpoint}"
    return hashlib.md5(key.encode()).hexdigest()


def save_to_cache(cnpj: str, endpoint: str, data: Any):
    """Salva dados no cache"""
    if not settings.CACHE_ENABLED:
        return

    cache_key = get_cache_key(cnpj, endpoint)
    cache_path = os.path.join(settings.CACHE_DIR, f"{cache_key}.json")

    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "timestamp": datetime.now().isoformat(),
                "cnpj": cnpj,
                "endpoint": endpoint,
                "data": data,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )


def load_from_cache(cnpj: str, endpoint: str) -> Any:
    """Carrega dados do cache"""
    if not settings.CACHE_ENABLED:
        return None

    cache_key = get_cache_key(cnpj, endpoint)
    cache_path = os.path.join(settings.CACHE_DIR, f"{cache_key}.json")

    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            cached_data = json.load(f)
            # Verifica se o cache não expirou (24 horas)
            cache_time = datetime.fromisoformat(cached_data["timestamp"])
            if (datetime.now() - cache_time).total_seconds() < 86400:
                return cached_data["data"]
    return None


def format_cnpj(cnpj: str) -> str:
    """Formata CNPJ para o padrão 00.000.000/0000-00"""
    cnpj = "".join(filter(str.isdigit, cnpj))
    if len(cnpj) != 14:
        return cnpj
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"


def get_all_cached_data() -> List[Dict]:
    """Retorna todos os dados em cache"""
    cached_files = []

    if os.path.exists(settings.CACHE_DIR):
        for filename in os.listdir(settings.CACHE_DIR):
            if filename.endswith(".json"):
                filepath = os.path.join(settings.CACHE_DIR, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        cached_data = json.load(f)
                        cached_files.append(cached_data)
                except Exception as e:
                    print(f"Erro ao ler arquivo {filename}: {e}")

    return cached_files


def export_to_json(cached_data: List[Dict], output_path: str):
    """Exporta dados para JSON"""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cached_data, f, ensure_ascii=False, indent=2)


def export_to_csv(cached_data: List[Dict], output_path: str):
    """Exporta dados para CSV"""
    if not cached_data:
        return

    # Extrai todos os campos únicos
    all_fields = set()
    for item in cached_data:
        if "data" in item:
            all_fields.update(item["data"].keys())

    fieldnames = ["cnpj", "timestamp", "endpoint"] + sorted(all_fields)

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for item in cached_data:
            if "data" in item:
                row = {
                    "cnpj": item.get("cnpj", ""),
                    "timestamp": item.get("timestamp", ""),
                    "endpoint": item.get("endpoint", ""),
                }
                row.update(item["data"])
                writer.writerow(row)


def export_to_excel(cached_data: List[Dict], output_path: str):
    """Exporta dados para Excel (CSV com formatação melhor)"""
    export_to_csv(cached_data, output_path)


def combine_cache_data(output_format: str = "json", output_file: str = None):
    """Combina todos os dados em cache e exporta no formato especificado"""
    cached_data = get_all_cached_data()

    if not cached_data:
        print("Nenhum dado encontrado em cache.")
        return False

    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(
            settings.DATA_DIR,
            "processed",
            f"empresas_combined_{timestamp}.{output_format}",
        )

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    try:
        if output_format == "json":
            export_to_json(cached_data, output_file)
        elif output_format == "csv":
            export_to_csv(cached_data, output_file)
        elif output_format == "xlsx":
            export_to_excel(cached_data, output_file.replace(".xlsx", ".csv"))
        else:
            print(f"Formato {output_format} não suportado.")
            return False

        print(f"Dados exportados com sucesso: {output_file}")
        print(f"Total de registros: {len(cached_data)}")
        return True

    except Exception as e:
        print(f"Erro ao exportar dados: {e}")
        return False
