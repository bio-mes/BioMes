import requests
import urllib.parse
from typing import List, Union
# agentflow/tool/ncbi.py

from typing import Any, List, Optional, Union

from langchain_core.tools import tool

class NCBIAPI:
    BASE_URL = "https://api.ncbi.nlm.nih.gov/datasets/v2"


    def __init__(self):
        self.session = requests.Session()

    def _get(self, endpoint, params=None):
        """Internal helper for GET requests."""
        url = self.BASE_URL + endpoint
        headers = {
            'accept': 'application/json',
        }
        r = requests.get(url, params=params, headers=headers)
        r.raise_for_status()
        return r.text

    def get_gene_metadata_by_gene_name(self, name: str, species: str = 'human'):
        """
        Get a gene summary by gene symbol. By default, in paged JSON format.
        
        The returned JSON contains detailed gene information including:
        - Basic gene info: gene ID, symbol, description, tax ID, species name
        - Gene type and orientation
        - Reference standards and genomic locations
        - Chromosome location
        - External database IDs (HGNC, Swiss-Prot, Ensembl, OMIM)
        - Gene synonyms
        - Transcript and protein counts
        - Gene summary/description
        - Gene Ontology annotations:
          - Molecular functions (e.g. DNA binding, transcription regulation)
          - Biological processes (e.g. apoptosis, cell cycle regulation)
          - Cellular components (e.g. nucleus, cytoplasm)

        Args:
            name: Gene name/symbol to search for
            species: Species to search within (default: 'human')

        Returns:
            Text response containing gene metadata in JSON format

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        endpoint = f"/gene/symbol/{urllib.parse.quote(name)}/taxon/{urllib.parse.quote(species)}"
        params = {}
        return self._get(endpoint, params)

    def get_gene_by_ids(self, gene_ids: Union[int, List[int]]):
        """
        Get gene information by gene ID.
        
        Args:
            gene_ids: A list of Gene IDs
            
        Returns:
            json format response
        """
        if isinstance(gene_ids, int):
            gene_ids = [gene_ids]
        endpoint = f"/gene/id/{urllib.parse.quote(','.join(map(str, gene_ids)))}"
        return self._get(endpoint)

    def get_gene_by_accession(self, accessions: Union[str, List[str]]):
        """
        Get gene information by accession.
        
        Args:
            accessions: A single Accession or a list of Accessions
            
        Returns:
            json format response including gene information
        """
        if isinstance(accessions, str):
            accessions = [accessions]
        endpoint = f"/gene/accession/{urllib.parse.quote(','.join(accessions))}"
        return self._get(endpoint)

    def get_gene_dataset_report_by_id(self, gene_ids: Union[int, List[int]]):
        """
        Get gene information by dataset report.
        
        Args:
            gene_ids: A single Gene ID or a list of Gene IDs
            
        Returns:
            json format response including dataset report
        """
        if isinstance(gene_ids, int):
            gene_ids = [gene_ids]
        endpoint = f"/gene/id/{urllib.parse.quote(','.join(map(str, gene_ids)))}/dataset_report"
        return self._get(endpoint)

    def get_gene_product_report_by_id(self, gene_ids: Union[int, List[int]]):
        """
        Get gene product report by gene ID.
        
        Args:
            gene_ids: Gene ID
            
        Returns:
            json format response including gene product report
        """
        if isinstance(gene_ids, int):
            gene_ids = [gene_ids]
        endpoint = f"/gene/id/{urllib.parse.quote(','.join(map(str, gene_ids)))}/product_report"
        return self._get(endpoint)

    def get_gene_orthologs(self, gene_id: int):
        """
        Get gene orthologs by gene ID.
        
        Args:
            gene_id: Gene ID
            
        Returns:
            json format response including gene orthologs
        """
        endpoint = f"/gene/id/{urllib.parse.quote(str(gene_id))}/orthologs"
        return self._get(endpoint)

    def get_gene_by_taxon(self, taxon: str):
        """
        Get gene information by taxon.
        
        Args:
            taxon: Taxon
            
        Returns:
            json format response including gene information
        """
        endpoint = f"/gene/taxon/{urllib.parse.quote(taxon)}"
        return self._get(endpoint)

    def get_gene_counts_by_taxon(self, taxon: str):
        """
        Get gene counts by taxon.
        
        Args:
            taxon: Taxon
            
        Returns:
            json format response including gene counts
        """
        endpoint = f"/gene/taxon/{urllib.parse.quote(taxon)}/counts"
        return self._get(endpoint)

    def get_chromosome_summary(self, taxon: str, annotation_name: str):
        """
        Get chromosome summary by taxon and annotation name.
        
        Args:
            taxon: Taxon
            annotation_name: Annotation name
            
        Returns:
            json format response including chromosome summary
        """
        endpoint = f"/gene/taxon/{urllib.parse.quote(taxon)}/annotation/{urllib.parse.quote(annotation_name)}/chromosome_summary"
        return self._get(endpoint)

    def get_genome_by_accession(self, accession: str):
        """
        Get genome information by accession.
        """
        endpoint = f"/genome/accession/{urllib.parse.quote(accession)}"
        params = {}
        return self._get(endpoint, params)

    def get_gene_by_accession_dataset_report(self, accessions: Union[str, List[str]]):
        """
        Get dataset reports by accession IDs.
        
        Args:
            accessions: A single Accession or a list of Accessions
            
        Returns:
            json format response including dataset report
        """
        if isinstance(accessions, str):
            accessions = [accessions]
        endpoint = f"/gene/accession/{urllib.parse.quote(','.join(accessions))}/dataset_report"
        return self._get(endpoint)

    def get_gene_by_accession_product_report(self, accessions: Union[str, List[str]]):
        """
        Get gene product reports by accession IDs.
        
        Args:
            accessions: A single Accession or a list of Accessions
            
        Returns:
            json format response including product report
        """
        if isinstance(accessions, str):
            accessions = [accessions]
        endpoint = f"/gene/accession/{urllib.parse.quote(','.join(accessions))}/product_report"
        return self._get(endpoint)

    def get_gene_download_by_id(self, gene_ids: Union[int, List[int]]):
        """
        Get a gene dataset by gene ID.
        
        Args:
            gene_ids: A single Gene ID or a list of Gene IDs
            
        Returns:
            json format response including gene dataset
        """
        if isinstance(gene_ids, int):
            gene_ids = [gene_ids]
        endpoint = f"/gene/id/{urllib.parse.quote(','.join(map(str, gene_ids)))}/download"
        return self._get(endpoint)

    def get_gene_download_summary_by_id(self, gene_ids: Union[int, List[int]]):
        """
        Get gene download summary by GeneID.
        
        Args:
            gene_ids: A single Gene ID or a list of Gene IDs
            
        Returns:
            json format response including download summary
        """
        if isinstance(gene_ids, int):
            gene_ids = [gene_ids]
        endpoint = f"/gene/id/{urllib.parse.quote(','.join(map(str, gene_ids)))}/download_summary"
        return self._get(endpoint)

    def get_gene_links_by_id(self, gene_ids: Union[int, List[int]]):
        """
        Get gene links by gene ID.
        
        Args:
            gene_ids: A single Gene ID or a list of Gene IDs
            
        Returns:
            json format response including gene links
        """
        if isinstance(gene_ids, int):
            gene_ids = [gene_ids]
        endpoint = f"/gene/id/{urllib.parse.quote(','.join(map(str, gene_ids)))}/links"
        return self._get(endpoint)

    def get_gene_dataset_report_by_locus_tag(self, locus_tags: Union[str, List[str]]):
        """
        Get gene dataset reports by locus tag.
        
        Args:
            locus_tags: A single Locus tag or a list of Locus tags
            
        Returns:
            json format response including dataset report
        """
        if isinstance(locus_tags, str):
            locus_tags = [locus_tags]
        endpoint = f"/gene/locus_tag/{urllib.parse.quote(','.join(locus_tags))}/dataset_report"
        return self._get(endpoint)

    def get_gene_product_report_by_locus_tag(self, locus_tags: Union[str, List[str]]):
        """
        Get gene product reports by locus tags.
        
        Args:
            locus_tags: A single Locus tag or a list of Locus tags
            
        Returns:
            json format response including product report
        """
        if isinstance(locus_tags, str):
            locus_tags = [locus_tags]
        endpoint = f"/gene/locus_tag/{urllib.parse.quote(','.join(locus_tags))}/product_report"
        return self._get(endpoint)

    def get_gene_by_symbol_dataset_report(self, symbols: str, taxon: str = 'human'):
        """
        Get dataset reports by taxons.
        
        Args:
            symbols: Gene symbol
            taxon: Taxon
            
        Returns:
            json format response including dataset report
        """
        endpoint = f"/gene/symbol/{urllib.parse.quote(symbols)}/taxon/{urllib.parse.quote(taxon)}/dataset_report"
        return self._get(endpoint)

    def get_gene_by_symbol_product_report(self, symbols: str, taxon: str = 'human'):
        """
        Get product reports by taxon.
        
        Args:
            symbols: Gene symbol
            taxon: Taxon
            
        Returns:
            json format response including product report
        """
        endpoint = f"/gene/symbol/{urllib.parse.quote(symbols)}/taxon/{urllib.parse.quote(taxon)}/product_report"
        return self._get(endpoint)

    def get_gene_by_taxon_dataset_report(self, taxon: str):
        """
        Get gene dataset reports by taxonomic identifier.
        
        Args:
            taxon: Taxon
            
        Returns:
            json format response including dataset report
        """
        endpoint = f"/gene/taxon/{urllib.parse.quote(taxon)}/dataset_report"
        return self._get(endpoint)

    def get_gene_by_taxon_product_report(self, taxon: str):
        """
        Get gene product reports by taxonomic identifier.
        
        Args:
            taxon: Taxon
            
        Returns:
            json format response including product report
        """
        endpoint = f"/gene/taxon/{urllib.parse.quote(taxon)}/product_report"
        return self._get(endpoint)

    def get_genome_annotation_report(self, accession: str):
        """
        Get genome annotation reports by genome accession.
        
        Args:
            accession: Genome accession
            
        Returns:
            json format response including annotation reports
        """
        endpoint = f"/genome/accession/{urllib.parse.quote(accession)}/annotation_report"
        return self._get(endpoint)

    def get_genome_annotation_report_download(self, accession: str):
        """
        Get an annotation report dataset by accession.
        
        Args:
            accession: Genome accession
            
        Returns:
            json format response including annotation report dataset
        """
        endpoint = f"/genome/accession/{urllib.parse.quote(accession)}/annotation_report/download"
        return self._get(endpoint)

    def get_genome_annotation_report_download_summary(self, accession: str):
        """
        Preview feature dataset download.
        
        Args:
            accession: Genome accession
            
        Returns:
            json format response including download summary
        """
        endpoint = f"/genome/accession/{urllib.parse.quote(accession)}/annotation_report/download_summary"
        return self._get(endpoint)

    def get_genome_annotation_summary(self, accession: str):
        """
        Get genome annotation report summary information.
        
        Args:
            accession: Genome accession
            
        Returns:
            json format response including annotation summary
        """
        endpoint = f"/genome/accession/{urllib.parse.quote(accession)}/annotation_summary"
        return self._get(endpoint)

    def get_genome_revision_history(self, accession: str):
        """
        Get revision history for assembly by accession.
        
        Args:
            accession: Genome accession
            
        Returns:
            json format response including revision history
        """
        endpoint = f"/genome/accession/{urllib.parse.quote(accession)}/revision_history"
        return self._get(endpoint)

    def get_genome_sequence_reports(self, accession: str):
        """
        Get sequence reports by accessions.
        
        Args:
            accession: Genome accession
            
        Returns:
            json format response including sequence reports
        """
        endpoint = f"/genome/accession/{urllib.parse.quote(accession)}/sequence_reports"
        return self._get(endpoint)

    def check_genome_accessions(self, accessions: Union[str, List[str]]):
        """
        Check the validity of genome accessions.
        
        Args:
            accessions: Comma-separated list of genome accessions
            
        Returns:
            json format response including validity check results
        """
        if isinstance(accessions, str):
            accessions = [accessions]
        endpoint = f"/genome/accession/{urllib.parse.quote(','.join(accessions))}/check"
        return self._get(endpoint)

    def get_genome_dataset_report_by_accession(self, accessions: Union[str, List[str]]):
        """
        Get dataset reports by accessions.
        
        Args:
            accessions: Comma-separated list of genome accessions
            
        Returns:
            json format response including dataset reports
        """
        if isinstance(accessions, str):
            accessions = [accessions]
        endpoint = f"/genome/accession/{urllib.parse.quote(','.join(accessions))}/dataset_report"
        return self._get(endpoint)

    def get_genome_download(self, accessions: Union[str, List[str]]):
        """
        Get a genome dataset by accession.
        
        Args:
            accessions: Comma-separated list of genome accessions
            
        Returns:
            json format response including genome dataset
        """
        if isinstance(accessions, str):
            accessions = [accessions]
        endpoint = f"/genome/accession/{urllib.parse.quote(','.join(accessions))}/download"
        return self._get(endpoint)

    def get_genome_download_summary(self, accessions: Union[str, List[str]]):
        """
        Preview genome dataset download.
        
        Args:
            accessions: Comma-separated list of genome accessions
            
        Returns:
            json format response including download summary
        """
        if isinstance(accessions, str):
            accessions = [accessions]
        endpoint = f"/genome/accession/{urllib.parse.quote(','.join(accessions))}/download_summary"
        return self._get(endpoint)

    def get_genome_links(self, accessions: Union[str, List[str]]):
        """
        Get assembly links by accessions.
        
        Args:
            accessions: Comma-separated list of genome accessions
            
        Returns:
            json format response including assembly links
        """
        if isinstance(accessions, str):
            accessions = [accessions]
        endpoint = f"/genome/accession/{urllib.parse.quote(','.join(accessions))}/links"
        return self._get(endpoint)

    def get_genome_dataset_report_by_assembly_name(self, assembly_names: Union[str, List[str]]):
        """
        Get dataset reports by assembly name (exact).
        
        Args:
            assembly_names: Assembly names
            
        Returns:
            json format response including dataset reports
        """
        if isinstance(assembly_names, str):
            assembly_names = [assembly_names]
        endpoint = f"/genome/assembly_name/{urllib.parse.quote(','.join(assembly_names))}/dataset_report"
        return self._get(endpoint)

    def get_genome_dataset_report_by_bioproject(self, bioprojects: Union[str, List[str]]):
        """
        Get dataset reports by bioproject.
        
        Args:
            bioprojects: BioProject accessions
            
        Returns:
            json format response including dataset reports
        """
        if isinstance(bioprojects, str):
            bioprojects = [bioprojects]
        endpoint = f"/genome/bioproject/{urllib.parse.quote(','.join(bioprojects))}/dataset_report"
        return self._get(endpoint)

    def get_genome_dataset_report_by_biosample(self, biosample_ids: Union[str, List[str]]):
        """
        Get dataset reports by biosample id.
        
        Args:
            biosample_ids: BioSample IDs
            
        Returns:
            json format response including dataset reports
        """
        if isinstance(biosample_ids, str):
            biosample_ids = [biosample_ids]
        endpoint = f"/genome/biosample/{urllib.parse.quote(','.join(biosample_ids))}/dataset_report"
        return self._get(endpoint)

    def get_sequence_assemblies(self, accession: str):
        """
        Get assembly accessions for a sequence accession.
        
        Args:
            accession: Sequence accession
            
        Returns:
            json format response including assembly accessions
        """
        endpoint = f"/genome/sequence_accession/{urllib.parse.quote(accession)}/sequence_assemblies"
        return self._get(endpoint)

    def get_genome_checkm_histogram(self, species_taxon: str):
        """
        Get CheckM histogram by species taxon.
        
        Args:
            species_taxon: Species taxon ID
            
        Returns:
            json format response including CheckM histogram
        """
        endpoint = f"/genome/taxon/{urllib.parse.quote(species_taxon)}/checkm_histogram"
        return self._get(endpoint)

    def get_genome_dataset_report_by_taxon(self, taxons: str):
        """
        Get dataset reports by taxons.
        
        Args:
            taxons: Comma-separated list of taxon IDs
            
        Returns:
            json format response including dataset reports
        """
        endpoint = f"/genome/taxon/{urllib.parse.quote(taxons)}/dataset_report"
        return self._get(endpoint)

    def get_genome_dataset_report_by_wgs(self, wgs_accessions: Union[str, List[str]]):
        """
        Get dataset reports by wgs accession.
        
        Args:
            wgs_accessions: WGS accessions
            
        Returns:
            json format response including dataset reports
        """
        if isinstance(wgs_accessions, str):
            wgs_accessions = [wgs_accessions]
        endpoint = f"/genome/wgs/{urllib.parse.quote(','.join(wgs_accessions))}/dataset_report"
        return self._get(endpoint)
    
    def get_prokaryote_gene_dataset_by_refseq_protein_accession(self, refseq_protein_accession: str):
        """
        Get a prokaryote gene dataset by RefSeq protein accession.
        """
        endpoint = f"/protein/accession/{urllib.parse.quote(refseq_protein_accession)}/download"
        return self._get(endpoint)

    # Virus related endpoints
    def get_virus_annotation_report(self, accessions: Union[str, List[str]]):
        """
        Get virus annotation report by accessions.
        
        Args:
            accessions: Virus accessions
            
        Returns:
            json format response including annotation report
        """
        if isinstance(accessions, str):
            accessions = [accessions]
        endpoint = f"/virus/accession/{urllib.parse.quote(','.join(accessions))}/annotation_report"
        return self._get(endpoint)

    def check_virus_accessions(self, accessions: Union[str, List[str]]):
        """
        Check virus accessions validity.
        
        Args:
            accessions: Virus accessions
            
        Returns:
            json format response including validity check results
        """
        if isinstance(accessions, str):
            accessions = [accessions]
        endpoint = f"/virus/accession/{urllib.parse.quote(','.join(accessions))}/check"
        return self._get(endpoint)

    def get_virus_dataset_report(self, accessions: Union[str, List[str]]):
        """
        Get virus dataset report by accessions.
        
        Args:
            accessions: Virus accessions
            
        Returns:
            json format response including dataset report
        """
        if isinstance(accessions, str):
            accessions = [accessions]
        endpoint = f"/virus/accession/{urllib.parse.quote(','.join(accessions))}/dataset_report"
        return self._get(endpoint)

    def get_virus_genome_download(self, accessions: Union[str, List[str]]):
        """
        Download virus genome by accessions.
        
        Args:
            accessions: Virus accessions
            
        Returns:
            json format response including genome data
        """
        if isinstance(accessions, str):
            accessions = [accessions]
        endpoint = f"/virus/accession/{urllib.parse.quote(','.join(accessions))}/genome/download"
        return self._get(endpoint)

    def get_virus_by_taxon_annotation_report(self, taxon: str):
        """
        Get virus annotation report by taxon.
        
        Args:
            taxon: Virus taxon
            
        Returns:
            json format response including annotation report
        """
        endpoint = f"/virus/taxon/{urllib.parse.quote(taxon)}/annotation_report"
        return self._get(endpoint)

    def get_virus_by_taxon_dataset_report(self, taxon: str):
        """
        Get virus dataset report by taxon.
        
        Args:
            taxon: Virus taxon
            
        Returns:
            json format response including dataset report
        """
        endpoint = f"/virus/taxon/{urllib.parse.quote(taxon)}/dataset_report"
        return self._get(endpoint)

    def get_virus_by_taxon_genome(self, taxon: str):
        """
        Get virus genome by taxon.
        
        Args:
            taxon: Virus taxon
            
        Returns:
            json format response including genome data
        """
        endpoint = f"/virus/taxon/{urllib.parse.quote(taxon)}/genome"
        return self._get(endpoint)

    def get_virus_by_taxon_genome_download(self, taxon: str):
        """
        Download virus genome by taxon.
        
        Args:
            taxon: Virus taxon
            
        Returns:
            json format response including genome data
        """
        endpoint = f"/virus/taxon/{urllib.parse.quote(taxon)}/genome/download"
        return self._get(endpoint)

    def get_virus_by_taxon_genome_table(self, taxon: str):
        """
        Get virus genome table by taxon.
        
        Args:
            taxon: Virus taxon
            
        Returns:
            json format response including genome table
        """
        endpoint = f"/virus/taxon/{urllib.parse.quote(taxon)}/genome/table"
        return self._get(endpoint)

    def get_sars2_protein(self, proteins: Union[str, List[str]]):
        """
        Get SARS-CoV-2 protein data.
        
        Args:
            proteins: Protein identifiers
            
        Returns:
            json format response including protein data
        """
        if isinstance(proteins, str):
            proteins = [proteins]
        endpoint = f"/virus/taxon/sars2/protein/{urllib.parse.quote(','.join(proteins))}"
        return self._get(endpoint)

    def get_sars2_protein_download(self, proteins: Union[str, List[str]]):
        """
        Download SARS-CoV-2 protein data.
        
        Args:
            proteins: Protein identifiers
            
        Returns:
            json format response including protein data
        """
        if isinstance(proteins, str):
            proteins = [proteins]
        endpoint = f"/virus/taxon/sars2/protein/{urllib.parse.quote(','.join(proteins))}/download"
        return self._get(endpoint)

    def get_sars2_protein_table(self, proteins: Union[str, List[str]]):
        """
        Get SARS-CoV-2 protein table.
        
        Args:
            proteins: Protein identifiers
            
        Returns:
            json format response including protein table
        """
        if isinstance(proteins, str):
            proteins = [proteins]
        endpoint = f"/virus/taxon/sars2/protein/{urllib.parse.quote(','.join(proteins))}/table"
        return self._get(endpoint)

    # Version endpoint
    def get_version(self):
        """
        Get current version of all services.
        
        Returns:
            json format response including version information
        """
        endpoint = "/version"
        return self._get(endpoint)

    # Taxonomy related endpoints
    def get_taxonomy_related_ids(self, tax_id: str):
        """
        Get related taxonomy IDs.
        
        Args:
            tax_id: Taxonomy ID
            
        Returns:
            json format response including related IDs
        """
        endpoint = f"/taxonomy/taxon/{urllib.parse.quote(str(tax_id))}/related_ids"
        return self._get(endpoint)

    def get_taxonomy_download(self, tax_ids: Union[int, List[int]]):
        """
        Download taxonomy data.
        
        Args:
            tax_ids: Taxonomy IDs
            
        Returns:
            json format response including taxonomy data
        """
        if isinstance(tax_ids, int):
            tax_ids = [tax_ids]
        endpoint = f"/taxonomy/taxon/{urllib.parse.quote(','.join(map(str, tax_ids)))}/download"
        return self._get(endpoint)

    def get_taxonomy_image(self, taxon: str):
        """
        Get taxonomy image.
        
        Args:
            taxon: Taxonomy ID
            
        Returns:
            json format response including image data
        """
        endpoint = f"/taxonomy/taxon/{urllib.parse.quote(taxon)}/image"
        return self._get(endpoint)

    def get_taxonomy_image_metadata(self, taxon: str):
        """
        Get taxonomy image metadata.
        
        Args:
            taxon: Taxonomy ID
            
        Returns:
            json format response including image metadata
        """
        endpoint = f"/taxonomy/taxon/{urllib.parse.quote(taxon)}/image/metadata"
        return self._get(endpoint)

    def get_taxonomy_links(self, taxon: str):
        """
        Get taxonomy links.
        
        Args:
            taxon: Taxonomy ID
            
        Returns:
            json format response including taxonomy links
        """
        endpoint = f"/taxonomy/taxon/{urllib.parse.quote(taxon)}/links"
        return self._get(endpoint)

    def get_taxonomy(self, taxons: Union[str, List[str]]):
        """
        Get taxonomy information.
        
        Args:
            taxons: Taxonomy IDs
            
        Returns:
            json format response including taxonomy information
        """
        if isinstance(taxons, str):
            taxons = [taxons]
        endpoint = f"/taxonomy/taxon/{urllib.parse.quote(','.join(taxons))}"
        return self._get(endpoint)

    def get_taxonomy_dataset_report(self, taxons: Union[str, List[str]]):
        """
        Get taxonomy dataset report.
        
        Args:
            taxons: Taxonomy IDs
            
        Returns:
            json format response including dataset report
        """
        if isinstance(taxons, str):
            taxons = [taxons]
        endpoint = f"/taxonomy/taxon/{urllib.parse.quote(','.join(taxons))}/dataset_report"
        return self._get(endpoint)

    def get_taxonomy_filtered_subtree(self, taxons: Union[str, List[str]]):
        """
        Get filtered taxonomy subtree.
        
        Args:
            taxons: Taxonomy IDs
            
        Returns:
            json format response including filtered subtree
        """
        if isinstance(taxons, str):
            taxons = [taxons]
        endpoint = f"/taxonomy/taxon/{urllib.parse.quote(','.join(taxons))}/filtered_subtree"
        return self._get(endpoint)

    def get_taxonomy_name_report(self, taxons: Union[str, List[str]]):
        """
        Get taxonomy name report.
        
        Args:
            taxons: Taxonomy IDs
            
        Returns:
            json format response including name report
        """
        if isinstance(taxons, str):
            taxons = [taxons]
        endpoint = f"/taxonomy/taxon/{urllib.parse.quote(','.join(taxons))}/name_report"
        return self._get(endpoint)

    def get_taxonomy_taxon_suggest(self, taxon_query: str):
        """
        Get taxonomy suggestions.
        
        Args:
            taxon_query: Query string
            
        Returns:
            json format response including suggestions
        """
        endpoint = f"/taxonomy/taxon_suggest/{urllib.parse.quote(taxon_query)}"
        return self._get(endpoint)

    # BioSample endpoint
    def get_biosample_report(self, accessions: Union[str, List[str]]):
        """
        Get biosample report.
        
        Args:
            accessions: BioSample accessions
            
        Returns:
            json format response including biosample report
        """
        if isinstance(accessions, str):
            accessions = [accessions]
        endpoint = f"/biosample/accession/{urllib.parse.quote(','.join(accessions))}/biosample_report"
        return self._get(endpoint)

    # Organelle related endpoints
    def get_organelle_download(self, accessions: Union[str, List[str]]):
        """
        Download organelle data.
        
        Args:
            accessions: Organelle accessions
            
        Returns:
            json format response including organelle data
        """
        if isinstance(accessions, str):
            accessions = [accessions]
        endpoint = f"/organelle/accession/{urllib.parse.quote(','.join(accessions))}/download"
        return self._get(endpoint)

    def get_organelle_dataset_report(self, accessions: Union[str, List[str]]):
        """
        Get organelle dataset report.
        
        Args:
            accessions: Organelle accessions
            
        Returns:
            json format response including dataset report
        """
        if isinstance(accessions, str):
            accessions = [accessions]
        endpoint = f"/organelle/accessions/{urllib.parse.quote(','.join(accessions))}/dataset_report"
        return self._get(endpoint)

    def get_organelle_by_taxon_dataset_report(self, taxons: Union[str, List[str]]):
        """
        Get organelle dataset report by taxon.
        
        Args:
            taxons: Taxonomy IDs
            
        Returns:
            json format response including dataset report
        """
        if isinstance(taxons, str):
            taxons = [taxons]
        endpoint = f"/organelle/taxon/{urllib.parse.quote(','.join(taxons))}/dataset_report"
        return self._get(endpoint)
    


# ncbi_tools.py

from typing import Any, Dict, List, Union, Optional

from langchain_core.tools import tool


_ncbi_api: Optional[NCBIAPI] = None


def initialize_ncbi_api(config: Optional[Dict[str, Any]] = None) -> None:
    """
    Initialize the global NCBIAPI client.
    """
    global _ncbi_api
    if _ncbi_api is None:
        _ncbi_api = NCBIAPI()


def get_ncbi_api() -> NCBIAPI:
    """
    Get the global NCBIAPI client, creating it if needed.
    """
    global _ncbi_api
    if _ncbi_api is None:
        _ncbi_api = NCBIAPI()
    return _ncbi_api


@tool(parse_docstring=True)
async def get_gene_metadata_by_gene_name(name: str, species: str = "human") -> Any:
    """
    Get a gene summary by gene symbol.

    Args:
        name: Gene name or symbol to search for
        species: Species to search within

    Returns:
        JSON object containing detailed gene information including basic gene info, locations, external IDs, transcripts, and ontology annotations.
    """
    api = get_ncbi_api()
    try:
        return api.get_gene_metadata_by_gene_name(name, species)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_gene_by_ids(gene_ids: Union[int, List[int]]) -> Any:
    """
    Get gene information by gene IDs.

    Args:
        gene_ids: A single Gene ID or a list of Gene IDs

    Returns:
        JSON object including gene information.
    """
    api = get_ncbi_api()
    try:
        return api.get_gene_by_ids(gene_ids)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_gene_by_accession(accessions: Union[str, List[str]]) -> Any:
    """
    Get gene information by accession.

    Args:
        accessions: A single accession or a list of accessions

    Returns:
        JSON object including gene information.
    """
    api = get_ncbi_api()
    try:
        return api.get_gene_by_accession(accessions)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_gene_by_accession_dataset_report(
    accessions: Union[str, List[str]]
) -> Any:
    """
    Get dataset reports by accession IDs.

    Args:
        accessions: A single accession or a list of accessions

    Returns:
        JSON object including dataset reports.
    """
    api = get_ncbi_api()
    try:
        return api.get_gene_by_accession_dataset_report(accessions)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_gene_by_accession_product_report(
    accessions: Union[str, List[str]]
) -> Any:
    """
    Get gene product reports by accession IDs.

    Args:
        accessions: A single accession or a list of accessions

    Returns:
        JSON object including product reports.
    """
    api = get_ncbi_api()
    try:
        return api.get_gene_by_accession_product_report(accessions)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_gene_download_summary_by_id(gene_ids: Union[int, List[int]]) -> Any:
    """
    Get gene download summary by GeneID.

    Args:
        gene_ids: A single Gene ID or a list of Gene IDs

    Returns:
        JSON object including download summary.
    """
    api = get_ncbi_api()
    try:
        return api.get_gene_download_summary_by_id(gene_ids)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_gene_links_by_id(gene_ids: Union[int, List[int]]) -> Any:
    """
    Get gene links by gene ID.

    Args:
        gene_ids: A single Gene ID or a list of Gene IDs

    Returns:
        JSON object including related links.
    """
    api = get_ncbi_api()
    try:
        return api.get_gene_links_by_id(gene_ids)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_gene_dataset_report_by_locus_tag(
    locus_tags: Union[str, List[str]]
) -> Any:
    """
    Get gene dataset reports by locus tag.

    Args:
        locus_tags: A single locus tag or a list of locus tags

    Returns:
        JSON object including dataset reports.
    """
    api = get_ncbi_api()
    try:
        return api.get_gene_dataset_report_by_locus_tag(locus_tags)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_gene_product_report_by_locus_tag(
    locus_tags: Union[str, List[str]]
) -> Any:
    """
    Get gene product reports by locus tag.

    Args:
        locus_tags: A single locus tag or a list of locus tags

    Returns:
        JSON object including product reports.
    """
    api = get_ncbi_api()
    try:
        return api.get_gene_product_report_by_locus_tag(locus_tags)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_gene_by_symbol_dataset_report(symbols: str, taxon: str = "human") -> Any:
    """
    Get dataset reports by gene symbol and taxon.

    Args:
        symbols: Gene symbol
        taxon: Taxon name or identifier

    Returns:
        JSON object including dataset reports.
    """
    api = get_ncbi_api()
    try:
        return api.get_gene_by_symbol_dataset_report(symbols, taxon)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_gene_by_symbol_product_report(symbols: str, taxon: str = "human") -> Any:
    """
    Get product reports by gene symbol and taxon.

    Args:
        symbols: Gene symbol
        taxon: Taxon name or identifier

    Returns:
        JSON object including product reports.
    """
    api = get_ncbi_api()
    try:
        return api.get_gene_by_symbol_product_report(symbols, taxon)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_gene_by_taxon_dataset_report(taxon: str) -> Any:
    """
    Get gene dataset reports by taxon.

    Args:
        taxon: Taxon name or identifier

    Returns:
        JSON object including dataset reports.
    """
    api = get_ncbi_api()
    try:
        return api.get_gene_by_taxon_dataset_report(taxon)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_gene_by_taxon_product_report(taxon: str) -> Any:
    """
    Get gene product reports by taxon.

    Args:
        taxon: Taxon name or identifier

    Returns:
        JSON object including product reports.
    """
    api = get_ncbi_api()
    try:
        return api.get_gene_by_taxon_product_report(taxon)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_gene_dataset_report_by_id(gene_ids: Union[int, List[int]]) -> Any:
    """
    Get gene information by dataset report.

    Args:
        gene_ids: A single Gene ID or a list of Gene IDs

    Returns:
        JSON object including dataset reports.
    """
    api = get_ncbi_api()
    try:
        return api.get_gene_dataset_report_by_id(gene_ids)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_genome_annotation_report(accession: str) -> Any:
    """
    Get genome annotation reports by genome accession.

    Args:
        accession: Genome accession

    Returns:
        JSON object including annotation reports.
    """
    api = get_ncbi_api()
    try:
        return api.get_genome_annotation_report(accession)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_genome_annotation_summary(accession: str) -> Any:
    """
    Get genome annotation summary information.

    Args:
        accession: Genome accession

    Returns:
        JSON object including annotation summary.
    """
    api = get_ncbi_api()
    try:
        return api.get_genome_annotation_summary(accession)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_genome_revision_history(accession: str) -> Any:
    """
    Get revision history for an assembly by accession.

    Args:
        accession: Genome accession

    Returns:
        JSON object including revision history.
    """
    api = get_ncbi_api()
    try:
        return api.get_genome_revision_history(accession)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_genome_sequence_reports(accession: str) -> Any:
    """
    Get genome sequence reports by accession.

    Args:
        accession: Genome accession

    Returns:
        JSON object including sequence reports.
    """
    api = get_ncbi_api()
    try:
        return api.get_genome_sequence_reports(accession)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def check_genome_accessions(accessions: Union[str, List[str]]) -> Any:
    """
    Check the validity of genome accessions.

    Args:
        accessions: Genome accessions

    Returns:
        JSON object including validity information.
    """
    api = get_ncbi_api()
    try:
        return api.check_genome_accessions(accessions)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_genome_dataset_report_by_accession(
    accessions: Union[str, List[str]]
) -> Any:
    """
    Get genome dataset reports by accessions.

    Args:
        accessions: Genome accessions

    Returns:
        JSON object including dataset reports.
    """
    api = get_ncbi_api()
    try:
        return api.get_genome_dataset_report_by_accession(accessions)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_genome_download(accessions: Union[str, List[str]]) -> Any:
    """
    Get a genome dataset by accession.

    Args:
        accessions: Genome accessions

    Returns:
        Binary or structured response representing the genome dataset.
    """
    api = get_ncbi_api()
    try:
        return api.get_genome_download(accessions)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_genome_download_summary(accessions: Union[str, List[str]]) -> Any:
    """
    Preview genome dataset download.

    Args:
        accessions: Genome accessions

    Returns:
        JSON object including download summary.
    """
    api = get_ncbi_api()
    try:
        return api.get_genome_download_summary(accessions)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_genome_links(accessions: Union[str, List[str]]) -> Any:
    """
    Get assembly links by accessions.

    Args:
        accessions: Genome accessions

    Returns:
        JSON object including related links.
    """
    api = get_ncbi_api()
    try:
        return api.get_genome_links(accessions)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_genome_dataset_report_by_assembly_name(
    assembly_names: Union[str, List[str]]
) -> Any:
    """
    Get genome dataset reports by assembly name.

    Args:
        assembly_names: Assembly names

    Returns:
        JSON object including dataset reports.
    """
    api = get_ncbi_api()
    try:
        return api.get_genome_dataset_report_by_assembly_name(assembly_names)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_genome_dataset_report_by_bioproject(
    bioprojects: Union[str, List[str]]
) -> Any:
    """
    Get genome dataset reports by bioproject.

    Args:
        bioprojects: Bioproject identifiers

    Returns:
        JSON object including dataset reports.
    """
    api = get_ncbi_api()
    try:
        return api.get_genome_dataset_report_by_bioproject(bioprojects)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_genome_dataset_report_by_biosample(
    biosample_ids: Union[str, List[str]]
) -> Any:
    """
    Get genome dataset reports by biosample ID.

    Args:
        biosample_ids: Biosample IDs

    Returns:
        JSON object including dataset reports.
    """
    api = get_ncbi_api()
    try:
        return api.get_genome_dataset_report_by_biosample(biosample_ids)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_sequence_assemblies(accession: str) -> Any:
    """
    Get assembly accessions for a sequence accession.

    Args:
        accession: Sequence accession

    Returns:
        JSON object including assembly accessions.
    """
    api = get_ncbi_api()
    try:
        return api.get_sequence_assemblies(accession)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_genome_dataset_report_by_taxon(taxons: str) -> Any:
    """
    Get genome dataset reports by taxons.

    Args:
        taxons: Taxon name or identifier

    Returns:
        JSON object including dataset reports.
    """
    api = get_ncbi_api()
    try:
        return api.get_genome_dataset_report_by_taxon(taxons)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_genome_dataset_report_by_wgs(
    wgs_accessions: Union[str, List[str]]
) -> Any:
    """
    Get genome dataset reports by WGS accession.

    Args:
        wgs_accessions: WGS accessions

    Returns:
        JSON object including dataset reports.
    """
    api = get_ncbi_api()
    try:
        return api.get_genome_dataset_report_by_wgs(wgs_accessions)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_virus_annotation_report(
    accessions: Union[str, List[str]]
) -> Any:
    """
    Get virus annotation report by accessions.

    Args:
        accessions: Virus accessions

    Returns:
        JSON object including annotation reports.
    """
    api = get_ncbi_api()
    try:
        return api.get_virus_annotation_report(accessions)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def check_virus_accessions(accessions: Union[str, List[str]]) -> Any:
    """
    Check virus accession validity.

    Args:
        accessions: Virus accessions

    Returns:
        JSON object including validity information.
    """
    api = get_ncbi_api()
    try:
        return api.check_virus_accessions(accessions)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_virus_dataset_report(accessions: Union[str, List[str]]) -> Any:
    """
    Get virus dataset report by accessions.

    Args:
        accessions: Virus accessions

    Returns:
        JSON object including dataset reports.
    """
    api = get_ncbi_api()
    try:
        return api.get_virus_dataset_report(accessions)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_virus_genome_download(accessions: Union[str, List[str]]) -> Any:
    """
    Download virus genome by accessions.

    Args:
        accessions: Virus accessions

    Returns:
        Binary or structured response representing the virus genome dataset.
    """
    api = get_ncbi_api()
    try:
        return api.get_virus_genome_download(accessions)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_virus_by_taxon_annotation_report(taxon: str) -> Any:
    """
    Get virus annotation report by taxon.

    Args:
        taxon: Virus taxon

    Returns:
        JSON object including annotation reports.
    """
    api = get_ncbi_api()
    try:
        return api.get_virus_by_taxon_annotation_report(taxon)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_virus_by_taxon_genome(taxon: str) -> Any:
    """
    Get virus genome by taxon.

    Args:
        taxon: Virus taxon

    Returns:
        JSON object or dataset including genome information.
    """
    api = get_ncbi_api()
    try:
        return api.get_virus_by_taxon_genome(taxon)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_virus_by_taxon_genome_table(taxon: str) -> Any:
    """
    Get virus genome table by taxon.

    Args:
        taxon: Virus taxon

    Returns:
        JSON object including genome table.
    """
    api = get_ncbi_api()
    try:
        return api.get_virus_by_taxon_genome_table(taxon)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_version() -> Any:
    """
    Get current version of all services.

    Returns:
        JSON object including version information.
    """
    api = get_ncbi_api()
    try:
        return api.get_version()
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_taxonomy_related_ids(tax_id: int) -> Any:
    """
    Get related taxonomy IDs.

    Args:
        tax_id: Taxonomy ID

    Returns:
        JSON object including related taxonomy IDs.
    """
    api = get_ncbi_api()
    try:
        return api.get_taxonomy_related_ids(tax_id)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_taxonomy_download(tax_ids: Union[int, List[int]]) -> Any:
    """
    Download taxonomy data.

    Args:
        tax_ids: Taxonomy IDs

    Returns:
        Downloadable taxonomy dataset or metadata.
    """
    api = get_ncbi_api()
    try:
        return api.get_taxonomy_download(tax_ids)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_taxonomy_links(taxon: str) -> Any:
    """
    Get taxonomy links.

    Args:
        taxon: Taxonomy ID

    Returns:
        JSON object including links to related resources.
    """
    api = get_ncbi_api()
    try:
        return api.get_taxonomy_links(taxon)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_taxonomy(taxons: Union[str, List[str]]) -> Any:
    """
    Get taxonomy information.

    Args:
        taxons: Taxonomy IDs

    Returns:
        JSON object including taxonomy information.
    """
    api = get_ncbi_api()
    try:
        return api.get_taxonomy(taxons)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_taxonomy_dataset_report(taxons: Union[str, List[str]]) -> Any:
    """
    Get taxonomy dataset report.

    Args:
        taxons: Taxonomy IDs

    Returns:
        JSON object including dataset reports.
    """
    api = get_ncbi_api()
    try:
        return api.get_taxonomy_dataset_report(taxons)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_taxonomy_filtered_subtree(taxons: Union[str, List[str]]) -> Any:
    """
    Get filtered taxonomy subtree.

    Args:
        taxons: Taxonomy IDs

    Returns:
        JSON object including subtree information.
    """
    api = get_ncbi_api()
    try:
        return api.get_taxonomy_filtered_subtree(taxons)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_taxonomy_name_report(taxons: Union[str, List[str]]) -> Any:
    """
    Get taxonomy name report.

    Args:
        taxons: Taxonomy IDs

    Returns:
        JSON object including taxonomy names.
    """
    api = get_ncbi_api()
    try:
        return api.get_taxonomy_name_report(taxons)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_taxonomy_taxon_suggest(taxon_query: str) -> Any:
    """
    Get taxonomy suggestions.

    Args:
        taxon_query: Taxonomy query string

    Returns:
        JSON object including suggestion results.
    """
    api = get_ncbi_api()
    try:
        return api.get_taxonomy_taxon_suggest(taxon_query)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_biosample_report(accessions: Union[str, List[str]]) -> Any:
    """
    Get biosample report.

    Args:
        accessions: BioSample accessions

    Returns:
        JSON object including biosample report.
    """
    api = get_ncbi_api()
    try:
        return api.get_biosample_report(accessions)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_organelle_download(accessions: Union[str, List[str]]) -> Any:
    """
    Download organelle data.

    Args:
        accessions: Organelle accessions

    Returns:
        Downloadable organelle dataset or metadata.
    """
    api = get_ncbi_api()
    try:
        return api.get_organelle_download(accessions)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_organelle_dataset_report(accessions: Union[str, List[str]]) -> Any:
    """
    Get organelle dataset report.

    Args:
        accessions: Organelle accessions

    Returns:
        JSON object including dataset reports.
    """
    api = get_ncbi_api()
    try:
        return api.get_organelle_dataset_report(accessions)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_organelle_by_taxon_dataset_report(
    taxons: Union[str, List[str]]
) -> Any:
    """
    Get organelle dataset report by taxon.

    Args:
        taxons: Taxonomy IDs

    Returns:
        JSON object including dataset reports.
    """
    api = get_ncbi_api()
    try:
        return api.get_organelle_by_taxon_dataset_report(taxons)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_gene_product_report_by_id(
    gene_ids: Union[int, List[int]]
) -> Any:
    """
    Get gene product report by gene ID.

    Args:
        gene_ids: Gene IDs

    Returns:
        JSON object including product reports.
    """
    api = get_ncbi_api()
    try:
        return api.get_gene_product_report_by_id(gene_ids)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_gene_orthologs(gene_id: int) -> Any:
    """
    Get gene orthologs by gene ID.

    Args:
        gene_id: Gene ID

    Returns:
        JSON object including ortholog information.
    """
    api = get_ncbi_api()
    try:
        return api.get_gene_orthologs(gene_id)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_gene_by_taxon(taxon: str) -> Any:
    """
    Get gene information by taxon.

    Args:
        taxon: Taxon name or identifier

    Returns:
        JSON object including gene information.
    """
    api = get_ncbi_api()
    try:
        return api.get_gene_by_taxon(taxon)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_gene_counts_by_taxon(taxon: str) -> Any:
    """
    Get gene counts by taxon.

    Args:
        taxon: Taxon name or identifier

    Returns:
        JSON object including gene counts.
    """
    api = get_ncbi_api()
    try:
        return api.get_gene_counts_by_taxon(taxon)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_chromosome_summary(taxon: str, annotation_name: str) -> Any:
    """
    Get chromosome summary by taxon and annotation name.

    Args:
        taxon: Taxon name or identifier
        annotation_name: Annotation name

    Returns:
        JSON object including chromosome summaries.
    """
    api = get_ncbi_api()
    try:
        return api.get_chromosome_summary(taxon, annotation_name)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_genome_by_accession(accession: str) -> Any:
    """
    Get genome information by accession.

    Args:
        accession: Genome accession

    Returns:
        JSON object including genome information.
    """
    api = get_ncbi_api()
    try:
        return api.get_genome_by_accession(accession)
    except Exception as e:
        return f"Error: {e}"


@tool(parse_docstring=True)
async def get_prokaryote_gene_dataset_by_refseq_protein_accession(
    refseq_protein_accession: str,
) -> Any:
    """
    Get a prokaryote gene dataset by RefSeq protein accession.

    Args:
        refseq_protein_accession: RefSeq protein accession

    Returns:
        JSON object including prokaryote gene dataset.
    """
    api = get_ncbi_api()
    try:
        return api.get_prokaryote_gene_dataset_by_refseq_protein_accession(
            refseq_protein_accession
        )
    except Exception as e:
        return f"Error: {e}"


ncbi_tools: Dict[str, Any] = {
    "get_gene_metadata_by_gene_name": get_gene_metadata_by_gene_name,
    "get_gene_by_ids": get_gene_by_ids,
    "get_gene_by_accession": get_gene_by_accession,
    "get_gene_by_accession_dataset_report": get_gene_by_accession_dataset_report,
    "get_gene_by_accession_product_report": get_gene_by_accession_product_report,
    "get_gene_download_summary_by_id": get_gene_download_summary_by_id,
    "get_gene_links_by_id": get_gene_links_by_id,
    "get_gene_dataset_report_by_locus_tag": get_gene_dataset_report_by_locus_tag,
    "get_gene_product_report_by_locus_tag": get_gene_product_report_by_locus_tag,
    "get_gene_by_symbol_dataset_report": get_gene_by_symbol_dataset_report,
    "get_gene_by_symbol_product_report": get_gene_by_symbol_product_report,
    "get_gene_by_taxon_dataset_report": get_gene_by_taxon_dataset_report,
    "get_gene_by_taxon_product_report": get_gene_by_taxon_product_report,
    "get_gene_dataset_report_by_id": get_gene_dataset_report_by_id,
    "get_genome_annotation_report": get_genome_annotation_report,
    "get_genome_annotation_summary": get_genome_annotation_summary,
    "get_genome_revision_history": get_genome_revision_history,
    "get_genome_sequence_reports": get_genome_sequence_reports,
    "check_genome_accessions": check_genome_accessions,
    "get_genome_dataset_report_by_accession": get_genome_dataset_report_by_accession,
    "get_genome_download": get_genome_download,
    "get_genome_download_summary": get_genome_download_summary,
    "get_genome_links": get_genome_links,
    "get_genome_dataset_report_by_assembly_name": get_genome_dataset_report_by_assembly_name,
    "get_genome_dataset_report_by_bioproject": get_genome_dataset_report_by_bioproject,
    "get_genome_dataset_report_by_biosample": get_genome_dataset_report_by_biosample,
    "get_sequence_assemblies": get_sequence_assemblies,
    "get_genome_dataset_report_by_taxon": get_genome_dataset_report_by_taxon,
    "get_genome_dataset_report_by_wgs": get_genome_dataset_report_by_wgs,
    "get_virus_annotation_report": get_virus_annotation_report,
    "check_virus_accessions": check_virus_accessions,
    "get_virus_dataset_report": get_virus_dataset_report,
    "get_virus_genome_download": get_virus_genome_download,
    "get_virus_by_taxon_annotation_report": get_virus_by_taxon_annotation_report,
    "get_virus_by_taxon_genome": get_virus_by_taxon_genome,
    "get_virus_by_taxon_genome_table": get_virus_by_taxon_genome_table,
    "get_version": get_version,
    "get_taxonomy_related_ids": get_taxonomy_related_ids,
    "get_taxonomy_download": get_taxonomy_download,
    "get_taxonomy_links": get_taxonomy_links,
    "get_taxonomy": get_taxonomy,
    "get_taxonomy_dataset_report": get_taxonomy_dataset_report,
    "get_taxonomy_filtered_subtree": get_taxonomy_filtered_subtree,
    "get_taxonomy_name_report": get_taxonomy_name_report,
    "get_taxonomy_taxon_suggest": get_taxonomy_taxon_suggest,
    "get_biosample_report": get_biosample_report,
    "get_organelle_download": get_organelle_download,
    "get_organelle_dataset_report": get_organelle_dataset_report,
    "get_organelle_by_taxon_dataset_report": get_organelle_by_taxon_dataset_report,
    "get_gene_product_report_by_id": get_gene_product_report_by_id,
    "get_gene_orthologs": get_gene_orthologs,
    "get_gene_by_taxon": get_gene_by_taxon,
    "get_gene_counts_by_taxon": get_gene_counts_by_taxon,
    "get_chromosome_summary": get_chromosome_summary,
    "get_genome_by_accession": get_genome_by_accession,
    "get_prokaryote_gene_dataset_by_refseq_protein_accession": get_prokaryote_gene_dataset_by_refseq_protein_accession,
}
