import requests
import json
from typing import Dict, List, Optional
from urllib.parse import urljoin
import urllib

class EnsemblClient:
    """
    A Python client for the Ensembl REST API.
    """
    
    BASE_URL = "https://rest.ensembl.org/"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    

    @staticmethod
    def _dumps(x):
        return json.dumps(x, ensure_ascii=False, separators=(",", ":"))
    
    def limit_dict_length(self, data, max_length):
        """
        Keep all keys without removing any; only shrink the values to ensure
        len(json.dumps(result)) <= max_length.
        Recursively handle nested structures.
        """
        assert isinstance(data, dict)
        dumps = self._dumps

        if len(dumps(data)) <= max_length:
            return data

        trimmed = {}
        for k, v in data.items():
            test = {**trimmed, k: v}
            if len(dumps(test)) <= max_length:
                trimmed[k] = v
            else:
                break
        return trimmed

    def limit_list_length(self, data, max_length):
        """
        Trim a list so that len(json.dumps(result)) <= max_length.
        """
        assert isinstance(data, list)
        dumps = self._dumps

        if len(dumps(data)) <= max_length:
            return data

        trimmed = []
        for item in data:
            test = trimmed + [item]
            if len(dumps(test)) <= max_length:
                trimmed.append(item)
            else:
                break
        return trimmed

    def limit_json_length(self, data, max_length):
        """
        Dispatch by type and ensure the JSON-serialized length does not exceed max_length.
        """
        try:
            if isinstance(data, dict):
                return self.limit_dict_length(data, max_length)
            elif isinstance(data, list):
                return self.limit_list_length(data, max_length)
            else:
                return data
        except Exception:
            return data


    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                     data: Optional[Dict] = None, max_length: int = 8192) -> Dict:
        """Make a request to the Ensembl REST API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters
            data: Request body data
            max_length: Maximum length of the response (in approximate token count)
            
        Returns:
            Dictionary containing the response or error information
        """
        url = urljoin(self.BASE_URL, endpoint)
        try:
            response = self.session.request(method, url, params=params, 
                                         json=data if data else None)
            response.raise_for_status()
            result = response.json()
            
            # Limit response size based on approximate token count
            result = self.limit_json_length(result, max_length*4)            
            return result
        
        except requests.exceptions.HTTPError as e:
            return {"error": f"HTTP Error: {str(e)}", "status_code": e.response.status_code}
        except requests.exceptions.ConnectionError:
            return {"error": "Connection Error: Failed to connect to Ensembl API"}
        except requests.exceptions.Timeout:
            return {"error": "Timeout Error: Request to Ensembl API timed out"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Request Error: {str(e)}"}
        except ValueError as e:
            return {"error": f"JSON Parsing Error: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected Error: {str(e)}"}

    # Archive endpoints
    def get_archive_id(self, id: str) -> Dict:
        """Get latest version of an identifier."""
        id = urllib.parse.quote(str(id))
        return self._make_request("GET", f"archive/id/{id}")

    def post_archive_id(self, ids: List[str]) -> Dict:
        """Get latest version for multiple identifiers."""
        return self._make_request("POST", "archive/id", data={"ids": ids})

    # Comparative Genomics endpoints
    def get_cafe_genetree_id(self, id: str) -> Dict:
        """Get cafe tree by gene tree stable identifier."""
        id = urllib.parse.quote(str(id))
        return self._make_request("GET", f"cafe/genetree/id/{id}")

    def get_cafe_genetree_member_symbol(self, species: str, symbol: str) -> Dict:
        """Get cafe tree by gene symbol."""
        species = urllib.parse.quote(str(species))
        symbol = urllib.parse.quote(str(symbol))
        return self._make_request("GET", f"cafe/genetree/member/symbol/{species}/{symbol}")

    def get_cafe_genetree_member_id(self, species: str, id: str) -> Dict:
        """Get cafe tree by member ID."""
        species = urllib.parse.quote(str(species))
        id = urllib.parse.quote(str(id))
        return self._make_request("GET", f"cafe/genetree/member/id/{species}/{id}")

    def get_genetree_id(self, id: str, max_length: int = 8192) -> Dict:
        """Get gene tree by ID."""
        id = urllib.parse.quote(str(id))
        return self._make_request("GET", f"genetree/id/{id}", max_length=max_length)

    def get_genetree_member_symbol(self, species: str, symbol: str) -> Dict:
        """Get gene tree by symbol."""
        species = urllib.parse.quote(str(species))
        symbol = urllib.parse.quote(str(symbol))
        return self._make_request("GET", f"genetree/member/symbol/{species}/{symbol}")

    def get_genetree_member_id(self, species: str, id: str) -> Dict:
        """Get gene tree by member ID."""
        species = urllib.parse.quote(str(species))
        id = urllib.parse.quote(str(id))
        return self._make_request("GET", f"genetree/member/id/{species}/{id}")

    def get_alignment_region(self, species: str, region: str) -> Dict:
        """Get genomic alignments by region."""
        species = urllib.parse.quote(str(species))
        region = urllib.parse.quote(str(region))
        return self._make_request("GET", f"alignment/region/{species}/{region}")

    def get_homology_id(self, species: str, id: str) -> Dict:
        """Get homology information by ID."""
        species = urllib.parse.quote(str(species))
        id = urllib.parse.quote(str(id))
        return self._make_request("GET", f"homology/id/{species}/{id}")

    def get_homology_symbol(self, species: str, symbol: str, max_length: int = 8192) -> Dict:
        """Get homology information by symbol."""
        species = urllib.parse.quote(str(species))
        symbol = urllib.parse.quote(str(symbol))
        return self._make_request("GET", f"homology/symbol/{species}/{symbol}", max_length=max_length)

    # Cross References endpoints
    def get_xrefs_symbol(self, species: str, symbol: str, max_length: int = 8192) -> Dict:
        """Get cross references by symbol."""
        species = urllib.parse.quote(str(species))
        symbol = urllib.parse.quote(str(symbol))
        return self._make_request("GET", f"xrefs/symbol/{species}/{symbol}", max_length=max_length)

    def get_xrefs_id(self, id: str) -> Dict:
        """Get cross references by ID."""
        id = urllib.parse.quote(str(id))
        return self._make_request("GET", f"xrefs/id/{id}")

    def get_xrefs_name(self, species: str, name: str) -> Dict:
        """Get cross references by name."""
        species = urllib.parse.quote(str(species))
        name = urllib.parse.quote(str(name))
        return self._make_request("GET", f"xrefs/name/{species}/{name}")

    # Information endpoints
    def get_info_analysis(self, species: str) -> Dict:
        """Get analysis information for a species."""
        species = urllib.parse.quote(str(species))
        return self._make_request("GET", f"info/analysis/{species}")

    def get_info_assembly(self, species: str, max_length: int = 8192) -> Dict:
        """Get assembly information for a species."""
        species = urllib.parse.quote(str(species))
        return self._make_request("GET", f"info/assembly/{species}", max_length=max_length)

    def get_assembly_info(self, species: str) -> Dict:
        """Get assembly information for a species. (Alias for get_info_assembly)"""
        return self.get_info_assembly(species)

    def get_assembly_region_info(self, species: str, region_name: str) -> Dict:
        """Get assembly information for a specific region."""
        species = urllib.parse.quote(str(species))
        region_name = urllib.parse.quote(str(region_name))
        return self._make_request("GET", f"info/assembly/{species}/{region_name}")

    def get_info_biotypes(self, species: str) -> Dict:
        """Get biotypes for a species."""
        species = urllib.parse.quote(str(species))
        return self._make_request("GET", f"info/biotypes/{species}")

    def get_biotypes(self, species: str) -> Dict:
        """Get biotypes for a species. (Alias for get_info_biotypes)"""
        return self.get_info_biotypes(species)

    def get_info_biotypes_groups(self, group: str, object_type: str) -> Dict:
        """Get biotype groups information."""
        group = urllib.parse.quote(str(group))
        object_type = urllib.parse.quote(str(object_type))
        return self._make_request("GET", f"info/biotypes/groups/{group}/{object_type}")

    def get_biotype_groups(self, group: str, object_type: str) -> Dict:
        """Get biotype groups information. (Alias for get_info_biotypes_groups)"""
        return self.get_info_biotypes_groups(group, object_type)

    def get_info_biotypes_name(self, name: str, object_type: str) -> Dict:
        """Get biotype information by name."""
        name = urllib.parse.quote(str(name))
        object_type = urllib.parse.quote(str(object_type))
        return self._make_request("GET", f"info/biotypes/name/{name}/{object_type}")

    def get_biotype_name(self, name: str, object_type: str) -> Dict:
        """Get biotype information by name. (Alias for get_info_biotypes_name)"""
        return self.get_info_biotypes_name(name, object_type)

    # Information endpoints (continued)
    def get_info_compara_methods(self) -> Dict:
        """Get comparative analysis methods."""
        return self._make_request("GET", "info/compara/methods")

    def get_compara_methods(self) -> Dict:
        """Get comparative analysis methods. (Alias for get_info_compara_methods)"""
        return self.get_info_compara_methods()

    def get_info_compara_species_sets(self, method: str) -> Dict:
        """Get species sets for a comparative analysis method."""
        method = urllib.parse.quote(str(method))
        return self._make_request("GET", f"info/compara/species_sets/{method}")

    def get_compara_species_sets(self, method: str) -> Dict:
        """Get species sets for a comparative analysis method. (Alias for get_info_compara_species_sets)"""
        return self.get_info_compara_species_sets(method)

    def get_info_comparas(self) -> Dict:
        """Get comparative genomics databases."""
        return self._make_request("GET", "info/comparas")

    def get_comparas(self) -> Dict:
        """Get comparative genomics databases. (Alias for get_info_comparas)"""
        return self.get_info_comparas()

    def get_info_data(self) -> Dict:
        """Get data release information."""
        return self._make_request("GET", "info/data")

    def get_data_info(self) -> Dict:
        """Get data release information. (Alias for get_info_data)"""
        return self.get_info_data()

    def get_info_eg_version(self) -> Dict:
        """Get Ensembl Genomes version."""
        return self._make_request("GET", "info/eg_version")

    def get_eg_version(self) -> Dict:
        """Get Ensembl Genomes version. (Alias for get_info_eg_version)"""
        return self.get_info_eg_version()

    def get_info_external_dbs(self, species: str) -> Dict:
        """Get external databases for a species."""
        species = urllib.parse.quote(str(species))
        return self._make_request("GET", f"info/external_dbs/{species}")

    def get_external_dbs(self, species: str) -> Dict:
        """Get external databases for a species. (Alias for get_info_external_dbs)"""
        return self.get_info_external_dbs(species)

    def get_info_divisions(self) -> Dict:
        """Get Ensembl divisions."""
        return self._make_request("GET", "info/divisions")

    def get_divisions(self) -> Dict:
        """Get Ensembl divisions. (Alias for get_info_divisions)"""
        return self.get_info_divisions()

    def get_info_genomes(self, genome_name: str) -> Dict:
        """Find information about a given genome."""
        genome_name = urllib.parse.quote(str(genome_name))
        return self._make_request("GET", f"info/genomes/{genome_name}")

    def get_info_genomes_accession(self, accession: str) -> Dict:
        """Find information about genomes containing a specified INSDC accession."""
        accession = urllib.parse.quote(str(accession))
        return self._make_request("GET", f"info/genomes/accession/{accession}")

    def get_info_genomes_assembly(self, assembly_id: str) -> Dict:
        """Find information about a genome with a specified assembly."""
        assembly_id = urllib.parse.quote(str(assembly_id))
        return self._make_request("GET", f"info/genomes/assembly/{assembly_id}")

    def get_info_genomes_division(self, division_name: str) -> Dict:
        """Find information about all genomes in a given division."""
        division_name = urllib.parse.quote(str(division_name))
        return self._make_request("GET", f"info/genomes/division/{division_name}")

    def get_info_genomes_taxonomy(self, taxon_name: str) -> Dict:
        """Find information about all genomes beneath a given node of the taxonomy."""
        taxon_name = urllib.parse.quote(str(taxon_name))
        return self._make_request("GET", f"info/genomes/taxonomy/{taxon_name}")

    def get_info_ping(self) -> Dict:
        """Checks if the service is alive."""
        return self._make_request("GET", "info/ping")

    def get_info_rest(self) -> Dict:
        """Shows the current version of the Ensembl REST API."""
        return self._make_request("GET", "info/rest")

    def get_info_software(self) -> Dict:
        """Shows the current version of the Ensembl API used by the REST server."""
        return self._make_request("GET", "info/software")

    def get_info_species(self) -> Dict:
        """Lists all available species, their aliases, available adaptor groups and data release."""
        return self._make_request("GET", "info/species")

    def get_info_variation(self, species: str) -> Dict:
        """List the variation sources used in Ensembl for a species."""
        species = urllib.parse.quote(str(species))
        return self._make_request("GET", f"info/variation/{species}")

    def get_info_variation_consequence_types(self) -> Dict:
        """Lists all variant consequence types."""
        return self._make_request("GET", "info/variation/consequence_types")

    def get_info_variation_populations(self, species: str, population_name: Optional[str] = None) -> Dict:
        """List all populations for a species or list all individuals for a population from a species."""
        species = urllib.parse.quote(str(species))
        if population_name:
            population_name = urllib.parse.quote(str(population_name))
            return self._make_request("GET", f"info/variation/populations/{species}/{population_name}")
        return self._make_request("GET", f"info/variation/populations/{species}")

    # Linkage Disequilibrium endpoints
    def get_ld(self, species: str, id: str, population_name: str) -> Dict:
        """Computes and returns LD values between the given variant and all other variants in a window."""
        species = urllib.parse.quote(str(species))
        id = urllib.parse.quote(str(id))
        population_name = urllib.parse.quote(str(population_name))
        return self._make_request("GET", f"ld/{species}/{id}/{population_name}")

    def get_ld_pairwise(self, species: str, id1: str, id2: str) -> Dict:
        """Computes and returns LD values between the given variants."""
        species = urllib.parse.quote(str(species))
        id1 = urllib.parse.quote(str(id1))
        id2 = urllib.parse.quote(str(id2))
        return self._make_request("GET", f"ld/{species}/pairwise/{id1}/{id2}")

    def get_ld_region(self, species: str, region: str, population_name: str) -> Dict:
        """Computes and returns LD values between all pairs of variants in the defined region."""
        species = urllib.parse.quote(str(species))
        region = urllib.parse.quote(str(region))
        population_name = urllib.parse.quote(str(population_name))
        return self._make_request("GET", f"ld/{species}/region/{region}/{population_name}")

    # Lookup endpoints
    def get_lookup_id(self, id: str) -> Dict:
        """Look up an identifier."""
        id = urllib.parse.quote(str(id))
        return self._make_request("GET", f"lookup/id/{id}")

    def post_lookup_id(self, ids: List[str]) -> Dict:
        """Look up multiple identifiers."""
        return self._make_request("POST", "lookup/id", data={"ids": ids})

    def get_lookup_symbol(self, species: str, symbol: str, max_length: int = 8192) -> Dict:
        """Look up a symbol."""
        species = urllib.parse.quote(str(species))
        symbol = urllib.parse.quote(str(symbol))
        return self._make_request("GET", f"lookup/symbol/{species}/{symbol}", max_length=max_length)

    def post_lookup_symbol(self, species: str, symbols: List[str]) -> Dict:
        """Look up multiple symbols."""
        species = urllib.parse.quote(str(species))
        return self._make_request("POST", f"lookup/symbol/{species}", data={"symbols": symbols})

    # Mapping endpoints
    def get_map_cdna(self, id: str, region: str) -> Dict:
        """Map cDNA coordinates to genomic coordinates."""
        id = urllib.parse.quote(str(id))
        region = urllib.parse.quote(str(region))
        return self._make_request("GET", f"map/cdna/{id}/{region}")

    def get_map_cds(self, id: str, region: str) -> Dict:
        """Map CDS coordinates to genomic coordinates."""
        id = urllib.parse.quote(str(id))
        region = urllib.parse.quote(str(region))
        return self._make_request("GET", f"map/cds/{id}/{region}")

    def get_map(self, species: str, asm_one: str, region: str, asm_two: str) -> Dict:
        """Map coordinates between assemblies."""
        species = urllib.parse.quote(str(species))
        asm_one = urllib.parse.quote(str(asm_one))
        region = urllib.parse.quote(str(region))
        asm_two = urllib.parse.quote(str(asm_two))
        return self._make_request("GET", f"map/{species}/{asm_one}/{region}/{asm_two}")

    def get_map_translation(self, id: str, region: str) -> Dict:
        """Map protein coordinates to genomic coordinates."""
        id = urllib.parse.quote(str(id))
        region = urllib.parse.quote(str(region))
        return self._make_request("GET", f"map/translation/{id}/{region}")

    # Ontologies and Taxonomy endpoints
    def get_ontology_ancestors(self, id: str) -> Dict:
        """Get ontology ancestors."""
        id = urllib.parse.quote(str(id))
        return self._make_request("GET", f"ontology/ancestors/{id}")

    def get_ontology_ancestors_chart(self, id: str) -> Dict:
        """Get ontology ancestors chart."""
        id = urllib.parse.quote(str(id))
        return self._make_request("GET", f"ontology/ancestors/chart/{id}")

    def get_ontology_descendants(self, id: str) -> Dict:
        """Get ontology descendants."""
        id = urllib.parse.quote(str(id))
        return self._make_request("GET", f"ontology/descendants/{id}")

    def get_ontology_id(self, id: str) -> Dict:
        """Get ontology by ID."""
        id = urllib.parse.quote(str(id))
        return self._make_request("GET", f"ontology/id/{id}")

    def get_ontology_name(self, name: str) -> Dict:
        """Get ontology by name."""
        name = urllib.parse.quote(str(name))
        return self._make_request("GET", f"ontology/name/{name}")

    def get_taxonomy_classification(self, id: str) -> Dict:
        """Return the taxonomic classification of a taxon node."""
        id = urllib.parse.quote(str(id))
        return self._make_request("GET", f"taxonomy/classification/{id}")

    def get_taxonomy_id(self, id: str) -> Dict:
        """Search for a taxonomic term by its identifier."""
        id = urllib.parse.quote(str(id))
        return self._make_request("GET", f"taxonomy/id/{id}")

    def get_taxonomy_name(self, name: str) -> Dict:
        """Search for a taxonomic id by a non-scientific name."""
        name = urllib.parse.quote(str(name))
        return self._make_request("GET", f"taxonomy/name/{name}")

    # Overlap endpoints
    def get_overlap_id(self, id: str) -> Dict:
        """Get features overlapping a region defined by an identifier."""
        id = urllib.parse.quote(str(id))
        return self._make_request("GET", f"overlap/id/{id}")

    def get_overlap_region(self, features: str, species: str, region: str) -> Dict:
        """Get features overlapping a genomic region."""
        features = urllib.parse.quote(str(features))
        species = urllib.parse.quote(str(species))
        region = urllib.parse.quote(str(region))
        return self._make_request("GET", f"overlap/region/{species}/{region}?{features}")

    def get_overlap_translation(self, id: str) -> Dict:
        """Get features overlapping a translation."""
        id = urllib.parse.quote(str(id))
        return self._make_request("GET", f"overlap/translation/{id}")

    # Phenotype endpoints
    def get_phenotype_accession(self, species: str, accession: str, max_length: int = 8192) -> Dict:
        """Get phenotype annotations by accession."""
        species = urllib.parse.quote(str(species))
        accession = urllib.parse.quote(str(accession))
        return self._make_request("GET", f"phenotype/accession/{species}/{accession}", max_length=max_length)

    def get_phenotype_gene(self, species: str, gene: str, max_length: int = 8192) -> Dict:
        """Get phenotype annotations by gene."""
        params = {
            'include_associated': '1',
            'include_overlap': '1',
            'include_pubmed_id': '1'
        }
        return self._make_request("GET", f"phenotype/gene/{species}/{gene}", params=params, max_length=max_length)

    def get_phenotype_region(self, species: str, region: str, max_length: int = 8192) -> Dict:
        """Get phenotype annotations by region."""
        species = urllib.parse.quote(str(species))
        region = urllib.parse.quote(str(region))
        return self._make_request("GET", f"phenotype/region/{species}/{region}", max_length=max_length)

    def get_phenotype_term(self, species: str, term: str, max_length: int = 8192) -> Dict:
        """Get phenotype annotations by term."""
        species = urllib.parse.quote(str(species))
        term = urllib.parse.quote(str(term))
        return self._make_request("GET", f"phenotype/term/{species}/{term}", max_length=max_length)

    # Regulation endpoints 
    def get_species_binding_matrix(self, species: str, binding_matrix_stable_id: str) -> Dict:
        """Get binding matrix."""
        species = urllib.parse.quote(str(species))
        binding_matrix_stable_id = urllib.parse.quote(str(binding_matrix_stable_id))
        return self._make_request("GET", f"species/{species}/binding_matrix/{binding_matrix_stable_id}")

    # Sequence endpoints
    def get_sequence_id(self, id: str) -> Dict:
        """Get sequence by ID."""
        id = urllib.parse.quote(str(id))
        return self._make_request("GET", f"sequence/id/{id}")

    def post_sequence_id(self, ids: List[str]) -> Dict:
        """Get sequences by multiple IDs."""
        return self._make_request("POST", "sequence/id", data={"ids": ids})

    def get_sequence_region(self, species: str, region: str, max_length: int = 8192) -> Dict:
        """Get sequence by region."""
        species = urllib.parse.quote(str(species))
        region = urllib.parse.quote(str(region))
        return self._make_request("GET", f"sequence/region/{species}/{region}", max_length=max_length)

    def post_sequence_region(self, species: str, regions: List[Dict]) -> Dict:
        """Get sequences by multiple regions."""
        species = urllib.parse.quote(str(species))
        return self._make_request("POST", f"sequence/region/{species}", data={"regions": regions})

    # Transcript Haplotypes endpoints
    def get_transcript_haplotypes(self, species: str, id: str) -> Dict:
        """Computes observed transcript haplotype sequences based on phased genotype data."""
        species = urllib.parse.quote(str(species))
        id = urllib.parse.quote(str(id))
        return self._make_request("GET", f"transcript_haplotypes/{species}/{id}")

    # VEP endpoints
    def get_vep_hgvs(self, species: str, hgvs_notation: str, max_length: int = 8192) -> Dict:
        """Get variant effect predictions by HGVS notation."""
        species = urllib.parse.quote(str(species))
        hgvs_notation = urllib.parse.quote(str(hgvs_notation))
        return self._make_request("GET", f"vep/{species}/hgvs/{hgvs_notation}", max_length=max_length)

    def post_vep_hgvs(self, species: str, hgvs_notations: List[str]) -> Dict:
        """Get variant effect predictions by multiple HGVS notations."""
        species = urllib.parse.quote(str(species))
        return self._make_request("POST", f"vep/{species}/hgvs", data={"hgvs_notations": hgvs_notations})

    def get_vep_id(self, species: str, id: str) -> Dict:
        """Get variant effect predictions by ID."""
        species = urllib.parse.quote(str(species))
        id = urllib.parse.quote(str(id))
        return self._make_request("GET", f"vep/{species}/id/{id}")

    def post_vep_id(self, species: str, ids: List[str]) -> Dict:
        """Get variant effect predictions by multiple IDs."""
        species = urllib.parse.quote(str(species))
        return self._make_request("POST", f"vep/{species}/id", data={"ids": ids})

    def get_vep_region(self, species: str, region: str, allele: str) -> Dict:
        """Get variant effect predictions by region."""
        species = urllib.parse.quote(str(species))
        region = urllib.parse.quote(str(region))
        allele = urllib.parse.quote(str(allele))
        return self._make_request("GET", f"vep/{species}/region/{region}/{allele}")

    def post_vep_region(self, species: str, variants: List[Dict]) -> Dict:
        """Get variant effect predictions by multiple regions."""
        species = urllib.parse.quote(str(species))
        return self._make_request("POST", f"vep/{species}/region", data={"variants": variants})

    # Variation endpoints
    def get_variant_recoder(self, species: str, id: str) -> Dict:
        """Translate variant identifiers."""
        species = urllib.parse.quote(str(species))
        id = urllib.parse.quote(str(id))
        return self._make_request("GET", f"variant_recoder/{species}/{id}")

    def post_variant_recoder(self, species: str, ids: List[str]) -> Dict:
        """Translate multiple variant identifiers."""
        species = urllib.parse.quote(str(species))
        return self._make_request("POST", f"variant_recoder/{species}", data={"ids": ids})

    def get_variation(self, species: str, id: str) -> Dict:
        """Get variation by ID."""
        species = urllib.parse.quote(str(species))
        id = urllib.parse.quote(str(id))
        return self._make_request("GET", f"variation/{species}/{id}")

    def get_variation_pmcid(self, species: str, pmcid: str) -> Dict:
        """Get variations by PubMed Central ID."""
        species = urllib.parse.quote(str(species))
        pmcid = urllib.parse.quote(str(pmcid))
        return self._make_request("GET", f"variation/{species}/pmcid/{pmcid}")

    def get_variation_pmid(self, species: str, pmid: str) -> Dict:
        """Get variations by PubMed ID."""
        species = urllib.parse.quote(str(species))
        pmid = urllib.parse.quote(str(pmid))
        return self._make_request("GET", f"variation/{species}/pmid/{pmid}")

    def post_variation(self, species: str, ids: List[str]) -> Dict:
        """Get variations by multiple IDs."""
        species = urllib.parse.quote(str(species))
        return self._make_request("POST", f"variation/{species}", data={"ids": ids})

    # GA4GH endpoints
    def get_ga4gh_beacon(self) -> Dict:
        """Get Beacon information."""
        return self._make_request("GET", "ga4gh/beacon")

    def get_ga4gh_beacon_query(self, params: Dict) -> Dict:
        """Query Beacon."""
        return self._make_request("GET", "ga4gh/beacon/query", params=params)

    def post_ga4gh_beacon_query(self, data: Dict) -> Dict:
        """Query Beacon with POST."""
        return self._make_request("POST", "ga4gh/beacon/query", data=data)

    def get_ga4gh_features(self, id: str) -> Dict:
        """Get GA4GH features by ID."""
        id = urllib.parse.quote(str(id))
        return self._make_request("GET", f"ga4gh/features/{id}")

    def post_ga4gh_features_search(self, data: Dict) -> Dict:
        """Search GA4GH features."""
        return self._make_request("POST", "ga4gh/features/search", data=data)

    def post_ga4gh_callsets_search(self, data: Dict) -> Dict:
        """Search GA4GH callsets."""
        return self._make_request("POST", "ga4gh/callsets/search", data=data)

    def get_ga4gh_callsets(self, id: str) -> Dict:
        """Get GA4GH callset by ID."""
        id = urllib.parse.quote(str(id))
        return self._make_request("GET", f"ga4gh/callsets/{id}")

    def post_ga4gh_datasets_search(self, data: Dict) -> Dict:
        """Search GA4GH datasets."""
        return self._make_request("POST", "ga4gh/datasets/search", data=data)

    def get_ga4gh_datasets(self, id: str) -> Dict:
        """Get GA4GH dataset by ID."""
        id = urllib.parse.quote(str(id))
        return self._make_request("GET", f"ga4gh/datasets/{id}")

    def post_ga4gh_featuresets_search(self, data: Dict) -> Dict:
        """Search GA4GH feature sets."""
        return self._make_request("POST", "ga4gh/featuresets/search", data=data)

    def get_ga4gh_featuresets(self, id: str) -> Dict:
        """Get GA4GH feature set by ID."""
        id = urllib.parse.quote(str(id))
        return self._make_request("GET", f"ga4gh/featuresets/{id}")

    def get_ga4gh_variants(self, id: str) -> Dict:
        """Get GA4GH variant by ID."""
        id = urllib.parse.quote(str(id))
        return self._make_request("GET", f"ga4gh/variants/{id}")

    def post_ga4gh_variantannotations_search(self, data: Dict) -> Dict:
        """Search GA4GH variant annotations."""
        return self._make_request("POST", "ga4gh/variantannotations/search", data=data)

    def post_ga4gh_variants_search(self, data: Dict) -> Dict:
        """Search GA4GH variants."""
        return self._make_request("POST", "ga4gh/variants/search", data=data)

    def post_ga4gh_variantsets_search(self, data: Dict) -> Dict:
        """Search GA4GH variant sets."""
        return self._make_request("POST", "ga4gh/variantsets/search", data=data)

    def get_ga4gh_variantsets(self, id: str) -> Dict:
        """Get GA4GH variant set by ID."""
        return self._make_request("GET", f"ga4gh/variantsets/{id}")

    def post_ga4gh_references_search(self, data: Dict) -> Dict:
        """Search GA4GH references."""
        return self._make_request("POST", "ga4gh/references/search", data=data)

    def get_ga4gh_references(self, id: str) -> Dict:
        """Get GA4GH reference by ID."""
        return self._make_request("GET", f"ga4gh/references/{id}")

    def post_ga4gh_referencesets_search(self, data: Dict) -> Dict:
        """Search GA4GH reference sets."""
        return self._make_request("POST", "ga4gh/referencesets/search", data=data)

    def get_ga4gh_referencesets(self, id: str) -> Dict:
        """Get GA4GH reference set by ID."""
        return self._make_request("GET", f"ga4gh/referencesets/{id}")

    def post_ga4gh_variantannotationsets_search(self, data: Dict) -> Dict:
        """Search GA4GH variant annotation sets."""
        return self._make_request("POST", "ga4gh/variantannotationsets/search", data=data)

    def get_ga4gh_variantannotationsets(self, id: str) -> Dict:
        """Get GA4GH variant annotation set by ID."""
        return self._make_request("GET", f"ga4gh/variantannotationsets/{id}") 
    


# ensembl_tools.py

from typing import Dict, Any, Optional, List
from langchain_core.tools import tool


DEFAULT_MAX_LENGTH = 10240

_ensembl_api: Optional[EnsemblClient] = None


def initialize_ensembl_api(config: Optional[Dict[str, Any]] = None) -> None:
    """
    Initialize the global Ensembl API client.

    Can be called once at application startup (for example inside initialize_tools(config)).
    The config parameter is reserved for future extensions (for example base URL, timeout),
    but is not used at the moment because EnsemblClient() takes no arguments in your code.
    """
    global _ensembl_api
    if _ensembl_api is None:
        _ensembl_api = EnsemblClient()


def get_ensembl_api() -> EnsemblClient:
    """
    Get the global Ensembl API client. Lazily initializes it if needed.
    """
    global _ensembl_api
    if _ensembl_api is None:
        _ensembl_api = EnsemblClient()
    return _ensembl_api


@tool(parse_docstring=True)
async def get_lookup_symbol(
    symbol: str,
    species: str = "homo_sapiens",
    max_length: int = DEFAULT_MAX_LENGTH,
) -> Dict[str, Any]:
    """
    Look up Ensembl gene information by external gene symbol.
    
    This function allows you to find Ensembl gene records using standard gene symbols
    (e.g., HGNC symbols for human genes).
    
    Args:
        species: Species name in snake_case format (e.g., 'homo_sapiens' for human, 'mus_musculus' for mouse)
        symbol: Official gene symbol (e.g., 'BRCA2', 'TP53', 'APOE')
        max_length: Maximum length of the response in approximate tokens (default: 8192)
    
    Query example: {"species": "homo_sapiens", "symbol": "BRCA2"}
    
    Returns:
        Dictionary containing comprehensive gene information including Ensembl ID, genomic location,
        biotype (e.g., protein_coding, lncRNA), description, and cross-references to external databases.
    """
    api = get_ensembl_api()
    result = api.get_lookup_symbol(species=species, symbol=symbol, max_length=max_length)
    if isinstance(result, dict) and "error" in result:
        return {"error": f"An error occurred while looking up gene: {result['error']}"}
    return result


@tool(parse_docstring=True)
async def get_homology_symbol(
    symbol: str,
    species: str = "homo_sapiens",
    max_length: int = DEFAULT_MAX_LENGTH,
) -> Dict[str, Any]:
    """
    Find evolutionary homologs (orthologs and paralogs) for a gene identified by symbol.
    
    Retrieve homologous genes across different species, with alignment statistics and
    taxonomic information. Essential for comparative genomics and evolutionary studies.
    
    Args:
        species: Species name in snake_case format (e.g., 'homo_sapiens' for human)
        symbol: Official gene symbol (e.g., 'BRCA2', 'TP53', 'FOXP2')
        max_length: Maximum length of the response in approximate tokens (default: 8192)
    
    Query example: {"species": "homo_sapiens", "symbol": "FOXP2"}
    
    Returns:
        Dictionary containing homology information including:
        - Orthologs (genes in different species derived from a common ancestral gene)
        - Paralogs (genes derived from duplication within a genome)
        - Alignment statistics (identity, coverage)
        - Taxonomic information for each homolog
    """
    api = get_ensembl_api()
    result = api.get_homology_symbol(species=species, symbol=symbol, max_length=max_length)
    if isinstance(result, dict) and "error" in result:
        return {"error": f"An error occurred while getting homology: {result['error']}"}
    return result


@tool(parse_docstring=True)
async def get_sequence_region(
    region: str,
    species: str = "homo_sapiens",
    max_length: int = DEFAULT_MAX_LENGTH,
) -> Dict[str, Any]:
    """
    Retrieve genomic DNA sequence for a specific chromosomal region.
    
    Extract the raw nucleotide sequence from a specific genomic location, which can be
    used for primer design, variant analysis, or sequence feature identification.
    
    Args:
        species: Species name in snake_case format (e.g., 'homo_sapiens' for human)
        region: Genomic region in format 'chromosome:start..end' (e.g., 'X:1000000..1000100', '7:55152337..55207337', 'MT:1..16569'). Coordinates are 1-based inclusive.
        max_length: Maximum length of the response in approximate tokens (default: 8192)
    
    Query example: {"species": "homo_sapiens", "region": "X:1000000..1000100"}
    
    Returns:
        Dictionary containing the DNA sequence as a string of nucleotides (A,C,G,T),
        along with metadata about the region, sequence length, and coordinate system.
    """
    api = get_ensembl_api()
    result = api.get_sequence_region(species=species, region=region, max_length=max_length)
    if isinstance(result, dict) and "error" in result:
        return {"error": f"An error occurred while getting sequence: {result['error']}"}
    return result


@tool(parse_docstring=True)
async def get_vep_hgvs(
    hgvs_notation: str,
    species: str = "homo_sapiens",
    max_length: int = DEFAULT_MAX_LENGTH,
) -> Dict[str, Any]:
    """
    Predict the functional effects of variants using Variant Effect Predictor (VEP) with HGVS notation.
    
    Analyzes the molecular consequences of genetic variants on genes, transcripts, and protein sequences.
    VEP provides comprehensive annotation including protein changes, regulatory effects, conservation scores,
    and pathogenicity predictions.

    Args:
        species: Species name in snake_case format (e.g., 'homo_sapiens' for human)
        hgvs_notation: Variant in HGVS (Human Genome Variation Society) notation format (e.g., 'ENST00000269305.4:c.2309C>T', 'NM_000059.3:c.274G>A', 'NC_000017.10:g.7676154G>T')
        max_length: Maximum length of the response in approximate tokens (default: 8192)

    Returns:
        Dictionary containing detailed variant effect predictions, including:
        - Affected genes and transcripts
        - Effect on protein sequence (missense, nonsense, etc.)
        - SIFT and PolyPhen pathogenicity scores
        - Conservation scores
        - Allele frequencies in population databases
        - Regulatory feature annotations
        - Clinical significance annotations
    """
    api = get_ensembl_api()
    result = api.get_vep_hgvs(
        species=species,
        hgvs_notation=hgvs_notation,
        max_length=max_length,
    )
    if isinstance(result, dict) and "error" in result:
        return {"error": f"An error occurred while getting variant effect: {result['error']}"}
    return result


@tool(parse_docstring=True)
async def get_genetree_id(
    id: str,
    max_length: int = DEFAULT_MAX_LENGTH,
    species: str = "homo_sapiens",
) -> Dict[str, Any]:
    """
    Retrieve a phylogenetic gene tree by its Ensembl stable identifier.
    
    Gene trees represent the evolutionary history of genes across species, showing
    orthologous and paralogous relationships. These trees are constructed using
    protein sequence alignments and phylogenetic algorithms.
    
    Args:
        id: Ensembl gene tree stable identifier (e.g., 'ENSGT00390000003602')
        max_length: Maximum length of the response in approximate tokens (default: 8192)
    
    Query example: {"id": "ENSGT00390000003602"}
    
    Returns:
        Dictionary containing gene tree information in a nested structure, including:
        - Taxonomy and sequence relationships
        - Branch lengths representing evolutionary distance
        - Bootstrap values indicating tree confidence
        - Sequence alignments used to build the tree
        - Member genes from different species
    """
    api = get_ensembl_api()
    result = api.get_genetree_id(id=id, max_length=max_length)
    if isinstance(result, dict) and "error" in result:
        return {"error": f"An error occurred while getting gene tree: {result['error']}"}
    return result


@tool(parse_docstring=True)
async def get_info_assembly(
    species: str,
    max_length: int = DEFAULT_MAX_LENGTH,
) -> Dict[str, Any]:
    """
    Retrieve genome assembly information for a species.
    
    Provides details about the reference genome assembly used in Ensembl, including
    assembly version, accession numbers, and overall structure. Essential for
    understanding coordinate systems and genome organization.
    
    Args:
        species: Species name in snake_case format (e.g., 'homo_sapiens' for human, 'mus_musculus' for mouse, 'danio_rerio' for zebrafish)
        max_length: Maximum length of the response in approximate tokens (default: 8192)
    
    Query example: {"species": "homo_sapiens"}
    
    Returns:
        Dictionary containing comprehensive assembly information including:
        - Assembly name and version (e.g., 'GRCh38' for human)
        - Assembly accession (e.g., 'GCA_000001405.15')
        - Toplevel sequences (chromosomes, scaffolds, contigs)
        - Coordinate system information
        - Assembly date and source
        - Assembly statistics (sequence counts, lengths)
    """
    api = get_ensembl_api()
    result = api.get_info_assembly(species=species, max_length=max_length)
    if isinstance(result, dict) and "error" in result:
        return {"error": f"An error occurred while getting assembly info: {result['error']}"}
    return result


@tool(parse_docstring=True)
async def get_xrefs_symbol(
    symbol: str,
    species: str = "homo_sapiens",
) -> Any:
    """
    Get cross references for a gene symbol.
    
    Args:
        species: Species name (e.g. 'homo_sapiens' for human)
        symbol: Gene symbol (e.g. 'BRCA2')
    
    Query example: {"species": "homo_sapiens", "symbol": "BRCA2"}
    
    Returns:
        A list of dictionaries containing cross references to other databases.
    """
    api = get_ensembl_api()
    try:
        result = api.get_xrefs_symbol(species=species, symbol=symbol)
    except Exception as e:
        return {"error": f"An error occurred while getting cross references: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_archive_id(id: str) -> Any:
    """
    Get the latest version of an Ensembl stable identifier.
    
    Args:
        id: Ensembl stable identifier (e.g., 'ENSG00000139618')
    
    Query example: {"id": "ENSG00000139618"}
    
    Returns:
        A dictionary containing the latest version information for the given identifier.
    """
    api = get_ensembl_api()
    try:
        result = api.get_archive_id(id=id)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def post_archive_id(ids: List[str]) -> Any:
    """
    Get the latest version for multiple Ensembl stable identifiers.
    
    Args:
        ids: A list of Ensembl stable identifiers.
    
    Query example: {"ids": ["ENSG00000139618", "ENSG00000168269"]}
    
    Returns:
        A dictionary where keys are the input IDs and values are dictionaries
        containing the latest version information for each ID.
    """
    api = get_ensembl_api()
    try:
        result = api.post_archive_id(ids=ids)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_cafe_genetree_id(id: str) -> Any:
    """
    Retrieve a CAFE (Computational Analysis of gene Family Evolution) gene tree by ID.
    
    CAFE analyzes the evolution of gene family size across a phylogenetic tree,
    identifying expansions and contractions of gene families throughout evolution.
    This helps understand adaptation, functional diversification, and species-specific traits.
    
    Args:
        id: Ensembl gene tree stable identifier (e.g., 'ENSGT00390000003602')
    
    Query example: {"id": "ENSGT00390000003602"}
    
    Returns:
        Dictionary containing CAFE gene tree data including:
        - Gene family size changes across evolutionary time
        - Statistical significance of expansions/contractions
        - P-values for gene family size changes
        - Species tree topology with gene count information
    """
    api = get_ensembl_api()
    try:
        result = api.get_cafe_genetree_id(id=id)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_cafe_genetree_member_symbol(
    symbol: str,
    species: str = "homo_sapiens",
) -> Any:
    """
    Retrieve a CAFE gene tree for a gene identified by symbol.
    
    Get gene family evolution analysis (expansions/contractions) for a gene family
    that contains the specified gene. Identifies evolutionary patterns without
    needing to know the specific gene tree ID.
    
    Args:
        species: Species name in snake_case format (e.g., 'homo_sapiens' for human)
        symbol: Official gene symbol (e.g., 'BRCA2', 'TP53', 'OR4F5')
    
    Query example: {"species": "homo_sapiens", "symbol": "OR4F5"}
    
    Returns:
        Dictionary containing CAFE gene tree data including:
        - Gene family size changes across evolutionary time
        - Statistical significance of expansions/contractions
        - P-values for gene family size changes
        - Species tree topology with gene count information
    """
    api = get_ensembl_api()
    try:
        result = api.get_cafe_genetree_member_symbol(species=species, symbol=symbol)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_cafe_genetree_member_id(
    id: str,
    species: str = "homo_sapiens",
) -> Any:
    """
    Retrieve the gene tree containing a gene identified by its Ensembl ID.
    
    Find the phylogenetic tree showing evolutionary relationships for a gene of interest,
    identified using its Ensembl stable identifier. Useful for understanding gene evolution
    when you have the specific gene ID.
    
    Args:
        species: Species name in snake_case format (e.g., 'homo_sapiens' for human)
        id: Ensembl gene, transcript, or translation stable identifier(e.g., 'ENSG00000139618' for human BRCA2 gene)
    
    Query example: {"species": "homo_sapiens", "id": "ENSG00000139618"}
    
    Returns:
        Dictionary containing gene tree information in a nested structure, including:
        - Taxonomy and sequence relationships
        - Branch lengths representing evolutionary distance
        - Bootstrap values indicating tree confidence
        - Sequence alignments used to build the tree
        - Member genes from different species
    """
    api = get_ensembl_api()
    try:
        result = api.get_cafe_genetree_member_id(species=species, id=id)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_genetree_member_symbol(
    symbol: str,
    species: str = "homo_sapiens",
) -> Any:
    """
    Get gene tree by symbol.
    
    Args:
        species: Species name (e.g. 'homo_sapiens' for human)
        symbol: Gene symbol
    
    Query example: {"species": "homo_sapiens", "symbol": "BRCA2"}
    
    Returns:
        Dictionary containing gene tree information.
    """
    api = get_ensembl_api()
    try:
        result = api.get_genetree_member_symbol(species=species, symbol=symbol)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_alignment_region(
    region: str,
    species: str = "homo_sapiens",
) -> Any:
    """
    Retrieve genomic alignments between species for a specific region.
    
    Get multiple sequence alignments of genomic regions across species, showing
    evolutionary conservation and divergence. Crucial for identifying conserved
    functional elements like enhancers or detecting selection pressure.
    
    Args:
        species: Reference species name in snake_case format (e.g., 'homo_sapiens')
        region: Genomic region in format 'chromosome:start..end' (e.g., 'X:1000000..1000100', '7:55152337..55207337', 'MT:1..16569'). Coordinates are 1-based inclusive.
    
    Query example: {"species": "homo_sapiens", "region": "X:1000000..1000100"}
    
    Returns:
        Dictionary containing aligned sequences from multiple species in the specified region,
        with alignment blocks, scores, and coordinate mappings between genomes.
    """
    api = get_ensembl_api()
    try:
        result = api.get_alignment_region(species=species, region=region)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_homology_id(
    id: str,
    species: str = "homo_sapiens",
) -> Any:
    """
    Find evolutionary homologs (orthologs and paralogs) for a gene identified by Ensembl ID.
    
    Retrieve homologous genes across different species, with alignment statistics and
    taxonomic information. Essential for comparative genomics and evolutionary studies.
    
    Args:
        species: Species name in snake_case format (e.g., 'homo_sapiens' for human)
        id: Ensembl gene ID (e.g., 'ENSG00000139618' for human BRCA2 gene)
    
    Query example: {"species": "homo_sapiens", "id": "ENSG00000139618"}
    
    Returns:
        Dictionary containing homology information including:
        - Orthologs (genes in different species derived from a common ancestral gene)
        - Paralogs (genes derived from duplication within a genome)
        - Alignment statistics (identity, coverage)
        - Taxonomic information for each homolog
    """
    api = get_ensembl_api()
    try:
        result = api.get_homology_id(species=species, id=id)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_xrefs_id(id: str) -> Any:
    """
    Get cross references by ID.
    
    Args:
        id: Ensembl stable identifier
    
    Query example: {"id": "ENSG00000139618"}
    
    Returns:
        A list of dictionaries containing cross references to other databases.
    """
    api = get_ensembl_api()
    try:
        result = api.get_xrefs_id(id=id)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_xrefs_name(
    name: str,
    species: str = "homo_sapiens",
) -> Any:
    """
    Get cross references by name.
    
    Args:
        species: Species name (e.g. 'homo_sapiens' for human)
        name: External name
    
    Query example: {"species": "homo_sapiens", "name": "BRCA2"}
    
    Returns:
        A list of dictionaries containing cross references to other databases.
    """
    api = get_ensembl_api()
    try:
        result = api.get_xrefs_name(species=species, name=name)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_info_analysis(
    species: str = "homo_sapiens",
) -> Any:
    """
    List the analyses and data processing pipelines used for a species genome.
    
    Provides information about the computational methods and analyses used to generate
    Ensembl data for a species, including gene annotation methods, comparative genomics
    analyses, and variation data processing.
    
    Args:
        species: Species name in snake_case format (e.g., 'homo_sapiens' for human)
    
    Query example: {"species": "homo_sapiens"}
    
    Returns:
        Dictionary containing analysis information for the species, including:
        - Gene annotation methods and sources
        - Alignment algorithms used
        - Variation calling procedures
        - Regulatory feature detection methods
        - Comparative genomics pipeline details
    """
    api = get_ensembl_api()
    try:
        result = api.get_info_analysis(species=species)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_assembly_region_info(
    region_name: str,
    species: str = "homo_sapiens",
) -> Any:
    """
    Retrieve detailed information about a specific genomic region or chromosome.
    
    Get assembly metadata for a particular sequence within a genome assembly,
    such as chromosome length, scaffold composition, or contig information.
    
    Args:
        species: Species name in snake_case format (e.g., 'homo_sapiens' for human)
        region_name: Name of the toplevel sequence (e.g., '1' for chromosome 1, 'X' for X chromosome, 'KZ622775.1' for a scaffold)
    
    Query example: {"species": "homo_sapiens", "region_name": "X"}
    
    Returns:
        Dictionary containing detailed information about the specified region, including:
        - Sequence length
        - Coordinate system
        - Assembly exceptions (if any)
        - Sequence composition
        - Associated metadata and attributes
    """
    api = get_ensembl_api()
    try:
        result = api.get_assembly_region_info(species=species, region_name=region_name)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_info_biotypes(
    species: str = "homo_sapiens",
) -> Any:
    """
    Retrieve the catalog of gene and transcript biotypes for a species.
    
    Biotypes classify genes and transcripts according to their biological nature,
    such as protein-coding, pseudogene, or various non-coding RNA categories.
    This information is crucial for filtering and interpreting genomic data.
    
    Args:
        species: Species name in snake_case format (e.g., 'homo_sapiens' for human)
    
    Query example: {"species": "homo_sapiens"}
    
    Returns:
        A list of dictionaries, where each dictionary describes an available biotype for the species.
    """
    api = get_ensembl_api()
    try:
        result = api.get_info_biotypes(species=species)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_info_compara_methods() -> Any:
    """
    Get comparative analysis methods used in Ensembl Compara.
    
    Args:
    
    Query example: {}
    
    Returns:
        A dictionary containing the different classes of compara methods
        and the specific methods within each class.
    """
    api = get_ensembl_api()
    try:
        result = api.get_info_compara_methods()
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_info_external_dbs(
    species: str,
) -> Any:
    """
    Get external databases for a species.
    
    Args:
        species: Species name (e.g. 'homo_sapiens' for human)
    
    Query example: {"species": "homo_sapiens"}
    
    Returns:
        A list of dictionaries, where each dictionary contains information
        about an external database linked for the species.
    """
    api = get_ensembl_api()
    try:
        result = api.get_info_external_dbs(species=species)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_map_cdna(
    id: str,
    region: str,
) -> Any:
    """
    Map cDNA coordinates to genomic coordinates.
    
    Args:
        id: Transcript ID
        region: cDNA coordinates
    
    Query example: {"id": "ENST00000380152", "region": "100..300"}
    
    Returns:
        A dictionary containing a list of coordinate mapping results, where each result
        provides the genomic coordinates (chromosome, start, end, strand) for a
        segment of the input cDNA region.
    """
    api = get_ensembl_api()
    try:
        result = api.get_map_cdna(id=id, region=region)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_map_cds(
    id: str,
    region: str,
) -> Any:
    """
    Map CDS coordinates to genomic coordinates.
    
    Args:
        id: Transcript ID
        region: CDS coordinates
    
    Query example: {"id": "ENST00000139618", "region": "1..200"}
    
    Returns:
        A dictionary containing a list of coordinate mapping results, where each result
        provides the genomic coordinates (chromosome, start, end, strand) for a
        segment of the input CDS region.
    """
    api = get_ensembl_api()
    try:
        result = api.get_map_cds(id=id, region=region)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_map_translation(
    id: str,
    region: str,
) -> Any:
    """
    Map protein coordinates to genomic coordinates.
    
    Args:
        id: Translation ID
        region: Protein coordinates
    
    Query example: {"id": "ENSP00000265436", "region": "1..50"}
    
    Returns:
        A dictionary containing a list of coordinate mapping results, where each result
        provides the genomic coordinates (chromosome, start, end, strand) for a
        segment of the input protein region.
    """
    api = get_ensembl_api()
    try:
        result = api.get_map_translation(id=id, region=region)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_ontology_ancestors(id: str) -> Any:
    """
    Get ontology ancestors. Note: This tool is sensitive to the format of the input ID and may return
    a 400 Bad Request error for some valid-looking IDs. It is recommended to use IDs obtained directly
    from other Ensembl tools.
    
    Args:
        id: An ontology term identifier (a GO term ID like 'GO:0005667').
    
    Query example: {"id": "GO:0005667"}
    
    Returns:
        A list of dictionaries, where each dictionary contains information about an ancestor ontology term.
    """
    api = get_ensembl_api()
    try:
        result = api.get_ontology_ancestors(id=id)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_ontology_descendants(id: str) -> Any:
    """
    Get ontology descendants. Note: This tool is sensitive to the format of the input ID and may return
    a 400 Bad Request error for some valid-looking IDs. It is recommended to use IDs obtained directly
    from other Ensembl tools.
    
    Args:
        id: Ontology term ID (e.g., a GO term ID like 'GO:0005667').
    
    Query example: {"id": "GO:0005667"}
    
    Returns:
        A list of dictionaries, where each dictionary contains information about a descendant ontology term.
    """
    api = get_ensembl_api()
    try:
        result = api.get_ontology_descendants(id=id)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_ontology_id(id: str) -> Any:
    """
    Get ontology by ID. Note: This tool is sensitive to the format of the input ID and may return
    a 400 Bad Request error for some valid-looking IDs. It is recommended to use IDs obtained directly
    from other Ensembl tools.
    
    Args:
        id: An ontology term identifier (a GO term ID like 'GO:0005667').
    
    Query example: {"id": "GO:0005667"}
    
    Returns:
        Dictionary containing ontology information for the specified term,
        including its children and parents in the hierarchy.
    """
    api = get_ensembl_api()
    try:
        result = api.get_ontology_id(id=id)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_ontology_name(name: str) -> Any:
    """
    Get ontology by name.
    
    Args:
        name: An ontology name. SQL wildcards are supported.
    
    Query example: {"name": "transcription factor complex"}
    
    Returns:
        Dictionary containing ontology information for the matched term.
    """
    api = get_ensembl_api()
    try:
        result = api.get_ontology_name(name=name)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_overlap_id(id: str) -> Any:
    """
    Get features overlapping a region defined by an identifier. Note: This tool is currently
    non-functional and returns a 400 Bad Request error for valid Ensembl IDs.
    
    Args:
        id: Ensembl stable identifier
    
    Query example: {"id": "ENST00000380152"}
    
    Returns:
        Dictionary containing overlapping features. Returns an error message upon failure.
    """
    api = get_ensembl_api()
    try:
        result = api.get_overlap_id(id=id)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_overlap_region(
    features: str,
    region: str,
    species: str = "homo_sapiens",
) -> Any:
    """
    Get features overlapping a genomic region. Note: This tool may fail with a 400 Bad Request error
    for valid queries.
    
    Args:
        features: The type of feature to retrieve. Multiple values are accepted if separated by comma(e.g. 'feature=gene;feature=transcript;').
        species: Species name (e.g. 'homo_sapiens' for human)
        region: Genomic region (e.g. 'X:1..1000:1','X:1..1000:-1','X:1..1000')
    
    Query example: {"species": "homo_sapiens", "region": "X:1000000..1000100", "features": "gene"}
    
    Returns:
        Dictionary containing overlapping features. Returns an error message upon failure.
    """
    api = get_ensembl_api()
    try:
        result = api.get_overlap_region(features=features, species=species, region=region)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_overlap_translation(id: str) -> Any:
    """
    Get features overlapping a translation.
    
    Args:
        id: Translation stable identifier
    
    Query example: {"id": "ENSP00000265436"}
    
    Returns:
        A list of dictionaries, where each dictionary contains information about a feature
        that overlaps with the genomic region of the specified translation ID.
    """
    api = get_ensembl_api()
    try:
        result = api.get_overlap_translation(id=id)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_phenotype_region(
    region: str,
    species: str = "homo_sapiens",
    max_length: int = DEFAULT_MAX_LENGTH,
) -> Any:
    """
    Retrieve phenotype associations for variants in a genomic region.
    
    Find diseases, traits, and phenotypes associated with genetic variants
    located within a specific genomic region. Useful for exploring disease
    associations in GWAS loci or candidate regions.
    
    Args:
        species: Species name in snake_case format (e.g., 'homo_sapiens' for human)
        region: Genomic region in format 'chromosome:start..end' (e.g., '9:22125500..22136000', '17:7669000..7676000')
    
    Query example: {"species": "homo_sapiens", "region": "9:22125500..22136000"}
    
    Returns:
        A list of dictionaries containing phenotype annotations for variants in the region, including:
        - Associated diseases and traits
        - Specific variant locations and alleles
        - Source of the association (e.g., ClinVar, GWAS Catalog)
    """
    api = get_ensembl_api()
    result = api.get_phenotype_region(
        species=species,
        region=region,
        max_length=max_length,
    )
    if isinstance(result, dict) and "error" in result:
        return {
            "error": f"An error occurred while fetching phenotype data: {result['error']}"
        }
    return result


@tool(parse_docstring=True)
async def get_phenotype_gene(
    gene: str,
    species: str = "homo_sapiens",
    max_length: int = DEFAULT_MAX_LENGTH,
) -> Any:
    """
    Retrieve phenotype associations for a specific gene.
    
    Find diseases, traits, and phenotypes associated with a gene of interest.
    These associations come from various sources including literature curation,
    GWAS studies, and clinical databases.
    
    Args:
        species: Species name in snake_case format (e.g., 'homo_sapiens' for human)
        gene: Gene stable ID or name (e.g., 'ENSG00000139618', 'BRCA2')
        max_length: Maximum length of the response in approximate tokens (default: 8192)
    
    Query example: {"species": "homo_sapiens", "gene": "BRCA2"}
    
    Returns:
        A list of dictionaries containing phenotype annotations for the gene, including:
        - Associated diseases and traits
        - Source of the association (e.g., ClinVar, GWAS Catalog)
        - Study references and citations
        - Variant details for genetic associations
        - Clinical significance where available
    """
    api = get_ensembl_api()
    result = api.get_phenotype_gene(
        species=species,
        gene=gene,
        max_length=max_length,
    )
    if isinstance(result, dict) and "error" in result:
        return {
            "error": f"An error occurred while fetching phenotype data: {result['error']}"
        }
    return result


@tool(parse_docstring=True)
async def get_phenotype_accession(
    accession: str,
    species: str = "homo_sapiens",
    max_length: int = DEFAULT_MAX_LENGTH,
) -> Any:
    """
    Retrieve genomic features associated with a specific phenotype ontology term.
    
    Find genes and variants linked to a specific disease or trait identified by
    an ontology accession (e.g., from the Human Phenotype Ontology or Experimental
    Factor Ontology).
    
    Args:
        species: Species name in snake_case format (e.g., 'homo_sapiens' for human)
        accession: Phenotype ontology accession (e.g., 'HP:0001250' for seizure)
        max_length: Maximum length of the response in approximate tokens (default: 8192)
    
    Query example: {"species": "homo_sapiens", "accession": "HP:0001250"}
    
    Returns:
        A list of dictionaries containing phenotype annotations for the gene, including:
        - Associated diseases and traits
        - Source of the association (e.g., ClinVar, GWAS Catalog)
        - Study references and citations
        - Variant details for genetic associations
    """
    api = get_ensembl_api()
    result = api.get_phenotype_accession(
        species=species,
        accession=accession,
        max_length=max_length,
    )
    if isinstance(result, dict) and "error" in result:
        return {
            "error": f"An error occurred while fetching phenotype data: {result['error']}"
        }
    return result


@tool(parse_docstring=True)
async def get_sequence_id(id: str) -> Any:
    """
    Retrieve sequence associated with an Ensembl identifier.
    
    Get the nucleotide sequence for a gene or transcript, or the amino acid sequence for a protein.
    Useful for analyzing gene structure, transcript variants, or protein domains.
    
    Args:
        id: Ensembl stable identifier (e.g., 'ENSG00000139618' for BRCA2 gene DNA,'ENST00000380152' for transcript sequence, or 'ENSP00000369497' for protein sequence)
    
    Query example: {"id": "ENST00000380152"}
    
    Returns:
        Dictionary containing the sequence (nucleotide or amino acid) and metadata about
        the entity, including length, sequence type, and coordinate information.
    """
    api = get_ensembl_api()
    try:
        result = api.get_sequence_id(id=id)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_vep_id(
    id: str,
    species: str = "homo_sapiens",
) -> Any:
    """
    Predict the functional effects of variants using Variant Effect Predictor (VEP) with variant identifier.
    
    Retrieves comprehensive variant annotation using known variant IDs (e.g., dbSNP rs identifiers).
    Provides molecular consequences, population frequencies, and pathogenicity predictions.
    
    Args:
        species: Species name in snake_case format (e.g., 'homo_sapiens' for human)
        id: Variant identifier (e.g., 'rs6025' for Factor V Leiden, 'rs429358' for APOE variant)
    
    Query example: {"species": "homo_sapiens", "id": "rs6025"}
    
    Returns:
        Dictionary containing detailed variant effect predictions, including:
        - Affected genes and transcripts
        - Effect on protein sequence (missense, nonsense, etc.)
        - SIFT and PolyPhen pathogenicity scores
        - Conservation scores
        - Allele frequencies in population databases
        - Regulatory feature annotations
        - Clinical significance annotations
    """
    api = get_ensembl_api()
    try:
        result = api.get_vep_id(species=species, id=id)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_vep_region(
    region: str,
    allele: str,
    species: str = "homo_sapiens",
) -> Any:
    """
    Predict the functional effects of variants using Variant Effect Predictor (VEP) with genomic coordinates.
    
    Analyzes variants specified by chromosome location and alternate allele.
    Particularly useful for novel variants or those without established identifiers.

    Args:
        species: Species name in snake_case format (e.g., 'homo_sapiens' for human)
        region: Genomic region in format 'chromosome:position' or 'chromosome:start-end'(e.g., '9:22125503', '1:230710048-230710048')
        allele: The variant allele sequence (alternate allele) that replaces the reference sequence

    Returns:
        Dictionary containing detailed variant effect predictions, including:
        - Affected genes and transcripts
        - Effect on protein sequence (missense, nonsense, etc.)
        - SIFT and PolyPhen pathogenicity scores
        - Conservation scores
        - Allele frequencies in population databases
        - Regulatory feature annotations
        - Clinical significance annotations
    """
    api = get_ensembl_api()
    try:
        result = api.get_vep_region(species=species, region=region, allele=allele)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_variation(
    id: str,
    species: str = "homo_sapiens",
) -> Any:
    """
    Retrieve detailed information about a genetic variant by its identifier.
    
    Provides comprehensive data about a known genetic variant, including its
    genomic location, alleles, frequency in populations, phenotype associations,
    and links to external databases.
    
    Args:
        species: Species name in snake_case format (e.g., 'homo_sapiens' for human)
        id: Variant identifier (e.g., 'rs6025' for Factor V Leiden, 'rs429358' for APOE variant)
    
    Query example: {"species": "homo_sapiens", "id": "rs6025"}
    
    Returns:
        Dictionary containing detailed variant information including:
        - Genomic location and alleles
        - Population frequencies across different populations
        - Clinical significance and phenotype associations
        - Consequence predictions for transcripts
        - Citations and references
        - External database links (dbSNP, ClinVar, etc.)
    """
    api = get_ensembl_api()
    try:
        result = api.get_variation(species=species, id=id)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_variant_recoder(
    id: str,
    species: str = "homo_sapiens",
) -> Any:
    """
    Translate between different variant nomenclature systems and representations.
    
    Convert variant identifiers between different formats (e.g., rsID, HGVS notation,
    genomic coordinates). Useful for integrating variant data from different sources
    or analysis tools.
    
    Args:
        species: Species name in snake_case format (e.g., 'homo_sapiens' for human)
        id: Variant identifier in any supported format (e.g., 'rs6025','ENST00000367640.3:c.1601G>A', '1:g.169519049G>T')
    
    Query example: {"species": "homo_sapiens", "id": "rs6025"}
    
    Returns:
        Dictionary containing the variant represented in various nomenclature systems:
        - dbSNP rsIDs
        - HGVS notations (genomic, transcript, protein)
        - Genomic coordinates in VCF format
        - SPDI notation (Sequence Position Deletion Insertion)
    """
    api = get_ensembl_api()
    try:
        result = api.get_variant_recoder(species=species, id=id)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_info_data() -> Any:
    """
    Get data release information.
    
    Query example: {}

    Returns:
        Dictionary containing data release information.
    """
    api = get_ensembl_api()
    try:
        result = api.get_info_data()
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_info_eg_version() -> Any:
    """
    Get Ensembl Genomes version.
    
    Args:
    
    Query example: {}
    
    Returns:
        Dictionary containing version information.
    """
    api = get_ensembl_api()
    try:
        result = api.get_info_eg_version()
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_info_divisions() -> Any:
    """
    Get Ensembl divisions.
    
    Args:
    
    Query example: {}
    
    Returns:
        A list containing the names of the main Ensembl divisions.
    """
    api = get_ensembl_api()
    try:
        result = api.get_info_divisions()
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_info_genomes(genome_name: str) -> Any:
    """
    Find information about a given genome.
    
    Args:
        genome_name: Name of the genome (e.g., 'homo_sapiens')
    
    Query example: {"genome_name": "homo_sapiens"}
    
    Returns:
        A dictionary containing detailed genome information.
    """
    api = get_ensembl_api()
    try:
        result = api.get_info_genomes(genome_name=genome_name)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_info_genomes_accession(accession: str) -> Any:
    """
    Find information about genomes containing a specified INSDC accession. Note: The underlying data
    is sparse, and many valid accessions may result in a null return.
    
    Args:
        accession: INSDC accession (e.g., 'GCA_000001635.9').
    
    Query example: {"accession": "GCA_000001635.9"}
    
    Returns:
        A dictionary containing genome information for the specified accession.
        Returns null if no information is found.
    """
    api = get_ensembl_api()
    try:
        result = api.get_info_genomes_accession(accession=accession)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_info_genomes_assembly(assembly_id: str) -> Any:
    """
    Find information about a genome with a specified assembly. Note: This tool may fail
    with a 400 Bad Request error for valid assembly IDs.
    
    Args:
        assembly_id: Assembly identifier
    
    Query example: {"assembly_id": "71511"}
    
    Returns:
        Dictionary containing genome information. Returns an error message upon failure.
    """
    api = get_ensembl_api()
    try:
        result = api.get_info_genomes_assembly(assembly_id=assembly_id)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_info_genomes_division(division_name: str) -> Any:
    """
    Find information about all genomes in a given division.
    
    Args:
        division_name: Division name (e.g., 'EnsemblVertebrates')
    
    Query example: {"division_name": "EnsemblVertebrates"}
    
    Returns:
        A list of dictionaries, where each dictionary contains information
        about a genome in the specified division.
    """
    api = get_ensembl_api()
    try:
        result = api.get_info_genomes_division(division_name=division_name)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_info_genomes_taxonomy(taxon_name: str) -> Any:
    """
    Find information about all genomes beneath a given node of the taxonomy.
    
    Args:
        taxon_name: Taxon name (e.g., 'Primates')
    
    Query example: {"taxon_name": "Primates"}
    
    Returns:
        A list of JSON strings, where each string is a dictionary containing
        genome information for a species within the specified taxon.
    """
    api = get_ensembl_api()
    try:
        result = api.get_info_genomes_taxonomy(taxon_name=taxon_name)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_info_ping() -> Any:
    """
    Checks if the service is alive.
    
    Args:
    
    Query example: {}
    
    Returns:
        Dictionary containing ping status (1 indicates alive).
    """
    api = get_ensembl_api()
    try:
        result = api.get_info_ping()
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_info_rest() -> Any:
    """
    Shows the current version of the Ensembl REST API.
    
    Args:
    
    Query example: {}
    
    Returns:
        Dictionary containing REST API version information.
    """
    api = get_ensembl_api()
    try:
        result = api.get_info_rest()
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_info_software() -> Any:
    """
    Shows the current version of the Ensembl API used by the REST server.
    
    Args:
    
    Query example: {}
    
    Returns:
        Dictionary containing software version information.
    """
    api = get_ensembl_api()
    try:
        result = api.get_info_software()
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_info_species() -> Any:
    """
    List all available species in the Ensembl database.
    
    Provides a comprehensive catalog of all organisms available in Ensembl,
    including their scientific names, common names, and assembly information.
    Useful for discovery and exploration of available genomic data.
    
    Args:
    
    Query example: {}
    
    Returns:
        A list of dictionaries, where each dictionary contains information
        about an available species.
    """
    api = get_ensembl_api()
    try:
        result = api.get_info_species()
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_info_variation(
    species: str,
) -> Any:
    """
    List all variation data sources used for a species in Ensembl.
    
    Provides information about the databases, studies, and projects that contributed
    variation data (SNPs, indels, structural variants) to Ensembl for a species.
    
    Args:
        species: Species name in snake_case format (e.g., 'homo_sapiens' for human)
    
    Query example: {"species": "homo_sapiens"}
    
    Returns:
        A list of dictionaries, where each dictionary contains information about
        a variation data source for the species.
    """
    api = get_ensembl_api()
    try:
        result = api.get_info_variation(species=species)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_info_variation_consequence_types() -> Any:
    """
    Lists all variant consequence types used by Ensembl.
    
    Args:
    
    Query example: {}
    
    Returns:
        A list of JSON strings, where each string is a dictionary containing
        information about a variant consequence type.
    """
    api = get_ensembl_api()
    try:
        result = api.get_info_variation_consequence_types()
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_info_variation_populations(
    species: str,
    population_name: Optional[str] = None,
) -> Any:
    """
    List all variation populations for a species, or list all individuals
    in a specific population.
    
    Args:
        species: Species name (e.g., 'homo_sapiens' for human).
        population_name: Optional population name to get individuals. If not provided,all populations for the species are returned.
    
    Query example for all populations: {"species": "homo_sapiens"}
    Query example for individuals in a population:
        {"species": "homo_sapiens", "population_name": "1000GENOMES:phase_3:ACB"}
    
    Returns:
        A list of dictionaries containing population information, or a dictionary
        containing individual information for a specific population.
    """
    api = get_ensembl_api()
    try:
        result = api.get_info_variation_populations(
            species=species,
            population_name=population_name,
        )
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_ld(
    species: str,
    id: str,
    population_name: str,
) -> Any:
    """
    Computes and returns LD values between the given variant and all other variants in a window.
    
    Args:
        species: Species name (e.g. 'homo_sapiens' for human)
        id: Variant identifier
        population_name: Population name
    
    Query example: {"species": "homo_sapiens", "id": "rs6025", "population_name": "1000GENOMES:phase_3:EUR"}
    
    Returns:
        A list of JSON strings, where each string is a dictionary containing LD values (d_prime, r2)
        between the query variant and another nearby variant.
    """
    api = get_ensembl_api()
    try:
        result = api.get_ld(species=species, id=id, population_name=population_name)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_ld_pairwise(
    species: str,
    id1: str,
    id2: str,
) -> Any:
    """
    Computes and returns LD values between the given variants.
    
    Args:
        species: Species name (e.g. 'homo_sapiens' for human)
        id1: First variant identifier
        id2: Second variant identifier
    
    Query example: {"species": "homo_sapiens", "id1": "rs6025", "id2": "rs2213868"}
    
    Returns:
        A list of JSON strings, where each string is a dictionary containing LD values
        for the pair of variants in a specific population.
    """
    api = get_ensembl_api()
    try:
        result = api.get_ld_pairwise(species=species, id1=id1, id2=id2)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_ld_region(
    species: str,
    region: str,
    population_name: str,
) -> Any:
    """
    Computes and returns LD values between all pairs of variants in the defined region.
    
    Args:
        species: Species name (e.g. 'homo_sapiens' for human)
        region: Genomic region
        population_name: Population name
    
    Query example: {"species": "homo_sapiens", "region": "1:169549800-169549900",
                    "population_name": "1000GENOMES:phase_3:EUR"}
    
    Returns:
        A list of JSON strings, where each string is a dictionary containing LD values
        for a pair of variants within the specified region and population. May return
        an empty list if no variant pairs with LD data are found in the region.
    """
    api = get_ensembl_api()
    try:
        result = api.get_ld_region(
            species=species,
            region=region,
            population_name=population_name,
        )
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_lookup_id(id: str) -> Any:
    """
    Look up details for any Ensembl stable identifier.
    
    Retrieve comprehensive information about any Ensembl entity (gene, transcript, protein, etc.)
    using its stable identifier.
    
    Args:
        id: Ensembl stable identifier (e.g., 'ENSG00000139618' for human BRCA2 gene,'ENST00000380152' for a transcript, or 'ENSP00000369497' for a protein)
    
    Query example: {"id": "ENSG00000139618"}
    
    Returns:
        Dictionary containing detailed information about the entity, including its type,
        location, relationships to other entities, and cross-references.
    """
    api = get_ensembl_api()
    try:
        result = api.get_lookup_id(id=id)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def post_lookup_id(ids: List[str]) -> Any:
    """
    Look up details for multiple Ensembl stable identifiers in a single request.
    
    Batch retrieval of information for multiple Ensembl entities (genes, transcripts, proteins, etc.).
    
    Args:
        ids: List of Ensembl stable identifiers (e.g., ['ENSG00000139618', 'ENSG00000141510']for human BRCA2 and TP53 genes)
    
    Returns:
        Dictionary mapping each input ID to its corresponding entity information.
        Identifiers that are not found will be excluded from the results.
    
    Query example: {"ids": ["ENSG00000157764", "ENSG00000248378"]}
    """
    api = get_ensembl_api()
    try:
        result = api.post_lookup_id(ids=ids)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def post_lookup_symbol(
    symbols: List[str],
    species: str = "homo_sapiens",
) -> Any:
    """
    Look up multiple gene symbols in a single request.
    
    Batch retrieval of Ensembl gene information for multiple external gene symbols.
    
    Args:
        species: Species name in snake_case format (e.g., 'homo_sapiens' for human)
        symbols: List of official gene symbols (e.g., ['BRCA2', 'TP53', 'APOE'])
    
    Returns:
        Dictionary mapping each input symbol to its corresponding gene information.
        Symbols that are not found will be excluded from the results.
    
    Query example: {"species": "homo_sapiens", "symbols": ["BRCA2"]}
    """
    api = get_ensembl_api()
    try:
        result = api.post_lookup_symbol(species=species, symbols=symbols)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_map(
    asm_one: str,
    region: str,
    asm_two: str,
    species: str = "homo_sapiens",
) -> Any:
    """
    Map coordinates between assemblies.

    Args:
        species: Species name (e.g. 'homo_sapiens' for human)
        asm_one: Source assembly
        region: Genomic region in source assembly
        asm_two: Target assembly

    Returns:
        Dictionary containing mapped coordinates.
    """
    api = get_ensembl_api()
    try:
        result = api.get_map(
            species=species,
            asm_one=asm_one,
            region=region,
            asm_two=asm_two,
        )
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_ontology_ancestors_chart(id: str) -> Any:
    """
    Reconstruct the entire ancestry of a term from is_a and part_of relationships.
    
    Args:
        id: Ontology term ID
    
    Returns:
        Dictionary containing ancestor chart information.
    
    Query example: {"id": "GO:0005667"}
    """
    api = get_ensembl_api()
    try:
        result = api.get_ontology_ancestors_chart(id=id)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_taxonomy_classification(id: str) -> Any:
    """
    Return the taxonomic classification of a taxon node.
    
    Args:
        id: Taxonomy ID
    
    Returns:
        Dictionary containing taxonomic classification.
    
    Query example: {"id": "9606"}
    """
    api = get_ensembl_api()
    try:
        result = api.get_taxonomy_classification(id=id)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_taxonomy_id(id: str) -> Any:
    """
    Search for a taxonomic term by its identifier or name
    
    Args:
        id: Taxonomy ID or name
    
    Returns:
        Dictionary containing taxonomy information.
    
    Query example: {"id": "9606"}
    """
    api = get_ensembl_api()
    try:
        result = api.get_taxonomy_id(id=id)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_taxonomy_name(name: str) -> Any:
    """
    Search for a taxonomic id by a non-scientific name.
    
    Args:
        name: Non-scientific name
    
    Returns:
        Dictionary containing taxonomy information.
    
    Query example: {"name": "Homo sapiens"}
    """
    api = get_ensembl_api()
    try:
        result = api.get_taxonomy_name(name=name)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_species_binding_matrix(
    binding_matrix_stable_id: str,
    species: str = "homo_sapiens",
) -> Any:
    """
    Return the specified binding matrix
    
    Args:
        species: Species name (e.g. 'homo_sapiens' for human)
        binding_matrix_stable_id: Binding matrix stable ID
    
    Returns:
        Dictionary containing binding matrix information.
    
    Query example: {"species": "homo_sapiens", "binding_matrix_stable_id": "ENSPFM0001"}
    """
    api = get_ensembl_api()
    try:
        result = api.get_species_binding_matrix(
            species=species,
            binding_matrix_stable_id=binding_matrix_stable_id,
        )
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def post_sequence_id(ids: List[str]) -> Any:
    """
    Request multiple types of sequence by a stable identifier list.
    
    Efficiently fetch sequences for multiple genes, transcripts, or proteins in a single request.
    
    Args:
        ids: List of Ensembl stable identifiers (e.g., ['ENSG00000139618', 'ENSG00000141510'])
    
    Returns:
        Dictionary mapping each identifier to its corresponding sequence and metadata.
    
    Query example: {"ids": ["ENSG00000157764", "ENSG00000248378"]}
    """
    api = get_ensembl_api()
    try:
        result = api.post_sequence_id(ids=ids)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def post_sequence_region(
    regions: List[Dict[str, Any]],
    species: str = "homo_sapiens",
) -> Any:
    """
    Get sequences by multiple regions.

    Args:
        species: Species name (e.g. 'homo_sapiens' for human)
        regions: List of genomic regions

    Returns:
        Dictionary containing sequences.
    """
    api = get_ensembl_api()
    try:
        result = api.post_sequence_region(species=species, regions=regions)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_transcript_haplotypes(
    id: str,
    species: str = "homo_sapiens",
) -> Any:
    """
    Computes observed transcript haplotype sequences based on phased genotype data.
    
    Args:
        species: Species name (e.g. 'homo_sapiens' for human)
        id: Transcript ID
    
    Returns:
        Dictionary containing transcript haplotype information.
    
    Query example: {"species": "homo_sapiens", "id": "ENST00000288602"}
    """
    api = get_ensembl_api()
    try:
        result = api.get_transcript_haplotypes(species=species, id=id)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def post_vep_hgvs(
    hgvs_notations: List[str],
    species: str = "homo_sapiens",
) -> Any:
    """
    Batch predict the functional effects of multiple variants using VEP with HGVS notation.
    
    Efficiently analyze multiple variants in a single request using the Variant Effect Predictor.
    Ideal for analyzing sets of variants from sequencing data or genetic studies.
    
    Args:
        species: Species name in snake_case format (e.g., 'homo_sapiens' for human)
        hgvs_notations: List of variants in HGVS notation format(e.g., ['ENST00000269305.4:c.2309C>T', 'NM_000059.3:c.274G>A'])
    
    Returns:
        List of dictionaries, each containing detailed variant effect predictions for one input variant.
    
    Query example: {"species": "human", "hgvs_notations": ["ENST00000366667:c.803C>T", "9:g.22125504G>C"]}
    """
    api = get_ensembl_api()
    try:
        result = api.post_vep_hgvs(species=species, hgvs_notations=hgvs_notations)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def post_vep_id(
    ids: List[str],
    species: str = "homo_sapiens",
) -> Any:
    """
    Batch predict the functional effects of multiple variants using VEP with variant identifiers.
    
    Efficiently analyze multiple known variants in a single request using the Variant Effect Predictor.
    Ideal for analyzing sets of common variants or SNP panel data.
    
    Args:
        species: Species name in snake_case format (e.g., 'homo_sapiens' for human)
        ids: List of variant identifiers (e.g., ['rs6025', 'rs429358'])
    
    Returns:
        List of dictionaries, each containing detailed variant effect predictions for one input variant.
    
    Query example: {"species": "human", "ids": ["rs56116432", "COSM476", "__VAR(sv_id)__"]}
    """
    api = get_ensembl_api()
    try:
        result = api.post_vep_id(species=species, ids=ids)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def post_vep_region(
    variants: List[Dict[str, Any]],
    species: str = "homo_sapiens",
) -> Any:
    """
    Get variant effect predictions by multiple regions.

    Args:
        species: Species name (e.g. 'homo_sapiens' for human)
        variants: List of variant definitions

    Returns:
        Dictionary containing variant effect predictions.
    """
    api = get_ensembl_api()
    try:
        result = api.post_vep_region(species=species, variants=variants)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def post_variant_recoder(
    ids: List[str],
    species: str = "homo_sapiens",
) -> Any:
    """
    Translate a list of variant identifiers, HGVS notations or genomic SPDI notations
    to all possible variant IDs, HGVS and genomic SPDI.
    
    Args:
        species: Species name (e.g. 'homo_sapiens' for human)
        ids: List of variant identifiers
    
    Returns:
        Dictionary containing variant identifier translations.
    
    Query example: {"species": "human", "ids": ["rs56116432", "rs1042779"]}
    """
    api = get_ensembl_api()
    try:
        result = api.post_variant_recoder(species=species, ids=ids)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_variation_pmcid(
    pmcid: str,
    species: str = "homo_sapiens",
) -> Any:
    """
    Fetch variants by publication using PubMed Central reference number (PMCID)
    
    Args:
        species: Species name (e.g. 'homo_sapiens' for human)
        pmcid: PubMed Central reference number
    
    Returns:
        Dictionary containing variation information.
    
    Query example: {"species": "human", "pmcid": "PMC5002951"}
    """
    api = get_ensembl_api()
    try:
        result = api.get_variation_pmcid(species=species, pmcid=pmcid)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_variation_pmid(
    pmid: str,
    species: str = "homo_sapiens",
) -> Any:
    """
    Fetch variants by publication using PubMed reference number (PMID)
    
    Args:
        species: Species name (e.g. 'homo_sapiens' for human)
        pmid: PubMed reference number
    
    Returns:
        Dictionary containing variation information.
    
    Query example: {"species": "human", "pmid": "26318936"}
    """
    api = get_ensembl_api()
    try:
        result = api.get_variation_pmid(species=species, pmid=pmid)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def post_variation(
    ids: List[str],
    species: str = "homo_sapiens",
) -> Any:
    """
    Uses a list of variant identifiers (e.g. rsID) to return the variation features including
    optional genotype, phenotype and population data.
    
    Args:
        species: Species name (e.g. 'homo_sapiens' for human)
        ids: List of variation identifiers
    
    Returns:
        Dictionary containing variation information.
    
    Query example: {"species": "human", "ids": ["rs56116432", "COSM476", "__VAR(sv_id)__"]}
    """
    api = get_ensembl_api()
    try:
        result = api.post_variation(species=species, ids=ids)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_ga4gh_beacon() -> Any:
    """
    Get Beacon information.
    
    Returns:
        Dictionary containing Beacon information.
    
    Args: None
    
    Query example: {}
    """
    api = get_ensembl_api()
    try:
        result = api.get_ga4gh_beacon()
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_ga4gh_beacon_query(params: Dict[str, Any]) -> Any:
    """
    Query Beacon.

    Args:
        params: Query parameters

    Returns:
        Dictionary containing Beacon response.
    """
    api = get_ensembl_api()
    try:
        result = api.get_ga4gh_beacon_query(params=params)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def post_ga4gh_beacon_query(data: Dict[str, Any]) -> Any:
    """
    Query Beacon with POST.

    Args:
        data: Query data

    Returns:
        Dictionary containing Beacon response.
    """
    api = get_ensembl_api()
    try:
        result = api.post_ga4gh_beacon_query(data=data)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_ga4gh_features(id: str) -> Any:
    """
    Get GA4GH features by ID.

    Args:
        id: Feature identifier

    Returns:
        Dictionary containing feature information.
    """
    api = get_ensembl_api()
    try:
        result = api.get_ga4gh_features(id=id)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def post_ga4gh_features_search(data: Dict[str, Any]) -> Any:
    """
    Get a list of sequence annotation features in GA4GH format
    
    Args:
        data: Search parameters
    
    Returns:
        Dictionary containing feature information.
    
    Query example:
        {"data": {"parentId": "ENST00000408937.7", "pageSize": 2, "featureSetId": "",
                  "featureTypes": ["cds"], "start": 197859, "end": 220023,
                  "referenceName": "X"}}
    """
    api = get_ensembl_api()
    try:
        result = api.post_ga4gh_features_search(data=data)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def post_ga4gh_callsets_search(data: Dict[str, Any]) -> Any:
    """
    Search GA4GH callsets.
    
    Args:
        data: Search parameters
    
    Returns:
        Dictionary containing callset information.
    
    Query example: {"data": {"variantSetId": 1, "pageSize": 3, "name": "HG00099"}}
    """
    api = get_ensembl_api()
    try:
        result = api.post_ga4gh_callsets_search(data=data)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_ga4gh_callsets(id: str) -> Any:
    """
    Get the GA4GH record for a specific CallSet given its identifier
    
    Args:
        id: Callset identifier
    
    Returns:
        Dictionary containing callset information.
    
    Query example: {"id": "1:NA19777"}
    """
    api = get_ensembl_api()
    try:
        result = api.get_ga4gh_callsets(id=id)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def post_ga4gh_datasets_search(data: Dict[str, Any]) -> Any:
    """
    Get a list of datasets in GA4GH format
    
    Args:
        data: Search parameters
    
    Returns:
        Dictionary containing dataset information.
    
    Query example: {"data": {}}
    """
    api = get_ensembl_api()
    try:
        result = api.post_ga4gh_datasets_search(data=data)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_ga4gh_datasets(id: str) -> Any:
    """
    Get the GA4GH record for a specific dataset given its identifier
    
    Args:
        id: Dataset identifier
    
    Returns:
        Dictionary containing dataset information.
    
    Query example: {"id": "6e340c4d1e333c7a676b1710d2e3953c"}
    """
    api = get_ensembl_api()
    try:
        result = api.get_ga4gh_datasets(id=id)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def post_ga4gh_featuresets_search(data: Dict[str, Any]) -> Any:
    """
    Search GA4GH feature sets.
    
    Args:
        data: Search parameters
    
    Returns:
        Dictionary containing feature set information.
    
    Query example: {"data": {"datasetId": "Ensembl", "pageToken": "", "pageSize": 2}}
    """
    api = get_ensembl_api()
    try:
        result = api.post_ga4gh_featuresets_search(data=data)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_ga4gh_featuresets(id: str) -> Any:
    """
    Return the GA4GH record for a specific featureSet given its identifier
    
    Args:
        id: Feature set identifier
    
    Returns:
        Dictionary containing feature set information.
    
    Query example: {"id": "Ensembl.114.GRCh38"}
    """
    api = get_ensembl_api()
    try:
        result = api.get_ga4gh_featuresets(id=id)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_ga4gh_variants(id: str) -> Any:
    """
    Get GA4GH variant by ID.
    
    Args:
        id: Variant identifier
    
    Returns:
        Dictionary containing variant information.
    
    Query example: {"id": "1:rs1333049"}
    """
    api = get_ensembl_api()
    try:
        result = api.get_ga4gh_variants(id=id)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def post_ga4gh_variantannotations_search(data: Dict[str, Any]) -> Any:
    """
    Return variant annotation information in GA4GH format for a region on a reference sequence
    
    Args:
        data: Search parameters
    
    Returns:
        Dictionary containing variant annotation information.
    
    Query example:
        {"data": {"pageSize": 2, "variantAnnotationSetId": "Ensembl",
                  "referenceId": "9489ae7581e14efcad134f02afafe26c",
                  "start": 25221400, "end": 25221500}}
    """
    api = get_ensembl_api()
    try:
        result = api.post_ga4gh_variantannotations_search(data=data)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def post_ga4gh_variants_search(data: Dict[str, Any]) -> Any:
    """
    Return variant call information in GA4GH format for a region on a reference sequence
    
    Args:
        data: Search parameters
    
    Returns:
        Dictionary containing variant information.
    
    Query example:
        {"data": {"variantSetId": 1, "callSetIds": ["1:NA19777", "1:HG01242", "1:HG01142"],
                  "referenceName": 22, "start": 17190024, "end": 17671934,
                  "pageToken": "", "pageSize": 3}}
    """
    api = get_ensembl_api()
    try:
        result = api.post_ga4gh_variants_search(data=data)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def post_ga4gh_variantsets_search(data: Dict[str, Any]) -> Any:
    """
    Search GA4GH variant sets.
    
    Args:
        data: Search parameters
    
    Returns:
        Dictionary containing variant set information.
    
    Query example:
        {"data": {"datasetId": "6e340c4d1e333c7a676b1710d2e3953c", "pageToken": "", "pageSize": 2}}
    """
    api = get_ensembl_api()
    try:
        result = api.post_ga4gh_variantsets_search(data=data)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_ga4gh_variantsets(id: str) -> Any:
    """
    Return the GA4GH record for a specific VariantSet given its identifier
    
    Args:
        id: Variant set identifier
    
    Returns:
        Dictionary containing variant set information.
    
    Query example: {"id": "1"}
    """
    api = get_ensembl_api()
    try:
        result = api.get_ga4gh_variantsets(id=id)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def post_ga4gh_references_search(data: Dict[str, Any]) -> Any:
    """
    Return a list of reference sequences in GA4GH format
    
    Args:
        data: Search parameters
    
    Returns:
        Dictionary containing reference information.
    
    Query example: {"data": {"referenceSetId": "GRCh38", "pageSize": 10}}
    """
    api = get_ensembl_api()
    try:
        result = api.post_ga4gh_references_search(data=data)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_ga4gh_references(id: str) -> Any:
    """
    Return data for a specific reference in GA4GH format by id
    
    Args:
        id: Reference identifier
    
    Returns:
        Dictionary containing reference information.
        
    Query example: {"id": "9489ae7581e14efcad134f02afafe26c"}
    """
    api = get_ensembl_api()
    try:
        result = api.get_ga4gh_references(id=id)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def post_ga4gh_referencesets_search(data: Dict[str, Any]) -> Any:
    """
    Search GA4GH reference sets.
    
    Args:
        data: Search parameters
    
    Returns:
        Dictionary containing following fields:
        referenceSets: contains all available reference genome collections
        nextPageToken: paging marker
    
    Query example: {"data": {}}
    """
    api = get_ensembl_api()
    try:
        result = api.post_ga4gh_referencesets_search(data=data)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_ga4gh_referencesets(id: str) -> Any:
    """
    Search data for a specific reference set in GA4GH format by ID
    
    Args:
        id: Reference set identifier
    
    Returns:
        Dictionary containing following fields:
        id: Unique identifier (short name) for genome
        name: Human-readable name
        assemblyId: Official Genome Assembly ID
        ncbiTaxonId: NCBI Species ID
        description: Full name of the genome
    """
    api = get_ensembl_api()
    try:
        result = api.get_ga4gh_referencesets(id=id)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def post_ga4gh_variantannotationsets_search(data: Dict[str, Any]) -> Any:
    """
    Return a list of annotation sets in GA4GH format
    
    Args:
        data: Search parameters
    
    Returns:
        Dictionary containing variant annotation set information.
    
    Query example: {"data": {"variantSetId": "Ensembl"}}
    """
    api = get_ensembl_api()
    try:
        result = api.post_ga4gh_variantannotationsets_search(data=data)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_ga4gh_variantannotationsets(id: str) -> Any:
    """
    Return meta data for a specific annotation set in GA4GH format by ID
    
    Args:
        id: Variant annotation set identifier
    
    Returns:
        Dictionary containing variant annotation set information.
    
    Query example: {"id": "Ensembl"}
    """
    api = get_ensembl_api()
    try:
        result = api.get_ga4gh_variantannotationsets(id=id)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_genetree_member_id(
    id: str,
    species: str = "homo_sapiens",
) -> Any:
    """
    Retrieve the gene tree containing a gene identified by its Ensembl ID.

    Find the phylogenetic tree showing evolutionary relationships for a gene of interest,
    identified using its Ensembl stable identifier. Useful for understanding gene evolution
    when you have the specific gene ID.
    
    Args:
        species: Species name in snake_case format (e.g., 'homo_sapiens' for human)
        id: Ensembl gene, transcript, or translation stable identifier(e.g., 'ENSG00000139618' for human BRCA2 gene)
    
    Returns:
        Dictionary containing gene tree information in a nested structure, including:
        - Taxonomy and sequence relationships
        - Branch lengths representing evolutionary distance
        - Bootstrap values indicating tree confidence
        - Sequence alignments used to build the tree
        - Member genes from different species
    
    Query example: {"species": "human", "id": "ENSG00000167664"}
    """
    api = get_ensembl_api()
    try:
        result = api.get_genetree_member_id(species=species, id=id)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_info_biotypes_groups(
    group: str,
    object_type: str,
) -> Any:
    """
    With :group argument provided, list the properties of biotypes within that group.
    Object type (gene or transcript) can be provided for filtering.
    
    Args:
        group: Biotype group
        object_type: Object type (gene or transcript)
    
    Returns:
        Dictionary containing:
        - object_type
        - biotype_group
        - so_term
        - so_acc
        - name
    """
    api = get_ensembl_api()
    try:
        result = api.get_info_biotypes_groups(group=group, object_type=object_type)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_info_biotypes_name(
    name: str,
    object_type: str,
) -> Any:
    """
    List the properties of biotypes with a given name. Object type (gene or transcript)
    can be provided for filtering.
    
    Args:
        name: Biotype name
        object_type: Object type (gene or transcript)
    
    Returns:
        Dictionary describing the biotype.
    
    Query example: {"name": "protein_coding", "object_type": "gene"}
    """
    api = get_ensembl_api()
    try:
        result = api.get_info_biotypes_name(name=name, object_type=object_type)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_info_compara_species_sets(method: str) -> Any:
    """
    List all collections of species analysed with the specified compara method.
    
    Args:
        method: Comparative analysis method
    
    Returns:
        Dictionary containing species set information.
    
    Query example: {"method": "EPO"}
    """
    api = get_ensembl_api()
    try:
        result = api.get_info_compara_species_sets(method=method)
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


@tool(parse_docstring=True)
async def get_info_comparas() -> Any:
    """
    Get all available comparative genomics databases and their data release.
    
    Args: None
    
    Query example: {}
    
    Returns:
        Dictionary containing:
            release: version or release number
            name: names of compara databases or analyses
    """
    api = get_ensembl_api()
    try:
        result = api.get_info_comparas()
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
    return result


def ensembl_system_prompt() -> str:
    """
    System prompt text for clients using these Ensembl tools.
    """
    return (
        "You have access to tools for querying the Ensembl REST API.\n"
        "Use these tools to get information about genes, sequences, variants, and more.\n"
        "The API provides access to genomic data across multiple species.\n"
        "For species names, use the format 'homo_sapiens' for human, 'mus_musculus' for mouse, etc.\n"
        "For regions, use the format 'chromosome:start..end' (e.g. 'X:1000000..1000100').\n"
        "For variants, use proper HGVS notation (e.g. 'ENST00000003084:c.1431_1433delTTC').\n"
    )


ensembl_tools = {
    "get_lookup_symbol": get_lookup_symbol,
    "get_homology_symbol": get_homology_symbol,
    "get_sequence_region": get_sequence_region,
    "get_vep_hgvs": get_vep_hgvs,
    "get_genetree_id": get_genetree_id,
    "get_info_assembly": get_info_assembly,
    "get_xrefs_symbol": get_xrefs_symbol,
    "get_archive_id": get_archive_id,
    "post_archive_id": post_archive_id,
    "get_cafe_genetree_id": get_cafe_genetree_id,
    "get_cafe_genetree_member_symbol": get_cafe_genetree_member_symbol,
    "get_cafe_genetree_member_id": get_cafe_genetree_member_id,
    "get_genetree_member_symbol": get_genetree_member_symbol,
    "get_alignment_region": get_alignment_region,
    "get_homology_id": get_homology_id,
    "get_xrefs_id": get_xrefs_id,
    "get_xrefs_name": get_xrefs_name,
    "get_info_analysis": get_info_analysis,
    "get_assembly_region_info": get_assembly_region_info,
    "get_info_biotypes": get_info_biotypes,
    "get_info_compara_methods": get_info_compara_methods,
    "get_info_external_dbs": get_info_external_dbs,
    "get_map_cdna": get_map_cdna,
    "get_map_cds": get_map_cds,
    "get_map_translation": get_map_translation,
    "get_ontology_ancestors": get_ontology_ancestors,
    "get_ontology_descendants": get_ontology_descendants,
    "get_ontology_id": get_ontology_id,
    "get_ontology_name": get_ontology_name,
    "get_overlap_id": get_overlap_id,
    "get_overlap_region": get_overlap_region,
    "get_overlap_translation": get_overlap_translation,
    "get_phenotype_region": get_phenotype_region,
    "get_phenotype_gene": get_phenotype_gene,
    "get_phenotype_accession": get_phenotype_accession,
    "get_sequence_id": get_sequence_id,
    "get_vep_id": get_vep_id,
    "get_vep_region": get_vep_region,
    "get_variation": get_variation,
    "get_variant_recoder": get_variant_recoder,
    "get_info_data": get_info_data,
    "get_info_eg_version": get_info_eg_version,
    "get_info_divisions": get_info_divisions,
    "get_info_genomes": get_info_genomes,
    "get_info_genomes_accession": get_info_genomes_accession,
    "get_info_genomes_assembly": get_info_genomes_assembly,
    "get_info_genomes_division": get_info_genomes_division,
    "get_info_genomes_taxonomy": get_info_genomes_taxonomy,
    "get_info_ping": get_info_ping,
    "get_info_rest": get_info_rest,
    "get_info_software": get_info_software,
    "get_info_species": get_info_species,
    "get_info_variation": get_info_variation,
    "get_info_variation_consequence_types": get_info_variation_consequence_types,
    "get_info_variation_populations": get_info_variation_populations,
    "get_ld": get_ld,
    "get_ld_pairwise": get_ld_pairwise,
    "get_ld_region": get_ld_region,
    "get_lookup_id": get_lookup_id,
    "post_lookup_id": post_lookup_id,
    "post_lookup_symbol": post_lookup_symbol,
    "get_map": get_map,
    "get_ontology_ancestors_chart": get_ontology_ancestors_chart,
    "get_taxonomy_classification": get_taxonomy_classification,
    "get_taxonomy_id": get_taxonomy_id,
    "get_taxonomy_name": get_taxonomy_name,
    "get_species_binding_matrix": get_species_binding_matrix,
    "post_sequence_id": post_sequence_id,
    "post_sequence_region": post_sequence_region,
    "get_transcript_haplotypes": get_transcript_haplotypes,
    "post_vep_hgvs": post_vep_hgvs,
    "post_vep_id": post_vep_id,
    "post_vep_region": post_vep_region,
    "post_variant_recoder": post_variant_recoder,
    "get_variation_pmcid": get_variation_pmcid,
    "get_variation_pmid": get_variation_pmid,
    "post_variation": post_variation,
    "get_ga4gh_beacon": get_ga4gh_beacon,
    "get_ga4gh_beacon_query": get_ga4gh_beacon_query,
    "post_ga4gh_beacon_query": post_ga4gh_beacon_query,
    "get_ga4gh_features": get_ga4gh_features,
    "post_ga4gh_features_search": post_ga4gh_features_search,
    "post_ga4gh_callsets_search": post_ga4gh_callsets_search,
    "get_ga4gh_callsets": get_ga4gh_callsets,
    "post_ga4gh_datasets_search": post_ga4gh_datasets_search,
    "get_ga4gh_datasets": get_ga4gh_datasets,
    "post_ga4gh_featuresets_search": post_ga4gh_featuresets_search,
    "get_ga4gh_featuresets": get_ga4gh_featuresets,
    "get_ga4gh_variants": get_ga4gh_variants,
    "post_ga4gh_variantannotations_search": post_ga4gh_variantannotations_search,
    "post_ga4gh_variants_search": post_ga4gh_variants_search,
    "post_ga4gh_variantsets_search": post_ga4gh_variantsets_search,
    "get_ga4gh_variantsets": get_ga4gh_variantsets,
    "post_ga4gh_references_search": post_ga4gh_references_search,
    "get_ga4gh_references": get_ga4gh_references,
    "post_ga4gh_referencesets_search": post_ga4gh_referencesets_search,
    "get_ga4gh_referencesets": get_ga4gh_referencesets,
    "post_ga4gh_variantannotationsets_search": post_ga4gh_variantannotationsets_search,
    "get_ga4gh_variantannotationsets": get_ga4gh_variantannotationsets,
    "get_genetree_member_id": get_genetree_member_id,
    "get_info_biotypes_groups": get_info_biotypes_groups,
    "get_info_biotypes_name": get_info_biotypes_name,
    "get_info_compara_species_sets": get_info_compara_species_sets,
    "get_info_comparas": get_info_comparas,
}
   