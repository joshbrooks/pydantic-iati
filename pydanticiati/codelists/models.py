from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from datetime import date
from enum import Enum
from pathlib import Path
from typing import List, Optional

from activity.models import Narratives
from models import Narrative, TextField, XmlBaseModel, XmlLanguageField
from pydantic import HttpUrl


class TitleNarratives(Narratives):
    narrative: List[Narrative]


class NameNarratives(Narratives):
    narrative: List[Narrative]


class CommentNarratives(Narratives):
    narrative: List[Narrative]


class DescriptionNarratives(Narratives):
    narrative: List[Narrative]


class CategoryNarratives(Narratives):
    narrative: List[Narrative]


class CodelistStatusEnum(str, Enum):
    ACTIVE = ("active",)
    WITHDRAWN = "withdrawn"


class CodelistItem(XmlBaseModel):
    code: TextField
    name: Optional[NameNarratives]
    description: Optional[DescriptionNarratives]
    category: Optional[CategoryNarratives]
    url: Optional[HttpUrl]
    public_database: Optional[int]
    status: Optional[CodelistStatusEnum]
    activation_date: Optional[date]
    withdrawal_date: Optional[date]

    @property
    def typescript(self):
        return f"""new CodelistItem("{self.code}", {'"'+self.name.default.text+'"' if self.name.default else 'null' }, {'"'+self.status+'"' if self.status else 'null'})"""


class CodelistItems(XmlBaseModel):
    codelist_item: List[CodelistItem]

    def to_typescript(self):
        return "\n".join([cli.to_typescript() for cli in self.codelist_item])


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

    @classmethod
    def from_file(cls, path: Path):
        element = ET.parse(path)
        root = element.getroot()
        return cls.from_element(root)


def codelists(path):
    """
    Return a set of Codelists from a directory
    of XML files
    """
    return {f"{f[:-4]}": Codelist.from_file(os.path.join(path, f)) for f in os.listdir(path) if f.endswith(".xml")}
