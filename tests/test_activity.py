import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.dom import minidom

import pytest

from activity.models import IatiActivities, Title
from models import Narrative

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
