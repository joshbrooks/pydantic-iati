import pytest
from httpx import AsyncClient
from pytest_httpx import HTTPXMock

from pydanticiati.registry.models import IatiPublishersList


@pytest.mark.asyncio
async def test_an_async_function(httpx_mock: HTTPXMock):

    httpx_mock.add_response(
        method="GET",
        url="https://www.iatiregistry.org/publisher/download/xml",
        content=b"""<?xml version="1.0" encoding="UTF-8" ?>
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
</iati-publishers-list>""",
        status_code=200,
        headers={"content-type": "text/xml"},
    )

    async with AsyncClient() as client:
        publishers = await IatiPublishersList.from_url(client=client)
    assert publishers
