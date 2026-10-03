# pubchem_tools.py

import json
import re
import time
import urllib.parse
from typing import Dict, Optional, Union, Any, List

import requests
import pubchempy as pcp
from langchain_core.tools import tool



def extract_description(response: Dict[str, Any]) -> Dict[str, Any]:

    related_sections = [
        "Names and Identifiers",
        "Drug and Medication Information",
        "Pharmacology and Biochemistry",
    ]

    def get_summary(section_data: Dict[str, Any]) -> Dict[str, Any]:
        summary_info: Dict[str, Any] = {"Others": []}
        try:
            data = section_data["Section"][0]["Information"]
        except Exception:
            return summary_info

        for each in data:
            try:
                value = each["Value"]["StringWithMarkup"][0]["String"]
            except Exception:
                continue

            if "Description" not in each:
                desc = "Others"
                summary_info.setdefault(desc, []).append(value)
            else:
                desc = each["Description"]
                summary_info[desc] = value
        return summary_info

    extracted_result: Dict[str, Any] = {}
    for data in response["Record"]["Section"]:
        if data.get("TOCHeading") in related_sections:
            extracted_result[data["TOCHeading"]] = get_summary(data)
    return extracted_result


class PubChemAPI:
    """PubChem API client for accessing chemical data from PubChem database."""

    BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
    VIEW_BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view"

    def __init__(self, delay: float = 0.2) -> None:

        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "PubChemPythonClient/1.0 (Python client for PubChem API)"}
        )
        self.delay = delay

    def _make_request(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict:

        time.sleep(self.delay)

        try:
            response = self.session.get(url, params=params, timeout=60)
            response.raise_for_status()

            if response.headers.get("Content-Type", "").startswith("application/json"):
                return response.json()
            else:
                return {"data": response.text}

        except requests.exceptions.RequestException as e:
            if hasattr(e, "response") and getattr(e.response, "text", None):
                error_info = f": {e.response.text}"
            else:
                error_info = ""
            raise requests.exceptions.RequestException(
                f"API request failed: {str(e)}{error_info}"
            )
        except ValueError as e:
            raise ValueError(f"Failed to parse API response as JSON: {str(e)}")

    def poll_pubchem_request(
        self, list_key: str, max_wait_time: int = 60, poll_interval: int = 2
    ) -> Dict:
        """
        Poll PubChem API for the status of an asynchronous request and retrieve results.
        """
        status_url = f"{self.BASE_URL}/compound/listkey/{list_key}/JSON"
        start_time = time.time()

        while time.time() - start_time < max_wait_time:
            try:
                response = requests.get(status_url, timeout=30)
                response.raise_for_status()
                status_response = response.json()

                if "Waiting" not in status_response:
                    results_url = (
                        f"{self.BASE_URL}/compound/listkey/{list_key}/cids/JSON"
                    )
                    result_response = requests.get(results_url, timeout=30)
                    result_response.raise_for_status()
                    return result_response.json()

                time.sleep(poll_interval)
            except requests.exceptions.RequestException as e:
                raise Exception(f"API request failed: {e}")

        raise TimeoutError("Request did not complete within the maximum wait time")


    def search_pubchem_by_name(self, name: str, **kwargs: Any) -> Dict:
        url = f"{self.BASE_URL}/compound/name/{urllib.parse.quote(name)}/JSON"
        return self._make_request(url, kwargs)

    def search_pubchem_by_smiles(self, smiles: str, **kwargs: Any) -> Dict:
        url = f"{self.BASE_URL}/compound/smiles/{urllib.parse.quote(smiles)}/JSON"
        return self._make_request(url, kwargs)

    def get_pubchem_compound_by_cid(self, cid: Union[int, str], **kwargs: Any) -> Dict:
        url = f"{self.BASE_URL}/compound/cid/{cid}/JSON"
        return self._make_request(url, kwargs)

    def search_pubchem_advanced(self, query: str, **kwargs: Any) -> Dict:
        encoded_query = urllib.parse.quote(query)
        url = f"{self.BASE_URL}/compound/fastformula/{encoded_query}/JSON"
        return self._make_request(url, kwargs)

    def get_substance_by_sid_rest(self, sid: Union[int, str], **kwargs: Any) -> Dict:
        url = f"{self.BASE_URL}/substance/sid/{sid}/JSON"
        return self._make_request(url, kwargs)

    def get_compound_by_cid(self, cid: Union[int, str], **kwargs: Any) -> Dict:
        return self.get_pubchem_compound_by_cid(cid, **kwargs)

    def get_compound_by_name(self, name: str, **kwargs: Any) -> Dict:
        search_results = self.search_pubchem_by_name(name, **kwargs)

        if "PC_Compounds" in search_results and search_results["PC_Compounds"]:
            cid = search_results["PC_Compounds"][0]["id"]["id"]["cid"]
            return self.get_compound_by_cid(cid, **kwargs)
        else:
            return {"error": f"No compound found with name: {name}"}

    def get_substance_by_name(self, name: str, **kwargs: Any) -> Dict:
        url = f"{self.BASE_URL}/substance/name/{urllib.parse.quote(name)}/JSON"
        return self._make_request(url, kwargs)

    def search_compound_by_substructure(self, smiles: str, **kwargs: Any) -> Dict:
        url = f"{self.BASE_URL}/compound/substructure/smiles/{urllib.parse.quote(smiles)}/JSON"
        response = self._make_request(url, kwargs)
        if "Waiting" in response and "ListKey" in response["Waiting"]:
            list_key = response["Waiting"]["ListKey"]
            return self.poll_pubchem_request(list_key)
        return response

    def search_compound_by_similarity(
        self, smiles: str, similarity: float = 95, **kwargs: Any
    ) -> Dict:
        url = f"{self.BASE_URL}/compound/similarity/smiles/{urllib.parse.quote(smiles)}/JSON"
        params = {"Threshold": similarity, **kwargs}
        response = self._make_request(url, params)
        if "Waiting" in response and "ListKey" in response["Waiting"]:
            list_key = response["Waiting"]["ListKey"]
            return self.poll_pubchem_request(list_key)
        return response

    def search_compound_by_identity(self, smiles: str, **kwargs: Any) -> Dict:
        url = f"{self.BASE_URL}/compound/identity/smiles/{urllib.parse.quote(smiles)}/JSON"
        response = self._make_request(url, kwargs)
        if "Waiting" in response and "ListKey" in response["Waiting"]:
            list_key = response["Waiting"]["ListKey"]
            return self.poll_pubchem_request(list_key)
        return response

    def search_compound_by_superstructure(self, smiles: str, **kwargs: Any) -> Dict:
        url = f"{self.BASE_URL}/compound/superstructure/smiles/{urllib.parse.quote(smiles)}/JSON"
        response = self._make_request(url, kwargs)
        if "Waiting" in response and "ListKey" in response["Waiting"]:
            list_key = response["Waiting"]["ListKey"]
            return self.poll_pubchem_request(list_key)
        return response


    def get_compound_property_by_name(
        self, name: str, property_name: str, **kwargs: Any
    ) -> Dict:
        url = f"{self.BASE_URL}/compound/name/{urllib.parse.quote(name)}/property/{property_name}/JSON"
        return self._make_request(url, kwargs)

    def get_compound_synonyms_by_name(self, name: str, **kwargs: Any) -> Dict:
        url = f"{self.BASE_URL}/compound/name/{urllib.parse.quote(name)}/synonyms/JSON"
        return self._make_request(url, kwargs)


    def get_description_by_sid(self, sid: Union[int, str], **kwargs: Any) -> Dict:
        url = f"{self.VIEW_BASE_URL}/data/substance/{sid}/JSON"
        return self._make_request(url, kwargs)

    def get_description_by_cid(self, cid: Union[int, str], **kwargs: Any) -> Dict:
        url = f"{self.VIEW_BASE_URL}/data/compound/{cid}/JSON"
        return self._make_request(url, kwargs)

    def get_description_by_name(self, name: str, **kwargs: Any) -> Dict:
        result = self.search_pubchem_by_name(name, **kwargs)
        cid = result["PC_Compounds"][0]["id"]["id"]["cid"]

        smiles = None
        for prop in result["PC_Compounds"][0].get("props", []):
            if prop.get("urn", {}).get("label") == "SMILES":
                smiles = prop["value"]["sval"]
                break

        all_desc_info = self.get_description_by_cid(cid, **kwargs)

        try:
            desc_info = extract_description(all_desc_info)
        except Exception as e:
            print(f"Error extracting description: {e}")
            desc_info = {"description": "No description found for the compound"}
        desc_info["SMILES"] = smiles
        return desc_info

    def get_description_by_aid(self, aid: Union[int, str], **kwargs: Any) -> Dict:
        url = f"{self.VIEW_BASE_URL}/data/assay/{aid}/JSON"
        return self._make_request(url, kwargs)

    def get_assay_summary_by_cid(self, cid: Union[int, str], **kwargs: Any) -> Dict:
        url = f"{self.BASE_URL}/compound/cid/{cid}/assaysummary/JSON"
        return self._make_request(url, kwargs)

    def get_assay_summary_by_sid(self, sid: Union[int, str], **kwargs: Any) -> Dict:
        url = f"{self.BASE_URL}/substance/sid/{sid}/assaysummary/JSON"
        return self._make_request(url, kwargs)

    def get_gene_summary_by_geneid(
        self, gene_id: Union[int, str], **kwargs: Any
    ) -> Dict:
        url = f"{self.BASE_URL}/gene/geneid/{gene_id}/summary/JSON"
        return self._make_request(url, kwargs)

    def get_protein_summary_by_accession(
        self, accession: str, **kwargs: Any
    ) -> Dict:
        url = f"{self.BASE_URL}/protein/accession/{accession}/summary/JSON"
        return self._make_request(url, kwargs)

    def get_taxonomy_summary_by_taxonomyid(
        self, taxonomy_id: Union[int, str], **kwargs: Any
    ) -> Dict:
        url = f"{self.BASE_URL}/taxonomy/taxid/{taxonomy_id}/summary/JSON"
        return self._make_request(url, kwargs)

    def get_conformers_by_cid(self, cid: Union[int, str], **kwargs: Any) -> Dict:
        url = f"{self.BASE_URL}/compound/cid/{cid}/conformers/JSON"
        return self._make_request(url, kwargs)


    def get_compounds_by_smiles(self, smiles: str):
        return pcp.get_compounds(smiles, "smiles")

    def get_compounds_by_formula(self, formula: str):
        return pcp.get_compounds(formula, "formula")

    def get_molecular_formula(self, compound: pcp.Compound) -> str:
        return compound.molecular_formula

    def get_molecular_weight(self, compound: pcp.Compound) -> float:
        return compound.molecular_weight

    def get_isomeric_smiles(self, compound: pcp.Compound) -> str:
        return compound.isomeric_smiles

    def get_xlogp(self, compound: pcp.Compound) -> float:
        return compound.xlogp

    def get_iupac_name(self, compound: pcp.Compound) -> str:
        return compound.iupac_name

    def get_synonyms(self, compound: pcp.Compound) -> List[str]:
        return compound.synonyms

    def get_cids_by_smiles(self, smiles: str) -> List[int]:
        return pcp.get_cids(smiles, "smiles")

    def get_cids_by_formula(self, formula: str) -> List[int]:
        return pcp.get_cids(formula, "formula")

    def get_sids_by_name(self, name: str) -> List[int]:
        return pcp.get_sids(name, "name")

    def get_substance_by_sid_pcp(self, sid: Union[int, str]):
        return pcp.Substance.from_sid(sid)

    def get_substances_by_name(self, name: str):
        return pcp.get_substances(name, "name")

    def get_substances_source_id(self, sid: Union[int, str]) -> Any:
        substance = pcp.Substance.from_sid(sid)
        return substance.source_id

    def get_substances_synonyms(self, sid: Union[int, str]) -> List[str]:
        substance = pcp.Substance.from_sid(sid)
        return substance.synonyms

    def download_structure_image_png(
        self, filename: str, query: str, query_type: str = "name"
    ) -> None:
        pcp.download("PNG", filename, query, query_type, overwrite=True)

    def download_properties_csv(
        self, filename: str, ids: Any, properties: List[str]
    ) -> None:
        pcp.download(
            "CSV",
            filename,
            ids,
            operation=f"property/{','.join(properties)}",
            overwrite=True,
        )

    def get_compound_dict(
        self, compound: pcp.Compound, properties: List[str]
    ) -> Dict[str, Any]:
        return compound.to_dict(properties=properties)

    def get_compounds_3d(self, name: str):
        return pcp.get_compounds(name, "name", record_type="3d")

    def get_compounds_dict(self, compound_cid: Union[int, str]) -> Dict[str, Any]:
        c = pcp.Compound.from_cid(compound_cid)
        return c.to_dict()

    def get_substructure_cas(self, smiles: str) -> List[str]:
        cas_rns: List[str] = []
        results = pcp.get_synonyms(smiles, "smiles", searchtype="substructure")
        for result in results:
            for syn in result.get("Synonym", []):
                match = re.match(r"(\d{2,7}-\d\d-\d)", syn)
                if match:
                    cas_rns.append(match.group(1))
        return cas_rns



_pubchem_api: Optional[PubChemAPI] = None


def initialize_pubchem_api(config: Optional[Dict[str, Any]] = None) -> None:

    global _pubchem_api
    delay = (config or {}).get("pubchem_delay", 0.2)
    _pubchem_api = PubChemAPI(delay=delay)


def get_pubchem_api() -> PubChemAPI:
    global _pubchem_api
    if _pubchem_api is None:
        _pubchem_api = PubChemAPI()
    return _pubchem_api



# pubchem_tools.py

from typing import Any, Dict, List, Optional

from langchain_core.tools import tool


_pubchem_api: Optional[PubChemAPI] = None


def initialize_pubchem(config: Optional[Dict[str, Any]] = None) -> None:
    """
    Initialize the global PubChemAPI client.
    """
    global _pubchem_api
    if _pubchem_api is None:
        _pubchem_api = PubChemAPI()


def get_pubchem_api() -> PubChemAPI:
    """
    Get the global PubChemAPI client, creating it if needed.
    """
    global _pubchem_api
    if _pubchem_api is None:
        _pubchem_api = PubChemAPI()
    return _pubchem_api


def pubchem_system_prompt() -> str:
    """
    System prompt string for PubChem tools.
    """
    return (
        "You have access to tools for searching and retrieving chemical information "
        "from PubChem, which is a database of chemical molecules and their activities "
        "against biological assays. PubChem is maintained by the National Center for "
        "Biotechnology Information (NCBI), a component of the National Library of "
        "Medicine (NLM), which is part of the United States National Institutes of "
        "Health (NIH).\n\n"
        "You can search for compounds by name, SMILES notation, molecular weight, or "
        "structural features. You can retrieve detailed information about compounds, "
        "including their properties, synonyms, and descriptions.\n\n"
        "Use the API tools to extract relevant chemical information for the user's "
        "queries. When the user asks about a chemical or drug, try to provide "
        "comprehensive information including:\n"
        "- Basic identifiers such as CID and molecular formula\n"
        "- Physical properties such as molecular weight\n"
        "- Common names and synonyms\n"
        "- Chemical structure information when available\n"
        "- Biological activities when relevant\n\n"
        "Fill in missing arguments with sensible values if the user has not provided them."
    )


@tool(parse_docstring=True)
async def search_pubchem_by_name(name: str) -> Any:
    """
    Search PubChem for compounds matching a chemical name.

    Be aware that matching chemical names to structure is an inexact process and a name
    may refer to more than one record.

    Args:
        name: Chemical name

    Query example:
        {"name": "aspirin", "kwargs": "{}"}

    Returns:
        Dictionary containing search results for compounds that match the name
    """
    api = get_pubchem_api()
    try:
        result = api.search_pubchem_by_name(name)
    except Exception as e:
        return {"error": f"An error occurred while searching PubChem by name: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def search_pubchem_by_smiles(smiles: str) -> Any:
    """
    Search PubChem for compounds matching a SMILES string.

    Args:
        smiles: SMILES notation to search for

    Returns:
        Dictionary containing search results with compounds that match the SMILES

    Query example:
        {"smiles": "C[C@H](N)C(=O)O"}
    """
    api = get_pubchem_api()
    try:
        result = api.search_pubchem_by_smiles(smiles)
    except Exception as e:
        return {"error": f"An error occurred while searching PubChem by SMILES: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_pubchem_compound_by_cid(cid: str) -> Any:
    """
    Get detailed compound information by PubChem CID.

    Args:
        cid: PubChem compound ID as integer or string

    Returns:
        Dictionary containing detailed information about the compound such as
        chemical properties, structural information, and relevant biological activities

    Query example:
        {"cid": 2244}
    """
    api = get_pubchem_api()
    try:
        result = api.get_pubchem_compound_by_cid(cid)
    except Exception as e:
        return {"error": f"An error occurred while getting PubChem compound by CID: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def search_pubchem_advanced(query: str) -> Any:
    """
    Perform an advanced search on PubChem using a complex query string.

    Args:
        query: Advanced search query string that follows PubChem syntax

    Returns:
        Dictionary containing search results that match the advanced query
    """
    api = get_pubchem_api()
    try:
        result = api.search_pubchem_advanced(query)
    except Exception as e:
        return {"error": f"An error occurred during advanced PubChem search: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_substance_by_sid(sid: str) -> Any:
    """
    Get substance information by PubChem SID.

    Args:
        sid: PubChem substance ID

    Returns:
        Dictionary containing information about the substance such as identifiers
        and basic description

    Query example:
        {"sid": 347827035}
    """
    api = get_pubchem_api()
    try:
        result = api.get_substance_by_sid(sid)
    except Exception as e:
        return {"error": f"An error occurred while getting substance by SID: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_compound_by_cid(cid: str) -> Any:
    """
    Get compound information by PubChem CID.

    Args:
        cid: PubChem compound ID

    Returns:
        Dictionary containing information about the compound
    """
    api = get_pubchem_api()
    try:
        result = api.get_compound_by_cid(cid)
    except Exception as e:
        return {"error": f"An error occurred while getting compound by CID: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_compound_by_name(name: str) -> Any:
    """
    Get compound information by chemical name.

    Be aware that matching chemical names to a structure is an inexact process and
    a name may refer to more than one record.

    Args:
        name: Chemical name

    Returns:
        Dictionary containing information about the compound such as CID, structure,
        and basic properties

    Query example:
        {"name": "aspirin"}
    """
    api = get_pubchem_api()
    try:
        result = api.get_compound_by_name(name)
    except Exception as e:
        return {"error": f"An error occurred while getting compound by name: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_substance_by_name(name: str) -> Any:
    """
    Get substance information by name.

    Args:
        name: Substance name

    Returns:
        Dictionary containing information about the substance

    Query example:
        {"name": "aspirin"}
    """
    api = get_pubchem_api()
    try:
        result = api.get_substance_by_name(name)
    except Exception as e:
        return {"error": f"An error occurred while getting substance by name: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_compound_property_by_name(name: str, property_name: str) -> Any:
    """
    Retrieve a specific chemical property for a compound by its name from PubChem.

    The response returns a table containing the requested property for the matching
    compound.

    Args:
        name: Chemical name of the compound
        property_name: Name of the property to retrieve such as MolecularWeight, MolecularFormula, XLogP, TPSA

    Returns:
        Dictionary containing a PropertyTable with a list of property entries.
        Each entry has CID and the requested property value.

    Query example:
        {"name": "caffeine", "property_name": "MolecularFormula"}
    """
    api = get_pubchem_api()
    try:
        result = api.get_compound_property_by_name(name, property_name)
    except Exception as e:
        return {"error": f"An error occurred while getting compound property by name: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_compound_synonyms_by_name(name: str) -> Any:
    """
    Retrieve all known synonyms for a compound by its chemical name from PubChem.

    The response returns a list of synonyms including registry numbers, alternate names,
    trade names, database identifiers, and systematic names.

    Args:
        name: Chemical name of the compound

    Returns:
        Dictionary containing an InformationList with entries for each matching compound.
        Each entry includes CID and a list of synonym strings.

    Query example:
        {"name": "caffeine"}
    """
    api = get_pubchem_api()
    try:
        result = api.get_compound_synonyms_by_name(name)
    except Exception as e:
        return {"error": f"An error occurred while getting compound synonyms by name: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_description_by_sid(sid: str) -> Any:
    """
    Get detailed description information for a PubChem substance given its SID.

    The response includes the full Record structure with sections such as
    2D structure, identity, source, external identifiers, synonyms, status, and
    related compounds.

    Args:
        sid: PubChem substance ID as integer or string

    Returns:
        Dictionary containing the full Record for the substance with fields such
        as RecordType, RecordNumber, RecordTitle, Section, and Reference

    Query example:
        {"sid": "12345"}
    """
    api = get_pubchem_api()
    try:
        result = api.get_description_by_sid(sid)
    except Exception as e:
        return {"error": f"An error occurred while getting description by SID: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_description_by_cid(cid: str) -> Any:
    """
    Retrieve detailed description information for a PubChem compound given its CID.

    The response returns the full Record structure with sections such as structures,
    identity, dates, status, and related records.

    Args:
        cid: PubChem compound ID as integer or string

    Returns:
        Dictionary containing the full Record for the compound with fields such as
        RecordType, RecordNumber, RecordTitle, Section, and Reference

    Query example:
        {"cid": "2244"}
    """
    api = get_pubchem_api()
    try:
        result = api.get_description_by_cid(cid)
    except Exception as e:
        return {"error": f"An error occurred while getting description by CID: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_general_info_by_compound_name(name: str) -> Any:
    """
    Get detailed description of a compound by name.

    The description includes overall information, drug or medication information,
    and pharmacology or biochemistry information.

    Args:
        name: PubChem compound name

    Returns:
        Dictionary containing description of the compound
    """
    api = get_pubchem_api()
    try:
        result = api.get_description_by_name(name)
    except Exception as e:
        return {"error": f"An error occurred while getting description by name: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_description_by_aid(aid: str) -> Any:
    """
    Retrieve detailed description information for a PubChem bioassay given its AID.

    The response returns the full Record structure including sections such as
    record description, bioassay overview, protocol, comments, result definitions,
    data table, targets, related targets, and assay annotations.

    Args:
        aid: PubChem assay ID as integer or string

    Returns:
        Dictionary containing the full Record for the assay with fields such as
        RecordType, RecordNumber, RecordTitle, Section, and Reference

    Query example:
        {"aid": "450"}
    """
    api = get_pubchem_api()
    try:
        result = api.get_description_by_aid(aid)
    except Exception as e:
        return {"error": f"An error occurred while getting description by AID: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_assay_summary_by_cid(cid: str) -> Any:
    """
    Retrieve a summary of bioassay activities for a PubChem compound CID.

    The response includes a table of assays where the compound has been tested,
    with information about activity outcome, targets, assay metadata, and references.

    Args:
        cid: PubChem compound ID as integer or string

    Returns:
        Dictionary containing an assay summary table under a Table key with
        columns such as AID, SID, CID, activity outcome, target gene, activity value,
        assay name, assay type, PubMed ID, and RNAi annotation

    Query example:
        {"cid": "2144"}
    """
    api = get_pubchem_api()
    try:
        result = api.get_assay_summary_by_cid(cid)
    except Exception as e:
        return {"error": f"An error occurred while getting assay summary by CID: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_assay_summary_by_sid(sid: str) -> Any:
    """
    Retrieve a summary of bioassay activities for a PubChem substance SID.

    The response includes a table that lists assays in which the substance was tested,
    with activity outcome, targets, assay metadata, and references.

    Args:
        sid: PubChem substance ID as integer or string

    Returns:
        Dictionary containing an assay summary table under a Table key with
        columns such as AID, SID, CID, activity outcome, target gene, activity value,
        assay name, assay type, PubMed ID, and RNAi annotation

    Query example:
        {"sid": "8149208"}
    """
    api = get_pubchem_api()
    try:
        result = api.get_assay_summary_by_sid(sid)
    except Exception as e:
        return {"error": f"An error occurred while getting assay summary by SID: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_gene_summary_by_geneid(gene_id: str) -> Any:
    """
    Get summary information for a gene by gene ID using PubChem linked data.

    Args:
        gene_id: Gene ID

    Returns:
        Dictionary containing summary information for the gene
    """
    api = get_pubchem_api()
    try:
        result = api.get_gene_summary_by_geneid(gene_id)
    except Exception as e:
        return {"error": f"An error occurred while getting gene summary by gene ID: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_protein_summary_by_accession(accession: str) -> Any:
    """
    Retrieve summary information for a protein from PubChem by its accession number.

    The response includes basic annotations such as the protein name, taxonomy,
    and known synonyms.

    Args:
        accession: Protein accession number such as UniProt ID or NCBI accession

    Returns:
        Dictionary containing a ProteinSummaries section with entries that include
        accession, name, taxonomy, and synonyms

    Query example:
        {"accession": "P00734"}
    """
    api = get_pubchem_api()
    try:
        result = api.get_protein_summary_by_accession(accession)
    except Exception as e:
        return {"error": f"An error occurred while getting protein summary by accession: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_taxonomy_summary_by_taxonomyid(taxonomy_id: str) -> Any:
    """
    Retrieve summary information for a taxonomy entry given an NCBI taxonomy ID.

    The response includes scientific and common names, rank, lineage, and synonyms.

    Args:
        taxonomy_id: NCBI taxonomy ID as integer or string

    Returns:
        Dictionary containing a TaxonomySummaries section with entries that include
        taxonomy ID, scientific name, common name, rank, ranked lineage, and synonyms

    Query example:
        {"taxonomy_id": "9606"}
    """
    api = get_pubchem_api()
    try:
        result = api.get_taxonomy_summary_by_taxonomyid(taxonomy_id)
    except Exception as e:
        return {"error": f"An error occurred while getting taxonomy summary by taxonomy ID: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_conformers_by_cid(cid: str) -> Any:
    """
    Retrieve available conformer identifiers for a PubChem compound CID.

    Conformers represent different 3D geometries computed or provided for the compound.

    Args:
        cid: PubChem compound ID as integer or string

    Returns:
        Dictionary containing an InformationList with entries that include CID and
        a list of conformer identifiers

    Query example:
        {"cid": "2244"}
    """
    api = get_pubchem_api()
    try:
        result = api.get_conformers_by_cid(cid)
    except Exception as e:
        return {"error": f"An error occurred while getting conformers by CID: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_compounds_by_smiles(smiles: str) -> Any:
    """
    Retrieve compound objects from PubChem based on a SMILES string.

    Each returned object represents a matching compound entry.

    Args:
        smiles: SMILES string of the query structure such as "CCO" for ethanol

    Returns:
        List of compound objects matching the SMILES query. An entry like
        "Compound(702)" indicates the PubChem compound with CID 702.

    Query example:
        {"smiles": "CCO"}
    """
    api = get_pubchem_api()
    try:
        result = api.get_compounds_by_smiles(smiles)
    except Exception as e:
        return {"error": f"An error occurred while getting compounds by SMILES: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_compounds_by_formula(formula: str) -> Any:
    """
    Retrieve compound objects from PubChem based on a molecular formula.

    Args:
        formula: Molecular formula string such as "C2H6O"

    Returns:
        List of compound objects matching the formula. Each entry is represented
        as "Compound(<CID>)" where CID is the PubChem compound ID.

    Query example:
        {"formula": "C2H6O"}
    """
    api = get_pubchem_api()
    try:
        result = api.get_compounds_by_formula(formula)
    except Exception as e:
        return {"error": f"An error occurred while getting compounds by formula: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_molecular_formula(compound: Any) -> Any:
    """
    Get the molecular formula of a compound.

    Args:
        compound: PubChemPy compound object

    Returns:
        Molecular formula of the compound as string
    """
    api = get_pubchem_api()
    try:
        result = api.get_molecular_formula(compound)
    except Exception as e:
        return {"error": f"An error occurred while getting molecular formula: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_molecular_weight(compound: Any) -> Any:
    """
    Get the molecular weight of a compound.

    Args:
        compound: PubChemPy compound object

    Returns:
        Molecular weight of the compound as float
    """
    api = get_pubchem_api()
    try:
        result = api.get_molecular_weight(compound)
    except Exception as e:
        return {"error": f"An error occurred while getting molecular weight: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_isomeric_smiles(compound: Any) -> Any:
    """
    Get the isomeric SMILES of a compound.

    Args:
        compound: PubChemPy compound object

    Returns:
        Isomeric SMILES string of the compound
    """
    api = get_pubchem_api()
    try:
        result = api.get_isomeric_smiles(compound)
    except Exception as e:
        return {"error": f"An error occurred while getting isomeric SMILES: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_xlogp(compound: Any) -> Any:
    """
    Get the XLogP value of a compound.

    Args:
        compound: PubChemPy compound object

    Returns:
        XLogP value of the compound as float
    """
    api = get_pubchem_api()
    try:
        result = api.get_xlogp(compound)
    except Exception as e:
        return {"error": f"An error occurred while getting XLogP: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_iupac_name(compound: Any) -> Any:
    """
    Get the IUPAC name of a compound.

    Args:
        compound: PubChemPy compound object

    Returns:
        IUPAC name of the compound as string
    """
    api = get_pubchem_api()
    try:
        result = api.get_iupac_name(compound)
    except Exception as e:
        return {"error": f"An error occurred while getting IUPAC name: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_synonyms(compound: Any) -> Any:
    """
    Get the synonyms of a compound.

    Args:
        compound: PubChemPy compound object

    Returns:
        List of synonyms of the compound
    """
    api = get_pubchem_api()
    try:
        result = api.get_synonyms(compound)
    except Exception as e:
        return {"error": f"An error occurred while getting synonyms: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_cids_by_smiles(smiles: str) -> Any:
    """
    Obtain the CIDs corresponding to a SMILES string.

    Args:
        smiles: SMILES notation

    Returns:
        List of PubChem CIDs that match the SMILES

    Query example:
        {"smiles": "CC(=O)OC1=CC=CC=C1C(=O)O"}
    """
    api = get_pubchem_api()
    try:
        result = api.get_cids_by_smiles(smiles)
    except Exception as e:
        return {"error": f"An error occurred while getting CIDs by SMILES: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_cids_by_formula(formula: str) -> Any:
    """
    Get a list of CIDs by molecular formula.

    Args:
        formula: Molecular formula of the compound

    Returns:
        List of PubChem CIDs

    Query example:
        {"formula": "C9H8O4"}
    """
    api = get_pubchem_api()
    try:
        result = api.get_cids_by_formula(formula)
    except Exception as e:
        return {"error": f"An error occurred while getting CIDs by formula: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_sids_by_name(name: str) -> Any:
    """
    Get a list of SIDs by name.

    Args:
        name: Name of the substance

    Returns:
        Dictionary containing CID of the compound and a list of PubChem SIDs

    Query example:
        {"name": "aspirin"}
    """
    api = get_pubchem_api()
    try:
        result = api.get_sids_by_name(name)
    except Exception as e:
        return {"error": f"An error occurred while getting SIDs by name: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_substance_by_sid_pcp(sid: str) -> Any:
    """
    Get a PubChemPy Substance object by SID.

    Args:
        sid: PubChem substance ID

    Returns:
        PubChemPy substance object. Often printed as a string such as "Substance(sid)".

    Query example:
        {"sid": 4594}
    """
    api = get_pubchem_api()
    try:
        result = api.get_substance_by_sid(sid)
    except Exception as e:
        return {"error": f"An error occurred while getting substance by SID (PubChemPy): {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_substances_by_name_pcp(name: str) -> Any:
    """
    Get a list of PubChemPy Substance objects by name.

    Args:
        name: Substance name

    Returns:
        List of PubChemPy substance objects. Each element is often printed as "Substance(sid)".

    Query example:
        {"name": "aspirin"}
    """
    api = get_pubchem_api()
    try:
        result = api.get_substances_by_name(name)
    except Exception as e:
        return {"error": f"An error occurred while getting substances by name (PubChemPy): {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_substances_source_id(sid: str) -> Any:
    """
    Get the source ID of a substance by SID.

    The source ID is the unique identifier assigned to the substance by the
    original database such as DrugBank or ChEMBL.

    Args:
        sid: PubChem substance ID

    Returns:
        Source ID of the substance as string

    Query example:
        {"sid": 123456}
    """
    api = get_pubchem_api()
    try:
        result = api.get_substances_source_id(sid)
    except Exception as e:
        return {"error": f"An error occurred while getting substance source ID: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_substances_synonyms(sid: str) -> Any:
    """
    Get synonyms of a substance by SID.

    Args:
        sid: PubChem substance ID

    Returns:
        List of synonyms of the substance

    Query example:
        {"sid": 123456}
    """
    api = get_pubchem_api()
    try:
        result = api.get_substances_synonyms(sid)
    except Exception as e:
        return {"error": f"An error occurred while getting substance synonyms: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_compound_dict(compound: Any, properties: List[str]) -> Any:
    """
    Get a dictionary of selected properties of a compound.

    Args:
        compound: PubChemPy compound object
        properties: List of property names to include in the dictionary

    Returns:
        Dictionary containing the specified properties of the compound
    """
    api = get_pubchem_api()
    try:
        result = api.get_compound_dict(compound, properties)
    except Exception as e:
        return {"error": f"An error occurred while getting compound dictionary: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_compounds_3d(name: str) -> Any:
    """
    Get a list of compound objects with 3D structures by name.

    Args:
        name: Chemical name

    Returns:
        List of PubChemPy compound objects with 3D structures
    """
    api = get_pubchem_api()
    try:
        result = api.get_compounds_3d(name)
    except Exception as e:
        return {"error": f"An error occurred while getting 3D compounds: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_compounds_dict(compound_cid: str) -> Any:
    """
    Get a dictionary representation of a compound by CID.

    Args:
        compound_cid: PubChem compound ID

    Returns:
        Dictionary containing compound information

    Query example:
        {"compound_cid": 962}
    """
    api = get_pubchem_api()
    try:
        result = api.get_compounds_dict(compound_cid)
    except Exception as e:
        return {"error": f"An error occurred while getting compound dictionary by CID: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_substructure_cas(smiles: str) -> Any:
    """
    Get CAS registry numbers for compounds that contain a specified substructure.

    Args:
        smiles: SMILES notation of the substructure

    Returns:
        List of CAS registry numbers

    Query example:
        {"smiles": "CN"}
    """
    api = get_pubchem_api()
    try:
        result = api.get_substructure_cas(smiles)
    except Exception as e:
        return {"error": f"An error occurred while getting substructure CAS numbers: {str(e)}"}
    return result


pubchem_tools: Dict[str, Any] = {
    "search_pubchem_by_name": search_pubchem_by_name,
    "search_pubchem_by_smiles": search_pubchem_by_smiles,
    "get_pubchem_compound_by_cid": get_pubchem_compound_by_cid,
    "search_pubchem_advanced": search_pubchem_advanced,
    "get_substance_by_sid": get_substance_by_sid,
    "get_compound_by_cid": get_compound_by_cid,
    "get_compound_by_name": get_compound_by_name,
    "get_substance_by_name": get_substance_by_name,
    "get_compound_property_by_name": get_compound_property_by_name,
    "get_compound_synonyms_by_name": get_compound_synonyms_by_name,
    "get_description_by_sid": get_description_by_sid,
    "get_description_by_cid": get_description_by_cid,
    "get_general_info_by_compound_name": get_general_info_by_compound_name,
    "get_description_by_aid": get_description_by_aid,
    "get_assay_summary_by_cid": get_assay_summary_by_cid,
    "get_assay_summary_by_sid": get_assay_summary_by_sid,
    "get_gene_summary_by_geneid": get_gene_summary_by_geneid,
    "get_protein_summary_by_accession": get_protein_summary_by_accession,
    "get_taxonomy_summary_by_taxonomyid": get_taxonomy_summary_by_taxonomyid,
    "get_conformers_by_cid": get_conformers_by_cid,
    "get_compounds_by_smiles": get_compounds_by_smiles,
    "get_compounds_by_formula": get_compounds_by_formula,
    "get_molecular_formula": get_molecular_formula,
    "get_molecular_weight": get_molecular_weight,
    "get_isomeric_smiles": get_isomeric_smiles,
    "get_xlogp": get_xlogp,
    "get_iupac_name": get_iupac_name,
    "get_synonyms": get_synonyms,
    "get_cids_by_smiles": get_cids_by_smiles,
    "get_cids_by_formula": get_cids_by_formula,
    "get_sids_by_name": get_sids_by_name,
    "get_substance_by_sid_pcp": get_substance_by_sid_pcp,
    "get_substances_by_name_pcp": get_substances_by_name_pcp,
    "get_substances_source_id": get_substances_source_id,
    "get_substances_synonyms": get_substances_synonyms,
    "get_compound_dict": get_compound_dict,
    "get_compounds_3d": get_compounds_3d,
    "get_compounds_dict": get_compounds_dict,
    "get_substructure_cas": get_substructure_cas,
}
