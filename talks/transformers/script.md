# Transformers: how every token learns from every other

Spine: a transformer is a stack of identical layers in which every token gathers what it needs from every other token
in one parallel step, then is transformed on its own; stack that many times and the last position predicts the next word.
Audience: engineers who use language models and have never seen the computation inside one. Afterwards they can name
every stage from text to next token and say what attention, heads, the mask and the residual each do.
Length: about 16 minutes, 31 clicks, 6 scene files across 5 moves; no opening slide. Every scene opens on the previous
scene's last frame and the title changes in place with the first change, so the deck is one picture from the six
tokens to the sampled word.

## 1. The parallel idea (3 min)
- **Sequential.** Recurrent networks read one token at a time (sequential steps = length) -> the bottleneck -> the transformer reads every token at once (steps = 1) -> the cost is connections growing with the square of the length, work a GPU does in parallel. Leads to: first, words must become numbers.

## 2. Words become vectors (3 min)
- **Embedding.** Opens on move 1's frame: the connections and counters go, the tokens shrink, the sentence appears above them -> tokens with ids (byte-pair encoding, vocab 50,257) -> an embedding table, id selects a row, a vector per token -> a set of vectors has no order -> add a position vector to each. Leads to: now let the vectors read one another.

## 3. Attention (6 min)
- **Attention.** Three matrices turn each vector into a query, key, value (the sweep, slow then fast) -> one token's query scored against every key (the fan, one dot product slow) -> softmax makes weights that sum to 1 (the bars) -> weighted sum of values is the token's new vector. Every token at once.
- **MaskAndHeads.** The full attention grid, still (who attends to whom) -> "mat"'s row flashes and the causal mask blocks the future (lower triangle only), because a language model predicts the next word -> one view is not enough: several heads in parallel, each own q/k/v -> concatenate and project back to model size.

## 4. The token thinks alone, many times (3 min)
- **Layer.** Feed-forward on each token alone: expand (512->2048), ReLU nonlinearity, contract -> the residual connection adds the update instead of replacing (LayerNorm as a note) -> the layer (attention + feed-forward) stacked N times (6 in the paper, 30-100 today).

## 5. One token at a time (2 min)
- **Predict.** Opens on the stack; the small vector grows into the one we read from and "mat" leaves the row (it is the word to predict) -> the last vector times the vocabulary matrix (shared with the embeddings) -> a score per vocab entry -> softmax to a distribution -> sample one token (temperature) -> append and run the whole model again -> why generation streams. Training vs inference as the closing note.

## Sources (read 2026-09-14)
- Vaswani et al., "Attention Is All You Need", 2017. arXiv:1706.03762 (abstract) and https://ar5iv.labs.arxiv.org/html/1706.03762 (body).
  Facts drawn: scaled dot-product attention softmax(QK^T/sqrt(d_k))V and the reason for sqrt(d_k); h=8 heads, d_k=d_v=64;
  feed-forward FFN(x)=max(0,xW1+b1)W2+b2 with d_model=512, d_ff=2048; N=6 layers; residual + LayerNorm(x+Sublayer(x));
  sinusoidal positional encodings added to embeddings; decoder masking for the auto-regressive property; embedding
  weights shared with the pre-softmax linear; self-attention connects all positions with a constant number of
  sequential operations versus O(n) for recurrence.
- Hugging Face LLM course, chapter 1.6 (decoder-only / auto-regressive models, one token at a time, causal attention):
  https://huggingface.co/learn/llm-course/chapter1/6
- Hugging Face Transformers docs, tokenizer summary (byte-pair encoding; byte-level BPE; GPT-2 vocabulary 50,257 =
  256 bytes + 50,000 merges + end-of-text): https://huggingface.co/docs/transformers/tokenizer_summary

## Simplifications (all named on screen or in the note)
- Vectors drawn as 8 cells; the paper's d_model is 512. Query/key/value drawn as 3 cells; the paper's d_k = d_v = 64. Feed-forward drawn 8->16; the paper is 512->2048.
- 3 heads drawn; the paper uses 8. 5 layers in the stack picture (each a miniature of the layer just shown); the paper has 6, modern LLMs 30-100.
- Attention scores and weights are illustrative numbers, not computed from the drawn cells; the mechanism (dot product,
  softmax, weighted sum) is exact. Positional encoding drawn as a second vector added; the paper's values are sinusoids.
- LayerNorm and the exact residual placement (pre- vs post-norm) are mentioned in the note, not drawn.
