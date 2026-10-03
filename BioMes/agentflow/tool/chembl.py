import requests
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ChemblAPI:
    BASE_URL = "https://www.ebi.ac.uk/chembl/api/data"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'Accept': 'application/json'})

    def get_activity(self):
        """Retrieve activity object list."""

        result = self.session.get(self.BASE_URL + "/activity/?limit=5&offset=0")
        return result.text

    def get_activity_by_id(self, activity_id):
        """Retrieve single activity object details by ID."""
        result = self.session.get(self.BASE_URL + f"/activity/{activity_id}")
        return result.text

    def get_activity_by_ids(self, activity_ids:list):
        """Retrieve multiple activity objects by IDs."""
        ids_str = ";".join([str(id) for id in activity_ids])
        result = self.session.get(self.BASE_URL + f"/activity?set/{ids_str}")
        return result.text

    def search_activity(self, query_str):
        """Search activity using query string"""
        result = self.session.get(self.BASE_URL + f"/activity/search?q={query_str}&limit=1&offset=0")
        return result.text

    def get_activity_supplementary_data_by_activity(self):
        """Retrieve activitysupplementarydatabyactivity object list."""
        result = self.session.get(self.BASE_URL + "/activity_supplementary_data_by_activity/?limit=5&offset=0")
        return result.text

    def get_activity_supplementary_data_by_activity_by_id(self, activity_id):
        """Retrieve single activitysupplementarydatabyactivity object details by ID."""
        result = self.session.get(self.BASE_URL + f"/activity_supplementary_data_by_activity/{activity_id}")
        return result.text

    def get_activity_supplementary_data_by_activity_by_ids(self, activity_ids:list[int]):
        """Retrieve multiple activitysupplementarydatabyactivity objects by IDs."""
        ids_str = ";".join([str(id) for id in activity_ids])
        result = self.session.get(self.BASE_URL + f"/activity_supplementary_data_by_activity/set/{ids_str}")
        return result.text

    def get_assay(self):
        """Retrieve assay object list."""
        result = self.session.get(self.BASE_URL + "/assay/?limit=5&offset=0")
        return result.text

    def get_assay_by_id(self, assay_chembl_id):
        """Retrieve single assay object details by ID."""
        result = self.session.get(self.BASE_URL + f"/assay/{assay_chembl_id}")
        return result.text

    def get_assay_by_ids(self, assay_chembl_ids:list[str]):
        """Retrieve multiple assay objects by IDs."""
        ids_str = ";".join(assay_chembl_ids)
        result = self.session.get(self.BASE_URL + f"/assay/set/{ids_str}")
        return result.text

    def search_assay(self, query_str):
        """Search assay using query string."""
        result = self.session.get(self.BASE_URL + f"/assay/search?q={query_str}&limit=5&offset=0")
        return result.text

    def get_assay_class(self):
        """Retrieve assay_class object list."""
        result = self.session.get(self.BASE_URL + "/assay_class/?limit=5&offset=0")
        return result.text

    def get_assay_class_by_id(self, assay_class_id):
        """Retrieve single assay_class object details by ID."""
        result = self.session.get(self.BASE_URL + f"/assay_class/{assay_class_id}")
        return result.text

    def get_assay_class_by_ids(self, assay_class_ids:list):
        """Retrieve multiple assay_class objects by IDs."""
        ids_str = ";".join([str(id) for id in assay_class_ids])
        result = self.session.get(self.BASE_URL + f"/assay_class/set/{ids_str}")
        return result.text

    def get_atc_class(self):
        """Retrieve atc_class object list."""
        return self.session.get(self.BASE_URL + "/atc_class/").text

    def get_atc_class_by_id(self, level5):
        """Retrieve single atc_class object details by ID."""
        return self.session.get(self.BASE_URL + f"/atc_class/{level5}").text

    def get_atc_class_by_ids(self, level5s:list[str]):
        """Retrieve multiple atc_class objects by IDs."""
        ids_str = ";".join(level5s)
        return self.session.get(self.BASE_URL + f"/atc_class/set/{ids_str}").text

    def get_binding_site(self):
        """Retrieve binding_site object list."""
        return self.session.get(self.BASE_URL + "/binding_site/?limit=5&offset=0").text

    def get_binding_site_by_id(self, site_id):
        """Retrieve single binding_site object details by ID."""
        return self.session.get(self.BASE_URL + f"/binding_site/{site_id}").text

    def get_binding_site_by_ids(self, site_ids:list):
        """Retrieve multiple binding_site objects by IDs."""
        ids_str = ";".join([str(id) for id in site_ids])
        return self.session.get(self.BASE_URL + f"/binding_site/set/{ids_str}").text

    def get_biotherapeutic(self):
        """Retrieve biotherapeutic object list."""
        return self.session.get(self.BASE_URL + "/biotherapeutic/?limit=5&offset=0").text

    def get_biotherapeutic_by_id(self, molecule_chembl_id):
        """Retrieve single biotherapeutic object details by ID."""
        return self.session.get(self.BASE_URL + f"/biotherapeutic/{molecule_chembl_id}").text

    def get_biotherapeutic_by_ids(self, molecule_chembl_ids:list[str]):
        """Retrieve multiple biotherapeutic objects by IDs."""
        ids_str = ";".join(molecule_chembl_ids)
        return self.session.get(self.BASE_URL + f"/biotherapeutic/set/{ids_str}").text

    def get_cell_line(self):
        """Retrieve cell line object list."""
        return self.session.get(self.BASE_URL + "/cell_line/?limit=5&offset=0").text

    def get_cell_line_by_id(self, cell_id):
        """Retrieve single cell line object details by ID."""
        return self.session.get(self.BASE_URL + f"/cell_line/{cell_id}").text

    def get_cell_line_by_ids(self, cell_ids:list):
        """Retrieve multiple cell line objects by IDs."""
        ids_str = ";".join([str(id) for id in cell_ids])
        return self.session.get(self.BASE_URL + f"/cell_line/set/{ids_str}").text

    def get_chembl_id_lookup(self):
        """Retrieve chembl_id_lookup object list."""
        return self.session.get(self.BASE_URL + "/chembl_id_lookup/?limit=5&offset=0").text

    def get_chembl_id_lookup_by_id(self, chembl_id):
        """Retrieve single chembl_id_lookup object details by ID."""
        return self.session.get(self.BASE_URL + f"/chembl_id_lookup/{chembl_id}").text

    def get_chembl_id_lookup_by_ids(self, chembl_ids:list[str]):
        """Retrieve multiple chembl_id_lookup objects by IDs."""
        ids_str = ";".join(chembl_ids)
        return self.session.get(self.BASE_URL + f"/chembl_id_lookup/set/{ids_str}").text

    def search_chembl_id_lookup(self, query_str):
        """Search chemblidlookup using query string."""
        return self.session.get(self.BASE_URL + f"/chembl_id_lookup/search?q={query_str}&limit=1&offset=0").text

    def get_chembl_release(self):
        """Retrieve chembl_release object list."""
        return self.session.get(self.BASE_URL + "/chembl_release/?limit=5&offset=0").text

    def get_chembl_release_by_id(self, chembl_release):
        """Retrieve single chembl_release object details by ID."""
        if isinstance(chembl_release, str) and "CHEMBL_" in chembl_release:
            chembl_release = chembl_release.split("_")[1]
        return self.session.get(self.BASE_URL + f"/chembl_release/{chembl_release}").text

    def get_chembl_release_by_ids(self, chembl_releases:list):
        """Retrieve multiple chembl_release objects by IDs."""
        try:
            ids_str = ";".join([id.split("_")[1] if isinstance(id, str) and "CHEMBL_" in str(id) else id for id in chembl_releases])
        except Exception:
            ids_str = ";".join([str(id) for id in chembl_releases])
        return self.session.get(self.BASE_URL + f"/chembl_release/set/{ids_str}").text

    def get_compound_record(self):
        """Retrieve compound_record object list."""
        return self.session.get(self.BASE_URL + "/compound_record/?limit=5&offset=0").text

    def get_compound_record_by_id(self, record_id):
        """Retrieve single compound_record object details by ID."""
        return self.session.get(self.BASE_URL + f"/compound_record/{record_id}").text

    def get_compound_record_by_ids(self, record_ids:list):
        """Retrieve multiple compound_record objects by IDs."""
        ids_str = ";".join([str(id) for id in record_ids])
        return self.session.get(self.BASE_URL + f"/compound_record/set/{ids_str}").text

    def get_compound_structural_alert(self):
        """Retrieve compound_structural_alert object list."""
        return self.session.get(self.BASE_URL + "/compound_structural_alert/").text

    def get_compound_structural_alert_by_id(self, cpd_str_alert_id):
        """Retrieve single compound_structural_alert object details by ID."""
        return self.session.get(self.BASE_URL + f"/compound_structural_alert/{cpd_str_alert_id}").text

    def get_compound_structural_alert_by_ids(self, cpd_str_alert_ids:list):
        """Retrieve multiple compound_structural_alert objects by IDs."""
        ids_str = ";".join([str(id) for id in cpd_str_alert_ids])
        return self.session.get(self.BASE_URL + f"/compound_structural_alert/set/{ids_str}").text

    def get_document(self):
        """Retrieve document object list."""
        return self.session.get(self.BASE_URL + "/document/?limit=5&offset=0").text

    def get_document_by_id(self, document_chembl_id):
        """Retrieve single document object details by ID."""
        return self.session.get(self.BASE_URL + f"/document/{document_chembl_id}").text

    def get_document_by_ids(self, document_chembl_ids:list[str]):
        """Retrieve multiple document objects by IDs."""
        ids_str = ";".join(document_chembl_ids)
        return self.session.get(self.BASE_URL + f"/document/set/{ids_str}").text

    def search_document(self, query_str):
        """Search document using query string."""
        return self.session.get(self.BASE_URL + f"/document/search?q={query_str}&limit=1&offset=0").text

    def get_document_similarity(self):
        """Retrieve document similarity object list."""
        return self.session.get(self.BASE_URL + "/document_similarity/?limit=5&offset=0").text

    def get_document_similarity_by_id(self, document_1_chembl_id):
        """Retrieve single document similarity object details by ID."""
        return self.session.get(self.BASE_URL + f"/document_similarity/{document_1_chembl_id}").text

    def get_document_similarity_by_ids(self, document_1_chembl_ids:list[str]):
        """Retrieve multiple document similarity objects by IDs."""
        ids_str = ";".join(document_1_chembl_ids)
        return self.session.get(self.BASE_URL + f"/document_similarity/set/{ids_str}").text

    def get_drug(self):
        """Retrieve drug object list."""
        return self.session.get(self.BASE_URL + "/drug/?limit=5&offset=0").text

    def get_drug_by_id(self, molecule_chembl_id:str):
        """Retrieve single drug object details by ID."""
        return self.session.get(self.BASE_URL + f"/drug/{molecule_chembl_id}").text

    def get_drug_by_ids(self, molecule_chembl_ids:list[str]):
        """Retrieve multiple drus objects by IDs."""
        ids_str = ";".join(molecule_chembl_ids)
        return self.session.get(self.BASE_URL + f"/drug/set/{ids_str}").text

    def get_drug_indication(self):
        """Retrieve drug indication object list."""
        return self.session.get(self.BASE_URL + "/drug_indication/?limit=5&offset=0").text

    def get_drug_indication_by_id(self, drugind_id):
        """Retrieve drug indication object details by ID."""
        return self.session.get(self.BASE_URL + f"/drug_indication/{drugind_id}").text

    def get_drug_indication_by_ids(self, drugind_ids:list):
        """Retrieve multiple drug indication objects by IDs."""
        ids_str = ";".join([str(id) for id in drugind_ids])
        return self.session.get(self.BASE_URL + f"/drug_indication/set/{ids_str}").text

    def get_drug_warning(self):
        """Retrieve drug_warning object list."""
        return self.session.get(self.BASE_URL + "/drug_warning/?limit=5&offset=0").text

    def get_drug_warning_id(self, warning_id):
        """Retrieve single drug_warning object details by ID."""
        return self.session.get(self.BASE_URL + f"/drug_warning/{warning_id}").text

    def get_drug_warning_ids(self, warning_ids:list):
        """Retrieve multiple drug_warning objects by IDs."""
        ids_str = ";".join([str(id) for id in warning_ids])
        return self.session.get(self.BASE_URL + f"/drug_warning/set/{ids_str}").text

    def get_go_slim(self):
        """Retrieve go_slim object list."""
        return self.session.get(self.BASE_URL + "/go_slim/?limit=5&offset=0").text

    def get_go_slim_id(self, go_id):
        """Retrieve single go_slim object details by ID."""
        return self.session.get(self.BASE_URL + f"/go_slim/{go_id}").text

    def get_go_slim_ids(self, go_ids:list[str]):
        """Retrieve multiple go_slim objects by IDs."""
        ids_str = ";".join(go_ids)
        return self.session.get(self.BASE_URL + f"/go_slim/set/{ids_str}").text

    def get_mechanism(self):
        """Retrieve mechanism object list."""
        return self.session.get(self.BASE_URL + "/mechanism/?limit=5&offset=0").text

    def get_mechanism_id(self, mec_id):
        """Retrieve single mechanism object details by ID."""
        return self.session.get(self.BASE_URL + f"/mechanism/{mec_id}").text

    def get_mechanism_ids(self, mec_ids:list):
        """Retrieve multiple mechanism objects by IDs."""
        ids_str = ";".join([f"{id}" for id in mec_ids])
        return self.session.get(self.BASE_URL + f"/mechanism/set/{ids_str}").text

    def get_metabolism(self):
        """Retrieve metabolism object list."""
        return self.session.get(self.BASE_URL + "/metabolism/?limit=5&offset=0").text

    def get_metabolism_id(self, met_id):
        """Retrieve single metabolism object details by ID."""
        return self.session.get(self.BASE_URL + f"/metabolism/{met_id}").text

    def get_metabolism_ids(self, met_ids:list):
        """Retrieve multiple metabolism objects by IDs."""
        ids_str = ";".join([f"{id}" for id in met_ids])
        return self.session.get(self.BASE_URL + f"/metabolism/set/{ids_str}").text

    def get_molecule(self):
        """
            Retrieve list of molecules. Apart from the standard set of relation types, there is one specific operator:

            flexmatch - matches SMILES with the same structure, as opposed to exact match, for example: COc1ccc2[C@@H]3[C@H](COc2c1)C(C)(C)OC4=C3C(=O)C(=O)C5=C4OC (C)(C)[C@H]6COc7cc(OC)ccc7[C@@H]56 will match two molecules with:

            COc1ccc2[C@@H]3[C@H](COc2c1)C(C)(C)OC4=C3C(=O)C(=O)C5=C4OC (C)(C)[C@H]6COc7cc(OC)ccc7[C@@H]56 and

            COc1ccc2[C@@H]3[C@H](COc2c1)C(C)(C)OC4=C3C(=O)C(=O)C5=C4OC (C)(C)[C@@H]6COc7cc(OC)ccc7[C@H]56
            SMILES.
        """
        return self.session.get(self.BASE_URL + "/molecule/?limit=1&offset=0").text

    def get_molecule_id(self, molecule_chembl_id):
        """Retrieve single molecule object details by ID."""
        return self.session.get(self.BASE_URL + f"/molecule/{molecule_chembl_id}").text

    def get_molecule_ids(self, molecule_chembl_ids:list):
        """Retrieve multiple molecule objects by IDs."""
        ids_str = ";".join([f"{id}" for id in molecule_chembl_ids])
        return self.session.get(self.BASE_URL + f"/molecule/set/{ids_str}").text

    def search_molecule(self, query_str):
        """Search molecule using query string."""
        return self.session.get(self.BASE_URL + f"/molecule/search?q={query_str}&limit=1&offset=0").text

    def get_molecule_form(self):
        """Retrieve molecule_form object list."""
        return self.session.get(self.BASE_URL + "/molecule_form/?limit=5&offset=0").text

    def get_molecule_form_id(self, molecule_chembl_id):
        """Retrieve single metabolism object details by ID."""
        return self.session.get(self.BASE_URL + f"/molecule_form/{molecule_chembl_id}").text

    def get_molecule_form_ids(self, molecule_chembl_ids:list):
        """Retrieve multiple molecule_form objects by IDs."""
        ids_str = ";".join(molecule_chembl_ids)
        return self.session.get(self.BASE_URL + f"/molecule_form/set/{ids_str}").text

    def get_organism(self):
        """Retrieve organism object list."""
        return self.session.get(self.BASE_URL + "/organism/?limit=5&offset=0").text

    def get_organism_id(self, oc_id):
        """Retrieve single organism object details by ID."""
        return self.session.get(self.BASE_URL + f"/organism/{oc_id}").text

    def get_organism_ids(self, oc_ids:list):
        """Retrieve multiple organism objects by IDs."""
        ids_str = ";".join([str(id) for id in oc_ids])
        return self.session.get(self.BASE_URL + f"/organism/set/{ids_str}").text

    def get_protein_classification(self):
        """Retrieve protein_classification object list."""
        return self.session.get(self.BASE_URL + "/protein_classification/?limit=5&offset=0").text

    def get_protein_classification_id(self, protein_class_id):
        """Retrieve single protein_classification object details by ID."""
        return self.session.get(self.BASE_URL + f"/protein_classification/{protein_class_id}").text

    def get_protein_classification_ids(self, protein_class_ids:list):
        """Retrieve multiple protein_classification objects by IDs."""
        ids_str = ";".join([str(id) for id in protein_class_ids])
        return self.session.get(self.BASE_URL + f"/protein_classification/set/{ids_str}").text

    def search_protein_classification(self, query_str):
        """Search protein_classification using query string."""
        return self.session.get(self.BASE_URL + f"/protein_classification/search?q={query_str}&limit=1&offset=0").text

    def get_similarity_smiles(self,standard_inchi_key, similarity):
        """Retrieve single similarity object details by ID."""
        return self.session.get(self.BASE_URL + f"/similarity/{standard_inchi_key}/85").text

    def get_source(self):
        """Retrieve source object list."""
        return self.session.get(self.BASE_URL + "/source/?limit=5&offset=0").text

    def get_source_id(self, src_id):
        """Retrieve single source object details by ID."""
        return self.session.get(self.BASE_URL + f"/source/{src_id}").text

    def get_source_ids(self, src_ids:list):
        """Retrieve multiple source objects by IDs."""
        ids_str = ";".join([str(id) for id in src_ids])
        return self.session.get(self.BASE_URL + f"/source/set/{ids_str}").text

    def get_status(self):
        """Retrieve status object list."""
        return self.session.get(self.BASE_URL + "/status/?limit=5&offset=0").text

    def substructure_info(self, molecule_chembl_id):
        """Retrieve single substructure object details by ID."""
        return self.session.get(self.BASE_URL + f"/substructure/{molecule_chembl_id}").text

    def get_target(self):
        """Retrieve target object list."""
        return self.session.get(self.BASE_URL + "/target/?limit=5&offset=0").text

    def get_target_id(self, target_chembl_id):
        """Retrieve single target object details by ID."""
        return self.session.get(self.BASE_URL + f"/target/{target_chembl_id}").text

    def get_target_ids(self, target_chembl_ids:list):
        """Retrieve multiple target objects by IDs."""
        ids_str = ";".join(target_chembl_ids)
        return self.session.get(self.BASE_URL + f"/target/set/{ids_str}").text

    def search_target(self, query_str):
        """Search target using query string."""
        return self.session.get(self.BASE_URL + f"/target/search?q={query_str}&limit=1&offset=0").text

    def get_target_component(self):
        """Retrieve target_component object list."""
        return self.session.get(self.BASE_URL + "/target_component/?limit=5&offset=0").text

    def get_target_component_id(self, component_id):
        """Retrieve single target_component object details by ID."""
        return self.session.get(self.BASE_URL + f"/target_component/{component_id}").text

    def get_target_component_ids(self, component_ids: list):
        """Retrieve multiple target_component objects by IDs."""
        ids_str = ";".join([str(id) for id in component_ids])
        return self.session.get(self.BASE_URL + f"/target_component/set/{ids_str}").text

    def get_target_relation(self):
        """Retrieve target object list."""
        return self.session.get(self.BASE_URL + "/target_relation/?limit=5&offset=0").text

    def get_target_relation_id(self, related_target_chembl_id):
        """Retrieve single target_relation object details by ID."""
        return self.session.get(self.BASE_URL + f"/target_relation/{related_target_chembl_id}").text

    def get_target_relation_ids(self, related_target_chembl_ids: list):
        """Retrieve multiple target_relation objects by IDs."""
        ids_str = ";".join(related_target_chembl_ids)
        return self.session.get(self.BASE_URL + f"/target_relation/set/{ids_str}").text

    def get_tissue(self):
        """Retrieve tissue object list."""
        return self.session.get(self.BASE_URL + "/tissue/?limit=5&offset=0").text

    def get_tissue_id(self, tissue_chembl_id):
        """Retrieve single tissue object details by ID."""
        return self.session.get(self.BASE_URL + f"/tissue/{tissue_chembl_id}").text

    def get_tissue_ids(self, tissue_chembl_ids: list):
        """Retrieve multiple tissue objects by IDs."""
        ids_str = ";".join(tissue_chembl_ids)
        return self.session.get(self.BASE_URL + f"/tissue/set/{ids_str}").text

    def get_xref_source(self):
        """Retrieve xref_source object list."""
        return self.session.get(self.BASE_URL + "/xref_source/?limit=5&offset=0").text

    def get_xref_source_id(self, xref_src_db):
        """Retrieve single xref_source object details by ID."""
        return self.session.get(self.BASE_URL + f"/xref_source/{xref_src_db}").text

    def get_xref_source_ids(self, xref_src_dbs: list):
        """Retrieve multiple xref_source objects by IDs."""
        ids_str = ";".join(xref_src_dbs)
        return self.session.get(self.BASE_URL + f"/xref_source/set/{ids_str}").text

    def get_image(self, chembl_id):
        """Get image of the compound, specified by

            ChEMBL ID or
            Standard InChI Key
            You can specify optional parameters:

            engine - chemistry toolkit used for rendering, can be rdkit only, default: rdkit.
            dimensions - size of the image (the length of the square image side). Can't be more than 500, default: 500.
            ignoreCoords - Ignore 2D coordinates encoded in the molfile and let the chemistry toolkit to recompute them.
        """
        # self.session.headers.update({'Accept': 'application/svg'})
        return self.session.get(self.BASE_URL + f"/image/{chembl_id}").text



from typing import Any, Dict, List, Optional
import json

from langchain_core.tools import tool


_chembl_api: Optional[ChemblAPI] = None


def initialize_chembl_api(config: Optional[Dict[str, Any]] = None) -> None:
    """
    Initialize the global ChemblAPI client.
    """
    global _chembl_api
    if _chembl_api is None:
        _chembl_api = ChemblAPI()


def get_chembl_api() -> ChemblAPI:
    """
    Get the global ChemblAPI client, creating it if needed.
    """
    global _chembl_api
    if _chembl_api is None:
        _chembl_api = ChemblAPI()
    return _chembl_api


@tool(parse_docstring=True)
async def get_activity() -> Any:
    """
    Retrieve a default list of bioactivity data entries from ChEMBL.

    Returns:
        A list of activity objects from the ChEMBL database.
    """
    api = get_chembl_api()
    try:
        result = api.get_activity()
    except Exception as e:
        return [{"error": f"An error occurred while querying get_activity: {str(e)}"}]
    return result


@tool(parse_docstring=True)
async def get_activity_by_id(activity_id: int) -> Any:
    """
    Retrieve details of a single bioactivity entry by its activity ID.

    Args:
        activity_id: Unique integer identifier for the ChEMBL activity entry.

    Returns:
        A dictionary with the detailed properties of the activity entry.
    """
    api = get_chembl_api()
    try:
        result = api.get_activity_by_id(activity_id)
    except Exception as e:
        return [
            {"error": f"An error occurred while querying get_activity_by_id: {str(e)}"}
        ]
    return result


@tool(parse_docstring=True)
async def get_activity_by_ids(activity_ids: List[int]) -> Any:
    """
    Retrieve a list of bioactivity entries by a list of activity IDs.

    Args:
        activity_ids: List of unique integer identifiers for activity entries.

    Returns:
        A list of activity objects, depending on API behavior.
    """
    api = get_chembl_api()
    try:
        result = api.get_activity_by_ids(activity_ids)
    except Exception as e:
        return [
            {"error": f"An error occurred while querying get_activity_by_ids: {str(e)}"}
        ]
    return result


@tool(parse_docstring=True)
async def search_activity(query_str: str) -> Any:
    """
    Search bioactivity data using a full-text query string.

    Args:
        query_str: Search string such as a target name or keyword.

    Returns:
        A list of activity objects that match the query.
    """
    api = get_chembl_api()
    try:
        result = api.search_activity(query_str)
    except Exception as e:
        return [
            {"error": f"An error occurred while querying search_activity: {str(e)}"}
        ]
    return result


@tool(parse_docstring=True)
async def get_activity_supplementary_data_by_activity() -> Any:
    """
    Retrieve a default list of supplementary bioactivity data from ChEMBL.

    Returns:
        A list of supplementary activity data objects.
    """
    api = get_chembl_api()
    try:
        result = api.get_activity_supplementary_data_by_activity()
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_activity: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def get_activity_supplementary_data_by_activity_by_id(
    activity_id: int,
) -> Any:
    """
    Retrieve supplementary activity data for a single activity ID.

    Args:
        activity_id: Unique ID for the activity.

    Returns:
        A supplementary data object for the activity.
    """
    api = get_chembl_api()
    try:
        result = api.get_activity_supplementary_data_by_activity_by_id(activity_id)
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_activity_supplementary_data_by_activity_by_id: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def get_activity_supplementary_data_by_activity_by_ids(
    activity_ids: List[int],
) -> Any:
    """
    Retrieve supplementary activity data for multiple activity IDs.

    Args:
        activity_ids: List of activity IDs.

    Returns:
        A list of supplementary data objects for the activities.
    """
    api = get_chembl_api()
    try:
        result = api.get_activity_supplementary_data_by_activity_by_ids(activity_ids)
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_activity_supplementary_data_by_activity_by_ids: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def get_assay() -> Any:
    """
    Retrieve a default list of assay-related data objects.

    Returns:
        A list of bioactivity or assay-related objects.
    """
    api = get_chembl_api()
    try:
        result = api.get_activity()
    except Exception as e:
        return [{"error": f"An error occurred while querying get_activity: {str(e)}"}]
    return result


@tool(parse_docstring=True)
async def get_assay_by_id(assay_chembl_id: str) -> Any:
    """
    Retrieve details for a single assay by its ChEMBL ID.

    Args:
        assay_chembl_id: ChEMBL identifier for the assay.

    Returns:
        A dictionary with assay properties.
    """
    api = get_chembl_api()
    try:
        result = api.get_assay_by_id(assay_chembl_id)
    except Exception as e:
        return [
            {"error": f"An error occurred while querying get_assay_by_id: {str(e)}"}
        ]
    return result


@tool(parse_docstring=True)
async def get_assay_by_ids(assay_chembl_ids: List[str]) -> Any:
    """
    Retrieve details for multiple assays by their ChEMBL IDs.

    Args:
        assay_chembl_ids: List of assay ChEMBL identifiers.

    Returns:
        A list of assay dictionaries.
    """
    api = get_chembl_api()
    try:
        result = api.get_assay_by_ids(assay_chembl_ids)
    except Exception as e:
        return [
            {"error": f"An error occurred while querying get_assay_by_ids: {str(e)}"}
        ]
    return result


@tool(parse_docstring=True)
async def search_assay(query_str: str) -> Any:
    """
    Search assays using a full-text query string.

    Args:
        query_str: Search string such as a protein name or keyword.

    Returns:
        A list of assay objects that match the query.
    """
    api = get_chembl_api()
    try:
        result = api.search_assay(query_str)
    except Exception as e:
        return [
            {"error": f"An error occurred while querying search_assay: {str(e)}"}
        ]
    return result


@tool(parse_docstring=True)
async def get_assay_class() -> Any:
    """
    Retrieve a default list of assay classifications.

    Returns:
        A list of assay classification objects.
    """
    api = get_chembl_api()
    try:
        result = api.get_assay_class()
    except Exception as e:
        return [
            {"error": f"An error occurred while querying get_assay_class: {str(e)}"}
        ]
    return result


@tool(parse_docstring=True)
async def get_assay_class_by_id(assay_class_id: int) -> Any:
    """
    Retrieve details for a single assay classification by ID.

    Args:
        assay_class_id: Unique integer identifier for the assay classification.

    Returns:
        A dictionary with assay classification properties.
    """
    api = get_chembl_api()
    try:
        result = api.get_assay_class_by_id(assay_class_id)
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_assay_class_by_id: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def get_assay_class_by_ids(assay_class_ids: List[int]) -> Any:
    """
    Retrieve details for multiple assay classifications by IDs.

    Args:
        assay_class_ids: List of integer identifiers for assay classifications.

    Returns:
        A list of assay classification dictionaries.
    """
    api = get_chembl_api()
    try:
        result = api.get_assay_class_by_ids(assay_class_ids)
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_assay_class_by_ids: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def get_atc_class() -> Any:
    """
    Retrieve a default list of ATC classifications.

    Returns:
        A list of ATC class objects.
    """
    api = get_chembl_api()
    try:
        result = api.get_atc_class()
    except Exception as e:
        return [{"error": f"An error occurred while querying get_atc_class: {str(e)}"}]
    return result


@tool(parse_docstring=True)
async def get_atc_class_by_id(level5: str) -> Any:
    """
    Retrieve details for a single ATC classification by level 5 ATC code.

    Args:
        level5: Level 5 ATC code string.

    Returns:
        A dictionary with ATC classification properties.
    """
    api = get_chembl_api()
    try:
        result = api.get_atc_class_by_id(level5)
    except Exception as e:
        return [
            {"error": f"An error occurred while querying get_atc_class_by_id: {str(e)}"}
        ]
    return result


@tool(parse_docstring=True)
async def get_atc_class_by_ids(level5s: List[str]) -> Any:
    """
    Retrieve details for multiple ATC classifications by level 5 codes.

    Args:
        level5s: List of level 5 ATC code strings.

    Returns:
        A list of ATC classification dictionaries.
    """
    api = get_chembl_api()
    try:
        result = api.get_atc_class_by_ids(level5s)
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_atc_class_by_ids: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def get_binding_site() -> Any:
    """
    Retrieve a default list of binding sites.

    Returns:
        A list of binding site objects.
    """
    api = get_chembl_api()
    try:
        result = api.get_binding_site()
    except Exception as e:
        return [
            {"error": f"An error occurred while querying get_binding_site: {str(e)}"}
        ]
    return result


@tool(parse_docstring=True)
async def get_binding_site_by_id(site_id: int) -> Any:
    """
    Retrieve details for a single binding site by ID.

    Args:
        site_id: Unique integer identifier for the binding site.

    Returns:
        A dictionary with binding site properties.
    """
    api = get_chembl_api()
    try:
        result = api.get_binding_site_by_id(site_id)
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_binding_site_by_id: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def get_binding_site_by_ids(site_ids: List[int]) -> Any:
    """
    Retrieve details for multiple binding sites by IDs.

    Args:
        site_ids: List of unique integer identifiers for binding sites.

    Returns:
        A list of binding site dictionaries.
    """
    api = get_chembl_api()
    try:
        result = api.get_binding_site_by_ids(site_ids)
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_binding_site_by_ids: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def get_biotherapeutic() -> Any:
    """
    Retrieve a default list of biotherapeutics.

    Returns:
        A list of biotherapeutic objects.
    """
    api = get_chembl_api()
    try:
        result = api.get_biotherapeutic()
    except Exception as e:
        return [
            {"error": f"An error occurred while querying get_biotherapeutic: {str(e)}"}
        ]
    return result


@tool(parse_docstring=True)
async def get_biotherapeutic_by_id(molecule_chembl_id: str) -> Any:
    """
    Retrieve details for a single biotherapeutic by molecule ChEMBL ID.

    Args:
        molecule_chembl_id: ChEMBL identifier for the biotherapeutic.

    Returns:
        A dictionary with biotherapeutic properties.
    """
    api = get_chembl_api()
    try:
        result = api.get_biotherapeutic_by_id(molecule_chembl_id)
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_biotherapeutic_by_id: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def get_biotherapeutic_by_ids(molecule_chembl_ids: List[str]) -> Any:
    """
    Retrieve details for multiple biotherapeutics by molecule ChEMBL IDs.

    Args:
        molecule_chembl_ids: List of biotherapeutic molecule ChEMBL identifiers.

    Returns:
        A list of biotherapeutic dictionaries.
    """
    api = get_chembl_api()
    try:
        result = api.get_biotherapeutic_by_ids(molecule_chembl_ids)
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_biotherapeutic_by_ids: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def get_cell_line() -> Any:
    """
    Retrieve a default list of cell lines.

    Returns:
        A list of cell line objects.
    """
    api = get_chembl_api()
    try:
        result = api.get_cell_line()
    except Exception as e:
        return [{"error": f"An error occurred while querying get_cell_line: {str(e)}"}]
    return result


@tool(parse_docstring=True)
async def get_cell_line_by_id(cell_id: int) -> Any:
    """
    Retrieve details for a single cell line by ID.

    Args:
        cell_id: Unique integer identifier for the cell line.

    Returns:
        A dictionary with cell line properties.
    """
    api = get_chembl_api()
    try:
        result = api.get_cell_line_by_id(cell_id)
    except Exception as e:
        return [
            {"error": f"An error occurred while querying get_cell_line_by_id: {str(e)}"}
        ]
    return result


@tool(parse_docstring=True)
async def get_cell_line_by_ids(cell_ids: List[int]) -> Any:
    """
    Retrieve details for multiple cell lines by IDs.

    Args:
        cell_ids: List of unique integer identifiers for cell lines.

    Returns:
        A list of cell line dictionaries.
    """
    api = get_chembl_api()
    try:
        result = api.get_cell_line_by_ids(cell_ids)
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_cell_line_by_ids: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def get_chembl_id_lookup() -> Any:
    """
    Retrieve a default list of ChEMBL ID lookup objects.

    Returns:
        A JSON object containing ChEMBL ID lookup data.
    """
    api = get_chembl_api()
    try:
        result = api.get_chembl_id_lookup()
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_chembl_id_lookup: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def get_chembl_id_lookup_by_id(chembl_id: str) -> Any:
    """
    Retrieve ChEMBL ID lookup information for a single ChEMBL ID.

    Args:
        chembl_id: ChEMBL identifier string.

    Returns:
        A JSON object with entity information mapped to the ChEMBL ID.
    """
    api = get_chembl_api()
    try:
        result = api.get_chembl_id_lookup_by_id(chembl_id)
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_chembl_id_lookup_by_id: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def get_chembl_id_lookup_by_ids(chembl_ids: List[str]) -> Any:
    """
    Retrieve ChEMBL ID lookup information for multiple ChEMBL IDs.

    Args:
        chembl_ids: List of ChEMBL identifier strings.

    Returns:
        A JSON object with bulk lookup results.
    """
    api = get_chembl_api()
    try:
        result = api.get_chembl_id_lookup_by_ids(chembl_ids)
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_chembl_id_lookup_by_ids: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def search_chembl_id_lookup(query_str: str) -> Any:
    """
    Search ChEMBL ID lookup using a Lucene query string.

    Args:
        query_str: Query string in Lucene syntax.

    Returns:
        A paginated JSON response with search results.
    """
    api = get_chembl_api()
    try:
        result = api.search_chembl_id_lookup(query_str)
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying search_chembl_id_lookup: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def get_chembl_release() -> Any:
    """
    Retrieve a list of ChEMBL release metadata objects.

    Returns:
        A JSON object with release metadata.
    """
    api = get_chembl_api()
    try:
        result = api.get_chembl_release()
    except Exception as e:
        return [
            {"error": f"An error occurred while querying get_chembl_release: {str(e)}"}
        ]
    return result


@tool(parse_docstring=True)
async def get_chembl_release_by_id(chembl_release: str) -> Any:
    """
    Retrieve metadata for a specific ChEMBL release.

    Args:
        chembl_release: ChEMBL release version string.

    Returns:
        A JSON object with metadata for the specified release.
    """
    api = get_chembl_api()
    try:
        result = api.get_chembl_release_by_id(chembl_release)
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_chembl_release_by_id: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def get_chembl_release_by_ids(chembl_releases: List[str]) -> Any:
    """
    Retrieve metadata for multiple ChEMBL releases.

    Args:
        chembl_releases: List of release version strings.

    Returns:
        A JSON object with metadata for each specified release.
    """
    api = get_chembl_api()
    try:
        result = api.get_chembl_release_by_ids(chembl_releases)
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_chembl_release_by_ids: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def get_compound_record() -> Any:
    """
    Retrieve a default list of compound record objects.

    Returns:
        A JSON object with compound record metadata.
    """
    api = get_chembl_api()
    try:
        result = api.get_compound_record()
    except Exception as e:
        return [
            {"error": f"An error occurred while querying get_compound_record: {str(e)}"}
        ]
    return result


@tool(parse_docstring=True)
async def get_compound_record_by_id(record_id: int) -> Any:
    """
    Retrieve compound record details by internal record ID.

    Args:
        record_id: Internal integer record ID for a compound.

    Returns:
        A JSON object with compound metadata.
    """
    api = get_chembl_api()
    try:
        result = api.get_compound_record_by_id(record_id)
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_compound_record_by_id: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def get_compound_record_by_ids(record_ids: List[int]) -> Any:
    """
    Retrieve compound record details for multiple record IDs.

    Args:
        record_ids: List of internal integer record IDs.

    Returns:
        A JSON object with compound metadata for each record ID.
    """
    api = get_chembl_api()
    try:
        result = api.get_compound_record_by_ids(record_ids)
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_compound_record_by_ids: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def get_compound_structural_alert() -> Any:
    """
    Retrieve a default list of compound structural alerts.

    Returns:
        A JSON object with structural alert metadata.
    """
    api = get_chembl_api()
    try:
        result = api.get_compound_structural_alert()
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_compound_structural_alert: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def get_compound_structural_alert_by_id(cpd_str_alert_id: int) -> Any:
    """
    Retrieve compound structural alert details by ID.

    Args:
        cpd_str_alert_id: Internal integer ID of the structural alert.

    Returns:
        A JSON object with structural alert details.
    """
    api = get_chembl_api()
    try:
        result = api.get_compound_structural_alert_by_id(cpd_str_alert_id)
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_compound_structural_alert_by_id: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def get_compound_structural_alert_by_ids(cpd_str_alert_ids: List[int]) -> Any:
    """
    Retrieve structural alert details for multiple IDs.

    Args:
        cpd_str_alert_ids: List of structural alert IDs.

    Returns:
        A JSON object with structural alert details for each ID.
    """
    api = get_chembl_api()
    try:
        result = api.get_compound_structural_alert_by_ids(cpd_str_alert_ids)
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_compound_structural_alert_by_ids: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def get_document() -> Any:
    """
    Retrieve a default list of ChEMBL documents.

    Returns:
        A JSON object with document metadata.
    """
    api = get_chembl_api()
    try:
        result = api.get_document()
    except Exception as e:
        return [{"error": f"An error occurred while querying get_document: {str(e)}"}]
    return result


@tool(parse_docstring=True)
async def get_document_by_id(document_chembl_id: str) -> Any:
    """
    Retrieve document details by document ChEMBL ID.

    Args:
        document_chembl_id: ChEMBL identifier of the document.

    Returns:
        A JSON object with document metadata.
    """
    api = get_chembl_api()
    try:
        result = api.get_document_by_id(document_chembl_id)
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_document_by_id: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def get_document_by_ids(document_chembl_ids: List[str]) -> Any:
    """
    Retrieve document details for multiple document ChEMBL IDs.

    Args:
        document_chembl_ids: List of document ChEMBL identifiers.

    Returns:
        A JSON object with document metadata for each ID.
    """
    api = get_chembl_api()
    try:
        result = api.get_document_by_ids(document_chembl_ids)
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_document_by_ids: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def search_document(query_str: str) -> Any:
    """
    Search documents using a Lucene query string.

    Args:
        query_str: Query string in Lucene syntax.

    Returns:
        A paginated JSON response with document search results.
    """
    api = get_chembl_api()
    try:
        result = api.search_document(query_str)
    except Exception as e:
        return [
            {"error": f"An error occurred while querying search_document: {str(e)}"}
        ]
    return result


@tool(parse_docstring=True)
async def get_document_similarity() -> Any:
    """
    Retrieve a default list of document similarity objects.

    Returns:
        A JSON object with similar documents and similarity scores.
    """
    api = get_chembl_api()
    try:
        result = api.get_document_similarity()
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_document_similarity: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def get_document_similarity_by_id(document_1_chembl_id: str) -> Any:
    """
    Retrieve document similarity results for a single reference document.

    Args:
        document_1_chembl_id: ChEMBL ID of the reference document.

    Returns:
        A JSON object with similarity results.
    """
    api = get_chembl_api()
    try:
        result = api.get_document_similarity_by_id(document_1_chembl_id)
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_document_similarity_by_id: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def get_document_similarity_by_ids(document_1_chembl_ids: List[str]) -> Any:
    """
    Retrieve document similarity results for multiple reference documents.

    Args:
        document_1_chembl_ids: List of reference document ChEMBL IDs.

    Returns:
        A JSON object with similarity results for each reference document.
    """
    api = get_chembl_api()
    try:
        result = api.get_document_similarity_by_ids(document_1_chembl_ids)
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_document_similarity_by_ids: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def get_drug() -> Any:
    """
    Retrieve a default list of drug objects.

    Returns:
        A JSON object with drug metadata.
    """
    api = get_chembl_api()
    try:
        result = api.get_drug()
    except Exception as e:
        return [{"error": f"An error occurred while querying get_drug: {str(e)}"}]
    return result


@tool(parse_docstring=True)
async def get_drug_by_id(molecule_chembl_id: str) -> Any:
    """
    Retrieve drug details by molecule ChEMBL ID.

    Args:
        molecule_chembl_id: ChEMBL identifier of the drug.

    Returns:
        A JSON object with drug metadata.
    """
    api = get_chembl_api()
    try:
        result = api.get_drug_by_id(molecule_chembl_id)
    except Exception as e:
        return [{"error": f"An error occurred while querying get_drug_by_id: {str(e)}"}]
    return result


@tool(parse_docstring=True)
async def get_drug_by_ids(molecule_chembl_ids: List[str]) -> Any:
    """
    Retrieve drug details for multiple molecule ChEMBL IDs.

    Args:
        molecule_chembl_ids: List of drug molecule ChEMBL identifiers.

    Returns:
        A JSON object with drug metadata for each ID.
    """
    api = get_chembl_api()
    try:
        result = api.get_drug_by_ids(molecule_chembl_ids)
    except Exception as e:
        return [
            {"error": f"An error occurred while querying get_drug_by_ids: {str(e)}"}
        ]
    return result


@tool(parse_docstring=True)
async def get_drug_indication() -> Any:
    """
    Retrieve a default list of drug indication objects.

    Returns:
        A JSON object with drug indication data.
    """
    api = get_chembl_api()
    try:
        result = api.get_drug_indication()
    except Exception as e:
        return [
            {"error": f"An error occurred while querying get_drug_indication: {str(e)}"}
        ]
    return result


@tool(parse_docstring=True)
async def get_drug_indication_by_id(drugind_id: int) -> Any:
    """
    Retrieve drug indication details by ID.

    Args:
        drugind_id: Internal integer ID of the drug indication.

    Returns:
        A JSON object with indication details.
    """
    api = get_chembl_api()
    try:
        result = api.get_drug_indication_by_id(drugind_id)
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_drug_indication_by_id: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def get_drug_indication_by_ids(drugind_ids: List[int]) -> Any:
    """
    Retrieve drug indication details for multiple IDs.

    Args:
        drugind_ids: List of drug indication IDs.

    Returns:
        A JSON object with indication details for each ID.
    """
    api = get_chembl_api()
    try:
        result = api.get_drug_indication_by_ids(drugind_ids)
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_drug_indication_by_ids: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def get_drug_warning() -> Any:
    """
    Retrieve a default list of drug warning objects.

    Returns:
        A JSON object with drug safety warning data.
    """
    api = get_chembl_api()
    try:
        result = api.get_drug_warning()
    except Exception as e:
        return [
            {"error": f"An error occurred while querying get_drug_warning: {str(e)}"}
        ]
    return result


@tool(parse_docstring=True)
async def get_drug_warning_id(warning_id: int) -> Any:
    """
    Retrieve drug warning details by ID.

    Args:
        warning_id: Internal integer ID of the drug warning.

    Returns:
        A JSON object with warning details.
    """
    api = get_chembl_api()
    try:
        result = api.get_drug_warning_id(warning_id)
    except Exception as e:
        return [
            {"error": f"An error occurred while querying get_drug_warning_id: {str(e)}"}
        ]
    return result


@tool(parse_docstring=True)
async def get_drug_warning_ids(warning_ids: List[int]) -> Any:
    """
    Retrieve drug warning details for multiple IDs.

    Args:
        warning_ids: List of internal IDs of drug warnings.

    Returns:
        A JSON object with warning details for each ID.
    """
    api = get_chembl_api()
    try:
        result = api.get_drug_warning_ids(warning_ids)
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_drug_warning_ids: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def get_go_slim() -> Any:
    """
    Retrieve a default list of GO slim classifications.

    Returns:
        A list of GO slim objects.
    """
    api = get_chembl_api()
    try:
        result = api.get_go_slim()
    except Exception as e:
        return [{"error": f"An error occurred while querying get_go_slim: {str(e)}"}]
    return result


@tool(parse_docstring=True)
async def get_go_slim_id(go_id: str) -> Any:
    """
    Retrieve GO slim classification details by GO ID.

    Args:
        go_id: GO identifier string.

    Returns:
        A dictionary with GO slim properties.
    """
    api = get_chembl_api()
    try:
        result = api.get_go_slim_id(go_id)
    except Exception as e:
        return [{"error": f"An error occurred while querying get_go_slim_id: {str(e)}"}]
    return result


@tool(parse_docstring=True)
async def get_go_slim_ids(go_ids: List[str]) -> Any:
    """
    Retrieve GO slim classification details for multiple GO IDs.

    Args:
        go_ids: List of GO identifier strings.

    Returns:
        A list of GO slim dictionaries.
    """
    api = get_chembl_api()
    try:
        result = api.get_go_slim_ids(go_ids)
    except Exception as e:
        return [
            {"error": f"An error occurred while querying get_go_slim_ids: {str(e)}"}
        ]
    return result


@tool(parse_docstring=True)
async def get_mechanism() -> Any:
    """
    Retrieve a default list of mechanisms of action.

    Returns:
        A list of mechanism objects.
    """
    api = get_chembl_api()
    try:
        result = api.get_mechanism()
    except Exception as e:
        return [{"error": f"An error occurred while querying get_mechanism: {str(e)}"}]
    return result


@tool(parse_docstring=True)
async def get_mechanism_id(mec_id: int) -> Any:
    """
    Retrieve mechanism of action details by ID.

    Args:
        mec_id: Unique integer identifier for the mechanism.

    Returns:
        A dictionary with mechanism properties.
    """
    api = get_chembl_api()
    try:
        result = api.get_mechanism_id(mec_id)
    except Exception as e:
        return [{"error": f"An error occurred while querying get_mechanism_id: {str(e)}"}]
    return result


@tool(parse_docstring=True)
async def get_mechanism_ids(mec_ids: List[int]) -> Any:
    """
    Retrieve mechanism of action details for multiple IDs.

    Args:
        mec_ids: List of mechanism IDs.

    Returns:
        A list of mechanism dictionaries.
    """
    api = get_chembl_api()
    try:
        result = api.get_mechanism_ids(mec_ids)
    except Exception as e:
        return [{"error": f"An error occurred while querying get_mechanism_ids: {str(e)}"}]
    return result


@tool(parse_docstring=True)
async def get_metabolism() -> Any:
    """
    Retrieve a default list of metabolism records.

    Returns:
        A list of metabolism objects.
    """
    api = get_chembl_api()
    try:
        result = api.get_metabolism()
    except Exception as e:
        return [{"error": f"An error occurred while querying get_metabolism: {str(e)}"}]
    return result


@tool(parse_docstring=True)
async def get_metabolism_id(met_id: int) -> Any:
    """
    Retrieve metabolism record details by ID.

    Args:
        met_id: Primary key of a metabolism record.

    Returns:
        A dictionary with metabolism record properties.
    """
    api = get_chembl_api()
    try:
        result = api.get_metabolism_id(met_id)
    except Exception as e:
        return [
            {"error": f"An error occurred while querying get_metabolism_id: {str(e)}"}
        ]
    return result


@tool(parse_docstring=True)
async def get_metabolism_ids(met_ids: List[int]) -> Any:
    """
    Retrieve metabolism record details for multiple IDs.

    Args:
        met_ids: List of metabolism record IDs.

    Returns:
        A list of metabolism dictionaries.
    """
    api = get_chembl_api()
    try:
        result = api.get_metabolism_ids(met_ids)
    except Exception as e:
        return [
            {"error": f"An error occurred while querying get_metabolism_ids: {str(e)}"}
        ]
    return result


@tool(parse_docstring=True)
async def get_molecule() -> Any:
    """
    Retrieve a default list of molecules.

    Returns:
        A list of molecule objects.
    """
    api = get_chembl_api()
    try:
        result = api.get_molecule()
    except Exception as e:
        return [{"error": f"An error occurred while querying get_molecule: {str(e)}"}]
    return result


@tool(parse_docstring=True)
async def get_molecule_id(molecule_chembl_id: str) -> Any:
    """
    Retrieve molecule details by molecule ChEMBL ID.

    Args:
        molecule_chembl_id: ChEMBL identifier for the molecule.

    Returns:
        A dictionary with molecule properties.
    """
    api = get_chembl_api()
    try:
        result = api.get_molecule_id(molecule_chembl_id)
    except Exception as e:
        return [{"error": f"An error occurred while querying get_molecule_id: {str(e)}"}]
    return result


@tool(parse_docstring=True)
async def get_molecule_ids(molecule_chembl_ids: List[str]) -> Any:
    """
    Retrieve molecule details for multiple molecule ChEMBL IDs.

    Args:
        molecule_chembl_ids: List of molecule ChEMBL identifiers.

    Returns:
        A list of molecule dictionaries.
    """
    api = get_chembl_api()
    try:
        result = api.get_molecule_ids(molecule_chembl_ids)
    except Exception as e:
        return [
            {"error": f"An error occurred while querying get_molecule_ids: {str(e)}"}
        ]
    return result


@tool(parse_docstring=True)
async def search_molecule(query_str: str) -> Any:
    """
    Search molecules using a full-text query string.

    Args:
        query_str: Search string, for example a molecule name.

    Returns:
        A list of molecule objects that match the query.
    """
    api = get_chembl_api()
    try:
        result = api.search_molecule(query_str)
    except Exception as e:
        return [
            {"error": f"An error occurred while querying search_molecule: {str(e)}"}
        ]
    return result


@tool(parse_docstring=True)
async def get_molecule_form() -> Any:
    """
    Retrieve a default list of molecule forms.

    Returns:
        A list of molecule form objects.
    """
    api = get_chembl_api()
    try:
        result = api.get_molecule_form()
    except Exception as e:
        return [
            {"error": f"An error occurred while querying get_molecule_form: {str(e)}"}
        ]
    return result


@tool(parse_docstring=True)
async def get_molecule_form_id(molecule_chembl_id: str) -> Any:
    """
    Retrieve molecule form information by molecule ChEMBL ID.

    Args:
        molecule_chembl_id: ChEMBL identifier for the molecule.

    Returns:
        A dictionary with molecule form details.
    """
    api = get_chembl_api()
    try:
        result = api.get_molecule_form_id(molecule_chembl_id)
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_molecule_form_id: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def get_molecule_form_ids(molecule_chembl_ids: List[str]) -> Any:
    """
    Retrieve molecule form information for multiple molecule ChEMBL IDs.

    Args:
        molecule_chembl_ids: List of molecule ChEMBL identifiers.

    Returns:
        A list of dictionaries with molecule form details.
    """
    api = get_chembl_api()
    try:
        result = api.get_molecule_form_ids(molecule_chembl_ids)
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_molecule_form_ids: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def get_organism() -> Any:
    """
    Retrieve a default list of organisms.

    Returns:
        A list of organism objects.
    """
    api = get_chembl_api()
    try:
        result = api.get_organism()
    except Exception as e:
        return [{"error": f"An error occurred while querying get_organism: {str(e)}"}]
    return result


@tool(parse_docstring=True)
async def get_organism_id(oc_id: int) -> Any:
    """
    Retrieve organism details by ID.

    Args:
        oc_id: Unique integer identifier for the organism.

    Returns:
        A dictionary with organism properties.
    """
    api = get_chembl_api()
    try:
        result = api.get_organism_id(oc_id)
    except Exception as e:
        return [{"error": f"An error occurred while querying get_organism_id: {str(e)}"}]
    return result


@tool(parse_docstring=True)
async def get_organism_ids(oc_ids: List[int]) -> Any:
    """
    Retrieve organism details for multiple IDs.

    Args:
        oc_ids: List of organism IDs.

    Returns:
        A list of organism dictionaries.
    """
    api = get_chembl_api()
    try:
        result = api.get_organism_ids(oc_ids)
    except Exception as e:
        return [{"error": f"An error occurred while querying get_organism_ids: {str(e)}"}]
    return result


@tool(parse_docstring=True)
async def get_protein_classification() -> Any:
    """
    Retrieve a default list of protein classifications.

    Returns:
        A list of protein classification objects.
    """
    api = get_chembl_api()
    try:
        result = api.get_protein_classification()
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_protein_classification: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def get_protein_classification_id(protein_class_id: int) -> Any:
    """
    Retrieve protein classification details by ID.

    Args:
        protein_class_id: Unique integer identifier for the protein classification.

    Returns:
        A dictionary with protein classification properties.
    """
    api = get_chembl_api()
    try:
        result = api.get_protein_classification_id(protein_class_id)
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_protein_classification_id: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def get_protein_classification_ids(protein_class_ids: List[int]) -> Any:
    """
    Retrieve protein classification details for multiple IDs.

    Args:
        protein_class_ids: List of protein classification IDs.

    Returns:
        A list of protein classification dictionaries.
    """
    api = get_chembl_api()
    try:
        result = api.get_protein_classification_ids(protein_class_ids)
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_protein_classification_ids: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def search_protein_classification(query_str: str) -> Any:
    """
    Search protein classifications using a query string.

    Args:
        query_str: Search string for protein classifications.

    Returns:
        A list of classification objects that match the query.
    """
    api = get_chembl_api()
    try:
        result = api.search_protein_classification(query_str)
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying search_protein_classification: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def get_similarity_smiles(standard_inchi_key: str, similarity: int) -> Any:
    """
    Retrieve compounds similar to a given standard InChI key.

    Args:
        standard_inchi_key: IUPAC standard InChI key for the compound.
        similarity: Similarity threshold as an integer.

    Returns:
        A list of compounds with similarity scores and metadata.
    """
    api = get_chembl_api()
    try:
        result = api.get_similarity_smiles(standard_inchi_key, similarity)
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_similarity_smiles: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def get_source() -> Any:
    """
    Retrieve a list of ChEMBL data sources.

    Returns:
        A list of source dictionaries.
    """
    api = get_chembl_api()
    try:
        result = api.get_source()
    except Exception as e:
        return [{"error": f"An error occurred while querying get_source: {str(e)}"}]
    return result


@tool(parse_docstring=True)
async def get_source_id(src_id: int) -> Any:
    """
    Retrieve source details by ID.

    Args:
        src_id: Source identifier.

    Returns:
        A dictionary with source properties.
    """
    api = get_chembl_api()
    try:
        result = api.get_source_id(src_id)
    except Exception as e:
        return [{"error": f"An error occurred while querying get_source_id: {str(e)}"}]
    return result


@tool(parse_docstring=True)
async def get_source_ids(src_ids: List[int]) -> Any:
    """
    Retrieve source details for multiple IDs.

    Args:
        src_ids: List of source identifiers.

    Returns:
        A list of source dictionaries.
    """
    api = get_chembl_api()
    try:
        result = api.get_source_ids(src_ids)
    except Exception as e:
        return [{"error": f"An error occurred while querying get_source_ids: {str(e)}"}]
    return result


@tool(parse_docstring=True)
async def get_status() -> Any:
    """
    Retrieve overall ChEMBL database status information.

    Returns:
        A list of status dictionaries with database statistics.
    """
    api = get_chembl_api()
    try:
        result = api.get_status()
    except Exception as e:
        return [{"error": f"An error occurred while querying get_status: {str(e)}"}]
    return result


@tool(parse_docstring=True)
async def substructure_info(molecule_chembl_id: str) -> Any:
    """
    Retrieve substructure search information for a query structure.

    Args:
        molecule_chembl_id: SMILES or identifier string for the substructure.

    Returns:
        A list of compound matches with metadata.
    """
    api = get_chembl_api()
    try:
        result = api.substructure_info(molecule_chembl_id)
    except Exception as e:
        return [
            {"error": f"An error occurred while querying substructure_info: {str(e)}"}
        ]
    return result


@tool(parse_docstring=True)
async def get_target() -> Any:
    """
    Retrieve a default list of targets.

    Returns:
        A list of target dictionaries.
    """
    api = get_chembl_api()
    try:
        result = api.get_target()
    except Exception as e:
        return [{"error": f"An error occurred while querying get_target: {str(e)}"}]
    return result


@tool(parse_docstring=True)
async def get_target_id(target_chembl_id: str) -> Any:
    """
    Retrieve target details by target ChEMBL ID.

    Args:
        target_chembl_id: Target ChEMBL identifier.

    Returns:
        A dictionary with target properties.
    """
    api = get_chembl_api()
    try:
        result = api.get_target_id(target_chembl_id)
    except Exception as e:
        return [{"error": f"An error occurred while querying get_target_id: {str(e)}"}]
    return result


@tool(parse_docstring=True)
async def get_target_ids(target_chembl_ids: List[str]) -> Any:
    """
    Retrieve target details for multiple target ChEMBL IDs.

    Args:
        target_chembl_ids: List of target ChEMBL identifiers.

    Returns:
        A list of target dictionaries.
    """
    api = get_chembl_api()
    try:
        result = api.get_target_ids(target_chembl_ids)
    except Exception as e:
        return [{"error": f"An error occurred while querying get_target_ids: {str(e)}"}]
    return result


@tool(parse_docstring=True)
async def search_target(query_str: str) -> Any:
    """
    Search targets using a query string.

    Args:
        query_str: Search string for target fields.

    Returns:
        A list of target dictionaries that match the query.
    """
    api = get_chembl_api()
    try:
        result = api.search_target(query_str)
    except Exception as e:
        return [{"error": f"An error occurred while querying search_target: {str(e)}"}]
    return result


@tool(parse_docstring=True)
async def get_target_component() -> Any:
    """
    Retrieve a list of target components.

    Returns:
        A list of target component dictionaries.
    """
    api = get_chembl_api()
    try:
        result = api.get_target_component()
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_target_component: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def get_target_component_id(component_id: int) -> Any:
    """
    Retrieve target component details by ID.

    Args:
        component_id: Target component identifier.

    Returns:
        A dictionary with target component properties.
    """
    api = get_chembl_api()
    try:
        result = api.get_target_component_id(component_id)
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_target_component_id: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def get_target_component_ids(component_ids: List[int]) -> Any:
    """
    Retrieve target component details for multiple IDs.

    Args:
        component_ids: List of target component identifiers.

    Returns:
        A list of target component dictionaries.
    """
    api = get_chembl_api()
    try:
        result = api.get_target_component_ids(component_ids)
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_target_component_ids: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def get_target_relation() -> Any:
    """
    Retrieve a list of target relation objects.

    Returns:
        A list of target relation dictionaries.
    """
    api = get_chembl_api()
    try:
        result = api.get_target_relation()
    except Exception as e:
        return [
            {"error": f"An error occurred while querying get_target_relation: {str(e)}"}
        ]
    return result


@tool(parse_docstring=True)
async def get_target_relation_id(related_target_chembl_id: str) -> Any:
    """
    Retrieve target relation details by related target ChEMBL ID.

    Args:
        related_target_chembl_id: ChEMBL ID of the related target.

    Returns:
        A dictionary with target relation properties.
    """
    api = get_chembl_api()
    try:
        result = api.get_target_relation_id(related_target_chembl_id)
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_target_relation_id: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def get_target_relation_ids(related_target_chembl_ids: List[str]) -> Any:
    """
    Retrieve target relation details for multiple related target ChEMBL IDs.

    Args:
        related_target_chembl_ids: List of related target ChEMBL IDs.

    Returns:
        A list of target relation dictionaries.
    """
    api = get_chembl_api()
    try:
        result = api.get_target_relation_ids(related_target_chembl_ids)
    except Exception as e:
        return [
            {
                "error": f"An error occurred while querying get_target_relation_ids: {str(e)}"
            }
        ]
    return result


@tool(parse_docstring=True)
async def get_tissue() -> Any:
    """
    Retrieve a list of tissue objects.

    Returns:
        A list of tissue dictionaries.
    """
    api = get_chembl_api()
    try:
        result = api.get_tissue()
    except Exception as e:
        return [{"error": f"An error occurred while querying get_tissue: {str(e)}"}]
    return result


@tool(parse_docstring=True)
async def get_tissue_id(tissue_chembl_id: str) -> Any:
    """
    Retrieve tissue details by tissue ChEMBL ID.

    Args:
        tissue_chembl_id: Tissue ChEMBL identifier.

    Returns:
        A dictionary with tissue properties.
    """
    api = get_chembl_api()
    try:
        result = api.get_tissue_id(tissue_chembl_id)
    except Exception as e:
        return [{"error": f"An error occurred while querying get_tissue_id: {str(e)}"}]
    return result


@tool(parse_docstring=True)
async def get_tissue_ids(tissue_chembl_ids: List[str]) -> Any:
    """
    Retrieve tissue details for multiple tissue ChEMBL IDs.

    Args:
        tissue_chembl_ids: List of tissue ChEMBL identifiers.

    Returns:
        A list of tissue dictionaries.
    """
    api = get_chembl_api()
    try:
        result = api.get_tissue_ids(tissue_chembl_ids)
    except Exception as e:
        return [{"error": f"An error occurred while querying get_tissue_ids: {str(e)}"}]
    return result


@tool(parse_docstring=True)
async def get_xref_source() -> Any:
    """
    Retrieve a list of cross reference sources.

    Returns:
        A list of xref source dictionaries.
    """
    api = get_chembl_api()
    try:
        result = api.get_xref_source()
    except Exception as e:
        return [
            {"error": f"An error occurred while querying get_xref_source: {str(e)}"}
        ]
    return result


@tool(parse_docstring=True)
async def get_xref_source_id(xref_src_db: str) -> Any:
    """
    Retrieve xref source details by source database name.

    Args:
        xref_src_db: Name of the source database.

    Returns:
        A dictionary with xref source properties.
    """
    api = get_chembl_api()
    try:
        result = api.get_xref_source_id(xref_src_db)
    except Exception as e:
        return [
            {"error": f"An error occurred while querying get_xref_source_id: {str(e)}"}
        ]
    return result


@tool(parse_docstring=True)
async def get_xref_source_ids(xref_src_dbs: List[str]) -> Any:
    """
    Retrieve xref source details for multiple database names.

    Args:
        xref_src_dbs: List of source database names.

    Returns:
        A list of xref source dictionaries.
    """
    api = get_chembl_api()
    try:
        result = api.get_xref_source_ids(xref_src_dbs)
    except Exception as e:
        return [
            {"error": f"An error occurred while querying get_xref_source_ids: {str(e)}"}
        ]
    return result


@tool(parse_docstring=True)
async def get_image(chembl_id: str) -> Any:
    """
    Retrieve an image of a compound by ChEMBL ID or InChI key.

    Args:
        chembl_id: ChEMBL ID or Standard InChI Key.

    Returns:
        An image or image-like object representing the compound structure.
    """
    api = get_chembl_api()
    try:
        result = api.get_image(chembl_id)
    except Exception as e:
        return [{"error": f"An error occurred while querying get_image: {str(e)}"}]
    return result


@tool(parse_docstring=True)
async def get_compound_chembl_id_by_name(name: str) -> Any:
    """
    Retrieve a compound ChEMBL ID by compound name.

    Args:
        name: Compound name to search for.

    Returns:
        The ChEMBL ID of the compound if found, otherwise a string message.
    """
    api = get_chembl_api()
    try:
        result = api.search_molecule(name)
        if isinstance(result, str):
            result = json.loads(result)
        chembl_id = result["molecules"][0]["molecule_chembl_id"]
    except Exception:
        chembl_id = "No compound found"
    return chembl_id


chembl_tools: Dict[str, Any] = {
    "get_activity": get_activity,
    "get_activity_by_id": get_activity_by_id,
    "get_activity_by_ids": get_activity_by_ids,
    "search_activity": search_activity,
    "get_activity_supplementary_data_by_activity": get_activity_supplementary_data_by_activity,
    "get_activity_supplementary_data_by_activity_by_id": get_activity_supplementary_data_by_activity_by_id,
    "get_activity_supplementary_data_by_activity_by_ids": get_activity_supplementary_data_by_activity_by_ids,
    "get_assay": get_assay,
    "get_assay_by_id": get_assay_by_id,
    "get_assay_by_ids": get_assay_by_ids,
    "search_assay": search_assay,
    "get_assay_class": get_assay_class,
    "get_assay_class_by_id": get_assay_class_by_id,
    "get_assay_class_by_ids": get_assay_class_by_ids,
    "get_atc_class": get_atc_class,
    "get_atc_class_by_id": get_atc_class_by_id,
    "get_atc_class_by_ids": get_atc_class_by_ids,
    "get_binding_site": get_binding_site,
    "get_binding_site_by_id": get_binding_site_by_id,
    "get_binding_site_by_ids": get_binding_site_by_ids,
    "get_biotherapeutic": get_biotherapeutic,
    "get_biotherapeutic_by_id": get_biotherapeutic_by_id,
    "get_biotherapeutic_by_ids": get_biotherapeutic_by_ids,
    "get_cell_line": get_cell_line,
    "get_cell_line_by_id": get_cell_line_by_id,
    "get_cell_line_by_ids": get_cell_line_by_ids,
    "get_chembl_id_lookup": get_chembl_id_lookup,
    "get_chembl_id_lookup_by_id": get_chembl_id_lookup_by_id,
    "get_chembl_id_lookup_by_ids": get_chembl_id_lookup_by_ids,
    "search_chembl_id_lookup": search_chembl_id_lookup,
    "get_chembl_release": get_chembl_release,
    "get_chembl_release_by_id": get_chembl_release_by_id,
    "get_chembl_release_by_ids": get_chembl_release_by_ids,
    "get_compound_record": get_compound_record,
    "get_compound_record_by_id": get_compound_record_by_id,
    "get_compound_record_by_ids": get_compound_record_by_ids,
    "get_compound_structural_alert": get_compound_structural_alert,
    "get_compound_structural_alert_by_id": get_compound_structural_alert_by_id,
    "get_compound_structural_alert_by_ids": get_compound_structural_alert_by_ids,
    "get_document": get_document,
    "get_document_by_id": get_document_by_id,
    "get_document_by_ids": get_document_by_ids,
    "search_document": search_document,
    "get_document_similarity": get_document_similarity,
    "get_document_similarity_by_id": get_document_similarity_by_id,
    "get_document_similarity_by_ids": get_document_similarity_by_ids,
    "get_drug": get_drug,
    "get_drug_by_id": get_drug_by_id,
    "get_drug_by_ids": get_drug_by_ids,
    "get_drug_indication": get_drug_indication,
    "get_drug_indication_by_id": get_drug_indication_by_id,
    "get_drug_indication_by_ids": get_drug_indication_by_ids,
    "get_drug_warning": get_drug_warning,
    "get_drug_warning_id": get_drug_warning_id,
    "get_drug_warning_ids": get_drug_warning_ids,
    "get_go_slim": get_go_slim,
    "get_go_slim_id": get_go_slim_id,
    "get_go_slim_ids": get_go_slim_ids,
    "get_mechanism": get_mechanism,
    "get_mechanism_id": get_mechanism_id,
    "get_mechanism_ids": get_mechanism_ids,
    "get_metabolism": get_metabolism,
    "get_metabolism_id": get_metabolism_id,
    "get_metabolism_ids": get_metabolism_ids,
    "get_molecule": get_molecule,
    "get_molecule_id": get_molecule_id,
    "get_molecule_ids": get_molecule_ids,
    "search_molecule": search_molecule,
    "get_molecule_form": get_molecule_form,
    "get_molecule_form_id": get_molecule_form_id,
    "get_molecule_form_ids": get_molecule_form_ids,
    "get_organism": get_organism,
    "get_organism_id": get_organism_id,
    "get_organism_ids": get_organism_ids,
    "get_protein_classification": get_protein_classification,
    "get_protein_classification_id": get_protein_classification_id,
    "get_protein_classification_ids": get_protein_classification_ids,
    "search_protein_classification": search_protein_classification,
    "get_similarity_smiles": get_similarity_smiles,
    "get_source": get_source,
    "get_source_id": get_source_id,
    "get_source_ids": get_source_ids,
    "get_status": get_status,
    "substructure_info": substructure_info,
    "get_target": get_target,
    "get_target_id": get_target_id,
    "get_target_ids": get_target_ids,
    "search_target": search_target,
    "get_target_component": get_target_component,
    "get_target_component_id": get_target_component_id,
    "get_target_component_ids": get_target_component_ids,
    "get_target_relation": get_target_relation,
    "get_target_relation_id": get_target_relation_id,
    "get_target_relation_ids": get_target_relation_ids,
    "get_tissue": get_tissue,
    "get_tissue_id": get_tissue_id,
    "get_tissue_ids": get_tissue_ids,
    "get_xref_source": get_xref_source,
    "get_xref_source_id": get_xref_source_id,
    "get_xref_source_ids": get_xref_source_ids,
    "get_image": get_image,
    "get_compound_chembl_id_by_name": get_compound_chembl_id_by_name,
}
