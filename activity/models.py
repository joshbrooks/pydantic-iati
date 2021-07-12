from datetime import date, datetime
from decimal import Decimal
from enum import Enum, IntEnum
from typing import List, Optional

from pydantic import Field, HttpUrl
from typing_extensions import Annotated

from models import (
    CodelistValue,
    DecimalText,
    IatiVersionEnum,
    Narrative,
    TextField,
    ThisElementTextField,
    XmlBaseModel,
    XmlLanguageField,
)
from organisation.models import ReportingOrg


class ChannelCode(CodelistValue):
    pass


class RecipientCountryCode(CodelistValue):
    pass


class LocationReachCode(CodelistValue):
    pass


class ActivityId(CodelistValue):
    pass


class OrganisationId(CodelistValue):
    pass


class CollaborationTypeCode(CodelistValue):
    pass


class DocumentCategoryCode(CodelistValue):
    pass


class LanguageCode(CodelistValue):
    pass


class IsoDateModel(XmlBaseModel):
    """
    For models which have an "iso-date" element
    """

    iso_date: date


NS = {"xml": "http://www.w3.org/XML/1998/namespace"}


class Narratives(XmlBaseModel):
    narrative: List[Narrative]


class DescriptionNarratives(Narratives):
    narrative: List[Narrative]


class TitleNarratives(Narratives):
    narrative: List[Narrative]


class CommentNarratives(Narratives):
    narrative: List[Narrative]


class ParticipatingOrg(XmlBaseModel):
    class OrganisationTypeCode(IntEnum):
        Government = 10
        Local_Government = 11
        Other_Public_Sector = 15
        International_NGO = 21
        National_NGO = 22
        Regional_NGO = 23
        Partner_Country_based_NGO = 24
        Public_Private_Partnership = 30
        Multilateral = 40
        Foundation = 60
        Private_Sector = 70
        Private_Sector_in_Provider_Country = 71
        Private_Sector_in_Aid_Recipient_Country = 72
        Private_Sector_in_Third_Country = 73
        Academic_Training_and_Research = 80
        Other = 90

    class OrganisationRoleCode(IntEnum):
        Funding = 1
        Accountable = 2
        Extending = 3
        Implementing = 4

    ref: Optional[str]
    type: Optional[OrganisationTypeCode]
    role: OrganisationRoleCode
    activity_id: Optional[str]
    crs_channel_code: Optional[str]
    narrative: List[Narrative]
    lang: Optional[str]


class Title(XmlBaseModel):
    narrative: List[Narrative]


class Description(XmlBaseModel):
    type: int
    narrative: List[Narrative]


class OwnerOrg(XmlBaseModel):
    """
    Where applicable, the organisation that owns the other identifier being reported.
    When used, then either other-identifier/owner-org/@ref
    or other-identifier/owner-org/narrative/text() MUST be present.
    """

    ref: Optional[str]
    narrative: Optional[List[Narrative]]
    lang: Optional[str]


class OtherIdentifier(XmlBaseModel):
    """
    An other identifier for the activity.
    This may be a publishers own identifier that it wishes to record with the activity.
    This element is also used to trace changes to activity identifiers,
    for example when and organisation has changed it’s organisation identifier.
    """

    class OtherIdentifierTypeCode(Enum):

        INTERNAL = "A1"
        CRS = "A2"
        PREVIOUS = "A3"
        OTHER_ACTIVITY = "A9"
        PREVIOUS_REPORTING_ORGANISATION = "B1"
        OTHER_ORGANISATION = "B9"

    ref: Optional[str]
    type: OtherIdentifierTypeCode
    owner_org: Optional[OwnerOrg]


class ActivityDate(XmlBaseModel):
    class ActivityDateTypeEnum(Enum):
        planned_start = "1"
        actual_start = "2"
        planned_end = "3"
        actual_end = "4"

    iso_date: date
    type_: ActivityDateTypeEnum
    narrative: List[Narrative]


class ActivityStatus(XmlBaseModel):
    class ActivityStatusCodeEnum(Enum):
        Pipeline_identification = "1"
        Implementation = "2"
        Finalisation = "3"
        Closed = "4"
        Cancelled = "5"
        Suspended = "6"

    code: str


class ContactInfoOrganisation(XmlBaseModel):
    narrative: List[Narrative]
    pass


class ContactInfoDepartment(XmlBaseModel):
    narrative: List[Narrative]
    pass


class ContactInfoPersonName(XmlBaseModel):
    narrative: List[Narrative]
    pass


class ContactInfoJobTitle(XmlBaseModel):
    narrative: List[Narrative]
    pass


class ContactInfoMailingAddress(XmlBaseModel):
    narrative: List[Narrative]


class ContactInfo(XmlBaseModel):
    class ContactType(Enum):
        General_Enquiries = "1"
        Project_Management = "2"
        Financial_Management = "3"
        Communications = "4"

    type_: Optional[ContactType]

    organisation: Optional[ContactInfoOrganisation]
    department: Optional[ContactInfoDepartment]
    person_name: Optional[ContactInfoPersonName]
    job_title: Optional[ContactInfoJobTitle]
    telephone: Optional[TextField]
    email: Optional[TextField]  # TODO: Make this a properly checked field
    website: Optional[TextField]  # TODO: Make this a properly checked field
    mailing_address: Optional[ContactInfoMailingAddress]


class RecipientRegion(XmlBaseModel):
    code: str
    vocabulary: Optional[str]
    vocabulary_uri: Optional[str]
    percentage: Optional[Decimal]


class PolicyMarker(XmlBaseModel):
    narrative: List[Narrative]
    vocabulary: Optional[str]
    vocabulary_uri: Optional[str]
    code: str
    significance: Optional[str]


class OtherFlags(XmlBaseModel):
    """
    This covers the four CRS++ columns titled: "Free standing technical cooperation"; "Programme-based approach"; "Investment project"; "Associated financing"
    """

    code: str
    significance: bool


class RepaymentPlan(XmlBaseModel):
    code: str


class RepaymentType(XmlBaseModel):
    code: str


class ActivityScope(XmlBaseModel):
    code: str


class LoanTerms(XmlBaseModel):
    rate_1: Optional[Decimal]
    rate_2: Optional[Decimal]

    repayment_type: Optional[RepaymentType]
    repayment_plan: Optional[RepaymentPlan]
    commitment_date: Optional[IsoDateModel]
    repayment_first_date: Optional[IsoDateModel]
    repayment_final_date: Optional[IsoDateModel]


class LoanStatus(XmlBaseModel):
    interest_received: Optional[TextField]
    principal_outstanding: Optional[TextField]
    principal_arrears: Optional[TextField]
    interest_arrears: Optional[TextField]

    currency: Optional[str]
    value_date: Optional[date]
    year: Optional[Decimal]


class CrsAdd(XmlBaseModel):
    """
    Additional items specific to CRS++ reporting.
    """

    other_flags: Optional[List[OtherFlags]]
    loan_terms: Optional[LoanTerms]
    loan_status: Optional[LoanStatus]
    channel_code: Optional[TextField] = Field(
        title="Channel Code",
        description="The CRS channel code for this activity. This should only be used for reporting to CRS. The code list contains both organisation types and names of organisations. For non-CRS purposes these should be reported using the participating-org element.",
    )


class RecipientCountry(XmlBaseModel):
    narrative: Optional[List[Narrative]]
    code: RecipientCountryCode
    percentage: Optional[Decimal]


class LocationReach(XmlBaseModel):
    code: LocationReachCode


class LocationId(XmlBaseModel):
    code: str
    vocabulary: str


class Pos(XmlBaseModel):
    text: ThisElementTextField


class Point(XmlBaseModel):
    pos: Pos
    srsName: str = "http://www.opengis.net/def/crs/EPSG/0/4326"


class Administrative(XmlBaseModel):
    code: str
    vocabulary: str
    level: str


class LocationClass(XmlBaseModel):
    code: str


class LocationName(XmlBaseModel):
    narrative: List[Narrative]


class LocationDescription(XmlBaseModel):
    narrative: List[Narrative]


class LocationActivityDescription(XmlBaseModel):
    narrative: List[Narrative]


class LocationExactness(XmlBaseModel):
    code: str


class LocationFeatureDesignation(XmlBaseModel):
    code: str


class Location(XmlBaseModel):
    location_reach: Optional[LocationReach]
    location_id: Optional[List[LocationId]]
    name: Optional[LocationName]
    description: Optional[LocationDescription]
    activity_description: Optional[LocationActivityDescription]
    administrative: Optional[Administrative]
    point: Optional[Point]
    ref: Optional[str]

    exactness: Optional[LocationExactness]
    location_class: Optional[LocationClass]

    feature_designation: Optional[LocationFeatureDesignation]


class DefaultFinanceType(XmlBaseModel):
    code: str


class DefaultAidType(XmlBaseModel):
    code: str
    vocabulary: Optional[str]


class DefaultTiedStatus(XmlBaseModel):
    code: str


class DefaultFlowType(XmlBaseModel):
    code: str


class Value(XmlBaseModel):
    currency: Optional[str]
    value_date: date
    amount: DecimalText


class TransactionType(XmlBaseModel):
    code: str


class Budget(XmlBaseModel):
    type: int
    status: int

    period_start: IsoDateModel
    period_end: IsoDateModel

    value: Value


class ProviderOrg(XmlBaseModel):
    provider_activity_id: Optional[ActivityId]
    type_: Optional[str]
    ref: Optional[OrganisationId]
    narrative: List[Narrative]


class ReceiverOrg(XmlBaseModel):
    receiver_activity_id: Optional[ActivityId]
    type_: Optional[str]
    ref: Optional[OrganisationId]
    narrative: List[Narrative]


class DisbursementChannel(XmlBaseModel):
    code: str


class Sector(XmlBaseModel):
    code: str
    vocabulary: str
    vocabulary_uri: Optional[HttpUrl]
    percentage: Optional[Decimal]
    narrative: Optional[List[Narrative]]


class TransactionRecipientCountry(XmlBaseModel):
    code: str


class TransactionRecipientRegion(XmlBaseModel):
    code: str
    vocabulary: str


class FlowType(XmlBaseModel):
    code: str


class AidType(XmlBaseModel):
    code: str
    vocabulary: str


class TransactionSector(XmlBaseModel):
    code: str
    vocabulary: str


class TiedStatus(XmlBaseModel):
    code: str


class FinanceType(XmlBaseModel):
    code: str


class Transaction(XmlBaseModel):

    transaction_type: TransactionType
    transaction_date: IsoDateModel
    value: Value
    description: Optional[DescriptionNarratives]
    provider_org: Optional[ProviderOrg]
    receiver_org: Optional[ReceiverOrg]

    disbursement_channel: Optional[DisbursementChannel]
    sector: List[TransactionSector]
    recipient_country: Optional[TransactionRecipientCountry]
    recipient_region: Optional[TransactionRecipientRegion]
    humanitarian: Optional[bool]
    ref: Optional[str]

    flow_type: Optional[FlowType]
    finance_type: Optional[FinanceType]
    aid_type: Optional[List[AidType]]
    tied_status: Optional[TiedStatus]


class CollaborationType(XmlBaseModel):
    code: CollaborationTypeCode


class DocumentCategory(XmlBaseModel):
    code: DocumentCategoryCode


class DocumentLanguage(XmlBaseModel):
    code: LanguageCode


class DocumentLink(XmlBaseModel):
    format: str = Field(description='An IANA code for the MIME type of the document being referenced, e.g. "application/pdf".')
    url: Optional[HttpUrl]
    title: TitleNarratives
    description: Optional[DescriptionNarratives]
    category: Optional[DocumentCategory]
    language: Optional[DocumentLanguage]
    document_date: Optional[IsoDateModel]


class ResultReference(XmlBaseModel):
    vocabulary: str
    code: str
    vocabulary_uri: HttpUrl


class ResultDocumentLink(DocumentLink):
    pass


class ResultIndicatorDocumentLink(DocumentLink):
    pass


class IndicatorMeasure(str):
    """
    To specify how an indicator is being measured. This includes qualitative and quantitative values.
    """

    pass


class Dimension(XmlBaseModel):
    name: str = Field("Freetext description of a category being disaggregated.")
    value: str = Field(description="Description of the value being disaggregated.")


class BaselineLocation(XmlBaseModel):
    ref: str


class ActualLocation(XmlBaseModel):
    ref: str


class TargetLocation(XmlBaseModel):
    ref: str


class Baseline(XmlBaseModel):
    year: int

    iso_date: Optional[date]
    value: str

    location: Optional[List[BaselineLocation]]
    dimension: Optional[List[Dimension]]

    document_link: List[DocumentLink]
    comment: Optional[CommentNarratives]


class Reference(XmlBaseModel):
    code: str
    vocabulary: str
    indicator_uri: Optional[HttpUrl]


class IndicatorPeriodActual(XmlBaseModel):

    location: Optional[List[ActualLocation]]
    dimension: Optional[List[Dimension]]

    comment: Optional[CommentNarratives]
    document_link: List[DocumentLink]
    value: str


class IndicatorPeriodTarget(XmlBaseModel):

    value: str
    location: Optional[List[TargetLocation]]
    dimension: Optional[List[Dimension]]
    comment: Optional[CommentNarratives]
    document_link: List[DocumentLink]


class Period(XmlBaseModel):
    period_start: IsoDateModel
    period_end: IsoDateModel

    target: List[IndicatorPeriodTarget]
    actual: List[IndicatorPeriodActual]


class Indicator(XmlBaseModel):

    measure: IndicatorMeasure
    ascending: Optional[bool] = True
    aggregation_status: Optional[bool]

    title: Optional[TitleNarratives]
    description: Optional[DescriptionNarratives]
    document_link: Optional[List[ResultIndicatorDocumentLink]]

    reference: Optional[List[Reference]]
    baseline: Optional[Baseline]
    period: Period


class Result(XmlBaseModel):
    type_: str
    aggregation_status: bool

    title: TitleNarratives
    description: Optional[DescriptionNarratives]
    document_link: List[ResultDocumentLink]

    reference: Optional[List[ResultReference]]
    indicator: List[Indicator]


class LegacyData(XmlBaseModel):
    """
    The legacy data element allows for the reporting of values held in a field in the reporting organisation's system which is similar, but not identical to an IATI element.
    """

    name: str
    value: str
    iati_equivalent: str


class Forecast(XmlBaseModel):
    year: int
    value_date: date
    currency: str
    value: ThisElementTextField


class ForwardSpendingSurvey(XmlBaseModel):
    extraction_date: date
    priority: bool = Field(description="True if the partner country is a priority partner country.")
    phaseout_year: Decimal = Field(description="If there are plans to phase out operations from the partner country, this column shows the projected year of last disbursements.")
    forecast: Optional[List[Forecast]]


class CapitalSpend(XmlBaseModel):
    percentage: Decimal


class Tag(XmlBaseModel):
    code: str
    vocabulary: str
    vocabulary_uri: Optional[HttpUrl]
    narrative: List[Narrative]


class HumanitarianScope(XmlBaseModel):
    type_: str
    vocabulary: str
    vocabulary_uri: Optional[HttpUrl]
    code: str
    narrative: List[Narrative]
    lang: Optional[XmlLanguageField]


class RelatedActivity(XmlBaseModel):
    ref: str
    type_: str


class BudgetItem(XmlBaseModel):
    code: str = Field(description="A code for the budget-item from the vocabulary specified.")
    percentage: Decimal = Field(
        description="When multiple budget-item elements are declared within a single country-budget-items element, then, for each vocabulary used, the percentage values should sum 100%."
    )
    description: DescriptionNarratives = Field(description="A longer, human-readable description of the budget-item. May be repeated for different languages")
    lang: Optional[XmlLanguageField] = Field(
        description="A code specifying the language of text in this element. It is recommended that wherever possible only codes from ISO 639-1 are used. If not present, the default language is assumed."
    )


class CountryBudgetItems(XmlBaseModel):
    vocabulary: str = Field(
        description="An IATI code for the common functional classification or country system (This allows for common codes, country-specific, or any other classification agreed between countries and donors"
    )
    budget_item: List[BudgetItem]


class Condition(XmlBaseModel):
    type_: str
    narrative: List[Narrative]
    lang: Optional[XmlLanguageField]


class Conditions(XmlBaseModel):
    condition: List[Condition]
    attached: bool


class PlannedDisbursement(XmlBaseModel):
    period_start: IsoDateModel
    period_end: IsoDateModel
    value: Value
    provider_org: Optional[ProviderOrg]
    receiver_org: Optional[ReceiverOrg]
    type_: str


class IatiActivity(XmlBaseModel):

    iati_identifier: TextField
    reporting_org: ReportingOrg

    last_updated_datetime: Optional[datetime]
    lang: Optional[XmlLanguageField]
    default_currency: Optional[str]
    humanitarian: Optional[bool]
    hierarchy: Optional[int]
    linked_data_uri: Optional[HttpUrl]
    budget_not_provided: Optional[str]
    title: Title
    description: Annotated[
        List[Description], Field(description="A longer, human-readable description containing a meaningful description of the activity. May be repeated for different languages.")
    ]
    participating_org: List[ParticipatingOrg]
    other_identifier: Optional[List[OtherIdentifier]]
    activity_status: ActivityStatus
    activity_date: List[ActivityDate]

    contact_info: List[ContactInfo]
    activity_scope: Optional[ActivityScope]
    recipient_country: Optional[List[RecipientCountry]]
    recipient_region: Optional[List[RecipientRegion]]
    location: Optional[List[Location]]
    sector: List[Sector]
    tag: List[Tag]
    country_budget_items: List[CountryBudgetItems]
    humanitarian_scope: List[HumanitarianScope]
    policy_marker: Optional[List[PolicyMarker]]
    collaboration_type: CollaborationType

    default_flow_type: DefaultFlowType
    default_finance_type: DefaultFinanceType
    default_aid_type: List[DefaultAidType]
    default_tied_status: DefaultTiedStatus

    budget: List[Budget]

    planned_disbursement: List[PlannedDisbursement]
    capital_spend: Optional[CapitalSpend]
    transaction: List[Transaction]
    document_link: List[DocumentLink]
    related_activity: List[RelatedActivity]
    legacy_data: Optional[List[LegacyData]]
    conditions: Conditions
    result: List[Result]

    crs_add: Optional[CrsAdd]
    fss: Optional[ForwardSpendingSurvey]


class IatiActivities(XmlBaseModel):
    generated_datetime: datetime
    version: IatiVersionEnum
    linked_data_default: Optional[HttpUrl]

    iati_activity: List[IatiActivity]
