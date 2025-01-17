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
import asyncio
import logging
import random
import uuid
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Optional

from grpc import aio  # type: ignore
from nucliadb_protos.writer_pb2_grpc import WriterStub

from nucliadb.common.maindb.driver import Transaction
from nucliadb.common.maindb.utils import get_driver
from nucliadb_protos import noderesources_pb2, nodewriter_pb2, utils_pb2, writer_pb2
from nucliadb_telemetry import errors
from nucliadb_utils.keys import KB_SHARDS
from nucliadb_utils.utilities import get_indexing, get_storage

from .abc import AbstractIndexNode
from .exceptions import (
    NodeClusterSmall,
    NodeError,
    NodesUnsync,
    ShardNotFound,
    ShardsNotFound,
)
from .index_node import IndexNode
from .settings import settings

logger = logging.getLogger(__name__)

INDEX_NODES: dict[str, AbstractIndexNode] = {}


def get_index_nodes() -> list[AbstractIndexNode]:
    return list(INDEX_NODES.values())


def get_index_node(node_id: str) -> Optional[AbstractIndexNode]:
    return INDEX_NODES.get(node_id)


def add_index_node(node: AbstractIndexNode) -> None:
    INDEX_NODES[node.id] = node


def remove_index_node(node_id: str) -> None:
    INDEX_NODES.pop(node_id, None)


class KBShardManager:
    async def get_shards_by_kbid_inner(self, kbid: str) -> writer_pb2.Shards:
        key = KB_SHARDS.format(kbid=kbid)
        driver = get_driver()
        async with driver.transaction() as txn:
            payload = await txn.get(key)
            if payload is None:
                # could be None because /shards doesn't exist, or beacause the whole KB does not exist.
                # In any case, this should not happen
                raise ShardsNotFound(kbid)

            pb = writer_pb2.Shards()
            pb.ParseFromString(payload)
            return pb

    async def get_shards_by_kbid(self, kbid: str) -> list[writer_pb2.ShardObject]:
        shards = await self.get_shards_by_kbid_inner(kbid)
        return [x for x in shards.shards]

    async def apply_for_all_shards(
        self,
        kbid: str,
        aw: Callable[[AbstractIndexNode, str, str], Awaitable[Any]],
        timeout: float,
    ) -> list[Any]:
        shards = await self.get_shards_by_kbid(kbid)
        ops = []

        for shard_obj in shards:
            node, shard_id, node_id = choose_node(shard_obj)
            if shard_id is None:
                raise ShardNotFound("Fount a node but not a shard")

            ops.append(aw(node, shard_id, node_id))

        try:
            results = await asyncio.wait_for(
                asyncio.gather(*ops, return_exceptions=True),  # type: ignore
                timeout=timeout,
            )
        except asyncio.TimeoutError as exc:
            errors.capture_exception(exc)
            raise NodeError("Node unavailable for operation") from exc

        return results

    async def get_all_shards(
        self, txn: Transaction, kbid: str
    ) -> Optional[writer_pb2.Shards]:
        key = KB_SHARDS.format(kbid=kbid)
        kb_shards_bytes: Optional[bytes] = await txn.get(key)
        if kb_shards_bytes is not None:
            kb_shards = writer_pb2.Shards()
            kb_shards.ParseFromString(kb_shards_bytes)
            return kb_shards
        else:
            return None

    async def get_current_active_shard(
        self, txn: Transaction, kbid: str
    ) -> Optional[writer_pb2.ShardObject]:
        key = KB_SHARDS.format(kbid=kbid)
        kb_shards_bytes: Optional[bytes] = await txn.get(key)
        if kb_shards_bytes is not None:
            kb_shards = writer_pb2.Shards()
            kb_shards.ParseFromString(kb_shards_bytes)
            shard: writer_pb2.ShardObject = kb_shards.shards[kb_shards.actual]
            return shard
        else:
            return None

    async def create_shard_by_kbid(
        self,
        txn: Transaction,
        kbid: str,
        similarity: utils_pb2.VectorSimilarity.ValueType = utils_pb2.VectorSimilarity.COSINE,
    ) -> writer_pb2.ShardObject:
        kb_shards_key = KB_SHARDS.format(kbid=kbid)
        kb_shards: Optional[writer_pb2.Shards] = None
        kb_shards_binary = await txn.get(kb_shards_key)
        if not kb_shards_binary:
            # First logic shard on the index
            kb_shards = writer_pb2.Shards()
            kb_shards.kbid = kbid
            kb_shards.actual = -1
            kb_shards.similarity = similarity
        else:
            # New logic shard on an existing index
            kb_shards = writer_pb2.Shards()
            kb_shards.ParseFromString(kb_shards_binary)

        try:
            existing_kb_nodes = [
                replica.node for shard in kb_shards.shards for replica in shard.replicas
            ]
            node_ids = find_nodes(avoid_nodes=existing_kb_nodes)
        except NodeClusterSmall as err:
            errors.capture_exception(err)
            logger.error(
                f"Shard creation for kbid={kbid} failed: Replication requirements could not be met."
            )
            raise

        sharduuid = uuid.uuid4().hex
        shard = writer_pb2.ShardObject(shard=sharduuid)
        try:
            for node_id in node_ids:
                logger.info(f"Node description: {node_id}")
                node = get_index_node(node_id)
                if node is None:
                    raise NodesUnsync(f"Node {node_id} is not found or not available")
                logger.info(f"Node obj: {node} Shards: {node.shard_count}")
                shard_created = await node.new_shard(
                    kbid, similarity=kb_shards.similarity
                )
                replica = writer_pb2.ShardReplica(node=str(node_id))
                replica.shard.CopyFrom(shard_created)
                shard.replicas.append(replica)
        except Exception as e:
            errors.capture_exception(e)
            logger.error("Error creating new shard")
            await self.rollback_shard(shard)
            raise e

        # Append the created shard and make `actual` point to it.
        kb_shards.shards.append(shard)
        kb_shards.actual += 1

        await txn.set(kb_shards_key, kb_shards.SerializeToString())

        return shard

    async def rollback_shard(self, shard: writer_pb2.ShardObject):
        for shard_replica in shard.replicas:
            node_id = shard_replica.node
            replica_id = shard_replica.shard.id
            node = get_index_node(node_id)
            if node is not None:
                try:
                    await node.delete_shard(replica_id)
                except Exception as rollback_error:
                    errors.capture_exception(rollback_error)
                    logger.error(
                        f"New shard rollback error. Node: {node_id} Shard: {replica_id}"
                    )

    def indexing_replicas(self, shard: writer_pb2.ShardObject) -> list[tuple[str, str]]:
        """
        Returns the replica ids and nodes for the shard replicas
        """
        result = []
        for replica in shard.replicas:
            result.append((replica.shard.id, replica.node))
        return result

    async def delete_resource(
        self,
        shard: writer_pb2.ShardObject,
        uuid: str,
        txid: int,
        partition: str,
        kb: str,
    ) -> None:
        indexing = get_indexing()
        storage = await get_storage()

        await storage.delete_indexing(
            resource_uid=uuid, txid=txid, kb=kb, logical_shard=shard.shard
        )

        for replica_id, node_id in self.indexing_replicas(shard):
            indexpb: nodewriter_pb2.IndexMessage = nodewriter_pb2.IndexMessage()
            indexpb.node = node_id
            indexpb.shard = replica_id
            indexpb.txid = txid
            indexpb.resource = uuid
            indexpb.typemessage = nodewriter_pb2.TypeMessage.DELETION
            indexpb.partition = partition
            indexpb.kbid = kb
            await indexing.index(indexpb, node_id)

    async def add_resource(
        self,
        shard: writer_pb2.ShardObject,
        resource: noderesources_pb2.Resource,
        txid: int,
        partition: str,
        kb: str,
        reindex_id: Optional[str] = None,
    ) -> None:
        if txid == -1 and reindex_id is None:
            # This means we are injecting a complete resource via ingest gRPC
            # outside of a transaction. We need to treat this as a reindex operation.
            reindex_id = uuid.uuid4().hex

        storage = await get_storage()
        indexing = get_indexing()

        indexpb: nodewriter_pb2.IndexMessage

        if reindex_id is not None:
            indexpb = await storage.reindexing(
                resource, reindex_id, partition, kb=kb, logical_shard=shard.shard
            )
        else:
            indexpb = await storage.indexing(
                resource, txid, partition, kb=kb, logical_shard=shard.shard
            )

        for replica_id, node_id in self.indexing_replicas(shard):
            indexpb.node = node_id
            indexpb.shard = replica_id
            await indexing.index(indexpb, node_id)


class StandaloneKBShardManager(KBShardManager):
    async def delete_resource(
        self,
        shard: writer_pb2.ShardObject,
        uuid: str,
        txid: int,
        partition: str,
        kb: str,
    ) -> None:
        req = noderesources_pb2.ResourceID()
        req.uuid = uuid

        for shardreplica in shard.replicas:
            req.shard_id = shardreplica.shard.id
            index_node = get_index_node(shardreplica.node)
            await index_node.writer.RemoveResource(req)  # type: ignore

    async def add_resource(
        self,
        shard: writer_pb2.ShardObject,
        resource: noderesources_pb2.Resource,
        txid: int,
        partition: str,
        kb: str,
        reindex_id: Optional[str] = None,
    ) -> None:
        for shardreplica in shard.replicas:
            resource.shard_id = resource.resource.shard_id = shardreplica.shard.id
            index_node = get_index_node(shardreplica.node)
            if index_node is None:  # pragma: no cover
                raise NodesUnsync(
                    f"Node {shardreplica.node} is not found or not available"
                )
            await index_node.writer.SetResource(resource)  # type: ignore


def setup_standalone_cluster():
    from .standalone.index_node import StandaloneIndexNode

    inode = StandaloneIndexNode(
        # "LOCAL NODE" is the name of the node for all shards
        # that have been created in standalone mode so far.
        # When we switch to supporting clustering in standalone,
        # we will need to generate a unique name for each node and update this
        id="LOCAL NODE",
        address="localhost",
        shard_count=0,
    )
    INDEX_NODES[inode.id] = inode


def choose_node(
    shard: writer_pb2.ShardObject, shard_replicas: Optional[list[str]] = None
) -> tuple[AbstractIndexNode, str, str]:
    """
    Choose an arbitrary node storing `shard`. If passed, choose only between
    nodes containing any of `shard_replicas`.
    """
    shard_replicas = shard_replicas or []
    nodes = [x for x in range(len(shard.replicas))]
    random.shuffle(nodes)
    node_obj = None
    shard_id = None
    for node in nodes:
        node_id = shard.replicas[node].node
        node_obj = get_index_node(node_id)
        if node_obj is not None:
            shard_id = shard.replicas[node].shard.id
            if len(shard_replicas) > 0 and shard_id not in shard_replicas:
                node_obj = None
                shard_id = None
            else:
                break

    if node_obj is None or node_id is None or shard_id is None:
        raise KeyError("Could not find a node to query")

    return node_obj, shard_id, node_id


@dataclass
class ScoredNode:
    id: str
    shard_count: int


def find_nodes(avoid_nodes: Optional[list[str]] = None) -> list[str]:
    """
    Returns a list of node ids sorted by increasing shard count and load score.
    It will avoid the node ids in `avoid_nodes` from the computation if possible.
    It raises an exception if it can't find enough nodes for the configured replicas.
    """
    target_replicas = settings.node_replicas
    available_nodes = [
        ScoredNode(id=node.id, shard_count=node.shard_count)
        for node in get_index_nodes()
    ]
    if len(available_nodes) < target_replicas:
        raise NodeClusterSmall(
            f"Not enough nodes. Total: {len(available_nodes)}, Required: {target_replicas}"
        )

    if settings.max_node_replicas >= 0:
        available_nodes = list(
            filter(
                lambda x: x.shard_count < settings.max_node_replicas, available_nodes  # type: ignore
            )
        )
        if len(available_nodes) < target_replicas:
            raise NodeClusterSmall(
                f"Could not find enough nodes with available shards. Available: {len(available_nodes)}, Required: {target_replicas}"  # noqa
            )

    # Sort available nodes by increasing shard_count
    sorted_nodes = sorted(available_nodes, key=lambda x: x.shard_count)
    available_node_ids = [node.id for node in sorted_nodes]

    avoid_nodes = avoid_nodes or []
    # get preferred nodes first
    preferred_nodes = [nid for nid in available_node_ids if nid not in avoid_nodes]
    # now, add to the end of the last nodes
    preferred_node_order = preferred_nodes + [
        nid for nid in available_node_ids if nid not in preferred_nodes
    ]

    return preferred_node_order[:target_replicas]


async def load_active_nodes():
    from nucliadb_utils.settings import nucliadb_settings

    stub = WriterStub(aio.insecure_channel(nucliadb_settings.nucliadb_ingest))
    request = writer_pb2.ListMembersRequest()
    members: writer_pb2.ListMembersResponse = await stub.ListMembers(request)  # type: ignore
    for member in members.members:
        INDEX_NODES[member.id] = IndexNode(
            id=member.id,
            address=member.listen_address,
            shard_count=member.shard_count,
            dummy=member.dummy,
        )


async def clean_and_upgrade(
    shard: writer_pb2.ShardObject,
) -> dict[str, writer_pb2.ShardCleaned]:
    replicas_cleaned: dict[str, writer_pb2.ShardCleaned] = {}
    for shardreplica in shard.replicas:
        index_node = get_index_node(shardreplica.node)
        replica_id = shardreplica.shard
        cleaned = await index_node.writer.CleanAndUpgradeShard(replica_id)  # type: ignore
        replicas_cleaned[replica_id.id] = cleaned
    return replicas_cleaned
