# Kafka: a log you can replay

Spine: a topic is an append-only log split into partitions, and every reader keeps one integer, an offset into it;
ordering, parallelism, replay and durability are consequences of those two facts.
Audience: engineers who have produced to or consumed from Kafka and never seen the machinery.
Length: about 15 minutes, 22 clicks, 6 scenes.

## 1. The log (3 min)
- **TheLog.** One producer, one broker, one partition drawn as a row of cells with offsets beneath. Records append
  and their offset never changes -> a consumer pulls from its offset and owns that one integer -> a second consumer
  has its own offset; reading deletes nothing -> replay is moving the offset back (auto.offset.reset for a new group).

## 2. Partitions (4 min)
- **Partitions.** Everything to one partition saturates one broker (the problem) -> the topic is split; the producer
  hashes the key to a partition, so order holds per key, not per topic -> a consumer group reads one partition per
  member -> a member leaves, its partition is reassigned (classic stop-the-world vs the 4.0 protocol, KIP-848) ->
  committed offsets live in __consumer_offsets, a compacted log of 50 partitions.

## 3. Replication (4 min)
- **Replication.** Three brokers hold one partition: leader and two followers that fetch like consumers. acks=all:
  committed when every in-sync replica has it, and only committed records reach consumers (high-water mark) -> a
  follower lags 30 s and leaves the in-sync set -> with one replica in sync and min.insync.replicas=2 the write is
  refused (NotEnoughReplicas) -> the leader dies; a new leader from the in-sync set, nothing committed lost;
  unclean.leader.election.enable=false -> the old leader returns as a follower.

## 4. Retention and compaction (3 min)
- **Retention.** A partition on disk is segment files named by first offset, rolled at 1 GiB or 168 h -> retention
  deletes whole segments after 168 h or beyond a byte limit; a consumer pointing into one is reset -> compaction keeps
  the latest record per key; offsets keep their gaps -> a tombstone (null value) deletes a key and is itself removed
  after delete.retention.ms (24 h).

## 5. The controller (2 min)
- **Controller.** Three controllers hold cluster metadata in __cluster_metadata, replicated by Raft; brokers fetch it
  -> a broker is fenced: one record appended, replicated, fetched in order -> Kafka 4.0 is KRaft only. The metadata
  log closes the spine: Kafka's own state is a log.

## Sources (read 2026-09-14)
- Apache Kafka design documentation (persistence, producer, consumer, delivery semantics, replication, log
  compaction): https://raw.githubusercontent.com/apache/kafka/trunk/docs/design/design.md (rendered at
  https://kafka.apache.org/documentation/#design)
- Log implementation (segments named by base offset, roll by size, deletion per segment):
  https://raw.githubusercontent.com/apache/kafka/trunk/docs/implementation/log.md
- Broker configuration defaults (num.partitions 1, default.replication.factor 1, min.insync.replicas 1,
  log.retention.hours 168, log.retention.bytes -1, log.segment.bytes 1073741824, log.roll.hours 168,
  log.cleanup.policy delete, unclean.leader.election.enable false, replica.lag.time.max.ms 30000,
  offsets.topic.num.partitions 50, offsets.topic.replication.factor 3): https://kafka.apache.org/43/generated/kafka_config.html
- Consumer defaults (enable.auto.commit true, auto.commit.interval.ms 5000, auto.offset.reset latest,
  group.protocol classic): https://kafka.apache.org/43/generated/consumer_config.html
- Producer defaults (acks all, enable.idempotence true, linger.ms 5, batch.size 16384, sticky partitioning
  without a key): https://kafka.apache.org/43/generated/producer_config.html
- KRaft operations (3 or 5 controllers, active and standby, __cluster_metadata, brokers fetch metadata, last bridge
  release 3.9): https://raw.githubusercontent.com/apache/kafka/trunk/docs/operations/kraft.md
- KIP-500 (why ZooKeeper was replaced by a Raft quorum over a metadata log):
  https://cwiki.apache.org/confluence/display/KAFKA/KIP-500%3A+Replace+ZooKeeper+with+a+Self-Managed+Metadata+Quorum
- Consumer rebalance protocol (KIP-848: server-side assignment, incremental, GA in 4.0, default in 5.0):
  https://raw.githubusercontent.com/apache/kafka/trunk/docs/operations/consumer-rebalance-protocol.md and
  https://cwiki.apache.org/confluence/display/KAFKA/KIP-848%3A+The+Next+Generation+of+the+Consumer+Rebalance+Protocol
- Upgrade notes 4.0 ("Apache Kafka 4.0 only supports KRaft mode - ZooKeeper mode has been removed"; KIP-848 GA;
  Eligible Leader Replicas KIP-966): https://raw.githubusercontent.com/apache/kafka/trunk/docs/getting-started/upgrade.md
- Release dates (4.0.0 on 2025-03-18; 4.3.1 on 2026-06-25): https://kafka.apache.org/blog
- Introduction (record = key, value, timestamp; replication factor 3 common; consumers decoupled):
  https://kafka.apache.org/intro

## Simplifications
- Records are drawn as coloured cells, colour = key, three keys; a real partition holds millions of records.
- The log rails show 8 to 14 slots; segments in the retention scene hold 9 records where a real one holds a
  gibibyte. The label names the real numbers.
- The producer's batching (linger.ms, batch.size) and the idempotent producer are in the notes, not drawn.
- The high-water mark is drawn only on the leader; followers hold their own copy of it.
- Eligible Leader Replicas (KIP-966) and tiered storage are not shown.
- The controller scene shows one metadata event; the real log carries every topic, partition, replica and
  configuration change.
