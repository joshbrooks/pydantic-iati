import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.dom import minidom

import pytest

from activity.models import IatiActivities, Title
from codelists.models import Codelist, CodelistItem
from models import Narrative
from organisation.models import ReportingOrg

logger = logging.getLogger(__name__)


def prettify(elem):
    rough_string = ET.tostring(elem, "utf-8")
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


@pytest.fixture
def narrative_element():
    return ET.fromstring("<narrative>Planned start</narrative>")


@pytest.fixture
def fr_narrative():
    return ET.fromstring('<narrative xml:lang="fr">Mondial</narrative>')


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


@pytest.fixture
def el_reporting_org():
    return ET.fromstring(
        """
        <reporting-org type="22" ref="BE-BCE_KBO-0421210424">
        <narrative xml:lang="nl">Koepel van de Vlaamse Noord-Zuidbeweging 11.11.11 VZW</narrative>
        </reporting-org>
    """
    )


@pytest.fixture
def el_title():
    return ET.fromstring(
        """
        <title>
        <narrative xml:lang="nl">11.11.11 KOEPEL-PROGRAMMA 2017-2021</narrative>
        <narrative xml:lang="en">11.11.11 UMBRELLA-PROGRAM 2017-2021</narrative>
        </title>
    """
    )


def test_narrative(narrative_element):
    n = Narrative.from_element(narrative_element)
    assert n.text == "Planned start"
    assert not n.lang


def test_narrative_lang(fr_narrative):
    n = Narrative.from_element(fr_narrative)
    assert n.text == "Mondial"
    assert n.lang == "fr"


def test_codelist_items(clitems):
    items = Codelist.from_element(clitems.getroot())  # type: Codelist
    assert isinstance(items, Codelist)


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


def test_reporting_org(el_reporting_org):
    el = ReportingOrg.from_element(el_reporting_org)
    assert el.type == 22
    assert el.ref == "BE-BCE_KBO-0421210424"
    assert not el.secondary_reporter
    assert len(el.narrative) == 1


@pytest.fixture
def activity_element():
    path = Path(".") / "data" / "sample" / "activity-standard-example-annotated.xml"
    return ET.parse(path)


@pytest.fixture
def activity_element_real_data():
    path = Path(".") / "data" / "sample" / "111111_publisher-activities.xml"
    return ET.parse(path)


def test_title(el_title):
    title = Title.from_element(el_title)
    assert len(title.narrative) == 2


def test_activity_blurb(activity_element):
    a = IatiActivities.from_element(activity_element.getroot())
    logger.warning(a.json())
    import json

    out = json.dumps(json.loads(a.json()), indent=1)
    print(out)

    # assert len(a.iati_activity) == 1
    # assert a.iati_activity[0].default_currency == "USD"

    # assert a.iati_activity[0]

    # For output debugging

    assert a.iati_activity[0].location[0].point.pos.text == "31.616944 65.716944"


def test_real_activity(activity_element_real_data):
    """
    Test that we can parse a "real" activity
    """
    IatiActivities.from_element(activity_element_real_data.getroot())


def test_activity_to_element(activity_element):
    a = IatiActivities.from_element(activity_element.getroot())
    el = a.to_element()
    path = Path(".") / "data" / "sample" / "activity-standard-example-annotated-out.xml"
    ET.ElementTree(el).write(path)


def test_canonical_comparison(activity_element):
    """
    Read and write the example activity
    and test that the two give equivalent results
    """
    a = IatiActivities.from_element(activity_element.getroot())
    el = a.to_element()

    input_path = Path(".") / "data" / "sample" / "activity-standard-example-annotated.xml"

    path = Path(".") / "test_results" / "activity-standard-example-annotated-out.xml"

    canon_input = Path(".") / "data" / "sample" / "activity-standard-example-annotated-canon.xml"
    # canon_output = Path(".") / "test_results" / activity-standard-example-annotated-out-canon.xml"
    s = prettify(el)

    with open(path, "w") as output_data:
        output_data.write(s)

    with open(canon_input, "w") as output_data:
        output_data.write(prettify(ET.parse(input_path).getroot()))
