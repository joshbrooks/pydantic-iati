
import pytest
import xml.etree.ElementTree as ET
from pathlib import Path
from registry.models import Publisher, IatiPublishersList

# Intended to work with data pulled from https://www.iatiregistry.org/publisher/download/xml

@pytest.fixture
def publisher_element():
    return ET.fromstring(
        """
        <iati-identifier id="AU-5">
            <publisher>Australia - Department of  Foreign Affairs and Trade</publisher>
            <organization-type>Government</organization-type>
            <hq-country-or-region>Australia</hq-country-or-region>
            <datasets-count>173</datasets-count>
            <datasets-link>https://iatiregistry.org/publisher/ausgov</datasets-link>
        </iati-identifier>
        """
    )

@pytest.fixture
def publishers_element():
    return ET.fromstring(
        """
        <iati-publishers-list>
        <iati-identifier id="AU-5">
            <publisher>Australia - Department of  Foreign Affairs and Trade</publisher>
            <organization-type>Government</organization-type>
            <hq-country-or-region>Australia</hq-country-or-region>
            <datasets-count>173</datasets-count>
            <datasets-link>https://iatiregistry.org/publisher/ausgov</datasets-link>
        </iati-identifier>
        </iati-publishers-list>
        """
    )


def test_publisher_item(publisher_element):
    items = Publisher.from_element(publisher_element)  # type: Publisher
    assert isinstance(items, Publisher)


def test_publishers_item(publishers_element):
    items = IatiPublishersList.from_element(publishers_element)  # type: IatiPublishersList
    assert isinstance(items, IatiPublishersList)
    assert isinstance(items.iati_identifier[0], Publisher)
