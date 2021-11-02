from __future__ import annotations

import logging
import re
import warnings
import xml.etree.ElementTree as ET
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, List, Optional, Set, Type, Union

import httpx
from pydantic import BaseModel as PydanticBaseModel
from pydantic import HttpUrl, fields

logger = logging.getLogger(__name__)


class CodelistValue(str):
    """
    Type used to indicate a codelist value
    """

    pass


NS = {"xml": "http://www.w3.org/XML/1998/namespace"}


class TextField(str):
    """
    Type used to obtain the text value of an element
    """

    pass


class ThisElementTextField(str):
    """
    Marker for "THIS element text"
    """

    pass


class IntField(int):
    """
    Type used to obtain the text value of an element, as a number
    For instance `crs-code`
    """

    pass


class DecimalText(Decimal):
    ...


class XmlLanguageField(str):
    """
    Returns an 'xml:lang' attribute content
    """

    pass


class XmlToModel:
    def __init__(self, model_class: Type[PydanticBaseModel], element: ET.Element):
        self.model_class = model_class
        self.element = element

    @staticmethod
    def attrib_name(field: fields.ModelField) -> str:
        """
        Return the attribute name expected for a given
        field name
        """
        if field.type_ == XmlLanguageField:
            return "{http://www.w3.org/XML/1998/namespace}lang"

        return field.name.strip("_").replace("_", "-")

    @staticmethod
    def tag_name(field: fields.ModelField) -> str:
        """
        Return the tag name expected for a given
        field name
        """
        return field.name.replace("_", "-")

    def check_unused_attribs(self) -> Optional[Set[str]]:
        """
        Check whether there are any attributes not listed in the "fields"
        This is information which is dropped on serialization
        """
        attribs = set(self.element.attrib.keys())
        fields = set([self.attrib_name(f) for f in self.model_class.__fields__.values()])
        unused_attribs = attribs.difference(fields)
        if unused_attribs:
            warnings.warn(f"Unprocessed attribs: {unused_attribs}  in {self.model_class}")
            return unused_attribs
        return None

    def check_unused_elements(self) -> Optional[Set[str]]:
        """
        Check whether there are any elements not listed in the "fields"
        This is information which is dropped on serialization
        """
        tags = set([e.tag for e in self.element])
        fields = set([self.attrib_name(f) for f in self.model_class.__fields__.values()])
        unused_elements = tags.difference(fields)
        if unused_elements:
            warnings.warn(f"Unprocessed elements: {unused_elements} in {self.model_class}")
            return unused_elements
        return None

    def from_element(self, verbose: bool = True):
        def get_attrib(field: fields.ModelField):
            return self.element.get(self.attrib_name(field))

        def get_text(field: fields.ModelField) -> Optional[Union[str, int]]:
            text_element = self.element.find(self.tag_name(field))
            if text_element is None:
                return None
            if field.type_ != str:
                return field.type_(text_element.text)
            return text_element.text

        def get_element_text(field: fields.ModelField):
            if field.type_ != str:
                return field.type_(self.element.text)
            return self.element.text

        def get_nested_xml(field: fields.ModelField):

            if field.shape == fields.SHAPE_SINGLETON:
                element = self.element.find(self.tag_name(field), namespaces=NS)
                if element is None:
                    return None
                return XmlToModel(model_class=field.type_, element=element).from_element()

            if field.shape == fields.SHAPE_LIST:
                return [XmlToModel(model_class=field.type_, element=child_element).from_element() for child_element in self.element.findall(self.tag_name(field), namespaces=NS)]

        def get_narratives(field: fields.ModelField):
            """
            Narratives are a special case of nested XML
            Since these are very often a simple list with no other info
            these can be specified like
            >>> description: List[Narrative]
            """

            if field.name == "narrative":
                path = "narrative"
            else:
                raise DeprecationWarning("Please use a nested Narrative")
            return [XmlToModel(model_class=field.type_, element=child_element).from_element() for child_element in self.element.findall(path, namespaces=NS)]

        def get_language_field(field: fields.ModelField):
            return self.element.get("xml:lang") or self.element.get(f"{{{NS['xml']}}}lang")

        def get_uri(field: fields.ModelField) -> Optional[str]:
            uri = self.element.get(self.attrib_name(field))
            if uri != "":
                return uri
            return None

        getters = {
            HttpUrl: get_uri,
            Narrative: get_narratives,
            TextField: get_text,
            IntField: get_text,
            XmlLanguageField: get_language_field,
            ThisElementTextField: get_element_text,
            DecimalText: get_element_text,
            XmlBaseModel: get_nested_xml,
            str: get_attrib,
            bool: get_attrib,
            int: get_attrib,
            datetime: get_attrib,
            date: get_attrib,
            Decimal: get_attrib,
            Enum: get_attrib,
        }
        """
        This is a "best effort" approach to parse an XML element into a sane Pydantic class.
        Common fields like "text" and "lang" and narratives are handled here
        as well as basic attributes and nested fields.
        """
        # Iterate over the fields for "nested", "narrative", "text" and "attribute" type fields
        data = dict()  # type: dict[str, Any]

        # Generally the attribute name or xml tag name
        # is the field name replacing '_' -> '-'

        for field in self.model_class.__fields__.values():  # type: fields.ModelField
            for type_, method in getters.items():
                if field.name not in data and issubclass(field.type_, type_):
                    data[field.name] = method(field)
            if field.name not in data:
                warnings.warn(f"Encountered unlisted type: {field.type_}, using default Attrib method")
                data[field.name] = get_attrib(field)

        if verbose:
            self.check_unused_attribs()
            self.check_unused_elements()

        try:
            return self.model_class(**data)
        except Exception as E:
            logger.error(ET.tostring(self.element))
            logger.error(data)
            logger.error(f"{E}")
            raise


class XmlBaseModel(PydanticBaseModel):
    """
    Adds class methods
    to extract useful data in a "standard"
    way from an Element based on attribute names
    and types
    """

    @classmethod
    def from_element(cls, element: ET.Element, verbose: bool = True):
        return XmlToModel(model_class=cls, element=element).from_element()

    @classmethod
    async def from_url(cls, url: str, client: Optional[httpx.AsyncClient] = None):
        if client:
            response = await client.get(url)
        else:
            with httpx.AsyncClient(timeout=httpx.Timeout(10.0, connect=60.0)) as client:
                response = await client.get(url)
        return cls.from_element(ET.fromstring(response.content))

    def to_element(self, field: Optional[fields.ModelField] = None, tag_name: Optional[str] = None):

        if not tag_name:
            if field:
                tag_name = field.alias.replace("_", "-").lower()
            else:
                tag_name = re.sub(r"(?<!^)(?=[A-Z])", "-", self.__class__.__name__).lower()

        el = ET.Element(f"{tag_name}" or "")

        def is_sub(field: fields.ModelField, klasses: Union[Type, List[Type]]) -> bool:
            if isinstance(klasses, List):
                return any([issubclass(field.type_, f) for f in klasses])
            else:
                return issubclass(field.type_, klasses)

        for field in self.__fields__.values():

            attr_key = field.name.strip("_").replace("_", "-")
            attr = getattr(self, field.name)

            if attr is None:
                continue

            if is_sub(field, Enum):
                el.set(attr_key, str(attr.value))

            elif is_sub(field, CodelistValue):
                el.set(attr_key, str(attr))

            elif is_sub(field, HttpUrl):
                el.set(attr_key, str(attr))

            elif is_sub(field, bool):
                el.set(attr_key, str(int(attr)))

            elif is_sub(field, [TextField]):
                ET.SubElement(el, attr_key).text = str(attr)

            elif is_sub(field, XmlLanguageField):
                el.set("xml:lang", attr)

            elif is_sub(field, ThisElementTextField):
                el.text = attr

            elif is_sub(field, DecimalText):
                el.text = f"{attr}"

            elif is_sub(field, [str, int, Decimal]):
                el.set(attr_key, str(attr))

            elif is_sub(field, [date, datetime]):

                timestring = attr.isoformat()
                if timestring.endswith("+00:00"):
                    timestring = timestring[:-6] + "Z"

                el.set(attr_key, timestring)

            elif is_sub(field, XmlBaseModel):
                # This is a 'nested' element
                try:
                    if field.shape == fields.SHAPE_SINGLETON:
                        el.append(attr.to_element(field))
                    if field.shape == fields.SHAPE_LIST:
                        el.extend([a.to_element(field) for a in attr])
                except TypeError:
                    raise

            else:
                raise NotImplementedError

        try:
            ET.tostring(el)
        except Exception as E:
            raise ValueError from E
        return el


class Narrative(XmlBaseModel):
    lang: Optional[XmlLanguageField]
    text: Optional[ThisElementTextField]


class IatiVersionEnum(str, Enum):
    v201 = "2.01"
    v202 = "2.02"
    v203 = "2.03"


class DatasetTypeEnum(str, Enum):
    activity = "Activity"
    organisation = "Organisation"


class DatasetPublisher(PydanticBaseModel):
    url: HttpUrl
    publisher_iati_id: str
    display_name: str
    name: str


class DatasetResult(PydanticBaseModel):

    url: HttpUrl
    name: str
    title: str
    filetype: DatasetTypeEnum
    publisher: DatasetPublisher
    source_url: HttpUrl
    activities: HttpUrl
    activity_count: int
    date_created: datetime
    date_updated: datetime
    last_found_in_registry: datetime
    iati_version: IatiVersionEnum
    sha1: str
    note_count: int
    added_manually: bool
    internal_url: HttpUrl


class Dataset(PydanticBaseModel):
    """
    Response received from `https://iatidatastore.iatistandard.org/api/datasets/?format=json`
    """

    count: int
    next: Optional[HttpUrl]
    previous: Optional[HttpUrl]
    results: List[DatasetResult]
