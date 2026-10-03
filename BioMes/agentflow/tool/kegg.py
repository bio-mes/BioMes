import io
import time
from urllib.request import urlopen

from Bio._utils import function_with_previous
import requests


class KeggAPI():
    BASE_URL = "https://rest.kegg.jp"
    
    def __init__(self):
        self.session = requests.Session()

    def query(self, op, arg1, arg2=None, arg3=None):

        URL = "https://rest.kegg.jp/%s"
        if arg2 and arg3:
            args = f"{op}/{arg1}/{arg2}/{arg3}"
        elif arg2:
            args = f"{op}/{arg1}/{arg2}"
        else:
            args = f"{op}/{arg1}"

        request_url = "/".join([self.BASE_URL, args])
        print('request_url: ', request_url)
        
        results = self.session.get(request_url)

        print('Request result:', results.text)

        return results.text



    # https://www.kegg.jp/kegg/rest/keggapi.html
    def kegg_info(self,database):
        """KEGG info - Displays the current statistics of a given database.

        db - database or organism (string)

        The argument db can be a KEGG database name (e.g. 'pathway' or its
        official abbreviation, 'path'), or a KEGG organism code or T number
        (e.g. 'hsa' or 'T01001' for human).

        A valid list of organism codes and their T numbers can be obtained
        via kegg_info('organism') or https://rest.kegg.jp/list/organism

        """
        # TODO - return a string (rather than the handle?)
        # TODO - cache and validate the organism code / T numbers?
        # TODO - can we parse the somewhat formatted output?
        #
        # https://rest.kegg.jp/info/<database>
        #
        # <database> = pathway | brite | module | disease | drug | environ |
        #              ko | genome |<org> | compound | glycan | reaction |
        #              rpair | rclass | enzyme | genomes | genes | ligand | kegg
        # <org> = KEGG organism code or T number
        return self.query("info", database)


    def kegg_list(self,database, org=None):
        """KEGG list - Entry list for database, or specified database entries.

        db - database or organism (string)
        org - optional organism (string), see below.

        For the pathway and module databases the optional organism can be
        used to restrict the results.

        """
        # TODO - split into two functions (dbentries seems separate)?
        #
        #  https://rest.kegg.jp/list/<database>/<org>
        #
        #  <database> = pathway | module
        #  <org> = KEGG organism code
        if database in ("pathway", "module") and org:
            resp = self.query("list", database, org)
        elif isinstance(database, str) and database and org:
            raise ValueError("Invalid database arg for kegg list request.")

        # https://rest.kegg.jp/list/<database>
        #
        # <database> = pathway | brite | module | disease | drug | environ |
        #              ko | genome | <org> | compound | glycan | reaction |
        #              rpair | rclass | enzyme | organism
        # <org> = KEGG organism code or T number
        #
        #
        # https://rest.kegg.jp/list/<dbentries>
        #
        # <dbentries> = KEGG database entries involving the following <database>
        # <database> = pathway | brite | module | disease | drug | environ |
        #              ko | genome | <org> | compound | glycan | reaction |
        #              rpair | rclass | enzyme
        # <org> = KEGG organism code or T number
        else:
            if isinstance(database, list):
                if len(database) > 100:
                    raise ValueError(
                        "Maximum number of databases is 100 for kegg list query"
                    )
                database = ("+").join(database)
            resp = self.query("list", database)

        return resp


    def kegg_find(self,database, query, option=None):
        """KEGG find - Data search.

        Finds entries with matching query keywords or other query data in
        a given database.

        db - database or organism (string)
        query - search terms (string)
        option - search option (string), see below.

        For the compound and drug database, set option to the string 'formula',
        'exact_mass' or 'mol_weight' to search on that field only. The
        chemical formula search is a partial match irrespective of the order
        of atoms given. The exact mass (or molecular weight) is checked by
        rounding off to the same decimal place as the query data. A range of
        values may also be specified with the minus(-) sign.

        """
        # TODO - return list of tuples?
        #
        # https://rest.kegg.jp/find/<database>/<query>/<option>
        #
        # <database> = compound | drug
        # <option> = formula | exact_mass | mol_weight
        if database in ["compound", "drug"] and option in [
            "formula",
            "exact_mass",
            "mol_weight",
        ]:
            resp = self.query("find", database, query, option)
        elif option:
            raise ValueError("Invalid option arg for kegg find request.")

        # https://rest.kegg.jp/find/<database>/<query>
        #
        # <database> = pathway | module | disease | drug | environ | ko |
        #              genome | <org> | compound | glycan | reaction | rpair |
        #              rclass | enzyme | genes | ligand
        # <org> = KEGG organism code or T number
        else:
            if isinstance(query, list):
                query = "+".join(query)
            resp = self.query("find", database, query)

        return resp


    def kegg_get(self,dbentries, option=None):
        """KEGG get - Data retrieval.

        dbentries - Identifiers (single string, or list of strings), see below.
        option - One of "aaseq", "ntseq", "mol", "kcf", "image", "kgml" (string)

        The input is limited up to 10 entries.
        The input is limited to one pathway entry with the image or kgml option.
        The input is limited to one compound/glycan/drug entry with the image option.

        Returns a handle.
        """
        if isinstance(dbentries, list) and len(dbentries) <= 10:
            dbentries = "+".join(dbentries)
        elif isinstance(dbentries, list) and len(dbentries) > 10:
            raise ValueError("Maximum number of dbentries is 10 for kegg get query")

        # https://rest.kegg.jp/get/<dbentries>[/<option>]
        #
        # <dbentries> = KEGG database entries involving the following <database>
        # <database> = pathway | brite | module | disease | drug | environ |
        #              ko | genome | <org> | compound | glycan | reaction |
        #              rpair | rclass | enzyme
        # <org> = KEGG organism code or T number
        #
        # <option> = aaseq | ntseq | mol | kcf | image
        if option in ["aaseq", "ntseq", "mol", "kcf", "image", "kgml", "json"]:
            resp = self.query("get", dbentries, option)
        elif option:
            raise ValueError("Invalid option arg for kegg get request.")
        else:
            resp = self.query("get", dbentries)

        return resp


    def kegg_conv(self,target_db, source_db, option=None):
        """KEGG conv - convert KEGG identifiers to/from outside identifiers.

        Arguments:
        - target_db - Target database
        - source_db_or_dbentries - source database or database entries
        - option - Can be "turtle" or "n-triple" (string).

        """
        # https://rest.kegg.jp/conv/<target_db>/<source_db>[/<option>]
        #
        # (<target_db> <source_db>) = (<kegg_db> <outside_db>) |
        #                             (<outside_db> <kegg_db>)
        #
        # For gene identifiers:
        # <kegg_db> = <org>
        # <org> = KEGG organism code or T number
        # <outside_db> = ncbi-gi | ncbi-geneid | uniprot
        #
        # For chemical substance identifiers:
        # <kegg_db> = drug | compound | glycan
        # <outside_db> = pubchem | chebi
        #
        # <option> = turtle | n-triple
        #
        # https://rest.kegg.jp/conv/<target_db>/<dbentries>[/<option>]
        #
        # For gene identifiers:
        # <dbentries> = database entries involving the following <database>
        # <database> = <org> | ncbi-gi | ncbi-geneid | uniprot
        # <org> = KEGG organism code or T number
        #
        # For chemical substance identifiers:
        # <dbentries> = database entries involving the following <database>
        # <database> = drug | compound | glycan | pubchem | chebi
        #
        # <option> = turtle | n-triple
        if option and option not in ["turtle", "n-triple"]:
            raise ValueError("Invalid option arg for kegg conv request.")

        if isinstance(source_db, list):
            source_db = "+".join(source_db)

        if (
            target_db in ["ncbi-gi", "ncbi-geneid", "uniprot"]
            or source_db in ["ncbi-gi", "ncbi-geneid", "uniprot"]
            or (
                target_db in ["drug", "compound", "glycan"]
                and source_db in ["pubchem", "glycan"]
            )
            or (
                target_db in ["pubchem", "glycan"]
                and source_db in ["drug", "compound", "glycan"]
            )
        ):
            if option:
                resp = self.query("conv", target_db, source_db, option)
            else:
                resp = self.query("conv", target_db, source_db)

            return resp
        else:
            raise ValueError("Bad argument target_db or source_db for kegg conv request.")


    def kegg_link(self, target_db, source_db, option=None):
        """KEGG link - find related entries by using database cross-references.

        target_db: Target database
        source_db_or_dbentries: source database
        option: Can be "turtle" or "n-triple" (string).

        <target_db> = <database>
        <source_db> = <database>
        <database> = pathway | brite | module | ko | genome | <org> | compound | glycan | reaction | rpair | rclass | enzyme | disease | drug | dgroup | environ

        <dbentries> = KEGG database entries involving the following <database>
        <database> = pathway | brite | module | ko | genome | <org> | compound | glycan | reaction | rpair | rclass | enzyme | disease | drug | dgroup | environ | genes

        """
        # https://rest.kegg.jp/link/<target_db>/<source_db>[/<option>]
        #
        # <target_db> = <database>
        # <source_db> = <database>
        #
        # <database> = pathway | brite | module | ko | genome | <org> | compound |
        #              glycan | reaction | rpair | rclass | enzyme | disease |
        #              drug | dgroup | environ
        #
        # <option> = turtle | n-triple
        # https://rest.kegg.jp/link/<target_db>/<dbentries>[/<option>]
        #
        # <dbentries> = KEGG database entries involving the following <database>
        # <database> = pathway | brite | module | ko | genome | <org> | compound |
        #              glycan | reaction | rpair | rclass | enzyme | disease |
        #              drug | dgroup | environ | genes
        #
        # <option> = turtle | n-triple

        if option and option not in ["turtle", "n-triple"]:
            raise ValueError("Invalid option arg for kegg conv request.")

        if isinstance(source_db, list):
            source_db = "+".join(source_db)

        if option:
            resp = self.query("link", target_db, source_db, option)
        else:
            resp = self.query("link", target_db, source_db)

        return resp




from typing import Dict, Any, Optional
from langchain_core.tools import tool


_kegg_api: Optional[KeggAPI] = None


def initialize_kegg_api(config: Optional[Dict[str, Any]] = None) -> None:
    """
    Initialize the global KEGG API client.

    This can be called once at application startup (for example inside initialize_tools(config)).
    The config parameter is reserved for future extensions (for example base URL, timeout),
    but is not used at the moment because KeggAPI() does not take arguments in your current code.
    """
    global _kegg_api
    if _kegg_api is None:
        _kegg_api = KeggAPI()


def get_kegg_api() -> KeggAPI:
    """
    Get the global KEGG API client. Lazily initializes it if needed.
    """
    global _kegg_api
    if _kegg_api is None:
        _kegg_api = KeggAPI()
    return _kegg_api


@tool(parse_docstring=True)
async def kegg_info(db: str) -> Any:
    """
    Get KEGG database release information and statistics for a given database.

    This operation displays the current statistics of a given KEGG database.
    For most databases (except 'kegg', 'genes', and 'ligand'), it also shows
    the list of linked databases that can be used in the link operation.

    Args:
        db: KEGG database name, for example "genes", "pathway", "brite".

    Example:
        {"db": "genes"}

    Returns:
        A text message (typically a multi-line string) with database statistics,
        or a JSON object with an "error" field when an exception occurs.
    """
    api = get_kegg_api()
    try:
        result = api.kegg_info(database=db)
    except Exception as e:
        return {"error": f"An error occurred while querying kegg_info: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def kegg_find(db: str, query: str, option: str = "") -> Any:
    """
    KEGG find - data search within a KEGG database.

    Finds entries with matching query keywords or other query data in a given
    KEGG database.

    Args:
        db:     KEGG database name, for example "genes", "compound", "drug".
        query:  Keywords or identifiers to search (string).
        option: Additional search options (string), can be empty.

    Example:
        {"db": "genes", "query": "p53", "option": ""}

    Returns:
        Tab-delimited text (typically a multi-line string) with search results,
        or a JSON object with an "error" field when an exception occurs.
    """
    api = get_kegg_api()
    try:
        result = api.kegg_find(database=db, query=query, option=option)
    except Exception as e:
        return {"error": f"An error occurred while querying kegg_find: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def kegg_list(db: str, org: str = "") -> Any:
    """
    KEGG list - list entries in a KEGG database.

    This operation can be used to:
      - obtain a list of all entries in a given database;
      - list organism-specific pathways when the organism code is known;
      - list BRITE hierarchies;
      - list definitions for a given set of entry identifiers.

    Args:
        db:  KEGG database name, for example "pathway", "brite", "genes".
        org: Optional organism code, only valid for certain databases. Can be empty.

    Example:
        {"db": "pathway", "org": ""}

    Returns:
        Tab-delimited text (typically a multi-line string) with entry list,
        or a JSON object with an "error" field when an exception occurs.
    """
    api = get_kegg_api()
    try:
        result = api.kegg_list(database=db, org=org)
    except Exception as e:
        return {"error": f"An error occurred while querying kegg_list: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def kegg_get(dbentries: str, option: str = "") -> Any:
    """
    KEGG get - retrieve KEGG entries in flat file or other formats.

    This operation retrieves database entries in a flat file format or
    in other formats specified by options. The input is limited to up to
    10 entries.

    Args:
        dbentries: One or more KEGG entry identifiers, separated by '+' if multiple.For example "path:hsa00010" or "hsa:10458+hsa:7157".
        option:    Controls the format or content of returned data, for example "kgml".

    Example:
        {"dbentries": "path:hsa00010", "option": "kgml"}

    Returns:
        Flat file content (typically a multi-line string) or other format text,
        or a JSON object with an "error" field when an exception occurs.
    """
    api = get_kegg_api()
    try:
        result = api.kegg_get(dbentries=dbentries, option=option)
    except Exception as e:
        return {"error": f"An error occurred while querying kegg_get: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def kegg_conv(target_db: str, source_db_or_dbentries: str, option: str = "") -> Any:
    """
    KEGG conv - convert entry identifiers between KEGG and external databases.

    This operation converts entry identifiers (accession numbers) of external
    databases to KEGG identifiers and vice versa. The first form allows database
    to database mapping, while the second form allows conversion of a selected
    number of entries. The database name "genes" may be used only in the second form.

    Args:
        target_db:               Target database name for mapping, for example "ncbi-geneid".
        source_db_or_dbentries:  Source database name or specific KEGG entry identifiers.
        option:                  Additional options controlling range or format of results.

    Example:
        {"target_db": "ncbi-geneid",
         "source_db_or_dbentries": "hsa:10458",
         "option": ""}

    Returns:
        Tab-delimited text (typically a multi-line string) with mapping results,
        or a JSON object with an "error" field when an exception occurs.
    """
    api = get_kegg_api()
    try:
        result = api.kegg_conv(
            target_db=target_db,
            source_db=source_db_or_dbentries,
            option=option,
        )
    except Exception as e:
        return {"error": f"An error occurred while querying kegg_conv: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def kegg_link(target_db: str, source_db_or_dbentries: str, option: str = "") -> Any:
    """
    KEGG link - find related entries using database cross-references.

    This operation finds related entries by using KEGG database
    cross-references between source and target databases.

    Args:
        target_db:               Target database name, for example "pathway".
        source_db_or_dbentries:  Source database name or specific entry identifiers.
        option:                  Options controlling the format or range of results.

    Example:
        {"target_db": "pathway",
         "source_db_or_dbentries": "hsa:10458",
         "option": ""}

    Returns:
        Tab-delimited text (typically a multi-line string) with cross-reference results,
        or a JSON object with an "error" field when an exception occurs.
    """
    api = get_kegg_api()
    try:
        result = api.kegg_link(
            target_db=target_db,
            source_db=source_db_or_dbentries,
            option=option,
        )
    except Exception as e:
        return {"error": f"An error occurred while querying kegg_link: {str(e)}"}
    return result


kegg_tools: Dict[str, Any] = {
    "kegg_info": kegg_info,
    "kegg_find": kegg_find,
    "kegg_list": kegg_list,
    "kegg_get": kegg_get,
    "kegg_conv": kegg_conv,
    "kegg_link": kegg_link,
}
