# Sources and execution boundary

The complete task and task-specific deep-learning guidance were loaded with the requested trial_io start operation. Supplied references were read only through trial_io readref:

- references/frameworks.md
- references/llm.md (read a second time to recover truncated output)
- references/training.md

No other trial, rubric, plan, scoring file, or new JAX skill was inspected. No ordinary local skill file was opened; the task's supplied deep-learning guidance was the only skill body applied. The ordinary catalog was available as context but was not treated as evidence for unsupported APIs. No repository files or runtime adapters were changed. No agent was spawned.

Primary external sources actually inspected through web tools:

- https://tunix.readthedocs.io/en/latest/models.html — supported configuration table, AutoModel examples; also followed its Llama source link, which returned an error.
- https://tunix.readthedocs.io/en/latest/algorithms.html — PEFT and preference/RL algorithm paths.
- https://github.com/google/tunix — project overview.
- https://github.com/google/qwix — LoRA/QLoRA and quantization capabilities.
- https://tunix.readthedocs.io/en/latest/_collections/examples/qlora_llama3_gpu.html — Llama GPU recipe, target-module names, Qwix insertion and model forward interface, source memory guidance.
- https://tunix.readthedocs.io/en/latest/_collections/examples/dpo_gemma.html — Gemma DPO recipe, SafeTensors loader, LoRA target differences, explicit policy/reference trainer parameters.
- https://raw.githubusercontent.com/google/tunix/main/tunix/models/automodel.py — signature and source dispatch details; local SafeTensors dispatch chosen rather than inventing a revision keyword on from_pretrained.
- https://raw.githubusercontent.com/google/tunix/main/tunix/sft/peft_trainer.py — nnx.LoRAParam selection, nnx.DiffState derivative boundary, optimizer update, accumulator semantics.
- https://flax.readthedocs.io/en/stable/api_reference/flax.nnx/training/optimizer.html — wrt and update(model, grads).
- https://flax.readthedocs.io/en/stable/api_reference/flax.nnx/graph.html — clone and buffer-sharing semantics, graph/state boundary.
- https://orbax.readthedocs.io/en/latest/guides/checkpoint/orbax_checkpoint_101.html — StandardCheckpointer and asynchronous completion.
- https://docs.jax.dev/en/latest/random-numbers.html — typed keys and splitting.
- https://huggingface.co/docs/transformers/main/en/chat_templating — chat-template tokens, generation prompt, special-token duplication.
- https://github.com/huggingface/transformers/blob/main/MIGRATION_GUIDE_V5.md and its raw content https://raw.githubusercontent.com/huggingface/transformers/main/MIGRATION_GUIDE_V5.md — JAX backend removal.
- https://arxiv.org/abs/2305.18290 — DPO.
- https://arxiv.org/abs/2106.09685 — LoRA.
- https://arxiv.org/abs/2305.14314 — QLoRA.

Additional unsuccessful read-only probes:

- https://raw.githubusercontent.com/google/qwix/main/qwix/_src/lora.py
- https://raw.githubusercontent.com/google/qwix/main/qwix/contrib/lora.py
- https://raw.githubusercontent.com/google/tunix/main/tunix/models/llama/model.py
- https://github.com/google/tunix/blob/main/tunix/models/llama/model.py

These failed probes were not treated as verified source content. Qwix insertion and Llama forward usage were grounded in the successfully read official GPU recipe. Inspected https://github.com/google/qwix/tree/main/qwix as read-only directory context and followed a project-root link; no code from an unread file was used as evidence.

All delivered Python is unexecuted. The only executed shell programs were trial_io start/readref and a Python file-content verification that read these two output files, printed sizes/first/last lines, and asserted nonempty text with no escaped Markdown backticks. Literal writes used apply_patch. No dependencies were installed, no model/dataset was downloaded, no JAX code was imported or executed, and no tests, training, conversion, accelerator allocation, or recovery checks were run. Web source inspection establishes source-backed planning/API choices, not target-environment runtime compatibility or training success.

The response contains a concrete two-stage training plan, complete objective/tokenization/preflight functions, a source-inspected loader starting point, and recovery helper functions. It explicitly distinguishes these from a distributed production trainer and supplies actual-result gates rather than fabricated passing results.
