# tcga_tools.py

import requests
import pandas as pd
from io import StringIO
from typing import Dict, Any, Optional
from langchain_core.tools import tool


class TCGA_API:
    BASE_URL = "http://firebrowse.org/api/v1/Samples/mRNASeq"
    
    def __init__(self) -> None:
        self.session = requests.Session()

    def get_gene_specific_expression_in_cancer_type(self, gene: str) -> Dict[str, Any]:
        """
        调用 Firebrowse API，获取指定基因在不同癌种中的 mRNA 表达，并按 cohort 聚合，
        计算均值 / 标准差 / 样本数和 z-score，返回高表达和低表达的癌种列表。
        """
        params: Dict[str, Any] = {
            "format": "tsv",
            "gene": gene,
            "sample_type": "TM,TP,TR",  
            "protocol": "RSEM",
            "page_size": 2000,
            "page": 1,
            "sort_by": "cohort",
        }

        all_data = []

        while True:
            resp = self.session.get(self.BASE_URL, params=params, timeout=60)
            if resp.status_code != 200:
                break

            content = resp.text.strip()
            if not content or content.startswith("No records"):
                break

            if params["page"] == 1:
                df = pd.read_csv(StringIO(content), sep="\t")
                columns = list(df.columns)
            else:
                df = pd.read_csv(StringIO(content), sep="\t", header=None)
                df.columns = columns

            all_data.append(df)
            params["page"] += 1

        if not all_data:
            return {
                "high_expression_cancers": [],
                "low_expression_cancers": [],
            }

        final_df = pd.concat(all_data, ignore_index=True)

        df_grouped = (
            final_df.groupby("cohort")["expression_log2"]
            .agg(["mean", "std", "count"])
            .sort_values("mean", ascending=False)
        )
        df_grouped["zscore"] = (df_grouped["mean"] - df_grouped["mean"].mean()) / df_grouped["mean"].std()

        high_expr = df_grouped[df_grouped["zscore"] > 1].sort_values("mean", ascending=False)
        low_expr = df_grouped[df_grouped["zscore"] < -1].sort_values("mean")

        return {
            "high_expression_cancers": [
                {
                    "cancer_type": idx,
                    "mean_expression": float(round(row["mean"], 3)),
                    "sample_count": int(row["count"]),
                    "zscore": float(round(row["zscore"], 3)),
                }
                for idx, row in high_expr.iterrows()
            ],
            "low_expression_cancers": [
                {
                    "cancer_type": idx,
                    "mean_expression": float(round(row["mean"], 3)),
                    "sample_count": int(row["count"]),
                    "zscore": float(round(row["zscore"], 3)),
                }
                for idx, row in low_expr.iterrows()
            ],
        }


_tcga_api: Optional[TCGA_API] = None


def initialize_tcga_api(config: Optional[Dict[str, Any]] = None) -> None:
    global _tcga_api
    if _tcga_api is None:
        _tcga_api = TCGA_API()


def get_tcga_api() -> TCGA_API:
    global _tcga_api
    if _tcga_api is None:
        _tcga_api = TCGA_API()
    return _tcga_api


@tool(parse_docstring=True)
async def get_gene_specific_expression_in_cancer_type(gene: str) -> Dict[str, Any]:
    """
    Analyze the tissue-specific expression pattern of a given gene across different cancer types
    using the Firebrowse API (TCGA mRNASeq). It computes mean expression per cancer (cohort),
    calculates z-score of mean expression, and returns cancer types where the gene is highly
    or lowly expressed.

    Args:
        gene: Gene symbol, such as "TP53", "BRCA1", "EGFR".

    Returns:
        A dictionary with two keys:
        - high_expression_cancers: List of cancer types where the gene is highly expressed (z > 1)
        - low_expression_cancers: List of cancer types where the gene is lowly expressed (z < -1)
    """
    api = get_tcga_api()
    try:
        result = api.get_gene_specific_expression_in_cancer_type(gene=gene)
    except Exception as e:
        return {"error": f"An error occurred while querying gene expression: {str(e)}"}
    return result


tcga_tools = {
    "get_gene_specific_expression_in_cancer_type": get_gene_specific_expression_in_cancer_type,
}
