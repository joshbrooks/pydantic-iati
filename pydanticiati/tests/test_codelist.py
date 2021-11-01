import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
from codelists.models import Codelist, CodelistItem


@pytest.fixture
def clitem():
    return ET.fromstring(
        """
     <codelist-item>
            <code>1</code>
            <name>
                <narrative>Global</narrative>
                <narrative xml:lang="fr">Mondial</narrative>
            </name>
            <description>
                <narrative>The activity scope is global</narrative>
                <narrative xml:lang="fr">L'activité est de portée mondiale</narrative>
            </description>
        </codelist-item>
        """
    )


@pytest.fixture
def clitems():
    channel_codes = Path(".") / "data" / "sample" / "CRSChannelCode.xml"
    return ET.parse(channel_codes)


def test_codelist_items(clitems):
    items = Codelist.from_element(clitems.getroot())  # type: Codelist
    assert isinstance(items, Codelist)
    assert items.lang == "en"


def test_shelve_codelist_items(clitems):
    """
    Store the JSON representation of
    codelist items
    """
    import shelve

    with shelve.open("tester") as shelf:
        items = Codelist.from_element(clitems.getroot())  # type: Codelist
        for item in items.codelist_items.codelist_item:
            shelf[f"{items.name}-{item.code}"] = item.dict()
            CodelistItem(**item.dict())

    # Test that we can rehydrate a codelist from a dbm


def test_codelist_item(clitem):
    n = CodelistItem.from_element(clitem)  # type: CodelistItem
    assert n.name.narrative[0].text == "Global"
    assert len(n.description.narrative) == 2
    assert n.description.narrative[1].text == "L'activité est de portée mondiale"
    assert n.description.narrative[1].lang == "fr"
    assert n.code == "1"
