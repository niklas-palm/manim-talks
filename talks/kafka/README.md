# Kafka: a log you can replay

About fifteen minutes on how Apache Kafka works, for engineers who have used it and never seen the machinery.
One spine: a topic is an append-only log split into partitions, and every reader keeps one integer, an offset into
it; ordering, parallelism, replay and durability follow from those two facts. Every scene is one picture of a log
that grows: records with their offsets, pointers under it, copies of it, segments of it, and finally the log Kafka
keeps about itself.

| Move | Scene | Minutes |
|---|---|---|
| 1. The log | `TheLog`: append, pull by offset, independent readers, replay | 3 |
| 2. Partitions | `Partitions`: one broker saturates, split by key hash, consumer group, rebalance, `__consumer_offsets` | 4 |
| 3. Replication | `Replication`: leader and followers, in-sync set, high-water mark, min.insync.replicas, failover | 4 |
| 4. Retention and compaction | `Retention`: segments, deletion by age, compaction per key, tombstones | 3 |
| 5. The controller | `Controller`: KRaft quorum, the metadata log, an event propagating, KRaft only since 4.0 | 2 |

```bash
bin/render.sh kafka ql      # preview; qh for the talk itself
bin/serve.sh kafka          # presenter and audience windows
```

There is no title scene; every scene opens on the previous scene's last frame and retitles in place while the picture rearranges (the one broker becomes three, the three partitions become three replicas, the leader's log opens into segment files, the compacted topic becomes the metadata log); the mechanism starts on the next click; first occurrences are slow, repeats fast. Sources and simplifications are in `script.md`; the speaker notes live next to the steps in `scenes/`. Defaults quoted
on screen are from the Apache Kafka 4.3 configuration reference.
