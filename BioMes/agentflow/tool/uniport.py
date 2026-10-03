import json
import requests
from langchain_core.tools import tool



class UNIPROTAPI:
    BASE_URL = "https://rest.uniprot.org/"

    def __init__(self):
        self.session = requests.Session()
        self.headers = {
        "accept": "application/json"
        }
    def _get(self, endpoint, params=None):
        """Internal helper for GET requests."""
        url = self.BASE_URL + endpoint
        try:
            r = requests.get(url, params=params, headers=self.headers)
            r.raise_for_status()
            return json.dumps(r.json(), indent=2)
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

    def get_uniprotkb_entry_by_accession(self, accession):
        """Search UniProtKB by protein entry accession to return all data associated with that entry. 
        Specify fields to return only data for specific sections of that entry that are of interest to you"""

        params = {
        # "fields": [
        #     "accession",
        #     "protein_name",
        #     "cc_function",
        #     "ft_binding"
        # ]
        }
        endpoint = "uniprotkb/" + accession
        return self._get(endpoint, params=params)
    
    def stream_uniprotkb_entries(self, query):
        """The stream endpoint uses a request query to return all entries associated with the search term in a single download. 
        Specify fields to return only data for specific sections of that entry that are of interest to you """
        params = {
            "query": query,
            # "fields": [
            #     "accession",
            #     "protein_name",
            #     "cc_function",
            #     "ft_binding"
            # ],
            # "sort": "accession desc"
        }
        endpoint = "uniprotkb/search"
        return self._get(endpoint, params=params)
    
    def search_uniprotkb_entries(self, query):
        """The search endpoint uses a request query to return all entries associated with the search term in a paginated list of entries. 
        Use ‘size’ to specify the number of entries per page of results. Specify fields to return only data for specific sections of that entry that are of interest to you"""
        params = {
            "query": query,
            "fields": [
                "accession", "id", "gene_names", "gene_primary", "organism_name", "organism_id", "protein_name", "lineage", "lineage_ids",
                "length", "ft_variant", "ft_act_site", "cc_catalytic_activity", "cc_cofactor", "ft_dna_bind", "ec", "cc_function", "kinetics", "cc_pathway",
                "ph_dependence", "redox_potential", "rhea", "cc_developmental_stage", "cc_induction", "cc_tissue_specificity", "go", "go_p", "go_c", "go_f",
                "xref_ensembl",
                "cc_function",
                "ft_binding",
                "structure_3d"
        ],
        # "sort": "accession desc",
        "size": "50"
        }
        endpoint = "uniprotkb/search"
        return self._get(endpoint, params=params)

    def get_general_info_by_protein_or_gene_name(self, name: str, species: str = 'Homo sapiens'):
        """
        Get general information of a protein or gene by name from UniProt database.
        Args:
            name: Protein or gene name.
            sepcies: Species name.
        Returns:
            JSON string with general information of the protein or gene.
        """
        result = self.search_uniprotkb_entries(query=name)
        if isinstance(result, str):
            result = json.loads(result)
        result = result.get('results', [])
        target_data = None
        for item in result:
            if item.get('organism', {}).get('scientificName') == species:
                target_data = item
                break
        if not target_data:
            return f"No data found for the species: {species}"
        
        pdb_id = None
        for cross_ref in target_data['uniProtKBCrossReferences']:
            if cross_ref['database'] == 'PDB':
                pdb_id = cross_ref['id']
                break
        
        remain_keys = ['comments', 'genes']
        ret_data = {k: v for k, v in target_data.items() if k in remain_keys}
        ret_data['pdb_id'] = pdb_id
    
        return ret_data
    
    def get_uniref_cluster_by_id(self, uniref_id):
        """Search UniRef entry by id to return all data associated with that entry. 
        Specify fields to return only data for specific sections of that entry that are of interest to you"""
        params = {
        "id": uniref_id,
        # "fields": [
        #     "id",
        #     "name",
        #     "types",
        #     "organism",
        #     "identity"
        # ]
        }
        endpoint = "uniref/%7Bid%7D"
        return self._get(endpoint, params=params)
    
    def get_uniref_cluster_members_by_id(self, uniref_id):
        """Search UniRef entry by member id to return all data associated with that entry. 
        Specify fields to return only data for specific sections of that entry that are of interest to you"""
        params = {
        "id": uniref_id,
        "facetFilter": "member_id_type:uniprotkb_id",
        "size": "10"
        }
        endpoint = "uniref/%7Bid%7D/members"
        return self._get(endpoint, params=params)
    
    def get_uniref_light_cluster_by_id(self, uniref_id):
        """Search light UniRef entry by id to return all data associated with that entry. 
        Specify fields to return only data for specific sections of that entry that are of interest to you"""
        params = {
        # "fields": [
        #     "id",
        #     "name",
        #     "types",
        #     "organism",
        #     "identity"
        # ]
        }
        endpoint = f"uniref/{uniref_id}/light"
        return self._get(endpoint, params=params)
    
    def stream_uniref_clusters(self, query):
        """The uniref stream endpoint uses a request query to return all entries associated with the search term in a single download. 
        Specify fields to return only data for specific sections of that entry that are of interest to you The stream endpoint has a maximum limit of 10 million entries"""
        params = {
        "query": query,
        # "fields": [
        #     "id",
        #     "name",
        #     "types",
        #     "organism",
        #     "identity"
        # ]
        }
        endpoint = "uniref/search"
        return self._get(endpoint, params=params)

    def search_uniref_clusters(self, query):
        """The uniref search endpoint uses a request query to return all entries associated with the search term in a paginated list of entries. 
        Use ‘size’ to specify the number of entries per page of results. Specify fields to return only data for specific sections of that entry that are of interest to you"""
        params = {
        "query": query,
        # "fields": [
        #     "id",
        #     "name",
        #     "types",
        #     "organism",
        #     "identity"
        # ],
        "size": "10"
        }
        endpoint = "uniref/search"
        return self._get(endpoint, params=params)
    
    def get_uniparc_entry_by_upi(self, uniparc_id):
        """Search UniParc entry by id(upi) to return all data associated with that entry. 
        Specify fields to return only data for specific sections of that entry that are of interest to you"""
        
        params = {
        "upi": uniparc_id,
        # "fields": [
        #     "upi",
        #     "organism",
        #     "length"
        # ],
        "dbTypes": "EnsemblBacteria,FlyBase",
        "taxonIds": "9606,10116,9913"
        }
        endpoint = "uniparc/%7Bupi%7D"
        return self._get(endpoint, params=params)
    
    def get_uniparc_light_entry_by_upi(self, uniparc_id):
        """Search UniParc entry by id(upi) to return all data associated with that entry. 
        Specify fields to return only data for specific sections of that entry that are of interest to you"""
        params = {
        # "fields": [
        #     "upi",
        #     "organism",
        #     "length"
        # ],
        }
        endpoint = f"uniparc/{uniparc_id}/light"
        return self._get(endpoint, params=params)
    
    #to do: error handling
    def get_uniparc_cross_references_by_upi(self, uniparc_id):
        """Get a page of database cross-reference entries by a upi"""
        params = {
        # "fields": [
        #     "organism"
        # ],
        "id": "Q0GNZ6",
        "dbTypes": "EnsemblBacteria,FlyBase",
        "taxonIds": "9606,10116,9913",
        "size": "10"
        }

        endpoint = f"uniparc/{uniparc_id}/databases"
        return self._get(endpoint, params=params)
    
    #to do: error handling
    def stream_uniparc_cross_references_by_upi(self, uniparc_id):
        """Get a page of database cross-reference entries by a upi"""
        params = {
        # "fields": [
        #     "organism"
        # ],
        "id": "Q0GNZ6",
        "dbTypes": "EnsemblBacteria,FlyBase",
        "taxonIds": "9606,10116,9913"
        }
        endpoint = f"uniparc/{uniparc_id}/databases/search"
        return self._get(endpoint, params=params)

    def stream_uniparc_entries(self, uniparc_id):
        """The stream endpoint uses a request query to return all entries associated with the search term in a single download. 
        Specify fields to return only data for specific sections of that entry that are of interest to you The stream endpoint has a maximum limit of 10 million entries"""
        params = {
        "query": uniparc_id,
        # "sort": "upi asc",
        # "fields": [
        #     "upi",
        #     "organism",
        #     "length"
        # ]
        }
        endpoint = "uniparc/stream"
        return self._get(endpoint, params=params)
    
    def search_uniparc_entries(self, entry):
        """The search endpoint uses a request query to return all entries associated with the search term in a paginated list of entries. 
        Use ‘size’ to specify the number of entries per page of results. Specify fields to return only data for specific sections of that entry that are of interest to you"""
        params = {
        "query": entry,
        # "sort": "upi asc",
        # "fields": [
        #     "upi",
        #     "organism",
        #     "length"
        # ],
        
        "size": "10"
        }
        endpoint = "uniparc/search"
        return self._get(endpoint, params=params)
    
    # to do
    def get_gene_centric_by_accession(self, accession):
        """Retrieve a GeneCentric entry by UniProtKB accession.Search GeneCentric entry by protein accession to return all data associated with that entry. 
        Specify fields to return only data for specific sections of that entry that are of interest to you"""
        params = {
        # "fields": [
        #     "accession",
        #     "gene_name",
        #     "proteome_id"
        # ]
        }
        endpoint = f"genecentric/{accession}"
        return self._get(endpoint, params=params)

    def get_gene_centric_by_proteome(self, upid):
        """Search GeneCentric entry by Proteome ID to return all data associated with that entry. 
        Specify fields to return only data for specific sections of that entry that are of interest to you"""
        params = {
        "upid": upid,
        # "fields": [
        #     "accession",
        #     "gene_name",
        #     "proteome_id"
        # ],
        "size": "10"
        }
        endpoint = "genecentric/upid/%7Bupid%7D"
        return self._get(endpoint, params=params)

    def stream_gene_centric(self, accession):
        """Stream GeneCentric entries matching a query (max 10M entries).The stream endpoint uses a request query to return all entries associated with the search term in a single download. 
        Specify fields to return only data for specific sections of that entry that are of interest to you"""
        params = {
        "query": accession
        }
        endpoint = "genecentric/stream"
        return self._get(endpoint, params=params)

    def search_gene_centric(self, accession):
        """Search GeneCentric entries with pagination.The search endpoint uses a request query to return all entries associated with the search term in a paginated list of entries. Use ‘size’ to specify the number of entries per page of results. 
        Specify fields to return only data for specific sections of that entry that are of interest to you"""
        params = {
        "query": accession,
        "size": "10"
        }
        endpoint = "genecentric/search"
        return self._get(endpoint, params=params)

    def get_proteome_by_id(self, upid):
        """Retrieve a proteome by UniProt Proteome ID.Search Proteome entry by Proteome ID(upid) to return all data associated with that entry. 
        Specify fields to return only data for specific sections of that entry that are of interest to you"""
        params = {
        # "fields": [
        #     "upid",
        #     "organism",
        #     "organism_id"
        # ]
        }
        endpoint = f"proteomes/{upid}"
        return self._get(endpoint, params=params)

    def stream_proteomes(self, query):
        """Stream Proteome entries matching a query (max 10M entries).The stream endpoint uses a request query to return all entries associated with the search term in a single download. 
        Specify fields to return only data for specific sections of that entry that are of interest to you"""
        params = {
        "query": query,
        # "sort": "organism_name asc",
        # "fields": [
        #     "upid",
        #     "organism",
        #     "organism_id"
        # ],
        }
        endpoint = "proteomes/search"
        return self._get(endpoint, params=params)

    def search_proteomes(self, query):
        """Search Proteome entries with pagination. The search endpoint uses a request query to return all entries associated with the search term in a paginated list of entries. Use ‘size’ to specify the number of entries per page of results. 
        Specify fields to return only data for specific sections of that entry that are of interest to you"""
        
        params = {
        "query": query,
        # "sort": "organism_name asc",
        # "fields": [
        #     "upid",
        #     "organism",
        #     "organism_id"
        # ],
        "size": "10"
        }
        endpoint = "proteomes/search"
        return self._get(endpoint, params=params)


uniprot_api = UNIPROTAPI()
def initialize_uniprot_api():
    global uniprot_api


@tool(parse_docstring=True)
async def get_general_info_by_protein_or_gene_name(name: str, species: str = 'Homo sapiens') -> dict:
    """
    Get general information of a protein or gene by name from UniProt database.
    
    Args:
        name: Protein or gene name, e.g. "TP53"
        species: Species name.

    Returns:
        JSON string with general information of the protein or gene.
    """
    try:
        result = uniprot_api.get_general_info_by_protein_or_gene_name(name=name, species=species)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result

@tool(parse_docstring=True)
async def get_uniprotkb_entry_by_accession(accession: str):
    """
    Search UniProtKB by protein entry accession to return all data associated with that entry.
    
    Args:
        accession: UniProtKB accession ID (string, required), e.g. "P68871"
    
    Returns:
        A JSON string containing all data associated with the specified UniProtKB entry, including entry type, primary and secondary accession IDs, UniProtKB ID, annotation score, organism details, protein description, gene names, functional comments, and additional annotations such as sequence and database cross-references.
    """

    try:
        result = uniprot_api.get_uniprotkb_entry_by_accession(accession=accession)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result

@tool(parse_docstring=True)
async def stream_uniprotkb_entries(query: str):
    """
    Stream all UniProtKB entries associated with the search term in a single download.
    
    Args:
        query: Search term for UniProtKB entries, such as a protein name or keyword (e.g., "hemoglobin") (string, required)
    
    Returns:
        A JSON string containing a list of UniProtKB entries matching the search query. Each entry includes the entry type, primary and secondary accession IDs, UniProtKB ID, entry audit information, annotation score, organism details, protein description (recommended name, alternative names, and contained molecules), gene names, functional comments, and additional annotations such as sequence and features.
    """

    try:
        result = uniprot_api.stream_uniprotkb_entries(query=query)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result

@tool(parse_docstring=True)
async def search_uniprotkb_entries(query: str):
    """
    Search UniProtKB entries using a query, returns paginated list.
    
    Args:
        query: Search term for UniProtKB entries, such as a protein name or keyword (e.g., "hemoglobin") (string, required)
    
    Returns:
        A JSON string containing a paginated list of UniProtKB entries matching the search query. Each entry includes the entry type, primary accession ID, UniProtKB ID, organism details, protein description (recommended name, alternative names, and contained molecules), gene names, functional comments, and additional features such as tissue specificity.
    """

    try:
        result = uniprot_api.search_uniprotkb_entries(query=query)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result

@tool(parse_docstring=True)
async def get_uniref_cluster_by_id(uniref_id: str):
    """
    Search UniRef entry by id to return all data associated with that entry.
    
    Args:
        uniref_id: UniRef cluster ID (string, required), e.g., "UniRef90_P68871"
    
    Returns:
        A JSON string containing all data associated with the specified UniRef cluster, including cluster ID, name, member count, update date, entry type, common taxonomy, representative member (with sequence and UniProtKB accessions), and a list of cluster members with their respective organism and sequence details.
    """

    try:
        result = uniprot_api.get_uniref_cluster_by_id(uniref_id=uniref_id)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result

@tool(parse_docstring=True)
async def get_uniref_cluster_members_by_id(uniref_id: str):
    """
    Search UniRef entry by member id to return all data associated with that entry.
    
    Args:
        uniref_id: UniRef cluster ID (string, required), e.g., "UniRef90_P68871"
    
    Returns:
        A JSON string containing a list of members in the specified UniRef cluster. Each member includes the member ID type, member ID, organism name and taxonomic ID, sequence length, protein name, UniProtKB accessions, related UniRef50/100 and UniParc IDs, and sequence details (value, length, molecular weight, CRC64 checksum, MD5 hash).
    """

    try:
        result = uniprot_api.get_uniref_cluster_members_by_id(uniref_id=uniref_id)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result

@tool(parse_docstring=True)
async def get_uniref_light_cluster_by_id(uniref_id: str):
    """
    Search light UniRef entry by id to return all data associated with that entry.
    
    Args:
        uniref_id: UniRef cluster ID (string, required), e.g. "UniRef90_P68871"
    
    Returns:
        A JSON string containing lightweight data for the specified UniRef cluster, including cluster ID, name, update date, entry type, common taxonomy, member and organism counts, representative member details (with sequence and UniProtKB accessions), seed ID, member ID types, a list of member IDs, and partial organism information.
    """

    try:
        result = uniprot_api.get_uniref_light_cluster_by_id(uniref_id=uniref_id)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result

@tool(parse_docstring=True)
async def stream_uniref_clusters(query: str):
    """
    Stream all UniRef clusters associated with the search term in a single download.
    
    Args:
        query: Search term for UniRef clusters, such as a protein name or keyword (e.g., "hemoglobin") (string, required)
    
    Returns:
        A JSON string containing a list of UniRef clusters matching the search query. Each cluster includes the cluster ID, name, update date, entry type, common taxonomy, member and organism counts, representative member details (with sequence and UniProtKB accessions), seed ID, member ID types, member IDs, and organism details.
    """

    try:
        result = uniprot_api.stream_uniref_clusters(query=query)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result

@tool(parse_docstring=True)
async def search_uniref_clusters(query: str):
    """
    Search UniRef clusters using a query, returns paginated list.
    
    Args:
        query: Search term for UniRef clusters, such as a protein name or keyword (e.g., "hemoglobin") (string, required)
    
    Returns:
        A JSON string containing a paginated list of UniRef clusters matching the search query. Each cluster includes the cluster ID, name, update date, entry type, common taxonomy, member and organism counts, representative member details (with sequence and UniProtKB accessions), seed ID, member ID types, member IDs, and organism details.
    """

    try:
        result = uniprot_api.search_uniref_clusters(query=query)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result

@tool(parse_docstring=True)
async def get_uniparc_entry_by_upi(uniparc_id: str):
    """
    Search UniParc entry by id (UPI) to return all data associated with that entry.
    
    Args:
        uniparc_id: UniParc UPI ID (string, required), e.g. "UPI00000015C9"
    
    Returns:
        A JSON string containing all data associated with the specified UniParc entry, including the UniParc ID, protein sequence (value, length, molecular weight, CRC64 checksum, MD5 hash), and sequence features from databases like Pfam, PROSITE, and InterPro.
    """

    try:
        result = uniprot_api.get_uniparc_entry_by_upi(uniparc_id=uniparc_id)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result

@tool(parse_docstring=True)
async def get_uniparc_light_entry_by_upi(uniparc_id: str):
    """
    Search UniParc entry by id (UPI) to return all data associated with that entry (light version).
    
    Args:
        uniparc_id: UniParc UPI ID (string, required), e.g. "UPI00000015C9"
    
    Returns:
        A JSON string containing lightweight data for the specified UniParc entry, including the UniParc ID, protein sequence (value, length, molecular weight, CRC64 checksum, MD5 hash), cross-reference count, common taxons, UniProtKB accessions, and sequence features from databases like Pfam, PROSITE, and InterPro.
    """

    try:
        result = uniprot_api.get_uniparc_light_entry_by_upi(uniparc_id=uniparc_id)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result

@tool(parse_docstring=True)
async def get_uniparc_cross_references_by_upi(uniparc_id: str):
    """
    Get a page of database cross-reference entries by a UPI.
    
    Args:
        uniparc_id: UniParc UPI ID (string, required), e.g. "UPI000035B535"
    
    Returns:
        A JSON string containing a paginated list of database cross-reference entries for the specified UniParc UPI, including database types, accession IDs, activity status, and associated properties like protein names and taxonomy.
    """

    try:
        result = uniprot_api.get_uniparc_cross_references_by_upi(uniparc_id=uniparc_id)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result

@tool(parse_docstring=True)
async def stream_uniparc_cross_references_by_upi(uniparc_id: str):
    """
    Stream database cross-reference entries for a specified UniParc UPI.
    
    Args:
        uniparc_id: UniParc UPI ID (string, required), e.g. "UPI000041C017"
    
    Returns:
        A JSON string containing streamed cross-reference entries, each linking the UniParc ID to source database accession numbers, including details such as database type, accession, version, activity status, and taxonomy information.
    """

    try:
        result = uniprot_api.stream_uniparc_cross_references_by_upi(uniparc_id=uniparc_id)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result

@tool(parse_docstring=True)
async def stream_uniparc_entries(uniparc_id: str):
    """
    Stream all UniParc entries associated with the specified search term in a single download.
    
    Args:
        uniparc_id: Search term for UniParc entries, typically a UniParc UPI ID (string, required), e.g. "UPI0000086E9C"

    Returns:
        A JSON string containing a list of UniParc entries matching the search term. Each entry includes the UniParc ID, sequence details (value, length, molecular weight, CRC64 checksum, MD5 hash), cross-reference count, UniProtKB accessions, common taxons, and sequence features from databases like Pfam, InterPro, and PROSITE.
    """

    try:
        result = uniprot_api.stream_uniparc_entries(uniparc_id=uniparc_id)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result

@tool(parse_docstring=True)
async def search_uniparc_entries(entry: str):
    """
    Search UniParc entries using a query, returns paginated list.
    
    Args:
        entry: Search term for UniParc entries, typically in the format "field:value" (e.g., "protein:hemoglobin") (string, required)
    
    Returns:
        A JSON string containing a paginated list of UniParc entries matching the search query. Each entry includes the UniParc ID, sequence details (value, length, molecular weight, CRC64 checksum, MD5 hash), cross-reference count, UniProtKB accessions, common taxons, sequence features from databases like Pfam and PROSITE, and cross-reference creation/update dates.
    """

    try:
        result = uniprot_api.search_uniparc_entries(entry=entry)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result

@tool(parse_docstring=True)
async def get_gene_centric_by_accession(accession: str):
    """
    Retrieve a GeneCentric entry by UniProtKB accession.
    
    Args:
        accession: UniProtKB accession ID (string), e.g., "P12345".
    
    Returns:
        A list of dictionaries containing:
        - Gene Name: The standardized gene symbol associated with the protein
        - Protein Name: The descriptive name of the protein
        - UniProtKB ID: The UniProt accession number (primary identifier)
        - Proteome ID: The identifier for the proteome entry containing the protein
        - Organism: Species name
        - Taxon ID: NCBI taxonomy identifier of the organism
        - Entry Type: UniProt entry status
        - Protein Existence: Evidence level for the protein
        - Flag Type: Additional annotation ('Precursor' indicates precursor status)
        - Sequence:
            - Length: Number of amino acids
            - Molecular Weight: Approximate mass in Daltons
            - CRC64: Checksum for the sequence
            - MD5: MD5 hash of the sequence
            - Sequence Version: Version number of the sequence in UniProt
    """

    try:
        result = uniprot_api.get_gene_centric_by_accession(accession=accession)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result

@tool(parse_docstring=True)
async def get_gene_centric_by_proteome(upid: str):
    """
    Search GeneCentric entry by Proteome ID to return all data associated with that entry.
    
    Args:
        upid: UniProt Proteome ID (string), e.g., "UP000005640".
    
    Returns:
        List of dictionaries containing:
        - Gene Name: The gene symbol
        - Protein Name: The full name or description of the protein
        - UniProtKB ID: The UniProt identifier for the canonical protein
        - Proteome ID: The proteome identifier where the protein belongs
        - Organism: The species name
        - Taxon ID: NCBI taxonomy ID
        - Entry Type: Status of the UniProt entry
        - Protein Existence: Evidence level
        - Flag Type: Annotation detail like "Precursor" or "Fragment"
        - Sequence:
            - Length: Amino acid count
            - Molecular Weight: In Daltons
            - CRC64: Checksum
            - MD5: MD5 hash
            - Sequence Version: The version number of the sequence
    """

    try:
        result = uniprot_api.get_gene_centric_by_proteome(upid=upid)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result

@tool(parse_docstring=True)
async def stream_gene_centric(accession: str):
    """
    Stream GeneCentric entries matching a query (max 10M entries).

    Args:
        accession (str): Search term for GeneCentric entries, e.g., "gene:PAX6".

    Returns:
        JSON string with all matching GeneCentric entries.
    """

    try:
        result = uniprot_api.stream_gene_centric(accession=accession)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result

@tool(parse_docstring=True)
async def search_gene_centric(accession: str):
    """
    Search GeneCentric entries with pagination, e.g., "gene:TP53".

    Args:
        accession (str): Search term for GeneCentric entries.

    Returns:
        JSON string with paginated GeneCentric entries.
    """

    try:
        result = uniprot_api.search_gene_centric(accession=accession)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result

@tool(parse_docstring=True)
async def get_proteome_by_id(upid: str):
    """
    Retrieve a proteome by UniProt Proteome ID.

    Args:
        upid (str): UniProt Proteome ID, e.g., "UP000002311".

    Returns:
        JSON string with proteome data.
    """

    try:
        result = uniprot_api.get_proteome_by_id(upid=upid)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result

@tool(parse_docstring=True)
async def stream_proteomes(query: str):
    """
    Stream Proteome entries matching a query (max 10M entries).

    Args:
        query (str): Search term for proteomes.

    Returns:
        JSON string with all matching proteomes.
    """
    try:
        result = uniprot_api.stream_proteomes(query=query)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result

@tool(parse_docstring=True)
async def search_proteomes(query: str, size: int = 50):
    """
    Search Proteome entries with pagination.

    Args:
        query (str): Search term for proteomes.
        size (int, optional): Number of entries per page. Default is 50.

    Returns:
        JSON string with paginated proteome entries.
    """
    try:
        result = uniprot_api.search_proteomes(query=query, size=size)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


uniport_tools = {
    "get_general_info_by_protein_or_gene_name": get_general_info_by_protein_or_gene_name,
    # "get_uniprotkb_entry_by_accession": get_uniprotkb_entry_by_accession,
    # "stream_uniprotkb_entries": stream_uniprotkb_entries,
    # "search_uniprotkb_entries": search_uniprotkb_entries,
    # "get_uniref_cluster_by_id": get_uniref_cluster_by_id,
    # "get_uniref_cluster_members_by_id": get_uniref_cluster_members_by_id,
    # "get_uniref_light_cluster_by_id": get_uniref_light_cluster_by_id,
    # "stream_uniref_clusters": stream_uniref_clusters,
    # "search_uniref_clusters": search_uniref_clusters,
    # "get_uniparc_entry_by_upi": get_uniparc_entry_by_upi,
    # "get_uniparc_light_entry_by_upi": get_uniparc_light_entry_by_upi,
    # "get_uniparc_cross_references_by_upi": get_uniparc_cross_references_by_upi,
    # "stream_uniparc_cross_references_by_upi": stream_uniparc_cross_references_by_upi,
    # "stream_uniparc_entries": stream_uniparc_entries,
    # "search_uniparc_entries": search_uniparc_entries,
    # "get_gene_centric_by_accession": get_gene_centric_by_accession,
    # "get_gene_centric_by_proteome": get_gene_centric_by_proteome,
    # "stream_gene_centric": stream_gene_centric,
    # "search_gene_centric": search_gene_centric,
    # "get_proteome_by_id": get_proteome_by_id,
    # "stream_proteomes": stream_proteomes,
    # "search_proteomes": search_proteomes
}