#!/usr/bin/env python3
"""
Script para buscar CNPJs reais de diferentes segmentos da B3
"""

import pandas as pd
from src.services.empresa_service import EmpresaService
from src.utils.logger import logger
from src.utils.helpers import format_cnpj
import time

# Lista de CNPJs conhecidos de diferentes segmentos
CNPJS_POR_SEGMENTO = {
    # "Bancos": [
    #     "60746948000112",  # Bradesco
    #     "60701190000104",  # Itaú Unibanco
    #     "33603457000190",  # Santander
    #     "59285411000113",  # Banco do Brasil
    #     "33657248000120",  # BTG Pactual
    #     "34111187000166",  # XP Investimentos
    #     "33172537000109",  # Safra
    #     "33112555000149",  # Banco Inter
    #     "02920684000101",  # Nu Holdings (Nubank)
    #     "04627095000100",  # C6 Bank
    #     "34088016000109",  # Mercado Pago
    #     "33172537000109",  # Banco Safra
    #     "04284723000101",  # PicPay
    #     "04627095000100",  # C6 Bank
    #     "34111187000166",  # XP Inc.
    #     "04284723000101",  # PicPay
    #     "04627095000100",  # C6 Bank
    #     "34111187000166",  # XP Inc.
    #     "04284723000101",  # PicPay
    #     "04627095000100",  # C6 Bank
    # ],
    # "Varejo": [
    #     "09346601000125",  # Magazine Luiza S.A.
    #     "88631334000159",  # Casas Bahia Comércio Eletrônico S.A. (Via S.A.)
    #     "61585865000151",  # RaiaDrogasil S.A.
    #     "45242914000171",  # CVC Brasil Operadora e Agência de Viagens S.A.
    #     "88661904000109",  # Via S.A. (antiga Via Varejo, controladora de Americanas, Casas Bahia, Ponto)
    #     "33041260065290",  # Lojas Renner S.A. (CNPJ Matriz correto)
    #     "05411936000142",  # Centauro (Empresa: Ômega Geração de Energia Elétrica Ltda, mas a marca é da Centauro Sports)
    #     "09206821000115",  # Netshoes (Mova Participações S.A. - holding do grupo)
    #     "10760308000180",  # Mobly S.A.
    #     "18452000000160",  # Petz S.A.
    #     "49337273000105",  # Le Biscuit (Dufrio S.A. - Eletro)
    #     "53113791000122",  # Tok&Stok (Tok&Stok S.A.)
    #     "61082097000150",  # Etna (Etna S.A. - Casa e Construção)
    #     "61186888000111",  # Fast Shop (Fast Shop Comércio Eletrônico S.A.)
    #     "60910988000109",  # Lojas Marisa (Marisa Lojas S.A.)
    #     "78457185000103",  # Havan (Havan Ltda - Matriz)
    #     "33211497000190",  # Riachuelo (Indústrias de Confecções Riachuelo S.A.)
    #     "88787230000105",  # Pernambucanas
    #     "05337021000138",  # Leader
    # ],
    "Mineração": [
        "33592510000154",  # Vale S.A.
        "08902291000115",  # CSN Mineração S.A.
        "34028316000100",  # Anglo American Brasil Ltda.
        "04252163000120",  # MRN - Mineração Rio do Norte S.A.
        "22685995000155",  # CBMM - Companhia Brasileira de Metalurgia e Mineração
        "02998301000120",  # Nexa Resources S.A. (antiga Votorantim Metais)
        "33611500000119",  # Gerdau S.A.
        "27351751000109",  # ArcelorMittal Brasil S.A.
        "60894730000105",  # Usiminas - Usinas Siderúrgicas de Minas Gerais S.A.
        "33042724000129",  # CSN - Companhia Siderúrgica Nacional
        "23199223000107",  # Ferro+ (Vale)
        "23199223000107",  # Mineração Usiminas S.A.
        "20506277000180",  # Samarco Mineração S.A.
        "02998301000120",  # Votorantim Metais (agora Nexa Resources)
        "61064061000107",  # Alcoa Alumínio S.A.
        "04683195000120",  # Norsk Hydro do Brasil Ltda.
        "04205955000120",  # Rio Tinto Mineração Brasil Ltda.
        "04683195000120",  # BHP Billiton Brasil Ltda. (agora parte da Samarco)
        "23199223000107",  # Vale Fertilizantes S.A. (CNPJ da Vale)
        "04683195000120",  # Yara Brasil Ltda.
    ],
    "Energia": [
        "00001180000126",  # Eletrobras - Centrais Elétricas Brasileiras S.A.
        "02474103000119",  # Engie Brasil Energia S.A.
        "02429144000193",  # CPFL Energia S.A. (CNPJ Correto: 02.998.301/0001-20)
        "37663076000107",  # AES Brasil Energia S.A. (AES Tietê)
        "01083200000118",  # Neoenergia S.A. (CNPJ da holding)
        "17155730000164",  # Cemig - Companhia Energética de Minas Gerais
        "76483817000120",  # Copel - Companhia Paranaense de Energia
        "03983431000103",  # EDP Brasil - EDP Energias do Brasil S.A.
        "03220438000173",  # Equatorial Energia S.A.
        "42500384000151",  # Omega Energia S.A.
        "08364948000138",  # Alupar Investimento S.A. (CNPJ Correto: 08.274.232/0001-30)
        "07859971000130",  # Taesa - Transmissora Aliança de Energia Elétrica S.A.
        "02998611000104",  # Transmissão Paulista - CTEEP (CNPJ Correto: 61.186.888/0001-11)
        "00864214000106",  # Energisa S.A.
        "01104937000170",  # Eletropar (Placeholder - Empresa menor, CNPJ pode variar)
        "08534605000174",  # Renova Energia S.A.
    ],
    # "Tecnologia": [
    #     "53113791000122",  # TOTVS S.A.
    #     "54517628000198",  # Linx S.A. (adquirida pela Stone, mas mantém CNPJ)
    #     "02351877000152",  # Locaweb Serviços de Internet S.A.
    #     "09042817000105",  # Bemobi Mobile Tech S.A.
    #     "81243735000148",  # Positivo Tecnologia S.A.
    #     "82901000000127",  # Intelbras S.A.
    #     "71208516000174",  # Algar Telecom S.A.
    #     "02421421000111",  # TIM S.A.
    #     "02558157000162",  # Telefônica Brasil S.A. (Vivo)
    #     "40432544000147",  # Claro S.A. (América Móvil)
    #     "76535764000143",  # Oi S.A.
    #     "33530486000129",  # Embratel Participações S.A.
    #     "01778972000174",  # Americanet
    #     "04601397000128",  # Brisanet Participações S.A.
    #     "02255187000108",  # Unifique Telecomunicações S.A.
    #     "04065791000199",  # Sinqia S.A.
    # ],
}


def buscar_cnpjs_por_segmento():
    """Busca CNPJs de diferentes segmentos"""
    service = EmpresaService()

    total_empresas = sum(len(cnpjs) for cnpjs in CNPJS_POR_SEGMENTO.values())
    empresas_processadas = 0

    for segmento, cnpjs in CNPJS_POR_SEGMENTO.items():
        print(f"\n🔍 Buscando segmento: {segmento}")
        print(f"📊 Total de CNPJs: {len(cnpjs)}")
        print("=" * 50)

        for i, cnpj in enumerate(cnpjs, 1):
            try:
                print(f"{i:2d}/{len(cnpjs)} - Buscando CNPJ: {format_cnpj(cnpj)}")
                empresa = service.buscar_empresa_por_cnpj(cnpj)

                if empresa:
                    print(f"   ✅ Encontrado: {empresa.razao_social}")
                else:
                    print(f"   ❌ Não encontrado ou erro na busca")

                empresas_processadas += 1
                print(
                    f"   📈 Progresso: {empresas_processadas}/{total_empresas} empresas"
                )

                # Delay para não sobrecarregar as APIs
                time.sleep(1)

            except Exception as e:
                print(f"   ⚠️  Erro ao buscar CNPJ {cnpj}: {e}")
                continue

    print(f"\n🎯 Busca concluída! {empresas_processadas} empresas processadas.")


def listar_empresas_em_cache():
    """Lista todas as empresas em cache"""
    from src.services.cache_service import CacheService

    service = CacheService()
    empresas = service.list_cached_empresas()

    print("\n📋 Empresas em Cache:")
    print("=" * 80)

    for emp in empresas:
        print(f"CNPJ: {format_cnpj(emp['cnpj'])}")
        print(f"Razão Social: {emp['razao_social']}")
        print(f"Segmento: {emp.get('segmento', 'N/A')}")
        print(f"Data Cache: {emp['timestamp'][:10]}")
        print("-" * 40)


if __name__ == "__main__":
    print("🚀 Iniciando busca de CNPJs por segmento...")
    print("⏰ Isso pode levar alguns minutos devido aos delays entre requisições")
    print("💤 Delay de 1 segundo entre cada busca para não sobrecarregar as APIs")
    print("=" * 60)

    buscar_cnpjs_por_segmento()
    listar_empresas_em_cache()
