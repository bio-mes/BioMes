# string_tools.py

import requests
from typing import List, Dict, Any, Optional, Union
from langchain_core.tools import tool


class StringAPI:
    BASE_URL = "https://version-12-0.string-db.org/api"

    def __init__(self) -> None:
        self.session = requests.Session()

    def _post_json(
        self,
        method: str,
        params: Dict[str, Any],
        output_format: str = "json",
    ) -> Any:
        """
        Internal helper for POST requests that returns parsed JSON.
        """
        request_url = "/".join([self.BASE_URL, output_format, method])
        resp = self.session.post(request_url, data=params, timeout=60)
        resp.raise_for_status()
        # STRING JSON API 返回 list 或 dict，这里直接解析
        return resp.json()

    def mapping_identifiers(
        self,
        identifiers: List[str],
        species: int,
        limit: int = 1,
        echo_query: int = 1,
        output_format: str = "json",
        caller_identity: str = "lglab",
    ) -> Any:
        """Get STRING identifiers for list of genes."""
        method = "get_string_ids"
        params = {
            "identifiers": "\r".join(identifiers),  # your protein list
            "species": species,  # NCBI/STRING taxon identifier
            "limit": limit,  # only top N identifiers per input
            "echo_query": echo_query,  # see your input identifiers in the output
            "caller_identity": caller_identity,  # your app name
        }
        return self._post_json(method, params, output_format=output_format)

    def get_string_network_interaction(
        self,
        identifiers: List[str],
        species: int,
        required_score: int,
        add_nodes: int,
        network_type: str = "functional",
        show_query_node_labels: int = 0,
        output_format: str = "json",
        caller_identity: str = "lglab",
    ) -> Any:
        """Get STRING interaction network for list of proteins."""
        method = "network"
        params = {
            "identifiers": "%0d".join(identifiers),
            "species": species,
            "required_score": required_score,
            "add_nodes": add_nodes,
            "network_type": network_type,
            "show_query_node_labels": show_query_node_labels,
            "caller_identity": caller_identity,
        }
        return self._post_json(method, params, output_format=output_format)

    def get_all_interaction_partners_of_the_protein_set(
        self,
        identifiers: List[str],
        species: int,
        limit: int,
        required_score: int,
        network_type: str = "functional",
        output_format: str = "json",
        caller_identity: str = "lglab",
    ) -> Any:
        """Get interaction partners for a protein set."""
        method = "interaction_partners"
        params = {
            "identifiers": "%0d".join(identifiers),
            "species": species,
            "required_score": required_score,
            "limit": limit,
            "network_type": network_type,
            "caller_identity": caller_identity,
        }
        return self._post_json(method, params, output_format=output_format)

    def get_similarity_scores_of_the_protein_set(
        self,
        identifiers: List[str],
        species: int,
        output_format: str = "json",
        caller_identity: str = "lglab",
    ) -> Any:
        """Get homology (Smith–Waterman bit scores) within a species."""
        method = "homology"
        params = {
            "identifiers": "%0d".join(identifiers),
            "species": species,
            "caller_identity": caller_identity,
        }
        return self._post_json(method, params, output_format=output_format)

    def get_best_similarity_hits_between_species(
        self,
        identifiers: List[str],
        species: int,
        species_b: Union[List[int], List[str], int, str],
        output_format: str = "json",
        caller_identity: str = "lglab",
    ) -> Any:
        """Get best similarity hits between species."""
        method = "homology_best"

        if isinstance(species_b, (list, tuple)):
            species_b_str = "%0d".join(str(x) for x in species_b)
        else:
            species_b_str = str(species_b)

        params = {
            "identifiers": "%0d".join(identifiers),
            "species": species,
            "species_b": species_b_str,
            "caller_identity": caller_identity,
        }
        return self._post_json(method, params, output_format=output_format)

    def get_functional_enrichment(
        self,
        identifiers: List[str],
        background_string_identifiers: str,
        species: int,
        output_format: str = "json",
        caller_identity: str = "lglab",
    ) -> Any:
        """Get functional enrichment for a protein set."""
        method = "enrichment"
        params = {
            "identifiers": "%0d".join(identifiers),
            "species": species,
            "background_string_identifiers": background_string_identifiers,
            "caller_identity": caller_identity,
        }
        return self._post_json(method, params, output_format=output_format)

    def get_functional_annotation(
        self,
        identifiers: List[str],
        species: int,
        allow_pubmed: int = 0,
        only_pubmed: int = 0,
        output_format: str = "json",
        caller_identity: str = "lglab",
    ) -> Any:
        """Get functional annotation (GO, pathways, domains, PubMed, etc.)."""
        method = "functional_annotation"
        params = {
            "identifiers": "%0d".join(identifiers),
            "species": species,
            "allow_pubmed": allow_pubmed,
            "only_pubmed": only_pubmed,
            "caller_identity": caller_identity,
        }
        return self._post_json(method, params, output_format=output_format)

    def get_ppi_enrichment(
        self,
        identifiers: List[str],
        species: int,
        output_format: str = "json",
        caller_identity: str = "lglab",
        **kwargs: Any,
    ) -> Any:
        """Get PPI enrichment for a protein set."""
        method = "ppi_enrichment"
        params = {
            "identifiers": "%0d".join(identifiers),
            "species": species,
            "caller_identity": caller_identity,
        }
        return self._post_json(method, params, output_format=output_format)


# 全局实例（多用户共享，无 per-user 状态）
_string_api: Optional[StringAPI] = None


def initialize_string_api(config: Optional[Dict[str, Any]] = None) -> None:
    """
    初始化 StringAPI。config 当前不用，仅为了和其他工具保持统一接口。
    在你的 initialize_tools(config) 里调用一次即可。
    """
    global _string_api
    if _string_api is None:
        _string_api = StringAPI()


def get_string_api() -> StringAPI:
    """内部辅助函数，确保 _string_api 已初始化。"""
    global _string_api
    if _string_api is None:
        _string_api = StringAPI()
    return _string_api


# ========= LangChain 工具封装部分 =========

@tool(parse_docstring=True)
async def mapping_identifiers(genes: List[str], species: int) -> Any:
    """
    Map common protein names, synonyms and UniProt identifiers into STRING identifiers.
    
    Args:
        genes: A list of gene / protein names, required.
        species: NCBI/STRING taxon ID (e.g. 9606 for human).
    
    Returns:
        A list of records containing STRING identifiers and mappings for the input genes.
    """
    api = get_string_api()
    try:
        return api.mapping_identifiers(identifiers=genes, species=species)
    except Exception as e:
        return {"error": f"An error occurred while mapping identifiers: {str(e)}"}


@tool(parse_docstring=True)
async def get_string_network_interaction(
    identifiers: List[str],
    species: int,
    required_score: int,
    add_nodes: int,
    network_type: str = "functional",
    show_query_node_labels: int = 0,
) -> Any:
    """
    Retrieve STRING interaction network for one or multiple proteins.
    It returns combined scores and channel-specific scores for interactions,
    and can extend the network neighborhood by adding high-confidence partners.
    
    Args:
        identifiers: List of input identifiers (gene/protein names or STRING IDs).
        species: NCBI/STRING taxon ID (e.g. 9606 for human).
        required_score: Minimum combined score (0–1000).
        add_nodes: Number of additional nodes to add to the network.
        network_type: "functional" (default) or "physical".
        show_query_node_labels: 1 to label query nodes, 0 otherwise.
    
    Returns:
        A list of interactions with fields such as:
        stringId_A, stringId_B, preferredName_A, preferredName_B,
        ncbiTaxonId, score, nscore, fscore, pscore, ascore, escore, dscore, tscore.
    """
    api = get_string_api()
    try:
        return api.get_string_network_interaction(
            identifiers=identifiers,
            species=species,
            required_score=required_score,
            add_nodes=add_nodes,
            network_type=network_type,
            show_query_node_labels=show_query_node_labels,
        )
    except Exception as e:
        return {
            "error": f"An error occurred while getting STRING network interaction: {str(e)}"
        }


@tool(parse_docstring=True)
async def get_all_interaction_partners_of_the_protein_set(
    identifiers: List[str],
    species: int,
    limit: int,
    required_score: int,
    network_type: str = "functional",
) -> Any:
    """
    Get interactions between your protein set and all other STRING proteins.
    Limits the number of interaction partners per protein with "limit".
    
    Args:
        identifiers: List of proteins (names or STRING IDs).
        species: NCBI/STRING taxon ID.
        limit: Maximum number of partners per protein (most confident first).
        required_score: Score threshold (0–1000).
        network_type: "functional" (default) or "physical".
    
    Returns:
        A list of interaction records similar to network calls.
    """
    api = get_string_api()
    try:
        return api.get_all_interaction_partners_of_the_protein_set(
            identifiers=identifiers,
            species=species,
            limit=limit,
            required_score=required_score,
            network_type=network_type,
        )
    except Exception as e:
        return {
            "error": f"An error occurred while getting interaction partners: {str(e)}"
        }


@tool(parse_docstring=True)
async def get_similarity_scores_of_the_protein_set(
    identifiers: List[str],
    species: int,
) -> Any:
    """
    Get Smith–Waterman bit scores (homology) between proteins in a species.
    Scores are symmetric (A–B = B–A), values below 50 are not stored.
    
    Args:
        identifiers: List of proteins (names or STRING IDs).
        species: NCBI/STRING taxon ID.
    
    Returns:
        A list of records with fields:
        ncbiTaxonId_A, stringId_A, ncbiTaxonId_B, stringId_B, bitscore.
    """
    api = get_string_api()
    try:
        return api.get_similarity_scores_of_the_protein_set(
            identifiers=identifiers,
            species=species,
        )
    except Exception as e:
        return {
            "error": f"An error occurred while getting similarity scores: {str(e)}"
        }


@tool(parse_docstring=True)
async def get_best_similarity_hits_between_species(
    identifiers: List[str],
    species: int,
    species_b: List[int],
) -> Any:
    """
    Retrieve the best (most similar) protein hits from target species for each input protein.
    
    Args:
        identifiers: List of proteins (names or STRING IDs) in the source species.
        species: Source NCBI/STRING taxon ID.
        species_b: List of target NCBI taxon IDs (e.g. [9606, 10090, 4932]).
    
    Returns:
        A list of records with fields:
        ncbiTaxonId_A, stringId_A, ncbiTaxonId_B, stringId_B, bitscore.
    """
    api = get_string_api()
    try:
        return api.get_best_similarity_hits_between_species(
            identifiers=identifiers,
            species=species,
            species_b=species_b,
        )
    except Exception as e:
        return {
            "error": f"An error occurred while getting best similarity hits: {str(e)}"
        }


@tool(parse_docstring=True)
async def get_functional_enrichment(
    identifiers: List[str],
    species: int,
    background_string_identifiers: str,
) -> Any:
    """
    Get functional enrichment for a set of proteins (GO, KEGG, domains, etc.).
    
    Args:
        identifiers: List of proteins (STRING IDs recommended for stable mapping).
        species: NCBI/STRING taxon ID.
        background_string_identifiers: Background proteome as STRING IDs separated by '%0d'.
    
    Returns:
        A list of enriched terms with fields such as:
        category, term, number_of_genes, number_of_genes_in_background,
        ncbiTaxonId, inputGenes, preferredNames, p_value, fdr, description.
    """
    api = get_string_api()
    try:
        return api.get_functional_enrichment(
            identifiers=identifiers,
            species=species,
            background_string_identifiers=background_string_identifiers,
        )
    except Exception as e:
        return {
            "error": f"An error occurred while getting functional enrichment: {str(e)}"
        }


@tool(parse_docstring=True)
async def get_functional_annotation(
    identifiers: List[str],
    species: int,
    allow_pubmed: int = 0,
    only_pubmed: int = 0,
) -> Any:
    """
    Get functional annotation (GO, pathways, domains, keywords, PubMed) for a protein set.
    
    Args:
        identifiers: List of proteins.
        species: NCBI/STRING taxon ID.
        allow_pubmed: 1 to include PubMed annotations, 0 to exclude.
        only_pubmed: 1 to return only PubMed annotations.
    
    Returns:
        A list of annotation records with fields such as:
        category, term, number_of_genes, ratio_in_set, ncbiTaxonId,
        inputGenes, preferredNames, description.
    """
    api = get_string_api()
    try:
        return api.get_functional_annotation(
            identifiers=identifiers,
            species=species,
            allow_pubmed=allow_pubmed,
            only_pubmed=only_pubmed,
        )
    except Exception as e:
        return {
            "error": f"An error occurred while getting functional annotation: {str(e)}"
        }


@tool(parse_docstring=True)
async def get_ppi_enrichment(
    identifiers: List[str],
    species: int,
) -> Any:
    """
    Get protein–protein interaction enrichment for a set of STRING identifiers.
    
    Args:
        identifiers: List of STRING protein identifiers.
        species: NCBI/STRING taxon ID.
    
    Returns:
        A record with fields such as:
        number_of_nodes, number_of_edges, average_node_degree,
        local_clustering_coefficient, expected_number_of_edges, p_value.
    """
    api = get_string_api()
    try:
        return api.get_ppi_enrichment(
            identifiers=identifiers,
            species=species,
        )
    except Exception as e:
        return {
            "error": f"An error occurred while getting PPI enrichment: {str(e)}"
        }


string_tools = {
    "mapping_identifiers": mapping_identifiers,
    "get_string_network_interaction": get_string_network_interaction,
    "get_all_interaction_partners_of_the_protein_set": get_all_interaction_partners_of_the_protein_set,
    "get_similarity_scores_of_the_protein_set": get_similarity_scores_of_the_protein_set,
    "get_best_similarity_hits_between_species": get_best_similarity_hits_between_species,
    "get_functional_enrichment": get_functional_enrichment,
    "get_functional_annotation": get_functional_annotation,
    "get_ppi_enrichment": get_ppi_enrichment,
}
