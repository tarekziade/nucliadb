# Copyright (C) 2021 Bosutech XXI S.L.
#
# nucliadb is offered under the AGPL v3.0 and as commercial software.
# For commercial licensing, contact us at info@nuclia.com.
#
# AGPL:
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar, Union

from google.protobuf.json_format import MessageToDict
from nucliadb_protos.audit_pb2 import ClientType
from nucliadb_protos.nodereader_pb2 import DocumentScored, OrderBy
from nucliadb_protos.nodereader_pb2 import ParagraphResult as PBParagraphResult
from nucliadb_protos.utils_pb2 import RelationNode
from nucliadb_protos.writer_pb2 import ShardObject as PBShardObject
from nucliadb_protos.writer_pb2 import Shards as PBShards
from pydantic import BaseModel, Field, validator

from nucliadb_models.common import FieldTypeName, ParamDefault
from nucliadb_models.metadata import RelationType
from nucliadb_models.resource import ExtractedDataTypeName, Resource
from nucliadb_models.vectors import VectorSimilarity

_T = TypeVar("_T")


class ModelParamDefaults:
    applied_autofilters = ParamDefault(
        default=[],
        title="Autofilters",
        description="List of filters automatically applied to the search query",
    )


class ResourceProperties(str, Enum):
    BASIC = "basic"
    ORIGIN = "origin"
    EXTRA = "extra"
    RELATIONS = "relations"
    VALUES = "values"
    EXTRACTED = "extracted"
    ERRORS = "errors"


class SearchOptions(str, Enum):
    PARAGRAPH = "paragraph"
    DOCUMENT = "document"
    RELATIONS = "relations"
    VECTOR = "vector"


class ChatOptions(str, Enum):
    PARAGRAPHS = "paragraphs"
    RELATIONS = "relations"


class SuggestOptions(str, Enum):
    PARAGRAPH = "paragraph"
    ENTITIES = "entities"
    INTENT = "intent"


class NucliaDBClientType(str, Enum):
    API = "api"
    WIDGET = "widget"
    WEB = "web"
    DASHBOARD = "dashboard"
    DESKTOP = "desktop"
    CHROME_EXTENSION = "chrome_extension"

    def to_proto(self) -> int:
        return ClientType.Value(self.name)


class Sort(int, Enum):
    DESC = 0
    ASC = 1


class Facet(BaseModel):
    facetresults: Dict[str, int]


FacetsResult = Dict[str, Any]


class TextPosition(BaseModel):
    page_number: Optional[int]
    index: int
    start: int
    end: int
    start_seconds: Optional[List[int]] = None
    end_seconds: Optional[List[int]] = None


class Sentence(BaseModel):
    score: float
    rid: str
    text: str
    field_type: str
    field: str
    index: Optional[str] = None
    position: Optional[TextPosition] = None


class Sentences(BaseModel):
    results: List[Sentence] = []
    facets: FacetsResult
    page_number: int = 0
    page_size: int = 20


class Paragraph(BaseModel):
    score: float
    rid: str
    field_type: str
    field: str
    text: str
    labels: List[str] = []
    start_seconds: Optional[List[int]] = None
    end_seconds: Optional[List[int]] = None
    position: Optional[TextPosition] = None


class Paragraphs(BaseModel):
    results: List[Paragraph] = []
    facets: Optional[FacetsResult] = None
    query: Optional[str] = None
    total: int = 0
    page_number: int = 0
    page_size: int = 20
    next_page: bool = False


class ResourceResult(BaseModel):
    score: Union[float, int]
    rid: str
    field_type: str
    field: str


class Resources(BaseModel):
    results: List[ResourceResult]
    facets: Optional[FacetsResult] = None
    query: Optional[str] = None
    total: int = 0
    page_number: int = 0
    page_size: int = 20
    next_page: bool = False


class RelationDirection(str, Enum):
    IN = "in"
    OUT = "out"


class EntityType(str, Enum):
    ENTITY = "entity"
    LABEL = "label"
    RESOURCE = "resource"
    USER = "user"


RelationNodeTypeMap = {
    RelationNode.NodeType.ENTITY: EntityType.ENTITY,
    RelationNode.NodeType.LABEL: EntityType.LABEL,
    RelationNode.NodeType.RESOURCE: EntityType.RESOURCE,
    RelationNode.NodeType.USER: EntityType.USER,
}


class DirectionalRelation(BaseModel):
    entity: str
    entity_type: EntityType
    relation: RelationType
    relation_label: str
    direction: RelationDirection


class EntitySubgraph(BaseModel):
    related_to: List[DirectionalRelation]


# TODO: uncomment and implement (next iteration)
# class RelationPath(BaseModel):
#     origin: str
#     destination: str
#     path: List[DirectionalRelation]


class Relations(BaseModel):
    entities: Dict[str, EntitySubgraph]
    # TODO: implement in the next iteration of knowledge graph search
    # graph: List[RelationPath]


class RelatedEntities(BaseModel):
    total: int = 0
    entities: List[str] = []


class ResourceSearchResults(BaseModel):
    """Search on resource results"""

    sentences: Optional[Sentences] = None
    paragraphs: Optional[Paragraphs] = None
    relations: Optional[Relations] = None
    nodes: Optional[List[Tuple[str, str, str]]]
    shards: Optional[List[str]]


class KnowledgeboxSearchResults(BaseModel):
    """Search on knowledgebox results"""

    resources: Dict[str, Resource] = {}
    sentences: Optional[Sentences] = None
    paragraphs: Optional[Paragraphs] = None
    fulltext: Optional[Resources] = None
    relations: Optional[Relations] = None
    nodes: Optional[List[Tuple[str, str, str]]]
    shards: Optional[List[str]]
    autofilters: List[str] = ModelParamDefaults.applied_autofilters.to_pydantic_field()


class KnowledgeboxSuggestResults(BaseModel):
    """Suggest on resource results"""

    paragraphs: Optional[Paragraphs] = None
    entities: Optional[RelatedEntities] = None
    shards: Optional[List[str]]


class KnowledgeboxCounters(BaseModel):
    resources: int
    paragraphs: int
    fields: int
    sentences: int
    shards: Optional[List[str]]


class SortField(str, Enum):
    SCORE = "score"
    CREATED = "created"
    MODIFIED = "modified"
    TITLE = "title"


SortFieldMap = {
    SortField.SCORE: None,
    SortField.CREATED: OrderBy.OrderField.CREATED,
    SortField.MODIFIED: OrderBy.OrderField.MODIFIED,
    SortField.TITLE: None,
}


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


SortOrderMap = {
    SortOrder.ASC: Sort.ASC,
    SortOrder.DESC: Sort.DESC,
}


class SortOptions(BaseModel):
    field: SortField
    limit: Optional[int] = Field(None, gt=0)
    order: SortOrder = SortOrder.DESC


class KnowledgeBoxCount(BaseModel):
    paragraphs: int
    fields: int
    sentences: int


class DocumentServiceEnum(str, Enum):
    DOCUMENT_V0 = "DOCUMENT_V0"
    DOCUMENT_V1 = "DOCUMENT_V1"


class ParagraphServiceEnum(str, Enum):
    PARAGRAPH_V0 = "PARAGRAPH_V0"
    PARAGRAPH_V1 = "PARAGRAPH_V1"


class VectorServiceEnum(str, Enum):
    VECTOR_V0 = "VECTOR_V0"
    VECTOR_V1 = "VECTOR_V1"


class RelationServiceEnum(str, Enum):
    RELATION_V0 = "RELATION_V0"
    RELATION_V1 = "RELATION_V1"


class ShardCreated(BaseModel):
    id: str
    document_service: DocumentServiceEnum
    paragraph_service: ParagraphServiceEnum
    vector_service: VectorServiceEnum
    relation_service: RelationServiceEnum


class ShardReplica(BaseModel):
    node: str
    shard: ShardCreated


class ShardObject(BaseModel):
    shard: str
    replicas: List[ShardReplica]

    @classmethod
    def from_message(cls: Type[_T], message: PBShardObject) -> _T:
        return cls(
            **MessageToDict(
                message,
                preserving_proto_field_name=True,
                including_default_value_fields=True,
            )
        )


class KnowledgeboxShards(BaseModel):
    kbid: str
    actual: int
    similarity: VectorSimilarity
    shards: List[ShardObject]

    @classmethod
    def from_message(cls: Type[_T], message: PBShards) -> _T:
        as_dict = MessageToDict(
            message,
            preserving_proto_field_name=True,
            including_default_value_fields=True,
        )
        as_dict["similarity"] = VectorSimilarity.from_message(message.similarity)
        return cls(**as_dict)


class SearchParamDefaults:
    query = ParamDefault(
        default="", title="Query", description="The query to search for"
    )
    suggest_query = ParamDefault(
        default=..., title="Query", description="The query to get suggestions for"
    )
    advanced_query = ParamDefault(
        default=None,
        title="Advanced query",
        description="An advanced query to search for. See https://docs.nuclia.dev/docs/query/#advanced-query for examples of advanced queries syntax.",  # noqa: E501
    )
    fields = ParamDefault(
        default=[],
        title="Fields",
        description="The list of fields to search in. For instance: `a/title` to search only on title field. For more details on filtering by field, see: https://docs.nuclia.dev/docs/query/#search-in-a-specific-field",  # noqa: E501
    )
    filters = ParamDefault(
        default=[],
        title="Filters",
        description="The list of filters to apply. Filtering examples can be found here: https://docs.nuclia.dev/docs/query/#filters",  # noqa: E501
    )
    faceted = ParamDefault(
        default=[],
        title="Faceted",
        description="The list of facets to calculate. The facets follow the same syntax as filters: https://docs.nuclia.dev/docs/query/#filters",  # noqa: E501
    )
    min_score = ParamDefault(
        default=0.70,
        title="Minimum result score",
        description="The minimum score to consider a result as valid. Results with a score lower than this value will not be returned",  # noqa: E501
    )
    autofilter = ParamDefault(
        default=False,
        title="Automatic search filtering",
        description="If set to true, the search will automatically add filters to the query. For example, it will filter results containing the entities detected in the query",  # noqa: E501
    )
    chat_query = ParamDefault(
        default=...,
        title="Query",
        description="The query to get a generative answer for",
    )
    shards = ParamDefault(
        default=[],
        title="Shards",
        description="The list of shards to search in. If empty, all shards will be searched",
    )
    page_number = ParamDefault(
        default=0,
        title="Page number",
        description="The page number of the results to return",
    )
    page_size = ParamDefault(
        default=20,
        title="Page size",
        description="The number of results to return per page",
    )
    highlight = ParamDefault(
        default=False,
        title="Highlight",
        description="If set to true, the query terms will be highlighted in the results between <mark>...</mark> tags",  # noqa: E501
    )
    with_duplicates = ParamDefault(
        default=False,
        title="With duplicate paragraphs",
        description="Whether to return duplicate paragraphs on the same document",  # noqa: E501
    )
    with_status = ParamDefault(
        default=None,
        title="With processing status",
        description="Filter results by resource processing status",
    )
    with_synonyms = ParamDefault(
        default=False,
        title="With custom synonyms",
        description="Whether to return matches for custom knowledge box synonyms of the query terms. Note: only supported for `paragraph` and `document` search options.",  # noqa: E501
    )
    sort_order = ParamDefault(
        default=SortOrder.DESC,
        title="Sort order",
        description="Order to sort results with",
    )
    sort_limit = ParamDefault(
        default=None,
        title="Sort limit",
        description="",
        gt=0,
    )
    sort_field = ParamDefault(
        default=None,
        title="Sort field",
        description="Field to sort results with",
    )
    sort = ParamDefault(
        default=None,
        title="Sort options",
        description="Options for results sorting",
    )
    search_features = ParamDefault(
        default=None,
        title="Search features",
        description="List of search features to use. Each value corresponds to a lookup into on of the different indexes.",  # noqa
    )
    debug = ParamDefault(
        default=False,
        title="Debug mode",
        description="If set, the response will include some extra metadata for debugging purposes, like the list of queried nodes.",  # noqa
    )
    show = ParamDefault(
        default=[ResourceProperties.BASIC],
        title="Show metadata",
        description="Controls which types of metadata are serialized on resources of search results",
    )
    extracted = ParamDefault(
        default=list(ExtractedDataTypeName),
        title="Extracted metadata",
        description="Controls which parts of the extracted metadata are serialized on search results",
    )
    field_type_filter = ParamDefault(
        default=list(FieldTypeName),
        title="Field type filter",
        description="Filter search results to match paragraphs of a specific field type. E.g: `['conversation', 'text']`",  # noqa
    )
    range_creation_start = ParamDefault(
        default=None,
        title="Resource creation range start",
        description="Resources created before this date will be filtered out of search results. Datetime are represented as a str in ISO 8601 format, like: 2008-09-15T15:53:00+05:00.",  # noqa
    )
    range_creation_end = ParamDefault(
        default=None,
        title="Resource creation range end",
        description="Resources created after this date will be filtered out of search results. Datetime are represented as a str in ISO 8601 format, like: 2008-09-15T15:53:00+05:00.",  # noqa
    )
    range_modification_start = ParamDefault(
        default=None,
        title="Resource modification range start",
        description="Resources modified before this date will be filtered out of search results. Datetime are represented as a str in ISO 8601 format, like: 2008-09-15T15:53:00+05:00.",  # noqa
    )
    range_modification_end = ParamDefault(
        default=None,
        title="Resource modification range end",
        description="Resources modified after this date will be filtered out of search results. Datetime are represented as a str in ISO 8601 format, like: 2008-09-15T15:53:00+05:00.",  # noqa
    )
    vector = ParamDefault(
        default=None,
        title="Search Vector",
        description="The vector to perform the search with. If not provided, NucliaDB will use Nuclia Predict API to create the vector off from the query.",  # noqa
    )
    vectorset = ParamDefault(
        default=None,
        title="Vectorset id",
        description="Id of the vectorset to perform the vector search into.",
    )
    chat_context = ParamDefault(
        default=None,
        title="Chat context",
        description="Use to control the context that is passed as input to the Generative AI model. If not specified, it is generated automatically.",  # noqa
    )

    chat_features = ParamDefault(
        default=[ChatOptions.PARAGRAPHS, ChatOptions.RELATIONS],
        title="Chat features",
        description="Features enabled for the chat endpoint. If `paragraphs` is included, the paragraphs from which the answer is generated are returned. If `relations` is included, a graph of entities related to the answer is returned.",  # noqa
    )
    suggest_features = ParamDefault(
        default=[
            SuggestOptions.PARAGRAPH,
            SuggestOptions.ENTITIES,
            SuggestOptions.INTENT,
        ],
        title="Suggest features",
        description="Features enabled for the suggest endpoint.",
    )


class BaseSearchRequest(BaseModel):
    query: str = SearchParamDefaults.query.to_pydantic_field()
    advanced_query: Optional[
        str
    ] = SearchParamDefaults.advanced_query.to_pydantic_field()
    fields: List[str] = SearchParamDefaults.fields.to_pydantic_field()
    filters: List[str] = SearchParamDefaults.filters.to_pydantic_field()
    faceted: List[str] = SearchParamDefaults.faceted.to_pydantic_field()
    page_number: int = SearchParamDefaults.page_number.to_pydantic_field()
    page_size: int = SearchParamDefaults.page_size.to_pydantic_field()
    min_score: float = SearchParamDefaults.min_score.to_pydantic_field()
    range_creation_start: Optional[
        datetime
    ] = SearchParamDefaults.range_creation_start.to_pydantic_field()
    range_creation_end: Optional[
        datetime
    ] = SearchParamDefaults.range_creation_end.to_pydantic_field()
    range_modification_start: Optional[
        datetime
    ] = SearchParamDefaults.range_modification_start.to_pydantic_field()
    range_modification_end: Optional[
        datetime
    ] = SearchParamDefaults.range_modification_end.to_pydantic_field()
    features: List[
        SearchOptions
    ] = SearchParamDefaults.search_features.to_pydantic_field(
        default=[
            SearchOptions.PARAGRAPH,
            SearchOptions.DOCUMENT,
            SearchOptions.VECTOR,
        ]
    )
    reload: bool = True
    debug: bool = SearchParamDefaults.debug.to_pydantic_field()
    highlight: bool = SearchParamDefaults.highlight.to_pydantic_field()
    show: List[ResourceProperties] = SearchParamDefaults.show.to_pydantic_field()
    field_type_filter: List[
        FieldTypeName
    ] = SearchParamDefaults.field_type_filter.to_pydantic_field()
    extracted: List[
        ExtractedDataTypeName
    ] = SearchParamDefaults.extracted.to_pydantic_field()
    shards: List[str] = SearchParamDefaults.shards.to_pydantic_field()
    vector: Optional[List[float]] = SearchParamDefaults.vector.to_pydantic_field()
    vectorset: Optional[str] = SearchParamDefaults.vectorset.to_pydantic_field()
    with_duplicates: bool = SearchParamDefaults.with_duplicates.to_pydantic_field()
    with_synonyms: bool = SearchParamDefaults.with_synonyms.to_pydantic_field()
    autofilter: bool = SearchParamDefaults.autofilter.to_pydantic_field()


class SearchRequest(BaseSearchRequest):
    sort: Optional[SortOptions] = SearchParamDefaults.sort.to_pydantic_field()


class Author(str, Enum):
    NUCLIA = "NUCLIA"
    USER = "USER"


class Message(BaseModel):
    author: Author
    text: str


class ChatModel(BaseModel):
    question: str
    user_id: str
    retrieval: bool = True
    system: Optional[str] = None
    context: List[Message] = []


class RephraseModel(BaseModel):
    question: str
    context: List[Message] = []
    user_id: str


class ChatRequest(BaseModel):
    query: str = SearchParamDefaults.chat_query.to_pydantic_field()
    fields: List[str] = SearchParamDefaults.fields.to_pydantic_field()
    filters: List[str] = SearchParamDefaults.filters.to_pydantic_field()
    min_score: float = SearchParamDefaults.min_score.to_pydantic_field()
    features: List[ChatOptions] = SearchParamDefaults.chat_features.to_pydantic_field()
    range_creation_start: Optional[
        datetime
    ] = SearchParamDefaults.range_creation_start.to_pydantic_field()
    range_creation_end: Optional[
        datetime
    ] = SearchParamDefaults.range_creation_end.to_pydantic_field()
    range_modification_start: Optional[
        datetime
    ] = SearchParamDefaults.range_modification_start.to_pydantic_field()
    range_modification_end: Optional[
        datetime
    ] = SearchParamDefaults.range_modification_end.to_pydantic_field()
    show: List[ResourceProperties] = SearchParamDefaults.show.to_pydantic_field()
    field_type_filter: List[
        FieldTypeName
    ] = SearchParamDefaults.field_type_filter.to_pydantic_field()
    extracted: List[
        ExtractedDataTypeName
    ] = SearchParamDefaults.extracted.to_pydantic_field()
    shards: List[str] = SearchParamDefaults.shards.to_pydantic_field()
    context: Optional[
        List[Message]
    ] = SearchParamDefaults.chat_context.to_pydantic_field()
    autofilter: bool = SearchParamDefaults.autofilter.to_pydantic_field()
    highlight: bool = SearchParamDefaults.highlight.to_pydantic_field()


class FindRequest(BaseSearchRequest):
    features: List[
        SearchOptions
    ] = SearchParamDefaults.search_features.to_pydantic_field(
        default=[
            SearchOptions.PARAGRAPH,
            SearchOptions.VECTOR,
        ]
    )

    @validator("features")
    def fulltext_not_supported(cls, v):
        if SearchOptions.DOCUMENT in v or SearchOptions.DOCUMENT == v:
            raise ValueError("fulltext search not supported")
        return v


class SCORE_TYPE(str, Enum):
    VECTOR = "VECTOR"
    BM25 = "BM25"
    BOTH = "BOTH"


class FindTextPosition(BaseModel):
    page_number: Optional[int]
    start_seconds: Optional[List[int]] = None
    end_seconds: Optional[List[int]] = None
    index: int
    start: int
    end: int


class FindParagraph(BaseModel):
    score: float
    score_type: SCORE_TYPE
    order: int = Field(0, ge=0)
    text: str
    id: str
    labels: Optional[List[str]] = []
    position: Optional[TextPosition] = None


@dataclass
class TempFindParagraph:
    rid: str
    field: str
    score: float
    start: int
    end: int
    id: str
    split: Optional[str] = None
    paragraph: Optional[FindParagraph] = None
    vector_index: Optional[DocumentScored] = None
    paragraph_index: Optional[PBParagraphResult] = None


class FindField(BaseModel):
    paragraphs: Dict[str, FindParagraph]


class FindResource(Resource):
    fields: Dict[str, FindField]

    def updated_from(self, origin: Resource):
        for key in origin.__fields__.keys():
            self.__setattr__(key, getattr(origin, key))


class KnowledgeboxFindResults(BaseModel):
    """Find on knowledgebox results"""

    resources: Dict[str, FindResource]
    relations: Optional[Relations] = None
    facets: FacetsResult
    query: Optional[str] = None
    total: int = 0
    page_number: int = 0
    page_size: int = 20
    next_page: bool = False
    nodes: Optional[List[Tuple[str, str, str]]]
    shards: Optional[List[str]]
    autofilters: List[str] = ModelParamDefaults.applied_autofilters.to_pydantic_field()


class FeedbackTasks(str, Enum):
    CHAT = "CHAT"


class FeedbackRequest(BaseModel):
    ident: str
    good: bool
    task: FeedbackTasks
    feedback: Optional[str]
