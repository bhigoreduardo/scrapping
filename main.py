#!/usr/bin/env python3
"""
Sistema de Análise Financeira por CNPJ
"""

import argparse
import json
from rich.console import Console
from rich.table import Table
from rich import box

from src.services.empresa_service import EmpresaService
from src.services.cache_service import CacheService
from src.services.analise_service import AnaliseService
from src.utils.helpers import ensure_directories, format_cnpj
from src.utils.logger import logger

console = Console()


def main():
    ensure_directories()

    parser = argparse.ArgumentParser(description="Busca dados empresariais por CNPJ")
    subparsers = parser.add_subparsers(dest="command", help="Comando a executar")

    # Comando search
    search_parser = subparsers.add_parser("search", help="Buscar empresa por CNPJ")
    search_parser.add_argument("cnpj", help="CNPJ da empresa (com ou sem formatação)")
    search_parser.add_argument(
        "--output",
        "-o",
        choices=["table", "json"],
        default="table",
        help="Formato de saída",
    )

    # Comando export
    export_parser = subparsers.add_parser("export", help="Exportar dados do cache")
    export_parser.add_argument(
        "--format",
        "-f",
        choices=["json", "csv", "xlsx"],
        default="json",
        help="Formato de exportação",
    )
    export_parser.add_argument("--output", "-o", help="Arquivo de saída (opcional)")

    # Comando cache
    cache_parser = subparsers.add_parser("cache", help="Gerenciar cache")
    cache_parser.add_argument(
        "action", choices=["list", "stats", "clear"], help="Ação a executar"
    )

    # Comando analyze
    analyze_parser = subparsers.add_parser("analyze", help="Análise de dados")
    analyze_parser.add_argument(
        "tipo",
        choices=["distribuicao", "outliers", "correlacao", "segmentos"],
        help="Tipo de análise",
    )
    analyze_parser.add_argument("--variavel", "-v", help="Variável para análise")
    analyze_parser.add_argument(
        "--metodo",
        "-m",
        choices=["iqr", "zscore"],
        default="iqr",
        help="Método para detecção de outliers",
    )
    analyze_parser.add_argument(
        "--por-segmento", "-s", action="store_true", help="Analisar por segmento"
    )
    analyze_parser.add_argument(
        "--variaveis", nargs="+", help="Variáveis para análise de correlação"
    )

    args = parser.parse_args()

    if args.command == "search":
        buscar_empresa(args.cnpj, args.output)
    elif args.command == "export":
        exportar_cache(args.format, args.output)
    elif args.command == "cache":
        gerenciar_cache(args.action)
    elif args.command == "analyze":
        analisar_dados(args)
    else:
        parser.print_help()


def buscar_empresa(cnpj: str, output_format: str):
    """Busca e exibe dados de uma empresa"""
    service = EmpresaService()
    empresa = service.buscar_empresa_por_cnpj(cnpj)

    if not empresa:
        console.print(
            f"[red]❌ Empresa com CNPJ {format_cnpj(cnpj)} não encontrada[/red]"
        )
        return

    if output_format == "json":
        console.print_json(data=empresa.to_dict())
    else:
        exibir_empresa_tabela(empresa)


def exportar_cache(format: str, output_file: str):
    """Exporta dados do cache"""
    service = CacheService()
    success = service.export_cache(format, output_file)

    if success:
        console.print(
            f"[green]✅ Cache exportado com sucesso no formato {format}[/green]"
        )
    else:
        console.print("[red]❌ Erro ao exportar cache[/red]")


def gerenciar_cache(action: str):
    """Gerencia o cache"""
    service = CacheService()

    if action == "list":
        empresas = service.list_cached_empresas()
        if empresas:
            table = Table(title="📊 Empresas em Cache", box=box.ROUNDED)
            table.add_column("CNPJ", style="cyan")
            table.add_column("Razão Social", style="green")
            table.add_column("Data Cache", style="yellow")

            for emp in empresas:
                table.add_row(
                    format_cnpj(emp["cnpj"]),
                    emp["razao_social"],
                    emp["timestamp"][:10],  # Apenas a data
                )
            console.print(table)
        else:
            console.print("[yellow]⚠️  Nenhuma empresa em cache[/yellow]")

    elif action == "stats":
        stats = service.get_cache_stats()
        console.print_json(data=stats)

    elif action == "clear":
        success = service.clear_cache()
        if success:
            console.print("[green]✅ Cache limpo com sucesso[/green]")
        else:
            console.print("[red]❌ Erro ao limpar cache[/red]")


def analisar_dados(args):
    """Executa análise de dados"""
    service = AnaliseService()

    if args.tipo == "distribuicao":
        if not args.variavel:
            console.print(
                "[red]❌ É necessário especificar uma variável com --variavel[/red]"
            )
            return
        service.analise_distribuicao(args.variavel, args.por_segmento)

    elif args.tipo == "outliers":
        if not args.variavel:
            console.print(
                "[red]❌ É necessário especificar uma variável com --variavel[/red]"
            )
            return
        outliers = service.detectar_outliers(
            args.variavel, args.metodo, args.por_segmento
        )
        console.print(f"\n[bold]🔍 Outliers detectados em {args.variavel}[/bold]")
        console.print(outliers)

    elif args.tipo == "correlacao":
        service.analise_correlacao(args.variaveis, args.por_segmento)

    elif args.tipo == "segmentos":
        if not args.variavel:
            console.print(
                "[red]❌ É necessário especificar uma variável com --variavel[/red]"
            )
            return
        service.analise_comparativa_segmentos(args.variavel)


def exibir_empresa_tabela(empresa):
    """Exibe dados da empresa em formato de tabela"""
    # Tabela de informações básicas
    table_basico = Table(
        title=f"📊 Dados da Empresa - {format_cnpj(empresa.cnpj)}", box=box.ROUNDED
    )
    table_basico.add_column("Campo", style="cyan")
    table_basico.add_column("Valor", style="green")

    table_basico.add_row("Razão Social", empresa.razao_social)
    table_basico.add_row("Nome Fantasia", empresa.nome_fantasia or "N/A")
    table_basico.add_row("Segmento", empresa.segmento or "N/A")
    table_basico.add_row("Setor", empresa.setor or "N/A")
    table_basico.add_row("Subsetor", empresa.subsetor or "N/A")
    table_basico.add_row("Atividade Principal", empresa.atividade_principal or "N/A")
    table_basico.add_row("Situação Cadastral", empresa.situacao_cadastral or "N/A")
    table_basico.add_row("Data de Abertura", empresa.data_abertura or "N/A")
    table_basico.add_row(
        "Capital Social",
        f"R$ {empresa.capital_social:,.2f}" if empresa.capital_social else "N/A",
    )
    table_basico.add_row("Ticker", empresa.ticker or "Não listada")
    table_basico.add_row("Bolsa", empresa.bolsa or "N/A")

    console.print(table_basico)

    # Tabela de endereço
    if empresa.endereco:
        table_endereco = Table(title="🏢 Endereço", box=box.ROUNDED)
        table_endereco.add_column("Campo", style="cyan")
        table_endereco.add_column("Valor", style="green")

        endereco = empresa.endereco
        table_endereco.add_row("Logradouro", endereco.get("logradouro", "N/A"))
        table_endereco.add_row("Número", endereco.get("numero", "N/A"))
        table_endereco.add_row("Complemento", endereco.get("complemento", "N/A"))
        table_endereco.add_row("Bairro", endereco.get("bairro", "N/A"))
        table_endereco.add_row("CEP", endereco.get("cep", "N/A"))
        table_endereco.add_row("Município", endereco.get("municipio", "N/A"))
        table_endereco.add_row("UF", endereco.get("uf", "N/A"))

        console.print(table_endereco)

    # Contatos
    if empresa.telefone or empresa.email:
        table_contato = Table(title="📞 Contatos", box=box.ROUNDED)
        table_contato.add_column("Tipo", style="cyan")
        table_contato.add_column("Valor", style="green")

        if empresa.telefone:
            table_contato.add_row("Telefone", empresa.telefone)
        if empresa.email:
            table_contato.add_row("Email", empresa.email)

        console.print(table_contato)

    # Balanço Patrimonial
    if empresa.balanco_patrimonial:
        table_balanco = Table(title="💰 Balanço Patrimonial (2023)", box=box.ROUNDED)
        table_balanco.add_column("Indicador", style="cyan")
        table_balanco.add_column("Valor (R$ milhões)", style="green")

        for balanco in empresa.balanco_patrimonial:
            if balanco.patrimonio_liquido:
                table_balanco.add_row(
                    "Patrimônio Líquido", f"R$ {balanco.patrimonio_liquido:,.2f}"
                )
            if balanco.receita_liquida:
                table_balanco.add_row(
                    "Receita Líquida", f"R$ {balanco.receita_liquida:,.2f}"
                )
            if balanco.lucro_liquido:
                table_balanco.add_row(
                    "Lucro Líquido", f"R$ {balanco.lucro_liquido:,.2f}"
                )
            if balanco.ebitda:
                table_balanco.add_row("EBITDA", f"R$ {balanco.ebitda:,.2f}")
            if balanco.divida_liquida:
                table_balanco.add_row(
                    "Dívida Líquida", f"R$ {balanco.divida_liquida:,.2f}"
                )
            if balanco.margem_ebitda:
                table_balanco.add_row("Margem EBITDA", f"{balanco.margem_ebitda:.2f}%")
            if balanco.roe:
                table_balanco.add_row("ROE", f"{balanco.roe:.2f}%")
            if balanco.roa:
                table_balanco.add_row("ROA", f"{balanco.roa:.2f}%")

        console.print(table_balanco)


if __name__ == "__main__":
    main()
