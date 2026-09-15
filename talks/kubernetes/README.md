# Kubernetes: desired state, and the loops that chase it

A fifteen-minute talk for engineers who use `kubectl` and have never watched what happens next. One command,
`kubectl apply` of a Deployment with three replicas, is followed from the API server's three gates, through etcd and
the controllers, to the scheduler and a kubelet starting the first container; then a node is killed and the same
loops heal it; then a Service gives the pods a stable address and a rolling update replaces them under it.

Spine: you write the state you want into one database; independent loops each watch it and take one step toward it,
forever.

| Move | Scene | Clicks | Minutes |
|---|---|---|---|
| 1. A record, not a process | `ApplyRequest` | 5 | 3 |
| 2. Loops that chase the gap | `Controllers` | 5 | 3 |
| 3. From record to process | `SchedulerKubelet` | 7 | 3 |
| 4. A node dies | `NodeDies` | 4 | 3 |
| 5. A stable address, and change | `ServiceRollout` | 8 | 3 |

No title slide: the deck opens on the first move's still picture. Every scene begins on the previous scene's last frame and
changes its title as the first thing moves, so nothing ever cuts; 29 clicks in all. One picture for the whole talk: the API
server as a bar across the middle with its three gates, the one door everything passes through; above it kubectl and the
row of control loops, each on a short dashed line down to the bar; below it etcd at the left holding the records, three
nodes at the right, each kubelet on a short dashed line up to the bar, and between them two counters, pods desired and
pods running. Every relation is vertical and nothing crosses anything. One accent per meaning: a record, what runs, a
loop, a machine, and a gap.

```bash
bin/render.sh kubernetes ql      # preview; qh for the talk itself
bin/serve.sh kubernetes          # presenter and audience windows
```

Sources and named simplifications are in `script.md`; speaker notes live next to the steps in `scenes/`.
