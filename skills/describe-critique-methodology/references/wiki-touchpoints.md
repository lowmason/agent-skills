# Wiki touchpoints (only when $LLM_WIKI_ROOT is set)

Both touchpoints are optional conveniences. When `$LLM_WIKI_ROOT` is unset,
skip both silently — no mention in output.

## Describe mode pre-flight (read-only)

Before writing the description, query the wiki for already-filed literature
on the system's method family, using the llm-wiki skill's query procedure.
Filed sampler/nowcasting notes often supply the evaluation-criteria slot or
sharpen the open questions. Read-only: no wiki mutation.

## Synthesize mode suggestion (one line, once)

After the critique file is committed, suggest that the human drop a copy
into `$LLM_WIKI_ROOT/raw/` for llm-wiki ingest — a Research-mode critique is
a citation-rich source document. The agent never writes `raw/` itself.
