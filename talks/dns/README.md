# DNS: how a name becomes an address

A 12 to 15 minute talk for engineers who use DNS all day and have never watched the mechanism. One picture that
grows: the laptop, the recursive resolver with its cache, the tree of zones. Two rules carry it: every answer is the
address or a pointer to who to ask next; every level remembers what it heard for exactly as long as it was told to.
There is no title slide: the deck opens on the first picture and the speaker introduces the talk over it. Every
scene begins on the previous scene's last frame and changes it (`bin/seams.py dns` reports every boundary as
"title only" or "identical"); the laptop from move one is the laptop of every later move, and the owner's zone at
the bottom of the tree in move three is the zone that fills the top of the frame in move four.

| Move | Scene | Clicks | Minutes |
|---|---|---|---|
| 1. One list for the whole internet | `OneList` | 4 | 2 |
| 2. Delegation: the name is a path | `Delegation` | 7 | 4 |
| 3. Caching: remember what you were told | `Caching` | 5 | 4 |
| 4. The price of remembering | `Price` | 5 | 3 |
| 5. What keeps it standing | `Standing` | 4 | 2 |

```bash
bin/render.sh dns ql      # preview; qh for the talk itself
bin/shots.py dns ql       # the frame every step holds on
bin/serve.sh dns          # presenter and audience windows
```

Every number on screen is from a primary source or a live trace, listed with dates in `script.md`, which also names
the simplifications. Speaker notes live next to each step in `scenes/`. Colours: blue is a name or a question, yellow
an address, violet a zone or a pointer, teal a remembered record and its time to live, red a miss or a name that does
not exist.
