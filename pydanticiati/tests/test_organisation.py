import xml.etree.ElementTree as ET

import pytest
from organisation.models import ReportingOrg


@pytest.fixture
def el_reporting_org():
    return ET.fromstring(
        """
        <reporting-org type="22" ref="BE-BCE_KBO-0421210424">
        <narrative xml:lang="nl">Koepel van de Vlaamse Noord-Zuidbeweging 11.11.11 VZW</narrative>
        </reporting-org>
    """
    )


def test_reporting_org(el_reporting_org):
    el = ReportingOrg.from_element(el_reporting_org)
    assert el.type == 22
    assert el.ref == "BE-BCE_KBO-0421210424"
    assert not el.secondary_reporter
    assert len(el.narrative) == 1
