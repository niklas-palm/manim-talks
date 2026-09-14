# DNS: how a name becomes an address

Spine: every answer is the address, or a pointer to who to ask next; and every level remembers what it heard for
exactly as long as it was told to. Delegation is the first rule at work, caching the second, and every failure mode
an engineer meets (slow propagation, the slow typo, a name resolving differently in two offices) is the two rules
colliding.

Audience: engineers at a large company who use DNS every day and have never watched the mechanism. Afterwards they
can read a trace (`dig +trace`), explain why a change takes as long as its TTL to land, choose a TTL, and say what
negative caching and a CNAME do.

Length: 12 to 15 minutes, 25 clicks, 5 scenes, no title slide. Every scene opens on the previous scene's last frame; its first click changes the title and transforms the picture into the new move's starting picture, which then holds before anything moves. One picture from move two on: the laptop on the left, the recursive
resolver with its cache in the middle, the tree of zones on the right; questions travel right, answers left.

## 1. One list for the whole internet (2 min) — `OneList`, 4 clicks
- One laptop, one list of name and address rows, a lookup succeeds: the job, and the design the early internet ran on.
- The list grows to the size of the internet; every machine needs all of it. Failure one: size.
- Copies everywhere; the owner changes an address; two copies are stale. Failure two: change. The two rules are the
  two fixes.

## 2. Delegation: the name is a path (4 min) — `Delegation`, 7 clicks
- The name read from the right: the final dot is the root, then com, example, www. A name is a path.
- Each level is a zone with an owner (root: 13 server names, 12 operators, 2,045 anycast instances; com: a registry
  among 1,393 TLDs; example.com: the owner). Each zone holds only pointers (NS records, with TTLs) to the zones below;
  only the last holds the address (A record).
- Two actors: the stub resolver asks one question; the recursive resolver walks.
- Hop one: the root answers with a referral to com's servers (glue attached); the pointer is kept.
- Hop two: com answers with a referral to example.com's servers; kept.
- Hop three: example.com answers with the address; kept; sent home. Delegation solved size and made every lookup
  three round trips; rule two fixes that.

## 3. Caching: remember what you were told (4 min) — `Caching`, 5 clicks
- The same name again: answered from the cache, zero hops into the tree.
- A different name under com: the root is skipped because its pointer is cached. The TTLs the zones chose: root
  pointers 6 days, com pointers 2 days, the address 5 minutes; the expensive part of the walk is cached longest.
- Time passes: the address expires; the next lookup is a miss and re-walks only the bottom. A hit costs no network;
  a miss about 130 ms on average across the internet's servers, 4 to 6% of which time out (Google Public DNS).
- Caches at every level (browser, OS, resolver), the same TTL counting down in each: 300 s leaves the resolver, 281 s
  arrives in the browser.

## 4. The price of remembering (3 min) — `Price`, 5 clicks
- The owner changes the address; five resolvers around the world keep the old copy until each expires. Propagation
  time is the TTL as seen from the slowest cache; there is no push.
- The trick: lower the TTL to 60 s, wait one old TTL, change, raise it again.
- A name that does not exist: the walk to authority answers NXDOMAIN; the "no" is cached for the zone's SOA minimum
  (1800 s for example.com; RFC 2308 suggests 1 to 3 hours).
- An alias (CNAME) is a pointer to another name; the resolver restarts the walk there. A name with a CNAME holds
  nothing else.

## 5. What keeps it standing (2 min) — `Standing`, 4 clicks
- 13 root server names, 12 operators, 2,045 anycast instances: routing delivers a packet to the nearest.
- The packet: one UDP question to port 53; answer, authority (the NS pointers) and additional (glue) sections; 512 bytes
  classic, TC flag, TCP fallback.
- The picture once more with the two rules written under it.

## Sources (all read 2026-09-14)
- RFC 1034, Domain names: concepts and facilities. Tree, zones, delegation and glue (§4.2), resolver algorithm (§5.3.3),
  TTL semantics, CNAME handling. https://www.rfc-editor.org/rfc/rfc1034.txt
- RFC 1035, Domain names: implementation and specification. Message format, RR types and codes, UDP 512 bytes and
  TC/TCP (§4.2), label 63 and name 255 octets, RCODE 3. https://www.rfc-editor.org/rfc/rfc1035.txt
- RFC 8499, DNS terminology: stub resolver, recursive resolver, referral, glue, TTL, negative caching, zone, delegation,
  TLD, root zone. https://www.rfc-editor.org/rfc/rfc8499.html
- RFC 2308, Negative caching of DNS queries: negative TTL = min(SOA MINIMUM, SOA TTL); 1 to 3 hours sensible, more than
  a day problematic; the redefinition of MINIMUM. https://www.rfc-editor.org/rfc/rfc2308.txt
- root-servers.org: 13 identities, 12 operators, 2,045 operational anycast instances. https://root-servers.org/
- IANA TLD list, version 2026091300: 1,393 top-level domains. https://data.iana.org/TLD/tlds-alpha-by-domain.txt
- The root zone file: root NS TTL 518400 s (6 days); TLD delegation NS and glue TTL 172800 s (2 days); root SOA
  minimum 86400 s. https://www.internic.net/domain/root.zone
- Google Public DNS, performance: cache misses the dominant cause of latency; 130 ms average resolution time for
  responsive servers; 4 to 6% of requests time out; 300 to 400 ms end to end including failures.
  https://developers.google.com/speed/public-dns/docs/performance
- A live trace on 2026-09-14 from this machine (`dig +trace www.example.com`, `dig example.com SOA`): com NS 172800 s,
  example.com NS 172800 s at the registry, www.example.com A 300 s (seen at 281 s in a cache), example.com SOA minimum
  1800 s.

## Simplifications, named on screen or in notes
- One record per zone box where a real zone holds many (thirteen NS records at the root, two at example.com). The notes
  say so.
- The root's pointer to com is shown with the TTL com's records carry in the root zone (2 days); the root's own NS set
  (6 days) is quoted in the caching note and the closing frame.
- The resolver's cache is drawn as a few rows; a real one holds millions.
- Resolver locations in move four are illustrative names; their TTL fractions are invented to show staggered expiry.
- mail.other.com and its addresses are documentation addresses (RFC 5737 ranges), stated as examples.
- The anycast map is an ellipse with one dot per about twelve instances, labelled as such.
- DNSSEC, EDNS(0) larger UDP payloads, DNS over TLS/HTTPS, and QNAME minimisation are left out; the transport note
  mentions the classic 512-byte limit only.
