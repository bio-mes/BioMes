# ucsc_tools.py

import requests
from typing import Optional, Dict, Any
from langchain_core.tools import tool


class UCSCAPI:
    BASE_URL = "https://api.genome.ucsc.edu/"

    def __init__(self) -> None:
        self.session = requests.Session()

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Internal helper for GET requests."""
        url = self.BASE_URL + endpoint
        r = self.session.get(url, params=params, timeout=30)
        r.raise_for_status()
        return r.json()

    # 1. List all supported genomes
    def list_genomes(self) -> Any:
        """Get all supported genome assemblies."""
        return self._get("list/ucscGenomes")

    # 2. List all tracks for a genome
    def list_tracks(self, genome: str) -> Any:
        """List all tracks for the given genome."""
        return self._get("list/tracks", params={"genome": genome})
    
    # 3. List all tracks in a hub
    def list_hub_tracks(self, hub_url: str, genome: str) -> Any:
        """Get all tracks in a given hub/genome."""
        return self._get("list/tracks", params={"hubUrl": hub_url, "genome": genome})

    # 4. List all chromosomes for a genome
    def list_chroms(self, genome: str) -> Any:
        """List all chromosomes for the given genome."""
        return self._get("list/chromosomes", params={"genome": genome})
    
    # 5. List all public track hubs
    def list_hubs(self) -> Any:
        """Get list of all public UCSC track hubs."""
        return self._get("list/publicHubs")

    # 6. Get chromosome sequence
    def get_chrom_sequence(self, genome: str, chrom: str) -> Any:
        """
        Get chromosome sequence.
        """
        params = {
            "genome": genome,
            "chrom": chrom,
        }
        return self._get("getData/sequence", params=params)

    # 7. Get DNA sequence for a region
    def get_sequence(
        self,
        genome: str,
        chrom: str,
        start: Optional[int] = None,
        end: Optional[int] = None,
        revcomp: bool = False,
        hub_url: Optional[str] = None,
    ) -> Any:
        """
        Get DNA sequence for a specified region.
        """
        params: Dict[str, Any] = {
            "genome": genome,
            "chrom": chrom,
        }
        if start is not None:
            params["start"] = start
        if end is not None:
            params["end"] = end
        if revcomp:
            params["revComp"] = 1
        if hub_url:
            params["hubUrl"] = hub_url

        return self._get("getData/sequence", params=params)

    # 8. Get data for a track
    def get_track_data(
        self,
        genome: str,
        track: str,
        chrom: Optional[str] = None,
        start: Optional[int] = None,
        end: Optional[int] = None,
        max_items_output: Optional[int] = None,
    ) -> Any:
        """
        Get track data (annotation) for a specified region.
        """
        params: Dict[str, Any] = {
            "genome": genome,
            "track": track,
        }
        if chrom:
            params["chrom"] = chrom
        if start is not None:
            params["start"] = start
        if end is not None:
            params["end"] = end
        if max_items_output is not None:
            params["maxItemsOutput"] = max_items_output

        return self._get("getData/track", params=params)

    # 9. Get cytoband info
    def get_cytoband(self, genome: str, chrom: Optional[str] = None) -> Any:
        """Get cytoband (chromosome banding) information."""
        params: Dict[str, Any] = {"genome": genome}
        if chrom:
            params["chrom"] = chrom
        return self._get("getData/cytoband", params=params)


_ucsc_api: Optional[UCSCAPI] = None


def initialize_ucsc_api(config: Optional[Dict[str, Any]] = None) -> None:
    """
    初始化 UCSCAPI，全局只需要一个实例。
    config 目前不使用，仅为了和其它工具初始化接口风格保持一致。
    """
    global _ucsc_api
    if _ucsc_api is None:
        _ucsc_api = UCSCAPI()


def get_ucsc_api() -> UCSCAPI:
    """内部辅助函数，确保全局 UCSCAPI 已经初始化。"""
    global _ucsc_api
    if _ucsc_api is None:
        _ucsc_api = UCSCAPI()
    return _ucsc_api



@tool(parse_docstring=True)
async def list_genomes() -> dict:
    """
    Get all supported genome assemblies from UCSC Genome Browser.
    
    Args:
        None
    
    Returns:
        Dictionary containing all supported genome assemblies from UCSC Genome Browser,
        with metadata (downloadTime, dataTime) and detailed genome info.
    """
    api = get_ucsc_api()
    try:
        return api.list_genomes()
    except Exception as e:
        return {"error": f"Failed to list genomes: {str(e)}"}


@tool(parse_docstring=True)
async def list_tracks(genome: str) -> dict:
    """
    List all tracks for a specific genome assembly.
    
    Args:
        genome: Genome assembly name (e.g., "hg38").
    
    Returns:
        Dictionary containing all tracks for the specified genome.
    """
    api = get_ucsc_api()
    try:
        return api.list_tracks(genome)
    except Exception as e:
        return {"error": f"Failed to list tracks: {str(e)}"}


@tool(parse_docstring=True)
async def list_hub_tracks(hub_url: str, genome: str) -> dict:
    """
    List all tracks in a specific track hub for a genome.
    
    Args:
        hub_url: URL of the track hub.
        genome: Genome assembly name.
    
    Returns:
        Dictionary containing tracks in the hub.
    """
    api = get_ucsc_api()
    try:
        return api.list_hub_tracks(hub_url, genome)
    except Exception as e:
        return {"error": f"Failed to list hub tracks: {str(e)}"}


@tool(parse_docstring=True)
async def list_chromosomes(genome: str) -> dict:
    """
    List all chromosomes for a genome assembly.
    
    Args:
        genome: Genome assembly name.
    
    Returns:
        Dictionary containing chromosome information, including a "chromosomes" key
        mapping chromosome names to their lengths (in base pairs), along with metadata
        such as download time and chromosome count.
    """
    api = get_ucsc_api()
    try:
        return api.list_chroms(genome)
    except Exception as e:
        return {"error": f"Failed to list chromosomes: {str(e)}"}


@tool(parse_docstring=True)
async def list_public_hubs() -> dict:
    """
    Get list of all public UCSC track hubs.
    
    Args:
        None
    
    Returns:
        Dictionary containing a list of public UCSC track hubs under the "publicHubs" key.
    """
    api = get_ucsc_api()
    try:
        return api.list_hubs()
    except Exception as e:
        return {"error": f"Failed to list public hubs: {str(e)}"}


@tool(parse_docstring=True)
async def get_chromosome_sequence(genome: str, chrom: str) -> dict:
    """
    Get sequence for an entire chromosome.
    
    Args:
        genome: Genome assembly name.
        chrom: Chromosome name (e.g., "chr1").
    
    Returns:
        Dictionary containing the DNA sequence for the chromosome under the "dna" key,
        along with metadata such as genome, chromosome, and download time.
    """
    api = get_ucsc_api()
    try:
        return api.get_chrom_sequence(genome, chrom)
    except Exception as e:
        return {"error": f"Failed to get chromosome sequence: {str(e)}"}


@tool(parse_docstring=True)
async def get_sequence(
    genome: str,
    chrom: str,
    start: Optional[int] = None,
    end: Optional[int] = None,
    revcomp: bool = False,
    hub_url: Optional[str] = None,
) -> dict:
    """
    Get DNA sequence for a genomic region.
    
    Args:
        genome: Genome assembly name.
        chrom: Chromosome name.
        start: Start position (optional).
        end: End position (optional).
        revcomp: Return reverse complement (default: False).
        hub_url: Track hub URL (optional).
    
    Returns:
        Dictionary containing the DNA sequence for the specified genomic region under
        the "dna" key, along with metadata such as genome, chromosome, start, end,
        and download time. The sequence may contain "N" for unknown or masked bases.
    """
    api = get_ucsc_api()
    try:
        return api.get_sequence(genome, chrom, start, end, revcomp, hub_url)
    except Exception as e:
        return {"error": f"Failed to get sequence: {str(e)}"}


@tool(parse_docstring=True)
async def get_track_data(
    genome: str,
    track: str,
    chrom: Optional[str] = None,
    start: Optional[int] = None,
    end: Optional[int] = None,
    max_items: Optional[int] = None,
) -> dict:
    """
    Get data from a specific track for a genomic region.
    
    Args:
        genome: Genome assembly name.
        track: Track name.
        chrom: Chromosome name (optional).
        start: Start position (optional).
        end: End position (optional).
        max_items: Maximum number of items to return (optional).
    
    Returns:
        Dictionary containing metadata about the track and a list of items (for example,
        gene objects) within the specified genomic region.
    """
    api = get_ucsc_api()
    try:
        return api.get_track_data(genome, track, chrom, start, end, max_items)
    except Exception as e:
        return {"error": f"Failed to get track data: {str(e)}"}


@tool(parse_docstring=True)
async def get_cytoband(genome: str, chrom: Optional[str] = None) -> dict:
    """
    Get cytoband (chromosome banding) information for a specified genome and chromosome.
    
    Args:
        genome: Genome assembly name.
        chrom: Chromosome name (optional).
    
    Returns:
        Dictionary containing cytoband information, including a list of cytoband records
        for the specified genome and chromosome (if provided).
    """
    api = get_ucsc_api()
    try:
        return api.get_cytoband(genome, chrom)
    except Exception as e:
        return {"error": f"Failed to get cytoband data: {str(e)}"}


ucsc_tools = {
    "list_genomes": list_genomes,
    "list_tracks": list_tracks,
    "list_hub_tracks": list_hub_tracks,
    "list_chromosomes": list_chromosomes,
    "list_public_hubs": list_public_hubs,
    "get_chromosome_sequence": get_chromosome_sequence,
    "get_sequence": get_sequence,
    "get_track_data": get_track_data,
    "get_cytoband": get_cytoband,
}
