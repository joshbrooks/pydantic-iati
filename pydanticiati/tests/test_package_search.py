import json
from pathlib import Path

from registry.packagemodels import Organization, Resource, Result
from sqlmodel import Session, SQLModel, create_engine

package_path = Path("pydanticiati") / "data" / "sample" / "iatiregistry.org" / "action" / "package_search.json"

engine = create_engine("sqlite://", connect_args={"check_same_thread": False})  #


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def test_create_request():
    """
    Test persisting the URL content to disk and the pydantic model
    """
    create_db_and_tables()

    with open(package_path) as content:
        package = json.loads(content.read())

    SQLModel.metadata.create_all(engine)  #

    with Session(engine) as session:

        for result_data in package["result"]["results"]:
            resources = result_data.pop("resources")
            org = result_data.pop("organization")

            result = Result(**result_data)
            session.add(result)
            session.commit()
            for r in resources:
                resource = Resource(**r, result=result)
                session.add(resource)

            o = Organization(**org)
            session.add(o)
            session.commit()
