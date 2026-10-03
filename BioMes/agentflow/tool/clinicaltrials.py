import requests
import json
from typing import Optional, Dict, List, Any, Union

class ClinicalTrialsAPI:
    BASE_URL = "https://clinicaltrials.gov/api/v2/"
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
        "accept": "application/json"
        }
    
    def _flatten_params(self, prefix: str, data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if not data:
            return {}
        return {f"{prefix}.{k}": v for k, v in data.items()}
    
    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Internal helper for GET requests."""
        url = self.BASE_URL + endpoint
        try:
            r = requests.get(url, params=params, headers=self.headers)
            r.raise_for_status()
            return r.json()
        except requests.exceptions.HTTPError as err:
            print(f"HTTP error occurred: {err}")
            try:
                content_type = r.headers.get("Content-Type", "")
                if "application/json" in content_type:
                    error_detail = r.json()
                    print("Error details (JSON):")
                    print(json.dumps(error_detail, indent=2))
                else:
                    print("Error details (text):")
                    print(r.text)
            except Exception as e:
                print(f"Failed to parse error response: {e}")
            return None
        except Exception as err:
            print(f"Other error occurred: {err}")
            return None

    def get_studies(
        self,
        query: Optional[Dict[str, Any]] = None,
        filter: Optional[Dict[str, Any]] = None,
        post_filter: Optional[Dict[str, Any]] = None,
        fields: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
        page_size: int = 50,
        page_token: Optional[str] = None,
        format: str = "json",
        markup_format: str = "markdown",
        count_total: bool = False
    ) -> Dict[str, Any]:
        """
        Query the /studies endpoint with support for structured query, filter, and postFilter parameters.

        Parameters:
            query (dict): Parameters for query.* fields (e.g., {"cond": "glioblastoma"}).
            filter (dict): Parameters for filter.* fields (e.g., {"overallStatus": "RECRUITING"}).
            post_filter (dict): Parameters for postFilter.* fields.
            fields (list of str): List of fields to return (e.g., ["NCTId", "BriefTitle"]).
            sort (list of str): Sort fields (e.g., ["@relevance", "EnrollmentCount:desc"]).
            page_size (int): Number of results per page (maximum 1000).
            page_token (str): Token for retrieving the next page.
            format (str): Response format, either "json" or "csv".
            markup_format (str): Markup formatting for text fields, either "markdown" or "legacy".
            count_total (bool): Whether to include the total number of studies.

        Returns:
            dict: A response object containing the list of studies, nextPageToken, and optional metadata.
        """
        params = {
            "format": format,
            "markupFormat": markup_format,
            "pageSize": str(page_size),
            "countTotal": str(count_total).lower()
        }

        if page_token:
            params["pageToken"] = page_token
        if fields:
            params["fields"] = ",".join(fields)
        if sort:
            params["sort"] = ",".join(sort)

        # 合并嵌套参数组
        params.update(self._flatten_params("query", query))
        params.update(self._flatten_params("filter", filter))
        params.update(self._flatten_params("postFilter", post_filter))
        endpoint = "studies"
        response = self._get(endpoint, params=params)

        return response
    
    def get_study(
        self,
        nct_id: str,
        format: str = "json",
        markup_format: str = "markdown",
        fields: Optional[List[str]] = None
    ) -> Union[Dict[str, Any], bytes, None]:
        """
        Retrieve details for a single clinical trial using its NCT ID.

        Args:
            nct_id (str): The NCT number of the study (e.g., "NCT04000165").
            format (str): Response format. One of 'json', 'csv', 'json.zip', 'fhir.json', 'ris'. Default is 'json'.
            markup_format (str): Markup formatting for text fields. Only applicable when format is 'json' or 'json.zip'.
                                Options are 'markdown' (default) or 'legacy'.
            fields (List[str], optional): List of fields to include in the response. Ignored if format is 'fhir.json'.

        Returns:
            dict: If format is 'json', returns a parsed JSON dictionary.
            bytes: For other formats (CSV, RIS, FHIR, ZIP), returns raw bytes content.
            None: If the request fails or an error occurs.
        """
        params = {"format": format}
        if format in {"json", "json.zip"}:
            params["markupFormat"] = markup_format
        if fields and format != "fhir.json":
            params["fields"] = ",".join(fields)

        endpoint = f"studies/{nct_id}"
        response = self._get(endpoint, params=params)
        return response

    def get_metadata(
        self,
        include_indexed_only: bool = False,
        include_historic_only: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve the list of study data model fields.

        Args:
            include_indexed_only (bool): If True, include fields that are indexed only.
            include_historic_only (bool): If True, include fields available only in historic datasets.

        Returns:
            dict: Metadata describing all available fields in the study data model.
        """
        params = {
            "includeIndexedOnly": str(include_indexed_only).lower(),
            "includeHistoricOnly": str(include_historic_only).lower()
        }
        endpoint = "studies/metadata"
        return self._get(endpoint, params=params)
    
    def get_search_areas(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve all available search documents and their search areas.

        Returns:
            dict: A dictionary describing all searchable documents and their corresponding areas.
        """
        endpoint = "studies/search-areas"
        return self._get(endpoint)
    
    def get_enums(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve all enumeration types and their corresponding values.

        Returns:
            dict: A dictionary containing enum type names, the pieces using them,
                  and all possible values including legacy mappings.
        """
        endpoint = "studies/enums"
        return self._get(endpoint)
    
    def get_study_size_stats(self) -> Optional[Dict[str, Any]]:
        """
        Retrieve statistics about the size of study records in JSON format.

        Returns:
            dict: Contains statistical information such as average, min, max,
                    and total JSON size for all studies.
        """
        endpoint = "stats/size"
        return self._get(endpoint)

    def get_field_value_stats(
        self,
        fields: List[str],
        types: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve value statistics for one or more leaf-level fields.

        Args:
            fields (List[str]): List of field names or paths (e.g., ["Phase", "Condition"]).
            types (List[str], optional): Filter by data types. Options: ENUM, STRING, DATE, INTEGER, NUMBER, BOOLEAN.

        Returns:
            dict: A dictionary containing value distributions for each requested field.
        """
        if not fields:
            raise ValueError("At least one field must be specified.")

        params = {
            "fields": ",".join(fields)
        }

        if types:
            params["types"] = ",".join(types)
        
        endpoint = "stats/field/values"

        return self._get(endpoint, params=params)
    
    def get_field_size_stats(
        self,
        fields: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve size statistics for list/array fields.

        Args:
            fields (List[str], optional): List of field names or paths to filter on.
                                          If None, stats for all list fields will be returned.

        Returns:
            dict: A dictionary containing list size distributions for each specified field.
        """
        params = {}
        if fields:
            params["fields"] = ",".join(fields)
        
        endpoint = "stats/field/sizes"

        return self._get(endpoint, params=params)
   


from typing import Optional, Dict, Any, List
from asyncio import to_thread

from langchain_core.tools import tool


# -------------------------
#   Global singleton client
# -------------------------

_clinicaltrials_api: Optional[ClinicalTrialsAPI] = None


def initialize_clinicaltrials_api(config: Optional[Dict[str, Any]] = None) -> None:
    """
    Initialize the global ClinicalTrialsAPI client.
    Call this once in initialize_tools(config).
    """
    global _clinicaltrials_api
    if _clinicaltrials_api is None:
        _clinicaltrials_api = ClinicalTrialsAPI()


def get_clinicaltrials_api() -> ClinicalTrialsAPI:
    global _clinicaltrials_api
    if _clinicaltrials_api is None:
        _clinicaltrials_api = ClinicalTrialsAPI()
    return _clinicaltrials_api


# -------------------------
#           Tools
# -------------------------

@tool(parse_docstring=True)
async def get_studies(
    query: Optional[Dict[str, Any]] = None,
    filter: Optional[Dict[str, Any]] = None,
    post_filter: Optional[Dict[str, Any]] = None,
    fields: Optional[List[str]] = None,
    sort: Optional[List[str]] = None,
    page_size: int = 50,
    page_token: Optional[str] = None,
    format: str = "json",
    markup_format: str = "markdown",
    count_total: bool = False,
) -> Dict[str, Any]:
    """
    Search clinical trials on ClinicalTrials.gov with structured query parameters.

    Args:
        query: Parameters for query.* fields (for example {"cond": "cancer"})
        filter: Parameters for filter.* fields (for example {"status": "RECRUITING"})
        post_filter: Parameters for postFilter.* fields
        fields: List of fields to return (for example ["NCTId", "BriefTitle"])
        sort: Sort fields (for example ["@relevance", "EnrollmentCount:desc"])
        page_size: Number of results per page (max 1000)
        page_token: Token for the next page
        format: Response format ("json" or "csv")
        markup_format: Text formatting ("markdown" or "legacy")
        count_total: Whether to include total count

    Returns:
        Dictionary with keys:
            studies: List of matching studies
            next_page_token: Token for the next page (if available)
            total_count: Total number of studies when count_total is True
    """
    api = get_clinicaltrials_api()
    result = await to_thread(
        api.get_studies,
        query=query,
        filter=filter,
        post_filter=post_filter,
        fields=fields,
        sort=sort,
        page_size=page_size,
        page_token=page_token,
        format=format,
        markup_format=markup_format,
        count_total=count_total,
    )
    return {
        "studies": result.get("studies", []),
        "next_page_token": result.get("nextPageToken"),
        "total_count": result.get("totalCount"),
    }


@tool(parse_docstring=True)
async def get_study(
    nct_id: str,
    format: str = "json",
    markup_format: str = "markdown",
    fields: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Get detailed information for a single clinical trial.

    Args:
        nct_id: NCT ID (for example "NCT000001")
        format: Response format ("json", "csv" and so on)
        markup_format: Text formatting ("markdown" or "legacy")
        fields: List of fields to include

    Returns:
        Dictionary containing study details.
    """
    api = get_clinicaltrials_api()
    return await to_thread(
        api.get_study,
        nct_id=nct_id,
        format=format,
        markup_format=markup_format,
        fields=fields,
    )


@tool(parse_docstring=True)
async def get_metadata(
    include_indexed_only: bool = False,
    include_historic_only: bool = False,
) -> Dict[str, Any]:
    """
    Get metadata about available study fields.

    Args:
        include_indexed_only: Whether to include indexed-only fields
        include_historic_only: Whether to include historic-only fields

    Returns:
        Dictionary of field metadata.
    """
    api = get_clinicaltrials_api()
    return await to_thread(
        api.get_metadata,
        include_indexed_only=include_indexed_only,
        include_historic_only=include_historic_only,
    )


@tool(parse_docstring=True)
async def get_search_areas() -> Dict[str, Any]:
    """
    Get available search documents and areas.

    Args:
        None

    Returns:
        Dictionary describing search areas and documents.
    """
    api = get_clinicaltrials_api()
    return await to_thread(api.get_search_areas)


@tool(parse_docstring=True)
async def get_enums() -> Dict[str, Any]:
    """
    Get enumeration types and values for ClinicalTrials.gov fields.

    Args:
        None

    Returns:
        Dictionary of enum types and their possible values.
    """
    api = get_clinicaltrials_api()
    return await to_thread(api.get_enums)


@tool(parse_docstring=True)
async def get_study_size_stats() -> Dict[str, Any]:
    """
    Get statistics about study record sizes.

    Args:
        None

    Returns:
        Dictionary of study size statistics.
    """
    api = get_clinicaltrials_api()
    return await to_thread(api.get_study_size_stats)


@tool(parse_docstring=True)
async def get_field_value_stats(fields: List[str], types: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Get value statistics for one or more fields.

    Args:
        fields: List of field names
        types: Optional list of data types (for example ["ENUM", "STRING"])

    Returns:
        Dictionary of field value statistics.
    """
    api = get_clinicaltrials_api()
    return await to_thread(
        api.get_field_value_stats,
        fields=fields,
        types=types,
    )


@tool(parse_docstring=True)
async def get_field_size_stats(fields: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Get size statistics for list or array fields.

    Args:
        fields: Optional list of field names to filter

    Returns:
        Dictionary of field size statistics.
    """
    api = get_clinicaltrials_api()
    return await to_thread(
        api.get_field_size_stats,
        fields=fields,
    )


# -------------------------
# Export dict for agent use
# -------------------------

clinicaltrials_tools: Dict[str, Any] = {
    "get_studies": get_studies,
    "get_study": get_study,
    "get_metadata": get_metadata,
    "get_search_areas": get_search_areas,
    "get_enums": get_enums,
    "get_study_size_stats": get_study_size_stats,
    "get_field_value_stats": get_field_value_stats,
    "get_field_size_stats": get_field_size_stats,
}
