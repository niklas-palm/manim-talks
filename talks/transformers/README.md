# Transformers: how every token learns from every other

A ~16-minute illustrated talk on the computation inside a transformer language model, for engineers who use these
models and have never seen what happens between the prompt and the next word. It follows one spine: a transformer
is a stack of identical layers; in each layer every token gathers what it needs from every other token in a single
parallel step, then is transformed on its own; stack that many times and the last position predicts the next word.
Every stage is drawn as something happening, from text to a sampled token.

| Move | Scenes | Minutes |
|---|---|---|
| 1. The parallel idea | `Sequential` (recurrent one-at-a-time vs. transformer all-at-once, and the n² cost) | 3 |
| 2. Words become vectors | `Embedding` (the tokens from move 1 shrink, the sentence appears; ids, the embedding table, the missing order, positional vectors) | 3 |
| 3. Attention | `Attention` (query/key/value, the score, softmax, the weighted sum), `MaskAndHeads` (the causal mask, multiple heads, concatenate and project) | 6 |
| 4. The token thinks alone, many times | `Layer` (feed-forward expand/ReLU/contract, the residual add, the stack of N) | 3 |
| 5. One token at a time | `Predict` ("mat" leaves the row, the vocabulary matrix, the distribution, the sampled word rejoins the row, the loop; training vs inference) | 2 |

Five moves in six scene files, 31 clicks. There is no title slide: the deck opens on the six tokens and the speaker
introduces the talk over them. Every scene starts on the previous scene's last frame and changes it (the title fades
in place as the first change plays), so the token row introduced in move 2 carries through to the last word;
`bin/seams.py transformers` reports every boundary as identical or title-only.

```bash
bin/render.sh transformers ql      # preview (480p); qh for 1080p60
bin/serve.sh transformers          # presenter and audience windows
bin/shots.py transformers ql       # the end frame of every step, tiled per scene
```

The spine, the moves, the primary sources (the 2017 paper and Hugging Face documentation), and every named
simplification are in `script.md`. Speaker notes live next to each step in `scenes/`. Talk-specific drawing helpers
(the shaded vector, the multiply sweep, the softmax bars) are in `scenes/objects.py`; the shared library is
`lib/palette.py`.
