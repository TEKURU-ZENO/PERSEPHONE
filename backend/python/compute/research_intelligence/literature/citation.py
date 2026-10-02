"""
Citation Manager module for PERSEPHONE Research Intelligence Platform.
Normalizes academic citations into canonical formats (Vancouver, NLM, DOI, PMID, PMCID).
"""
from typing import Dict, Any, Optional


class CitationManager:
    """
    Normalizes bibliographic metadata into research-grade academic citations.
    """

    @classmethod
    def format_vancouver(cls, paper: Dict[str, Any]) -> str:
        """
        Formats paper metadata into standard Vancouver / NLM citation format.
        Example: Moore K, Colombo N, Scambia G, et al. Maintenance Olaparib in Patients with Newly Diagnosed Advanced Ovarian Cancer. N Engl J Med. 2018;379(26):2495-2505.
        """
        authors = paper.get("authors") or paper.get("author", "Unknown Author")
        if isinstance(authors, list):
            if len(authors) > 3:
                author_str = f"{', '.join(authors[:3])}, et al."
            else:
                author_str = ", ".join(authors)
        else:
            author_str = str(authors)

        title = paper.get("title", "Untitled Document").rstrip(".")
        journal = paper.get("journal", "Unknown Journal")
        year = paper.get("year", "n.d.")
        volume = paper.get("volume", "")
        issue = paper.get("issue", "")
        pages = paper.get("pages", "")

        vol_str = f";{volume}" if volume else ""
        if issue:
            vol_str += f"({issue})"
        page_str = f":{pages}" if pages else ""

        citation = f"{author_str}. {title}. {journal}. {year}{vol_str}{page_str}."
        return citation

    @classmethod
    def resolve_identifiers(cls, paper: Dict[str, Any]) -> Dict[str, str]:
        """
        Resolves canonical IDs (PMID, DOI, PMCID, NCT ID) and provides permalink URLs.
        """
        pmid = str(paper.get("pmid", "")).strip()
        doi = str(paper.get("doi", "")).strip()
        pmcid = str(paper.get("pmcid", "")).strip()
        nct_id = str(paper.get("nct_id", paper.get("nctId", ""))).strip()

        urls = {}
        if pmid:
            urls["pubmed_url"] = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        if doi:
            clean_doi = doi.replace("https://doi.org/", "")
            urls["doi_url"] = f"https://doi.org/{clean_doi}"
        if pmcid:
            urls["pmc_url"] = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/"
        if nct_id:
            urls["clinical_trials_url"] = f"https://clinicaltrials.gov/study/{nct_id}"

        return {
            "pmid": pmid or None,
            "doi": doi or None,
            "pmcid": pmcid or None,
            "nct_id": nct_id or None,
            "urls": urls
        }
