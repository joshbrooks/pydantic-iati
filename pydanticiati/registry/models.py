from typing import Any, List, Optional

from base_models import IntField, TextField, XmlBaseModel
from pydantic import BaseModel
from pydantic.networks import HttpUrl


class Publisher(XmlBaseModel):
    id: str
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


class KeyValuePair(BaseModel):
    key: str
    value: Any


class PackageSearchResultResults(BaseModel):
    license_title: str
    maintainer: Optional[str]
    relationships_as_object: list
    private: bool
    maintainer_email: Optional[str]
    num_tags: int
    id: str
    metadata_created: str
    metadata_modified: str
    author: Optional[str]
    author_email: str
    state: str
    version: Optional[str]
    creator_user_id: str
    type: str
    resources: list
    num_resources: int
    tags: list
    groups: list
    license_id: str
    relationships_as_subject: list
    organization: dict
    name: str
    isopen: bool
    url: Optional[HttpUrl]
    notes: str
    owner_org: str
    extras: List[KeyValuePair]
    license_url: Optional[HttpUrl]
    title: str
    revision_id: Optional[str]


class PackageSearchResult(BaseModel):
    count: int
    sort: str
    facets: dict
    results: List[PackageSearchResultResults]


class PackageSearch(BaseModel):
    """
    This is the result of fetching
    https://iatiregistry.org/api/3/action/package_search
    """

    help: HttpUrl
    success: bool
    result: PackageSearchResult
