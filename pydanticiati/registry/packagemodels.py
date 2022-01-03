from datetime import datetime
from typing import Any, List, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel
from pydantic.networks import AnyHttpUrl
from sqlmodel import Field, Relationship, SQLModel

T = TypeVar("T")


class KeyValuePair(BaseModel):
    key: str
    value: Any


class Organization(SQLModel, table=True):
    pk: Optional[int] = Field(default=None, primary_key=True)
    result_id: Optional[UUID] = Field(default=None, foreign_key="result.id")
    result: Optional["Result"] = Relationship(back_populates="organisation")
    created: Optional[datetime]
    title: Optional[str]
    name: Optional[str]
    is_organization: Optional[bool]
    state: Optional[str]
    image_url: Optional[str]
    type: Optional[str]
    id: Optional[UUID]
    approval_status: Optional[str]


class Result(SQLModel, table=True):

    id: Optional[UUID] = Field(default=None, primary_key=True)

    license_title: Optional[str]
    maintainer: Optional[str]
    private: Optional[bool]
    maintainer_email: Optional[str]
    num_tags: Optional[int]
    metadata_created: Optional[str]
    metadata_modified: Optional[str]
    author: Optional[str]
    author_email: Optional[str]
    state: Optional[str]
    version: Optional[str]
    creator_user_id: Optional[str]
    type: Optional[str]
    num_resources: Optional[int]
    license_id: Optional[str]
    name: Optional[str]
    isopen: Optional[bool]
    url: Optional[AnyHttpUrl]
    notes: Optional[str]
    owner_org: Optional[str]
    license_url: Optional[AnyHttpUrl]
    title: Optional[str]
    revision_id: Optional[str]

    resources: List["Resource"] = Relationship(back_populates="result")
    organisation: Optional["Organization"] = Relationship(back_populates="result")

    # relationships_as_object: list
    # tags: list
    # groups: list
    # extras: List[KeyValuePair]
    # relationships_as_subject: list
    # organization: dict


class Resource(SQLModel, table=True):

    id: Optional[UUID] = Field(default=None, primary_key=True)

    mimetype: str = Field(default="")
    cache_url: Optional[AnyHttpUrl]
    hash: str
    description: str
    metadata_modified: Optional[datetime]
    cache_last_updated: Optional[datetime]
    url: AnyHttpUrl
    name: Optional[str]
    format: Optional[str]
    package_id: UUID
    created: datetime
    state: Optional[str]
    mimetype_inner: Optional[str]
    last_modified: Optional[datetime]
    position: Optional[int]
    revision_id: UUID
    url_type: Optional[str]

    resource_type: Optional[str]
    size: int

    result_id: Optional[UUID] = Field(default=None, foreign_key="result.id")
    result: Optional[Result] = Relationship(back_populates="resources")


class PackageSearchResult(BaseModel):
    count: int
    sort: str
    facets: dict
    results: List[Result]


class PackageSearch(BaseModel):
    """
    This is the result of fetching
    https://iatiregistry.org/api/3/action/package_search
    """

    help: AnyHttpUrl
    success: bool
    result: PackageSearchResult
