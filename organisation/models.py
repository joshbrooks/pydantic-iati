from typing import List, Optional

from models import Narrative, XmlBaseModel


class ReportingOrg(XmlBaseModel):
    type: int
    ref: str
    narrative: List[Narrative]
    secondary_reporter: Optional[bool]
