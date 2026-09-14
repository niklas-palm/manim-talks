# Kubernetes: desired state, and the loops that chase it

A fifteen-minute talk for engineers who use `kubectl` and have never watched what happens next. One command,
`kubectl apply` of a Deployment with three replicas, is followed from the API server's three gates, through etcd and
the controllers, to the scheduler and a kubelet starting the first container; then a node is killed and the same
loops heal it; then a Service gives the pods a stable address and a rolling update replaces them under it.

Spine: you write the state you want into one database; independent loops each watch it and take one step toward it,
forever.

| Move | Scene | Clicks | Minutes |
|---|---|---|---|
| 0. Opening | `Opening` | 1 | 1 |
| 1. A record, not a process | `ApplyRequest` | 5 | 3 |
| 2. Loops that chase the gap | `Controllers` | 4 | 3 |
| 3. From record to process | `SchedulerKubelet` | 6 | 3 |
| 4. A node dies | `NodeDies` | 4 | 3 |
| 5. A stable address, and change | `ServiceRollout` | 7 | 3 |

Every scene opens on a still picture and the mechanism starts on the second click; 27 clicks in all. One picture for the whole talk: kubectl at the left, the API server with its three gates, etcd under it holding the
records, a column of control loops, three nodes at the right, and two counters, pods desired and pods running. Blue
is a record, yellow is what runs, violet is a loop, teal is a machine, red is a gap.

```bash
bin/render.sh kubernetes ql      # preview; qh for the talk itself
bin/serve.sh kubernetes          # presenter and audience windows
```

Sources and named simplifications are in `script.md`; speaker notes live next to the steps in `scenes/`.
