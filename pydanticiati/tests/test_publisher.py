import xml.etree.ElementTree as ET

import pytest
from httpx import AsyncClient
from pytest_httpx import HTTPXMock
from registry import models
from sqlmodel import Session, SQLModel, create_engine

publisher_content = """
<iati-identifier id="AU-5">
    <publisher>Australia - Department of  Foreign Affairs and Trade</publisher>
    <organization-type>Government</organization-type>
    <hq-country-or-region>Australia</hq-country-or-region>
    <datasets-count>173</datasets-count>
    <datasets-link>https://iatiregistry.org/publisher/ausgov</datasets-link>
</iati-identifier>
"""

pu_list_content = """<?xml version="1.0" encoding="UTF-8" ?>
<iati-publishers-list>
<iati-identifier id="AU-5">
   <publisher>Australia - Department of  Foreign Affairs and Trade</publisher>
   <organization-type>Government</organization-type>
   <hq-country-or-region>Australia</hq-country-or-region>
   <datasets-count>173</datasets-count>
   <datasets-link>https://iatiregistry.org/publisher/ausgov</datasets-link>
</iati-identifier>
    <iati-identifier id="44000">
    <publisher>The World Bank</publisher>
    <organization-type>Multilateral</organization-type>
    <hq-country-or-region>(No country assigned)</hq-country-or-region>
    <datasets-count>145</datasets-count>
    <datasets-link>https://iatiregistry.org/publisher/worldbank</datasets-link>
    </iati-identifier>
</iati-publishers-list>"""

url = "https://www.iatiregistry.org/publisher/download/xml"


@pytest.fixture
def publisher_element():
    return ET.fromstring(publisher_content)


@pytest.fixture
def publishers_element():
    return ET.fromstring(pu_list_content)


def test_publisher_item(publisher_element):
    items = models.Publisher.from_element(publisher_element)  # type: models.Publisher
    assert isinstance(items, models.Publisher)


def test_publishers_item(publishers_element):
    items = models.Publisher.from_parent_element(publishers_element)
    assert isinstance(items[0], models.Publisher)


@pytest.mark.asyncio
async def test_an_async_function(httpx_mock: HTTPXMock):

    httpx_mock.add_response(
        method="GET",
        url=url,
        content=pu_list_content,
        status_code=200,
        headers={"content-type": "text/xml"},
    )

    async with AsyncClient() as client:
        publishers = await models.IatiPublishersList.from_url(url=url, client=client)
    assert isinstance(publishers, models.IatiPublishersList)
    assert isinstance(publishers.iati_identifier[0], models.Publisher)


@pytest.mark.asyncio
async def test_persist_publishers(httpx_mock: HTTPXMock):
    """
    Test persisting the URL content to disk and the pydantic model
    """
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})  #

    httpx_mock.add_response(
        method="GET",
        url=url,
        content=pu_list_content,
        status_code=200,
        headers={"content-type": "text/xml"},
    )

    SQLModel.metadata.create_all(engine)

    async with AsyncClient() as client:
        publishers = await models.IatiPublishersList.from_url(url=url, client=client)

    with Session(engine) as session:
        for publisher in publishers.iati_identifier:
            publisher_in_db = session.get(models.Publisher, publisher.id)
            if publisher_in_db:
                session.delete(publisher_in_db)
            session.add(models.Publisher.from_orm(publisher))
        session.commit()


def test_publisher_item_persist(publisher_element):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})  #
    SQLModel.metadata.create_all(engine)
    publisher = models.Publisher.from_element(publisher_element)
    assert isinstance(publisher, models.Publisher)

    with Session(engine) as session:
        publisher_in_db = session.get(models.Publisher, publisher.id)
        if publisher_in_db:
            session.delete(publisher_in_db)
        session.add(publisher)
        session.commit()
