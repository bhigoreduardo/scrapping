import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from scipy import stats
import matplotlib

matplotlib.use("Agg")  # Força backend não-interativo
import matplotlib.pyplot as plt
import seaborn as sns
from rich.console import Console
from rich.table import Table
from rich import box
import json
import os
from datetime import datetime

from src.utils.helpers import get_all_cached_data
from src.utils.logger import logger
from config.settings import settings

console = Console()


class AnaliseService:
    def __init__(self):
        self.cached_data = get_all_cached_data()
        self.output_dir = os.path.join(settings.DATA_DIR, "plots")
        os.makedirs(self.output_dir, exist_ok=True)

    def get_dataframe(self) -> pd.DataFrame:
        """Converte dados do cache para DataFrame"""
        rows = []

        for item in self.cached_data:
            if "data" in item and "balanco_patrimonial" in item["data"]:
                for balanco in item["data"]["balanco_patrimonial"]:
                    row = {
                        "cnpj": item["data"].get("cnpj", ""),
                        "razao_social": item["data"].get("razao_social", ""),
                        "segmento": item["data"].get("segmento", ""),
                        "setor": item["data"].get("setor", ""),
                        "subsetor": item["data"].get("subsetor", ""),
                        "periodo": balanco.get("periodo", ""),
                        "patrimonio_liquido": balanco.get("patrimonio_liquido"),
                        "ativo_total": balanco.get("ativo_total"),
                        "passivo_total": balanco.get("passivo_total"),
                        "divida_liquida": balanco.get("divida_liquida"),
                        "receita_liquida": balanco.get("receita_liquida"),
                        "lucro_liquido": balanco.get("lucro_liquido"),
                        "ebitda": balanco.get("ebitda"),
                        "margem_ebitda": balanco.get("margem_ebitda"),
                        "roe": balanco.get("roe"),
                        "roa": balanco.get("roa"),
                    }
                    rows.append(row)

        df = pd.DataFrame(rows)
        # Converter colunas numéricas
        numeric_cols = [
            "patrimonio_liquido",
            "ativo_total",
            "passivo_total",
            "divida_liquida",
            "receita_liquida",
            "lucro_liquido",
            "ebitda",
            "margem_ebitda",
            "roe",
            "roa",
        ]

        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        return df.dropna(subset=numeric_cols, how="all")

    def _save_plot(self, plt, filename: str):
        """Salva o plot como imagem"""
        try:
            plot_path = os.path.join(self.output_dir, filename)
            plt.savefig(plot_path, bbox_inches="tight", dpi=300)
            plt.close()
            console.print(f"[green]📊 Plot salvo como: {plot_path}[/green]")
            return plot_path
        except Exception as e:
            logger.error(f"Erro ao salvar plot: {e}")
            return None

    def analise_distribuicao(self, coluna: str, por_segmento: bool = False):
        """Análise de distribuição dos dados"""
        df = self.get_dataframe()

        if coluna not in df.columns:
            console.print(f"[red]❌ Coluna '{coluna}' não encontrada[/red]")
            return

        if por_segmento:
            self._analise_distribuicao_por_segmento(df, coluna)
        else:
            self._analise_distribuicao_geral(df, coluna)

    def _analise_distribuicao_geral(self, df: pd.DataFrame, coluna: str):
        """Análise de distribuição geral"""
        dados = df[coluna].dropna()

        if len(dados) == 0:
            console.print(f"[red]❌ Nenhum dado disponível para {coluna}[/red]")
            return

        table = Table(title=f"📊 Distribuição - {coluna}", box=box.ROUNDED)
        table.add_column("Estatística", style="cyan")
        table.add_column("Valor", style="green")

        table.add_row("Média", f"{dados.mean():.2f}")
        table.add_row("Mediana", f"{dados.median():.2f}")
        table.add_row("Desvio Padrão", f"{dados.std():.2f}")
        table.add_row("Mínimo", f"{dados.min():.2f}")
        table.add_row("Máximo", f"{dados.max():.2f}")
        table.add_row("Assimetria", f"{dados.skew():.4f}")
        table.add_row("Curtose", f"{dados.kurtosis():.4f}")
        table.add_row("Q1 (25%)", f"{dados.quantile(0.25):.2f}")
        table.add_row("Q3 (75%)", f"{dados.quantile(0.75):.2f}")
        table.add_row("IQR", f"{dados.quantile(0.75) - dados.quantile(0.25):.2f}")
        table.add_row("N", f"{len(dados)}")

        console.print(table)

        # Histograma
        plt.figure(figsize=(10, 6))
        sns.histplot(dados, kde=True)
        plt.title(f"Distribuição de {coluna}")
        plt.xlabel(coluna)
        plt.ylabel("Frequência")
        self._save_plot(plt, f"distribuicao_{coluna}.png")

    def _analise_distribuicao_por_segmento(self, df: pd.DataFrame, coluna: str):
        """Análise de distribuição por segmento"""
        dados_por_segmento = (
            df.groupby("segmento")[coluna]
            .agg(
                [
                    ("Média", "mean"),
                    ("Mediana", "median"),
                    ("Desvio Padrão", "std"),
                    ("Assimetria", "skew"),
                    ("Curtose", lambda x: x.kurtosis()),
                    ("Count", "count"),
                ]
            )
            .round(2)
        )

        console.print(f"\n[bold]📊 Distribuição de {coluna} por Segmento[/bold]")
        console.print(dados_por_segmento)

        # Boxplot por segmento
        plt.figure(figsize=(12, 8))
        sns.boxplot(data=df, x="segmento", y=coluna)
        plt.title(f"Distribuição de {coluna} por Segmento")
        plt.xticks(rotation=45)
        plt.tight_layout()
        self._save_plot(plt, f"boxplot_{coluna}_por_segmento.png")

        # Violin plot para melhor visualização da distribuição
        plt.figure(figsize=(12, 8))
        sns.violinplot(data=df, x="segmento", y=coluna)
        plt.title(f"Distribuição de {coluna} por Segmento (Violin Plot)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        self._save_plot(plt, f"violin_{coluna}_por_segmento.png")

    def detectar_outliers(
        self, coluna: str, metodo: str = "iqr", por_segmento: bool = False
    ):
        """Detecta outliers usando diferentes métodos"""
        df = self.get_dataframe()

        if coluna not in df.columns:
            console.print(f"[red]❌ Coluna '{coluna}' não encontrada[/red]")
            return

        if metodo == "iqr":
            outliers = self._detectar_outliers_iqr(df, coluna, por_segmento)
        elif metodo == "zscore":
            outliers = self._detectar_outliers_zscore(df, coluna, por_segmento)
        else:
            console.print(f"[red]❌ Método '{metodo}' não suportado[/red]")
            return

        # Plot de outliers
        if por_segmento and outliers:
            self._plot_outliers_por_segmento(df, coluna, outliers)
        elif not por_segmento and not outliers.empty:
            self._plot_outliers_geral(df, coluna, outliers)

        return outliers

    def _plot_outliers_geral(
        self, df: pd.DataFrame, coluna: str, outliers: pd.DataFrame
    ):
        """Plot de outliers geral"""
        plt.figure(figsize=(12, 8))
        sns.boxplot(data=df, y=coluna)
        plt.title(f"Outliers em {coluna} (Geral)")
        self._save_plot(plt, f"outliers_{coluna}_geral.png")

    def _plot_outliers_por_segmento(
        self, df: pd.DataFrame, coluna: str, outliers: Dict
    ):
        """Plot de outliers por segmento"""
        plt.figure(figsize=(14, 8))
        sns.boxplot(data=df, x="segmento", y=coluna)
        plt.title(f"Outliers em {coluna} por Segmento")
        plt.xticks(rotation=45)
        plt.tight_layout()
        self._save_plot(plt, f"outliers_{coluna}_por_segmento.png")

    def _detectar_outliers_iqr(
        self, df: pd.DataFrame, coluna: str, por_segmento: bool = False
    ):
        """Detecta outliers usando método IQR"""
        if por_segmento:
            resultados = {}
            for segmento, group in df.groupby("segmento"):
                if len(group) > 1:  # Precisa de pelo menos 2 observações
                    Q1 = group[coluna].quantile(0.25)
                    Q3 = group[coluna].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR

                    segmento_outliers = group[
                        (group[coluna] < lower_bound) | (group[coluna] > upper_bound)
                    ]
                    if not segmento_outliers.empty:
                        resultados[segmento] = segmento_outliers
            return resultados
        else:
            Q1 = df[coluna].quantile(0.25)
            Q3 = df[coluna].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            return df[(df[coluna] < lower_bound) | (df[coluna] > upper_bound)]

    def _detectar_outliers_zscore(
        self, df: pd.DataFrame, coluna: str, por_segmento: bool = False
    ):
        """Detecta outliers usando método Z-Score"""
        if por_segmento:
            resultados = {}
            for segmento, group in df.groupby("segmento"):
                if len(group) > 2:  # Precisa de pelo menos 3 observações para z-score
                    z_scores = np.abs(stats.zscore(group[coluna].dropna()))
                    segmento_outliers = group[z_scores > 3]
                    if not segmento_outliers.empty:
                        resultados[segmento] = segmento_outliers
            return resultados
        else:
            z_scores = np.abs(stats.zscore(df[coluna].dropna()))
            return df[z_scores > 3]

    def analise_correlacao(
        self, variaveis: List[str] = None, por_segmento: bool = False
    ):
        """Análise de correlação entre variáveis"""
        df = self.get_dataframe()

        if variaveis is None:
            variaveis = [
                "patrimonio_liquido",
                "receita_liquida",
                "lucro_liquido",
                "ebitda",
                "roe",
                "roa",
            ]

        variaveis = [v for v in variaveis if v in df.columns]

        if len(variaveis) < 2:
            console.print(
                "[red]❌ É necessário pelo menos 2 variáveis para análise de correlação[/red]"
            )
            return

        if por_segmento:
            self._analise_correlacao_por_segmento(df, variaveis)
        else:
            self._analise_correlacao_geral(df, variaveis)

    def _analise_correlacao_geral(self, df: pd.DataFrame, variaveis: List[str]):
        """Análise de correlação geral"""
        correlacao = df[variaveis].corr()

        console.print("\n[bold]📈 Matriz de Correlação[/bold]")
        console.print(correlacao.round(3))

        # Heatmap
        plt.figure(figsize=(10, 8))
        sns.heatmap(correlacao, annot=True, cmap="coolwarm", center=0, fmt=".3f")
        plt.title("Matriz de Correlação")
        plt.tight_layout()
        self._save_plot(plt, "correlacao_geral.png")

    def _analise_correlacao_por_segmento(self, df: pd.DataFrame, variaveis: List[str]):
        """Análise de correlação por segmento"""
        resultados = {}

        for segmento, group in df.groupby("segmento"):
            if len(group) > 1:  # Precisa de pelo menos 2 observações
                correlacao = group[variaveis].corr()
                resultados[segmento] = correlacao

                # Heatmap por segmento
                plt.figure(figsize=(8, 6))
                sns.heatmap(
                    correlacao, annot=True, cmap="coolwarm", center=0, fmt=".3f"
                )
                plt.title(f"Correlação - {segmento}")
                plt.tight_layout()
                self._save_plot(plt, f"correlacao_{segmento}.png")

        for segmento, correlacao in resultados.items():
            console.print(f"\n[bold]📈 Correlação - {segmento}[/bold]")
            console.print(correlacao.round(3))

    def analise_comparativa_segmentos(self, coluna: str):
        """Análise comparativa entre segmentos"""
        df = self.get_dataframe()

        if coluna not in df.columns:
            console.print(f"[red]❌ Coluna '{coluna}' não encontrada[/red]")
            return

        # Estatísticas descritivas por segmento
        stats_segmentos = (
            df.groupby("segmento")[coluna]
            .agg(
                [
                    ("Média", "mean"),
                    ("Mediana", "median"),
                    ("Desvio Padrão", "std"),
                    ("Mínimo", "min"),
                    ("Máximo", "max"),
                    ("Count", "count"),
                ]
            )
            .round(2)
        )

        console.print(f"\n[bold]📊 Estatísticas de {coluna} por Segmento[/bold]")
        console.print(stats_segmentos)

        # Boxplot comparativo
        plt.figure(figsize=(12, 8))
        sns.boxplot(data=df, x="segmento", y=coluna)
        plt.title(f"Comparação de {coluna} entre Segmentos")
        plt.xticks(rotation=45)
        plt.tight_layout()
        self._save_plot(plt, f"comparacao_{coluna}_segmentos.png")

        # ANOVA entre segmentos
        grupos = [
            group[coluna].values
            for name, group in df.groupby("segmento")
            if len(group) > 1
        ]
        if len(grupos) > 1:
            try:
                f_stat, p_value = stats.f_oneway(*grupos)
                console.print(f"\n[bold]📋 ANOVA - {coluna}[/bold]")
                console.print(f"F-statistic: {f_stat:.4f}")
                console.print(f"p-value: {p_value:.4f}")

                if p_value < 0.05:
                    console.print(
                        "[green]✅ Diferenças significativas entre segmentos (p < 0.05)[/green]"
                    )
                else:
                    console.print(
                        "[yellow]⚠️  Não há diferenças significativas entre segmentos[/yellow]"
                    )
            except Exception as e:
                console.print(f"[red]❌ Erro na ANOVA: {e}[/red]")
