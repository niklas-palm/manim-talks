# Kubernetes: desired state, and the loops that chase it

Spine: you write the state you want into one database; independent loops each watch it and take one step toward it,
forever. Everything Kubernetes does is one of those loops closing a gap between desired and actual.
Audience: engineers who use kubectl daily and have not watched the machinery. Afterwards they can explain what happens
between `kubectl apply` and a running container, why a lost node heals itself, and why a Service address is stable.
Length: about 15 minutes, 27 clicks, 5 scenes. No title slide: the deck opens on the first move's still picture and the
speaker introduces the talk over it. Every scene begins on the previous scene's last frame and changes its title as the
first thing moves, so the audience keeps one picture from the first click to the last.

Colours: blue = records, the state you asked for; yellow = what actually runs and the status it reports; violet = the
control plane and its loops; teal = the machines (nodes, kubelet, kube-proxy, and etcd's members); red = failure or a gap.

## 1. A record, not a process (3 min) — `ApplyRequest`, 5 clicks
- The request is a description of state, not a command. It reaches the API server, the only door.
- Zoom into the API server. Three gates in order: authentication (401 on failure), authorisation (403), admission (may modify or reject; writes
  only); then validation and a write to etcd; "201 created".
- etcd is n members; a write is done at quorum n/2 + 1: 3 tolerate 1 failure, 5 tolerate 2. The database is the only
  durable part.
- The nodes appear, empty: 3 desired, 0 running. The API server did not talk to a node.

## 2. Loops that chase the gap (3 min) — `Controllers`, 4 clicks
- A controller is observe, compare, act; it acts by writing records through the API server. The Deployment controller
  wants one ReplicaSet with this template, has none, creates it; then has nothing to do.
- The ReplicaSet controller, opened under a zoom: wants 3, has 0, gap 3, acts three times: three Pod records with no
  node. Still nothing runs.
- Every line points at the API server: components never talk to each other; the database is the coordination, which is
  why each loop can be simple and can fail and restart.

## 3. From record to process (3 min) — `SchedulerKubelet`, 6 clicks
- The scheduler's trigger: a Pod record with no node.
- Zoom into the node column. Filtering: feasible nodes, e.g. enough memory; node 3 is out. No feasible node means the Pod stays pending.
- Scoring: rank feasible nodes (least allocated here); ties broken at random; binding writes the node name into the
  record.
- Zoom into node 1. The kubelet on that node watches for Pods bound to it, pulls the image, starts the container, reports Running into the
  same record. The first process of the talk.
- The other two at speed; desired 3 = running 3; every loop finds no gap and waits.

## 4. A node dies (3 min) — `NodeDies`, 4 clicks
- Heartbeats: each kubelet renews a Lease every 10 s; the node controller watches.
- Node 2 goes silent. After 40 s (node-monitor-grace-period) it is NotReady and tainted; pods tolerate the taint for
  300 s by default; at 340 s the pod is evicted: a record goes away, the count drops to 2.
- The same loops close the gap: ReplicaSet controller creates one Pod record, scheduler filters (NotReady, memory) and
  binds to node 1, kubelet runs it. Self-healing is not a feature; it is what loops do when the gap reopens.

## 5. A stable address, and change (3 min) — `ServiceRollout`, 8 clicks
- The cluster settles as the title changes: node two returns, the node controller fades, the four Pod records leave the
  store to make room (they still exist; the note says so), the ReplicaSet card becomes "v1".
- Problem: pods have their own IPs and the set changes with every replacement.
- A Service record: selector and a cluster IP that never changes; the EndpointSlice controller derives the list of
  ready pod addresses, rewritten whenever pods change.
- kube-proxy on every node watches Services and EndpointSlices and programs packet rules: traffic to the cluster IP is
  rewritten to one listed address, chosen at random by default.
- `kubectl set image`: one field changes; the Deployment controller creates a second ReplicaSet at 0 and scales the two
  in opposite directions under maxSurge 25% (rounded up: 1 extra) and maxUnavailable 25% (rounded down: 0 missing); old
  ReplicaSets kept for rollback (10 by default).
- The rollout at speed: v2 up one, v1 down one, the EndpointSlice following; never fewer than 3 ready, never more than 4.
- Rollback: set the template back; the same two ReplicaSets scale the other way.

## Sources (read 2026-09-14)
- Kubernetes components: https://kubernetes.io/docs/concepts/overview/components/
- Controlling access to the API (authentication, authorisation, admission, persistence): https://kubernetes.io/docs/concepts/security/controlling-access/
- Controllers (control loop, desired vs current state, act via the API server, independence): https://kubernetes.io/docs/concepts/architecture/controller/
- Deployments (ReplicaSets, rolling updates, pod-template-hash, revisionHistoryLimit 10): https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
- Deployment API (maxSurge and maxUnavailable default 25%, rounding up and down): https://kubernetes.io/docs/reference/kubernetes-api/workload-resources/deployment-v1/
- kube-scheduler (filtering, scoring, random tie-break, binding): https://kubernetes.io/docs/concepts/scheduling-eviction/kube-scheduler/
- Nodes (heartbeats every 10 s, node-monitor-period 5 s, node-monitor-grace-period 40 s, taints on unreachable nodes): https://kubernetes.io/docs/concepts/architecture/nodes/
- Taints and tolerations (default tolerationSeconds 300 for not-ready and unreachable): https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/
- Services and EndpointSlices: https://kubernetes.io/docs/concepts/services-networking/service/
- Virtual IPs and service proxies (kube-proxy watches Services and EndpointSlices, random backend by default): https://kubernetes.io/docs/reference/networking/virtual-ips/
- kubelet (PodSpecs from the API server, ensures containers run): https://kubernetes.io/docs/reference/command-line-tools-reference/kubelet/
- etcd FAQ (quorum n/2 + 1, 3 tolerates 1, 5 tolerates 2, odd sizes): https://etcd.io/docs/v3.5/faq/

## Simplifications (named in labels or notes)
- Controllers are drawn as separate boxes; in a real cluster they run inside kube-controller-manager as one process.
- Three pod slots per node and one memory bar stand for a node's capacity; real filtering checks many resources and rules.
- The manifest on screen is trimmed to the lines the talk uses (kind, replicas, image); the label says so; apiVersion and
  metadata are in the note.
- The scheduler's score is drawn as free memory in percent (one common plugin); real scoring sums several plugins.
- The etcd write is drawn as one card reaching two of three members; Raft's leader and log are not drawn.
- The eviction timeline is drawn as one counter: 40 s grace, then 300 s toleration; the node-monitor-period (5 s) is
  in the note only.
- Cards show a kind and one status line; names (web-7d4f-a), labels and the pod-template-hash live in the note.
- Pod IP addresses are not drawn; the EndpointSlice card counts them and the note gives the cluster IP.
- A v2 pod is drawn as a yellow block with a white outline; the counter names the convention.
- A rollout is drawn with pod readiness as instantaneous; readiness probes are mentioned in the note only.
