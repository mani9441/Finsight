from dataclasses import dataclass, field
from typing import Optional, List, Dict

@dataclass
class CompanyInfo:
    """
    Metadata representation of a corporation.
    """
    ticker: str
    name: str
    sector: str
    industry: str
    summary: str
    website: str
    logo_url: Optional[str] = None
    officers: List[Dict[str, str]] = field(default_factory=list)
