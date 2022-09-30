"""
@generated by mypy-protobuf.  Do not edit manually!
isort:skip_file
"""
import abc
import collections.abc
import grpc
import nucliadb_protos.knowledgebox_pb2
import nucliadb_protos.writer_pb2
from nucliadb_protos.knowledgebox_pb2 import (
    CONFLICT as CONFLICT,
    DeleteKnowledgeBoxResponse as DeleteKnowledgeBoxResponse,
    ERROR as ERROR,
    EntitiesGroup as EntitiesGroup,
    Entity as Entity,
    GCKnowledgeBoxResponse as GCKnowledgeBoxResponse,
    KnowledgeBox as KnowledgeBox,
    KnowledgeBoxConfig as KnowledgeBoxConfig,
    KnowledgeBoxID as KnowledgeBoxID,
    KnowledgeBoxNew as KnowledgeBoxNew,
    KnowledgeBoxPrefix as KnowledgeBoxPrefix,
    KnowledgeBoxResponseStatus as KnowledgeBoxResponseStatus,
    KnowledgeBoxUpdate as KnowledgeBoxUpdate,
    Label as Label,
    LabelSet as LabelSet,
    Labels as Labels,
    NOTFOUND as NOTFOUND,
    NewKnowledgeBoxResponse as NewKnowledgeBoxResponse,
    OK as OK,
    UpdateKnowledgeBoxResponse as UpdateKnowledgeBoxResponse,
    Widget as Widget,
)
from nucliadb_protos.noderesources_pb2 import (
    EmptyQuery as EmptyQuery,
    EmptyResponse as EmptyResponse,
    IndexMetadata as IndexMetadata,
    IndexParagraph as IndexParagraph,
    IndexParagraphs as IndexParagraphs,
    Resource as Resource,
    ResourceID as ResourceID,
    Shard as Shard,
    ShardCreated as ShardCreated,
    ShardId as ShardId,
    ShardIds as ShardIds,
    ShardList as ShardList,
    TextInformation as TextInformation,
    VectorSentence as VectorSentence,
)
from nucliadb_protos.resources_pb2 import (
    Basic as Basic,
    Block as Block,
    CONVERSATION as CONVERSATION,
    Classification as Classification,
    CloudFile as CloudFile,
    Conversation as Conversation,
    DATETIME as DATETIME,
    Entity as Entity,
    ExtractedTextWrapper as ExtractedTextWrapper,
    ExtractedVectorsWrapper as ExtractedVectorsWrapper,
    FILE as FILE,
    FieldComputedMetadata as FieldComputedMetadata,
    FieldComputedMetadataWrapper as FieldComputedMetadataWrapper,
    FieldConversation as FieldConversation,
    FieldDatetime as FieldDatetime,
    FieldFile as FieldFile,
    FieldID as FieldID,
    FieldKeywordset as FieldKeywordset,
    FieldLargeMetadata as FieldLargeMetadata,
    FieldLayout as FieldLayout,
    FieldLink as FieldLink,
    FieldMetadata as FieldMetadata,
    FieldText as FieldText,
    FieldType as FieldType,
    FileExtractedData as FileExtractedData,
    FilePages as FilePages,
    GENERIC as GENERIC,
    KEYWORDSET as KEYWORDSET,
    Keyword as Keyword,
    LAYOUT as LAYOUT,
    LINK as LINK,
    LargeComputedMetadata as LargeComputedMetadata,
    LargeComputedMetadataWrapper as LargeComputedMetadataWrapper,
    LayoutContent as LayoutContent,
    LinkExtractedData as LinkExtractedData,
    Message as Message,
    MessageContent as MessageContent,
    Metadata as Metadata,
    NestedPosition as NestedPosition,
    Origin as Origin,
    PagePositions as PagePositions,
    Paragraph as Paragraph,
    ParagraphAnnotation as ParagraphAnnotation,
    Relations as Relations,
    RowsPreview as RowsPreview,
    Sentence as Sentence,
    TEXT as TEXT,
    TokenSplit as TokenSplit,
    UserFieldMetadata as UserFieldMetadata,
    UserMetadata as UserMetadata,
)

class WriterStub:
    def __init__(self, channel: grpc.Channel) -> None: ...
    GetKnowledgeBox: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.knowledgebox_pb2.KnowledgeBoxID,
        nucliadb_protos.knowledgebox_pb2.KnowledgeBox,
    ]
    NewKnowledgeBox: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.knowledgebox_pb2.KnowledgeBoxNew,
        nucliadb_protos.knowledgebox_pb2.NewKnowledgeBoxResponse,
    ]
    DeleteKnowledgeBox: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.knowledgebox_pb2.KnowledgeBoxID,
        nucliadb_protos.knowledgebox_pb2.DeleteKnowledgeBoxResponse,
    ]
    UpdateKnowledgeBox: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.knowledgebox_pb2.KnowledgeBoxUpdate,
        nucliadb_protos.knowledgebox_pb2.UpdateKnowledgeBoxResponse,
    ]
    ListKnowledgeBox: grpc.UnaryStreamMultiCallable[
        nucliadb_protos.knowledgebox_pb2.KnowledgeBoxPrefix,
        nucliadb_protos.knowledgebox_pb2.KnowledgeBoxID,
    ]
    GCKnowledgeBox: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.knowledgebox_pb2.KnowledgeBoxID,
        nucliadb_protos.knowledgebox_pb2.GCKnowledgeBoxResponse,
    ]
    ResourceFieldExists: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.writer_pb2.ResourceFieldId,
        nucliadb_protos.writer_pb2.ResourceFieldExistsResponse,
    ]
    ProcessMessage: grpc.StreamUnaryMultiCallable[
        nucliadb_protos.writer_pb2.BrokerMessage,
        nucliadb_protos.writer_pb2.OpStatusWriter,
    ]
    GetLabels: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.writer_pb2.GetLabelsRequest,
        nucliadb_protos.writer_pb2.GetLabelsResponse,
    ]
    """Labels"""
    GetLabelSet: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.writer_pb2.GetLabelSetRequest,
        nucliadb_protos.writer_pb2.GetLabelSetResponse,
    ]
    SetLabels: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.writer_pb2.SetLabelsRequest,
        nucliadb_protos.writer_pb2.OpStatusWriter,
    ]
    DelLabels: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.writer_pb2.DelLabelsRequest,
        nucliadb_protos.writer_pb2.OpStatusWriter,
    ]
    GetEntities: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.writer_pb2.GetEntitiesRequest,
        nucliadb_protos.writer_pb2.GetEntitiesResponse,
    ]
    """Entities"""
    GetEntitiesGroup: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.writer_pb2.GetEntitiesGroupRequest,
        nucliadb_protos.writer_pb2.GetEntitiesGroupResponse,
    ]
    SetEntities: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.writer_pb2.SetEntitiesRequest,
        nucliadb_protos.writer_pb2.OpStatusWriter,
    ]
    DelEntities: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.writer_pb2.DelEntitiesRequest,
        nucliadb_protos.writer_pb2.OpStatusWriter,
    ]
    GetWidget: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.writer_pb2.GetWidgetRequest,
        nucliadb_protos.writer_pb2.GetWidgetResponse,
    ]
    """Widgets"""
    GetWidgets: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.writer_pb2.GetWidgetsRequest,
        nucliadb_protos.writer_pb2.GetWidgetsResponse,
    ]
    SetWidgets: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.writer_pb2.SetWidgetsRequest,
        nucliadb_protos.writer_pb2.OpStatusWriter,
    ]
    DelWidgets: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.writer_pb2.DetWidgetsRequest,
        nucliadb_protos.writer_pb2.OpStatusWriter,
    ]
    Status: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.writer_pb2.WriterStatusRequest,
        nucliadb_protos.writer_pb2.WriterStatusResponse,
    ]
    ListMembers: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.writer_pb2.ListMembersRequest,
        nucliadb_protos.writer_pb2.ListMembersResponse,
    ]
    Index: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.writer_pb2.IndexResource,
        nucliadb_protos.writer_pb2.IndexStatus,
    ]
    ReIndex: grpc.UnaryUnaryMultiCallable[
        nucliadb_protos.writer_pb2.IndexResource,
        nucliadb_protos.writer_pb2.IndexStatus,
    ]
    Export: grpc.UnaryStreamMultiCallable[
        nucliadb_protos.writer_pb2.ExportRequest,
        nucliadb_protos.writer_pb2.BrokerMessage,
    ]

class WriterServicer(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def GetKnowledgeBox(
        self,
        request: nucliadb_protos.knowledgebox_pb2.KnowledgeBoxID,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.knowledgebox_pb2.KnowledgeBox: ...
    @abc.abstractmethod
    def NewKnowledgeBox(
        self,
        request: nucliadb_protos.knowledgebox_pb2.KnowledgeBoxNew,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.knowledgebox_pb2.NewKnowledgeBoxResponse: ...
    @abc.abstractmethod
    def DeleteKnowledgeBox(
        self,
        request: nucliadb_protos.knowledgebox_pb2.KnowledgeBoxID,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.knowledgebox_pb2.DeleteKnowledgeBoxResponse: ...
    @abc.abstractmethod
    def UpdateKnowledgeBox(
        self,
        request: nucliadb_protos.knowledgebox_pb2.KnowledgeBoxUpdate,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.knowledgebox_pb2.UpdateKnowledgeBoxResponse: ...
    @abc.abstractmethod
    def ListKnowledgeBox(
        self,
        request: nucliadb_protos.knowledgebox_pb2.KnowledgeBoxPrefix,
        context: grpc.ServicerContext,
    ) -> collections.abc.Iterator[nucliadb_protos.knowledgebox_pb2.KnowledgeBoxID]: ...
    @abc.abstractmethod
    def GCKnowledgeBox(
        self,
        request: nucliadb_protos.knowledgebox_pb2.KnowledgeBoxID,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.knowledgebox_pb2.GCKnowledgeBoxResponse: ...
    @abc.abstractmethod
    def ResourceFieldExists(
        self,
        request: nucliadb_protos.writer_pb2.ResourceFieldId,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.writer_pb2.ResourceFieldExistsResponse: ...
    @abc.abstractmethod
    def ProcessMessage(
        self,
        request_iterator: collections.abc.Iterator[nucliadb_protos.writer_pb2.BrokerMessage],
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.writer_pb2.OpStatusWriter: ...
    @abc.abstractmethod
    def GetLabels(
        self,
        request: nucliadb_protos.writer_pb2.GetLabelsRequest,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.writer_pb2.GetLabelsResponse:
        """Labels"""
    @abc.abstractmethod
    def GetLabelSet(
        self,
        request: nucliadb_protos.writer_pb2.GetLabelSetRequest,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.writer_pb2.GetLabelSetResponse: ...
    @abc.abstractmethod
    def SetLabels(
        self,
        request: nucliadb_protos.writer_pb2.SetLabelsRequest,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.writer_pb2.OpStatusWriter: ...
    @abc.abstractmethod
    def DelLabels(
        self,
        request: nucliadb_protos.writer_pb2.DelLabelsRequest,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.writer_pb2.OpStatusWriter: ...
    @abc.abstractmethod
    def GetEntities(
        self,
        request: nucliadb_protos.writer_pb2.GetEntitiesRequest,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.writer_pb2.GetEntitiesResponse:
        """Entities"""
    @abc.abstractmethod
    def GetEntitiesGroup(
        self,
        request: nucliadb_protos.writer_pb2.GetEntitiesGroupRequest,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.writer_pb2.GetEntitiesGroupResponse: ...
    @abc.abstractmethod
    def SetEntities(
        self,
        request: nucliadb_protos.writer_pb2.SetEntitiesRequest,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.writer_pb2.OpStatusWriter: ...
    @abc.abstractmethod
    def DelEntities(
        self,
        request: nucliadb_protos.writer_pb2.DelEntitiesRequest,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.writer_pb2.OpStatusWriter: ...
    @abc.abstractmethod
    def GetWidget(
        self,
        request: nucliadb_protos.writer_pb2.GetWidgetRequest,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.writer_pb2.GetWidgetResponse:
        """Widgets"""
    @abc.abstractmethod
    def GetWidgets(
        self,
        request: nucliadb_protos.writer_pb2.GetWidgetsRequest,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.writer_pb2.GetWidgetsResponse: ...
    @abc.abstractmethod
    def SetWidgets(
        self,
        request: nucliadb_protos.writer_pb2.SetWidgetsRequest,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.writer_pb2.OpStatusWriter: ...
    @abc.abstractmethod
    def DelWidgets(
        self,
        request: nucliadb_protos.writer_pb2.DetWidgetsRequest,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.writer_pb2.OpStatusWriter: ...
    @abc.abstractmethod
    def Status(
        self,
        request: nucliadb_protos.writer_pb2.WriterStatusRequest,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.writer_pb2.WriterStatusResponse: ...
    @abc.abstractmethod
    def ListMembers(
        self,
        request: nucliadb_protos.writer_pb2.ListMembersRequest,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.writer_pb2.ListMembersResponse: ...
    @abc.abstractmethod
    def Index(
        self,
        request: nucliadb_protos.writer_pb2.IndexResource,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.writer_pb2.IndexStatus: ...
    @abc.abstractmethod
    def ReIndex(
        self,
        request: nucliadb_protos.writer_pb2.IndexResource,
        context: grpc.ServicerContext,
    ) -> nucliadb_protos.writer_pb2.IndexStatus: ...
    @abc.abstractmethod
    def Export(
        self,
        request: nucliadb_protos.writer_pb2.ExportRequest,
        context: grpc.ServicerContext,
    ) -> collections.abc.Iterator[nucliadb_protos.writer_pb2.BrokerMessage]: ...

def add_WriterServicer_to_server(servicer: WriterServicer, server: grpc.Server) -> None: ...
