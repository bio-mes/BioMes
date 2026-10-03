from Bio.Blast import NCBIWWW, NCBIXML
from Bio import SeqIO, Entrez
from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq
from typing import List, Optional, Union, Dict
import time
import os
import requests
import re
import pandas as pd
from io import StringIO


NOW_DIR = os.path.dirname(os.path.abspath(__file__))
CYTO_FILE = os.path.join(NOW_DIR, 'db/cytoBand.txt')
CACHE_FILE = os.path.join(NOW_DIR, 'db/refseq_cache.fa')


class DBSearch:
    """Unified class combining all database search APIs from db_search directory"""
    
    def __init__(self, cyto_file=CYTO_FILE, email="liyu0377@lglab.ac.cn"):
        """
        Initialize DBSEARCH with common configurations.
        
        Args:
            cyto_file (str): Path to UCSC-style cytoBand.txt file (for Ensembl queries)
            email (str): Email for NCBI/Entrez queries
        """
        # Common configurations
        self.email = email
        self.CACHE_FILE = CACHE_FILE
        self.cyto_file = cyto_file
        self.promoter_dir = "./genes_promoter[-1000,+100]"
        
        # API endpoints
        self.entrez_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi'
        self.gsea_base_url = "https://www.gsea-msigdb.org/gsea/msigdb/human/download_geneset.jsp"
        self.phipster_base_url = "http://ec2-18-215-31-69.compute-1.amazonaws.com:8000/home/"
        self.uniprot_api_url = "https://rest.uniprot.org/uniprotkb/search"
        
        # Initialize session objects
        self.session = requests.Session()
        self.headers = {"accept": "application/json"}

    # --------------------------
    # CLINVAR API Methods
    # --------------------------
    def load_cache(self) -> dict:
        """Load cached RefSeq sequences from FASTA file into memory."""
        if not os.path.exists(self.CACHE_FILE):
            return {}
        cache = {}
        for record in SeqIO.parse(self.CACHE_FILE, "fasta"):
            cache[str(record.seq)] = record.id
        return cache

    def append_to_cache(self, refseq_id: str, sequence: str) -> None:
        """Append a new RefSeq ID and sequence to the cache file."""
        record = SeqRecord(Seq(sequence), id=refseq_id, description="")
        with open(self.CACHE_FILE, "a", newline='\n') as f:
            SeqIO.write(record, f, "fasta")

    def clinvar_get_best_refseqid_by_sequence(self, seq: str, retries: int = 3, wait: int = 5) -> Optional[str]:
        """Find best matching RefSeq ID for a protein sequence using BLASTP."""
        cache = self.load_cache()
        if seq in cache:
            return cache[seq]

        for i in range(retries):
            try:
                result_handle = NCBIWWW.qblast(
                    program="blastp",
                    database="nr",
                    sequence=seq,
                    hitlist_size=10,
                    expect=1e-5,
                    format_type="XML",
                    service="plain"
                )
                break
            except Exception as e:
                time.sleep(wait)
        
        blast_record = NCBIXML.read(result_handle)
        for alignment in blast_record.alignments:
            if alignment.accession.startswith('NP'):
                for hsp in alignment.hsps:
                    if hsp.identities == hsp.align_length:
                        best_refseqid = alignment.accession
                        self.append_to_cache(best_refseqid, seq)
                        return best_refseqid
        return None

    def clinvar_query_variant_significance(self, refseqid: Optional[str] = None, 
                                         variant: Optional[str] = None,
                                         hgvs: Optional[str] = None) -> Union[dict, str]:
        """Query ClinVar for variant classification/significance."""
        Entrez.email = self.email
        if hgvs is None:
            if not (refseqid and variant):
                return "Error: Either hgvs or (refseqid and variant) must be provided"
            hgvs = f"{refseqid}:p.{variant}"
        if "=" in hgvs:
            return {'description': 'Likely benign'}
        
        try:
            handle = Entrez.esearch(db="clinvar", term=hgvs)
            record = Entrez.read(handle)
            handle.close()

            if not record["IdList"]:
                return {'description': 'Not found'}

            clinvar_id = record["IdList"][0]
            params = {'db': 'clinvar', 'id': clinvar_id, 'retmode': 'json'}
            res = requests.get(self.entrez_url, params=params)
            return res.json()['result'][clinvar_id]['germline_classification']
        except Exception as e:
            return f"Error: {str(e)}"

    # --------------------------
    # ENSEMBL API Methods
    # --------------------------
    def get_genes_in_region(self, chrom: str, start: int, end: int) -> List[str]:
        """Query Ensembl REST API to get genes within a genomic region."""
        region = f"{chrom}:{start}-{end}"
        url = f"https://rest.ensembl.org/overlap/region/human/{region}?feature=gene"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        data = response.json()
        return [gene["external_name"] for gene in data if "external_name" in gene]

    def ensembl_get_genes_by_band(self, query_band: str) -> List[str]:
        """Extract genes in a cytogenetic band region (e.g., 'chr10q21')."""
        match = re.match(r'chr(\d+|X|Y)([pq])(\d+)', query_band)
        if not match:
            raise ValueError("Invalid input format, expected like 'chr10q21'")

        chrom = f'chr{match.group(1)}'
        arm = match.group(2)
        band_prefix = match.group(3)
        target_prefix = f"{arm}{band_prefix}"

        regions = []
        with open(self.cyto_file) as f:
            for line in f:
                fields = line.strip().split('\t')
                chr_name, start, end, band_name, stain = fields
                if chr_name != chrom:
                    continue
                if band_name.startswith(target_prefix):
                    regions.append((int(start), int(end)))

        if not regions:
            raise ValueError(f"No bands found for {query_band} in {self.cyto_file}.")

        MAX_SPAN = 4000000
        genes = []
        for start, end in regions:
            start, end = min(start, end), max(start, end)
            if end - start < MAX_SPAN:
                genes += self.get_genes_in_region(chrom, start, end)
            else:
                for chunk_start in range(start, end, MAX_SPAN):
                    chunk_end = min(chunk_start + MAX_SPAN, end)
                    genes += self.get_genes_in_region(chrom, chunk_start, chunk_end)
        return genes

    # --------------------------
    # GSEA API Methods
    # --------------------------
    def gsea_get_genelist_from_genesetname(self, genesetname: str) -> List[str]:
        """Retrieve gene list from a GSEA gene set."""
        params = {"geneSetName": genesetname, "fileType": "json"}
        d = self._get_gsea(params=params)
        return d[genesetname]['geneSymbols'] if d else []

    def _get_gsea(self, params=None):
        """Internal helper for GSEA GET requests."""
        try:
            r = requests.get(self.gsea_base_url, params=params, headers=self.headers)
            r.raise_for_status()
            return r.json()
        except Exception as err:
            print(f"GSEA API error: {err}")
            return None

    # --------------------------
    # GTRD API Methods
    # --------------------------
    def gtrd_gene_to_entry(self, gene_name: str, organism: str = "9606") -> str:
        """Convert gene symbol to UniProt protein entry ID."""
        params = {
            "query": f"gene:{gene_name} AND organism_id:{organism} AND reviewed:true",
            "fields": "accession",
            "format": "json",
            "size": 10
        }

        try:
            response = requests.get(self.uniprot_api_url, params=params)
            response.raise_for_status()
            results = response.json().get("results", [])
            if not results:
                raise ValueError(f"No UniProt entry found for gene: {gene_name}")
            return results[0]["primaryAccession"]
        except Exception as e:
            raise Exception(f"Failed to query UniProt: {str(e)}")

    def gtrd_entry_to_target_genes(self, entry: str) -> List[str]:
        """Query promoter files for target genes of a UniProt entry."""
        file_path = os.path.join(self.promoter_dir, f"{entry}.txt")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Promoter file not found: {file_path}")

        target_genes = []
        with open(file_path, 'r') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    target_genes.append(parts[1])
        return target_genes

    # --------------------------
    # MIRDB API Methods
    # --------------------------
    def mirdb_get_geneset_by_mirname(self, mirname: str, candidates: List[str]) -> dict:
        """Get predicted target genes for a miRNA."""
        url = "https://mirdb.org/cgi-bin/search.cgi"
        data = {
            "species": "Human",
            "searchBox": mirname,
            "submitButton": "Go",
            "searchType": "miRNA"
        }
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Origin": "https://mirdb.org",
            "Referer": "https://mirdb.org/mirdb/index.html",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        try:
            response = requests.post(url, data=data, headers=headers, timeout=10)
            response.raise_for_status()
            tables = pd.read_html(StringIO(response.text))
            if not tables:
                return {"error": "EmptyResult", "message": f"No result for miRNA '{mirname}'", "fallback": True}

            df = tables[0]
            header = df.iloc[0].tolist()
            df.columns = header
            df = df[1:]
            gene_list = df["Gene Symbol"].dropna().tolist()
            gene_set = set(gene_list)
            matched = [g for g in candidates if g in gene_set]
            unmatched = [g for g in candidates if g not in gene_set]
            return {"predicted_targets": matched, "not_predicted_targets": unmatched}
        except Exception as e:
            return {"error": "ToolExecutionError", "message": str(e), "fallback": True}

    # --------------------------
    # MOUSEMINE API Methods
    # --------------------------
    def mousemine_get_geneset_from_mpid(self, mpid: str) -> List[str]:
        """Get mouse gene symbols associated with a MGI phenotype ID."""
        url = f"https://www.mousemine.org/mousemine/keywordSearchResults.do?searchTerm={mpid}&searchSubmit=search"
        tables = pd.read_html(url)
        df = tables[0]
        gene_names = []
        for i, row in df.iterrows():
            if row['Type'] == 'Protein Coding Gene':
                parts = row['Details'].split('|')
                if len(parts) >= 2:
                    gene = parts[1].strip().split()[0]
                    gene_names.append(gene)
        return gene_names

    # --------------------------
    # PHIPSTER API Methods
    # --------------------------
    def phipster_vpname2vpid(self, vpname: str) -> Optional[str]:
        """Convert viral protein name to VPID."""
        params = {"format": "json"}
        d = self._get_phipster("vpid2name", params=params)
        if d:
            for k, v in d.items():
                if vpname in v:
                    return k
        return None

    def phipster_get_hpid_list_by_vpid(self, vpid: str) -> List[str]:
        """Get human protein IDs interacting with a viral protein."""
        params = {"format": "json"}
        endpoint = f"ppi/vp-lrfilter/{vpid}/100"
        vpid_hpid_ppi = self._get_phipster(endpoint, params=params)
        return [entry["humanprotein_id"] for entry in vpid_hpid_ppi] if vpid_hpid_ppi else []

    def phipster_hpid_list_to_hpname_list(self, hpid_list: List[str]) -> List[str]:
        """Convert human protein IDs to names."""
        params = {"format": "json"}
        d_hpid2name = self._get_phipster("hpid2name", params=params)
        return [d_hpid2name.get(str(hpid), f"Unknown_{hpid}") for hpid in hpid_list] if d_hpid2name else []

    def _get_phipster(self, endpoint: str, params=None):
        """Internal helper for PHIPSTER GET requests."""
        url = self.phipster_base_url + endpoint
        try:
            r = requests.get(url, params=params, headers=self.headers)
            r.raise_for_status()
            return r.json()
        except Exception as err:
            print(f"PHIPSTER API error: {err}")
            return None



from typing import Dict, Any, Optional, List
from langchain_core.tools import tool


# -------------------------
#   Global singleton client
# -------------------------

_dbsearch: Optional[DBSearch] = None


def initialize_dbsearch_api(config: Optional[Dict[str, Any]] = None) -> None:
    """
    Initialize the global DBSearch client. This should be called once in initialize_tools(config).
    """
    global _dbsearch
    if _dbsearch is None:
        _dbsearch = DBSearch()


def get_dbsearch() -> DBSearch:
    global _dbsearch
    if _dbsearch is None:
        _dbsearch = DBSearch()
    return _dbsearch


# -------------------------
#        Tools
# -------------------------

@tool(parse_docstring=True)
async def clinvar_get_best_refseqid_by_sequence(seq: str, retries: int = 3, wait: int = 5) -> Any:
    """
    Find best matching RefSeq ID for a protein sequence using BLASTP.

    Args:
        seq: Protein sequence
        retries: Number of retry attempts (default: 3)
        wait: Seconds to wait between retries (default: 5)

    Returns:
        Matching RefSeq ID (e.g. "NP_123456") with 100% identity, or None if not found.
    """
    api = get_dbsearch()
    try:
        return api.clinvar_get_best_refseqid_by_sequence(seq, retries, wait)
    except Exception:
        return None


@tool(parse_docstring=True)
async def clinvar_query_variant_significance(refseqid: str = None, variant: str = None, hgvs: str = None) -> Any:
    """
    Query ClinVar for variant classification/significance.

    Args:
        refseqid: RefSeq protein ID (e.g. "NP_123456")
        variant: Protein variant in HGVS protein form (e.g. "P123L")
        hgvs: Full HGVS notation (e.g. "NP_123456.1:p.P123L")

    Returns:
        ClinVar classification result as a dict, or error string when not found.
    """
    api = get_dbsearch()
    try:
        return api.clinvar_query_variant_significance(refseqid, variant, hgvs)
    except Exception as e:
        return {"error": str(e)}


@tool(parse_docstring=True)
async def clinvar_query_sequence_variants(sequence: str, variants: List[str]) -> Any:
    """
    Query ClinVar for multiple variants on a protein sequence.

    Args:
        sequence: Reference protein sequence
        variants: List of variant strings (e.g. ["P123L", "R456K"])

    Returns:
        Mapping of variant → ClinVar significance. Empty dict if no RefSeq ID found.
    """
    api = get_dbsearch()
    try:
        return api.clinvar_query_sequence_variants(sequence, variants)
    except Exception as e:
        return {"error": str(e)}


@tool(parse_docstring=True)
async def clinvar_find_single_mutation(mutant_seq: str) -> Any:
    """
    Find single amino acid mutation between mutant and reference sequences.

    Args:
        mutant_seq: Mutant protein sequence

    Returns:
        Dictionary with mutation details:
            ref_id, hgvs, variant, pos, wildtype, mutant
        or None if no single mutation found.
    """
    api = get_dbsearch()
    try:
        return api.clinvar_find_single_mutation(mutant_seq)
    except Exception as e:
        return {"error": str(e)}


@tool(parse_docstring=True)
async def get_genes_in_region(chrom: str, start: int, end: int) -> Any:
    """
    Query Ensembl REST API to get genes within a genomic region.

    Args:
        chrom: Chromosome name (e.g. "chr10")
        start: Start coordinate
        end: End coordinate

    Returns:
        List of gene names within the region.
    """
    api = get_dbsearch()
    return api.get_genes_in_region(chrom, start, end)


@tool(parse_docstring=True)
async def ensembl_get_genes_by_band(query_band: str) -> Any:
    """
    Extract genes in a cytogenetic band (e.g. "chr10q21").

    Args:
        query_band: Cytoband query (e.g. "chr10q21")

    Returns:
        List of gene names in the specified band.
    """
    api = get_dbsearch()
    return api.ensembl_get_genes_by_band(query_band)


@tool(parse_docstring=True)
async def gsea_get_genelist_from_genesetname(genesetname: str) -> Any:
    """
    Retrieve list of genes from a specific GSEA gene set.

    Args:
        genesetname: GSEA gene set name (e.g. "CAMP_UP.V1_DN")

    Returns:
        List of gene symbols in the given gene set.
    """
    api = get_dbsearch()
    return api.gsea_get_genelist_from_genesetname(genesetname)


@tool(parse_docstring=True)
async def gtrd_gene_to_entry(gene_name: str, organism: str = None) -> Any:
    """
    Convert a gene symbol to UniProt entry ID(s) using GTRD.

    Args:
        gene_name: Gene symbol (e.g. "TP53")
        organism: Optional taxonomy ID

    Returns:
        UniProt entry ID string, or None if not found.
    """
    api = get_dbsearch()
    try:
        return api.gtrd_gene_to_entry(gene_name, organism)
    except Exception as e:
        return {"error": str(e)}


@tool(parse_docstring=True)
async def gtrd_entry_to_target_genes(entry: str, promoter_dir: str = None) -> Any:
    """
    Retrieve target genes for a UniProt entry using GTRD promoter data.

    Args:
        entry: UniProt accession ID (e.g. "P04637")
        promoter_dir: Optional path to promoter files

    Returns:
        List of gene symbols targeted by the entry.
    """
    api = get_dbsearch()
    try:
        return api.gtrd_entry_to_target_genes(entry, promoter_dir)
    except Exception as e:
        return {"error": str(e)}


@tool(parse_docstring=True)
async def mirdb_get_geneset_by_mirname(mirname: str, candidates: List[str]) -> Any:
    """
    Predict target gene symbols of a human miRNA from miRDB.

    Args:
        mirname: miRNA name (e.g. "hsa-miR-3140-5p")
        candidates: Candidate gene symbol list

    Returns:
        Dict with predicted and not predicted targets.
    """
    api = get_dbsearch()
    return api.mirdb_get_geneset_by_mirname(mirname, candidates)


@tool(parse_docstring=True)
async def mousemine_get_geneset_from_mpid(mpid: str) -> Any:
    """
    Retrieve mouse gene symbols associated with a given MPID.

    Args:
        mpid: Example "MP:0005386"

    Returns:
        List of protein-coding mouse genes linked to the MPID.
    """
    api = get_dbsearch()
    return api.mousemine_get_geneset_from_mpid(mpid)


@tool(parse_docstring=True)
async def phipster_vpname2vpid(vpname: str) -> Any:
    """
    Convert viral protein name to Phipster VPID.

    Args:
        vpname: Viral protein name without species prefix

    Returns:
        VPID string, e.g. "23488", or None if not found.
    """
    api = get_dbsearch()
    return api.phipster_vpname2vpid(vpname)


@tool(parse_docstring=True)
async def phipster_get_hpid_list_by_vpid(vpid: str) -> Any:
    """
    Retrieve human protein interaction IDs for a viral protein (VPID).

    Args:
        vpid: Viral protein ID

    Returns:
        List of human protein IDs interacting with the viral protein.
    """
    api = get_dbsearch()
    return api.phipster_get_hpid_list_by_vpid(vpid)


@tool(parse_docstring=True)
async def phipster_hpid_list_to_hpname_list(hpid_list: List[int]) -> Any:
    """
    Convert PHIPSTER HPIDs to human protein names.

    Args:
        hpid_list: List of HPIDs

    Returns:
        List of protein names. Unknown IDs get name "Unknown_{id}".
    """
    api = get_dbsearch()
    return api.phipster_hpid_list_to_hpname_list(hpid_list)


# -------------------------
# Export dict for agent use
# -------------------------

dbsearch_tools: Dict[str, Any] = {
    "clinvar_get_best_refseqid_by_sequence": clinvar_get_best_refseqid_by_sequence,
    "clinvar_query_variant_significance": clinvar_query_variant_significance,
    "clinvar_query_sequence_variants": clinvar_query_sequence_variants,
    "clinvar_find_single_mutation": clinvar_find_single_mutation,
    "get_genes_in_region": get_genes_in_region,
    "ensembl_get_genes_by_band": ensembl_get_genes_by_band,
    "gsea_get_genelist_from_genesetname": gsea_get_genelist_from_genesetname,
    "gtrd_gene_to_entry": gtrd_gene_to_entry,
    "gtrd_entry_to_target_genes": gtrd_entry_to_target_genes,
    "mirdb_get_geneset_by_mirname": mirdb_get_geneset_by_mirname,
    "mousemine_get_geneset_from_mpid": mousemine_get_geneset_from_mpid,
    "phipster_vpname2vpid": phipster_vpname2vpid,
    "phipster_get_hpid_list_by_vpid": phipster_get_hpid_list_by_vpid,
    "phipster_hpid_list_to_hpname_list": phipster_hpid_list_to_hpname_list,
}
