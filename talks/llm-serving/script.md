# Speaker notes

One line per step (each `next_slide()` in the scenes), with the section of `docs/tuning.md` in the
companion repository that carries the measurement. Timings are targets for a 45-minute slot.

## Opening (2 min)
- Title. Say who the talk is for: engineers who will host a model, or buy hosting, and want to know what they are paying for.
- The spine. Read it slowly. Everything that follows is this sentence with numbers.
- The seven moves. Do not explain them; the list is a promise.

## 1. Two jobs, two costs (9 min)
- **Mechanics**, one continuous picture. The sentence, then its tokens with ids, then the lookup that turns each into a vector. The stage: layer stack, empty cache rack, the two gauges, two counters. Zoom into layer one with all five vectors as a block: one row of a matrix, read once, multiplies all five columns; the sweep fills five output columns per read; five keys and values into the cache row; each query fans out over the keys up to its own; feed-forward read once for five columns; layer two replays the same at speed. Zoom out, the block continues down the stack: one read of the model for the whole prompt, compute gauge pegged. Sample a token. Decode: the token goes back in alone; zoom in a second time and the same stages run for one column, with the weights read and the cache read named where they happen, ghost columns showing what prefill had; bus pegged, compute idle. Back out, the loop runs, the cache counter grows by one column per token. (*Two phases*, *Decode speed per request is capped by bandwidth*)

## 2. Why the engine batches (6 min)
- **DecodeCeiling, "GPU latency and throughput".** The two words defined on screen. The card named (RTX PRO 6000 Blackwell Server Edition, g7e, 1.6 TB/s) and the model named (dense 32B fp8, 32 GB per token): 50 tokens/s, 20 ms between tokens, the latency ceiling. This talk's model (30B mixture of experts, 3B active): 530, 1.9 ms. Measured alone 175, 5.7 ms, bus 39% busy; with one request latency and throughput are the same number. H100 (p5, 3.35 TB/s): 105 and 1,120; measured at eight in flight 67 to 102, half again, not twice. The card sets the latency ceiling; throughput is the engine's job, and its knob is the batch. (*Decode speed per request is capped by bandwidth*, *Choosing an instance type*)
- **Batching, the mechanism.** Decode as a timeline of steps. One request: every step reads all the weights, one token out. Four requests: the same read, four tokens; reads per step stay at one. The step gets a little longer (a column of arithmetic and a cache read per request), so latency creeps and throughput climbs almost in proportion, until arithmetic or cache reads reach the size of the weights read.
- **Continuous batching, running.** Requests never arrive together, so the batch is re-formed every step. A conveyor: eight slots as rows, the newest step entering at the right, time scrolling left at a constant rate so a longer step is a wider column. Each request is a colour from the queue to its slot to its last token; a hollow cell is a slot the weights read did nothing for. Light load: two or three colours, hollow columns, the GPU waiting. Heavy load: every slot full, a queue, columns about twice as wide (measured: 6 ms alone, 12 ms at eight), four times the tokens per second. A finished request frees its slot and the next waiting one takes it at the very next step. "Requests waiting" is the saturation signal. Eight slots drawn; the engine's limit is max_num_seqs, 256 in our engine. (*Engine metrics*)
- **Batching, measured.** One click per measured point, both curves on the decode clock (per request, and per request times in flight): 174 at one; 86 each and 688 together at eight, the step from 5.7 to 11.6 ms; 56 and 1,792 at 32, bus 76%; 48 and 3,072 at 64, the bend; 41 and 5,248 at 128, bus 77% and flat. Wall-clock totals measured were 166 and 4,971 (prefill and gaps included). (*Two ceilings*, *Choosing an operating concurrency*)
- The limit is the cache. Every request's context lives in the memory left after the weights. Full means preemption: evicted and recomputed. Lost work. (*Engine metrics*, *gpuMemoryUtilization*)
- So what is left after the weights decides how many fit. Shrink the weights and more fit. Bridge to move 3.

## 3. Three knobs (8 min)
- **Quantisation, "fewer bytes per weight".** Every quantity named on screen: 30B parameters at 2 bytes is 57 GB read per decode step, leaving room for about 330,000 tokens of context across all requests (about 40 conversations of 8k tokens, 96 KB per token; one request at the model's full 262k). fp8: 29 GB, about 630,000 tokens; an fp8 cache at 48 KB per token: 1.27 million (the engine's own figure at start). (*Quantisation*)
- Measured: 7,900 against 16,200 prompt tokens prefilled per second, one GPU, inside an eight-second latency budget. Half the fleet for the same work. (*Every weight option, measured*)
- Two independent decisions: the weights' precision and the cache's. What it costs in answers comes in move 5.
- **MixtureOfExperts, "dense versus mixture of experts".** Dense, 32B parameters: every weight read for every token, 32 GB. Mixture of experts, 30B parameters: 128 experts per layer, a router picks 8, 3B active, 3 GB per token; drawn as 8 experts with 2 chosen. Same depth, a tenth of the bytes, ten times the decode ceiling.
- The catch: a batch touches most experts. Drawn as 8 experts with 2 chosen (the model has 128 with 8); measured on the memory bus: 39% busy at one request reading the active 3 GB, 77% at 128 in flight reading essentially all 29 GB. Plan on the loaded number. (*Two ceilings*, *Choosing a model to host*)
- **PrefixCache, "reusing the KV cache, across turns and across engines".** Turn 2 resends turn 1. Nine of thirteen tokens were already read; prefix caching reuses the matching blocks.
- The twist: the cache lives inside one engine; the balancer sends the next turn to the next engine. Measured 21% hits on eight engines.
- A session cookie steering each conversation home: 75%, +14% throughput. Caching is a routing decision. (*Prefix caching is a routing decision*)
- The other way out: blocks are content-hashed, so a connector can park evicted blocks in host RAM (per engine) or a shared store over the network that every engine reads (LMCache, Mooncake, Dynamo KVBM): a long document many users ask about, a shared system prompt, an agent's context between tool calls. Measured: a 32 GB host tier behind a 58 GB cache at 1.4x working set served zero hits; at 9x the cache, 79% of prompt tokens came back. The tier must outsize the churn.

## 4. More than one GPU (6 min)
- **Parallelism.** A model too big for one card, four GPUs.
- Tensor parallelism drawn: the same whole vector arrives on every GPU; each GPU holds a quarter of every matrix, multiplies (a quarter of the arithmetic, in parallel) and ends with partial sums for every output; the all-reduce adds them across GPUs. Once per pair of matrices in practice (the first split by columns keeps a slice of the intermediate and needs no exchange, the second split by rows produces partial sums and does): two per layer. Pipeline parallelism (whole layers per GPU, the token walks) exists for spanning machines and is mentioned in one sentence; not measured, not common inside one box. Makes it fit; does not make it faster. (*Tensor parallelism*)
- Expert parallelism: whole experts placed on GPUs, tokens travel (all-to-all instead of all-reduce). Used when the model is too big for slicing alone (hundreds of experts across dozens of GPUs) and the batch keeps every GPU's experts busy. Measured at the small end, 235B on 8 GPUs: one request 108 tokens/s without, 86 with; 7 to 20% fewer requests/s under load. Some fp8 checkpoints need it to start at TP=8 (expert tile width).
- Eight GPUs: one engine at TP=8, 13.4 requests/s. Two engines at TP=4, 22.5. Same model, same load. (*Topology*)
- The rule: smallest degree that fits, then replicas. Lockstep is the third wall.

## 5. What precision costs in answers (7 min)
- **Rounding.** The mechanism first. A weight is a number; fewer bits means fewer levels (8 on a unit stretch at 4-bit); every weight moves a little; every score moves a little; a sure position keeps its pick, a close call flips. So the cost is a flip rate on close calls, and it must be measured against a baseline that flips too.
- **NoiseFloor.** Before any number: the same bf16 model deployed twice and scored twice. 3% of tool-call items flip, 27% of agent tasks, 12% of code fixes, 2% of extraction sentences. That is the flip rate of nothing. (*What quantisation costs an agent*)
- Agent trajectories diverge on the first different token. Compare aggregates, same task list, repeat your baseline.
- **PrecisionCost.** fp8 flips like the noise floor, gains equal losses, on every family. The 2x option is free. (*What quantisation costs in answers*)
- 4-bit: about a point, one answer in twenty, losses ahead four to three. Small, real, the same for every format.
- One build passed every chat benchmark and lost 27 points of tool-use judgement and 15 of 22 code fixes. Format is not the risk; the build is. Measure on your task.

## 6. The fleet (5 min)
- **Fleet.** Independent requests, so engines add up: size from one engine's measured rate at your latency budget and prompt shape, with headroom, rounded up. The companion numbers (about 16 requests/s, 16,075 input tokens/s, at 1,000 tokens inside 8 s p95; six engines at 99% of six times one) are the worked example: 100 requests/s needs 8 engines. (*Sizing a fleet*)
- Shape: independent engines behind a balancer. Replicas over parallelism past the degree that fits; a failure costs one engine; capacity in engine-sized steps. Edge concerns (TLS, keys) are ordinary web infrastructure, not the subject.
- Adding an engine means getting a machine and loading tens of GB of weights: minutes in any stack (11 measured here). Size the fixed fleet for the peak; autoscale for trends. (*Autoscaling*)
- The balancer sees latency; the engines know why: requests waiting, cache usage, preemptions. Scrape them. (*Engine metrics*)
- Agents: tools in, structured calls out (the engine needs the parser); long steps that outlive proxy timeouts, so stream.

## 7. Where the industry is (4 min)
- **Industry.** Every engine is a batching scheduler over prefill and decode. Six fronts, each an attack on one of the two costs, re-validated against vLLM, llm-d, NVIDIA Dynamo and NVIDIA's NVFP4 documentation (September 2026):
- Disaggregated serving: separate pools per phase; buys independent TTFT and ITL tuning and isolation, not throughput per GPU by itself (vLLM's docs say so). Orchestration layers (Dynamo, llm-d) are built around it.
- Caches with an address: KV-aware routers (llm-d endpoint picker, Dynamo KV router, about 2x TTFT reported) and tiered offloading (vLLM tiered KV offloading, Dynamo KVBM). Our campaign 8 is the caution: size the tier to the churn.
- Sparse attention: a token scores a chosen subset of cached keys (DeepSeek V3.2 in vLLM), so the cache read stops growing with context.
- Speculative decoding: EAGLE, MTP, suffix decoding, parallel drafting (P-EAGLE, DFlash); high gain at low load, medium at best when busy. Measured here +24 to +41% lightly loaded, nothing under heavy load.
- 4-bit as arithmetic: Blackwell NVFP4 with a scale per 16 values; NVIDIA reports within a point of fp8 on calibrated builds.
- Reasoning effort: tokens per answer as the capacity setting, 1.7 to 3.5x.

## 7. Where the industry is (5 min)
- **Industry.** Every engine is a batching scheduler over the two phases. The frontier is a list of attacks on them.
- Disaggregated serving: prefill and decode on separate hardware. Prefix-aware routing: a router that knows which engine holds which cache. (*What this project does not do*)
- Speculative decoding: +24 to 41% here, fading under load. 4-bit as native compute on Blackwell. Reasoning effort as the capacity setting. (*Speculative decoding with EAGLE-3*, *NVFP4*, *Reasoning models*)
- The spine again.
- **Close.** Three lines, then the repository.
