from typing import Dict, Any

from .literature import literature_tools
from .uniport import initialize_uniprot_api, uniport_tools
from .ucsc import initialize_ucsc_api, ucsc_tools
from .tcga import initialize_tcga_api, tcga_tools
from .STRING import initialize_string_api, string_tools
from .pubchem import initialize_pubchem_api, pubchem_tools
from .pdb import  initialize_pdb_api, pdb_tools
from .ncbi import initialize_ncbi_api, ncbi_tools
from .kegg import initialize_kegg_api, kegg_tools
from .ensembl import initialize_ensembl_api, ensembl_tools
from .dbsearch import initialize_dbsearch_api, dbsearch_tools
from .clinicaltrials import initialize_clinicaltrials_api, clinicaltrials_tools
from .chembl import initialize_chembl_api, chembl_tools
# from .search import initialize_search_engines, search_tools


def initialize_tools(config: Dict[str, Any]):
    """Initialize any global tool resources if needed"""
    pass
    initialize_uniprot_api()
    initialize_ucsc_api()
    initialize_tcga_api()
    initialize_string_api()
    initialize_pubchem_api(config.get("pubchem", {}))
    initialize_pdb_api()
    initialize_ncbi_api()
    initialize_kegg_api()
    initialize_ensembl_api()
    initialize_dbsearch_api()
    initialize_clinicaltrials_api()
    initialize_chembl_api()
    # initialize_search_engines(config.get("search_engines", {}))

def get_all_tools():
    """Get all available tools"""
    tools = {
        **literature_tools,
        **uniport_tools,
        **ucsc_tools,
        **tcga_tools,
        **string_tools,
        **pubchem_tools,
        **pdb_tools,
        **ncbi_tools,
        **kegg_tools,
        **ensembl_tools,
        **dbsearch_tools,
        **clinicaltrials_tools,
        **chembl_tools,
        # **search_tools,
    }

    return tools
