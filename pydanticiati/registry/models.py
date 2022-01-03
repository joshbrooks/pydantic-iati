from __future__ import annotations

from typing import List, Optional, TypeVar

import httpx
from base_models import IntField, TextField, XmlBaseModel
from sqlmodel import Field, SQLModel

T = TypeVar("T")


class Publisher(SQLModel, XmlBaseModel, table=True):
    id: str = Field(default=None, primary_key=True)
    publisher: TextField
    organization_type: TextField
    hq_country_or_region: TextField
    datasets_count: IntField
    datasets_link: TextField


class IatiPublishersList(XmlBaseModel):
    """
    This is data pulled from
    https://www.iatiregistry.org/publisher/download/xml
    """

    iati_identifier: List[Publisher]

    @classmethod
    async def from_url(cls: T, url: str = "https://www.iatiregistry.org/publisher/download/xml", client: Optional[httpx.AsyncClient] = None) -> T:
        result = await super().from_url(url, client=client)
        return result
