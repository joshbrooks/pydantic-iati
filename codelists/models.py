from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import HttpUrl

from models import Narrative, TextField, XmlBaseModel, XmlLanguageField


class TitleNarratives(XmlBaseModel):
    narrative: List[Narrative]


class NameNarratives(XmlBaseModel):
    narrative: List[Narrative]


class CommentNarratives(XmlBaseModel):
    narrative: List[Narrative]


class DescriptionNarratives(XmlBaseModel):
    narrative: List[Narrative]


class CategoryNarratives(XmlBaseModel):
    narrative: List[Narrative]


class CodelistItem(XmlBaseModel):
    code: TextField
    name: NameNarratives
    description: Optional[DescriptionNarratives]
    category: Optional[CategoryNarratives]
    url: Optional[HttpUrl]
    public_database: Optional[int]
    status: Optional[str]
    activation_date: Optional[date]
    withdrawal_date: Optional[date]


class CodelistItems(XmlBaseModel):
    codelist_item: List[CodelistItem]


class CodelistMetadata(XmlBaseModel):
    name: NameNarratives
    description: Optional[DescriptionNarratives]
    category: Optional[CategoryNarratives]
    url: Optional[HttpUrl]


class Codelist(XmlBaseModel):
    metadata: CodelistMetadata
    codelist_items: CodelistItems
    ref: Optional[str]
    name: str
    category_codelist: Optional[str]
    lang: Optional[XmlLanguageField]
    complete: Optional[bool]
    embedded: Optional[bool]
