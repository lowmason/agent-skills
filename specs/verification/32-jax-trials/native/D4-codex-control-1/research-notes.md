# Research notes

Trial: /private/tmp/jax-skill-trials-pAYZ0t/native/D4-codex-control-1

## Authorized task and scope

The first action was exactly:
python3 /private/tmp/jax-skill-trials-pAYZ0t/trial_io.py start /private/tmp/jax-skill-trials-pAYZ0t/native/D4-codex-control-1

Its complete output authorized an inline plan/code answer for JAX adapter fine-tuning followed by language-model preference optimization, covering loading, data/loss, and pre-run checks. It stated that execution was not required and that no new design approval workflow or skill modification was needed.

An rg --files inventory was restricted to this assigned directory. It listed prompt.txt, conditions.json, and read-events.jsonl. I did not read conditions.json or inspect any other trial, rubric, scoring, or plan. There were no supplied reference files in this trial inventory.

## Ordinary skills actually read and used

- /Users/lowell/.agents/skills/clean-code/SKILL.md
  Read completely. Used its guidance on descriptive names, cohesive functions, numerical constants, and boundary checks while authoring the delivered Python.
- /Users/lowell/.agents/skills/verification-before-completion/SKILL.md
  Read completely. Used its evidence-before-claims rule to distinguish artifact delivery from unexecuted runtime verification.

No JAX-specific skill files were searched for or read. No subagents were spawned or delegated to.

## Actual external primary sources used

1. https://huggingface.co/docs/transformers/v4.44.2/en/model_doc/gpt2
   Read the versioned FlaxGPT2LMHeadModel API, explicit params/train interface, computational dtype versus parameter dtype distinction, and GPT-2 tokenizer/model details.
2. https://huggingface.co/docs/transformers/v4.44.2/en/main_classes/model
   Read the Flax pretrained-loading section, revision behavior, and dtype/saving details.
3. https://huggingface.co/openai-community/gpt2/tree/main
   Confirmed that the public model file listing includes flax_model.msgpack and the tokenizer files. Did not download weights.
4. https://github.com/huggingface/transformers/blob/v4.44.2/src/transformers/modeling_flax_utils.py
   Read relevant source for _do_init=False, params_shape_tree, required parameter paths, missing-weight behavior, and shape checks.
5. https://huggingface.co/transformers/v4.11.1/_modules/transformers/models/gpt2/modeling_flax_gpt2.html
   Read legacy official source for FlaxConv1D stored-kernel orientation, c_attn/c_proj names, attention/position masking, and explicit model params.
   This was used as supplementary architectural context, not represented as proof that the v4.44.2 GPT-2 implementation had been executed or fully inspected. The delivered code validates its loaded target map and shapes.
6. https://arxiv.org/abs/2106.09685
   Read the LoRA paper entry for frozen pretrained weights and low-rank trainable adaptation.
7. https://arxiv.org/html/2305.18290v3
   Read the original DPO paper's objective, reference-policy setup, preference pairs, and supplied implementation/sign.
8. https://optax.readthedocs.io/en/latest/api/generated/optax.losses.softmax_cross_entropy_with_integer_labels.html
   Verified integer-label loss interface and valid vocabulary-index requirement.
9. https://optax.readthedocs.io/en/stable/api/optimizers.html#optax.adamw
   Read optimizer API and update behavior.
10. https://docs.jax.dev/en/latest/notebooks/thinking_in_jax.html
    Read JIT static-shape constraints and synchronized timing guidance.

Search queries also returned secondary articles, Reddit discussions, unrelated papers, current PyTorch Transformers documentation, and an older generic Flax loading document. Those were not used as supporting sources for the answer.

## Retrieval limitations

Several attempts to retrieve the v4.44.2 modeling_flax_gpt2.py source through web open/click returned cache-miss/Internal Error results. A read-only curl retrieval piped to rg produced no source output and exit code 1. I did not treat those failed retrievals as verified source evidence. The official versioned API, loader source, older official architecture source, and runtime target/shape checks are the stated basis.

## Explicit nonexecution

No delivered application/model code was executed. No model was instantiated, no pretrained weight was downloaded, no JAX/Flax/Optax/Transformers dependency was installed, no tensor operation or model training was run, and no benchmark/test result was inferred as passing.

The only Python execution was the required trial_io.py start helper and artifact-text verification after writing, which does not execute the delivered code. Shell commands were read-only inventories/skill reads/source retrievals and literal artifact writes. All application checks in response.txt are future checks or delivered code, not session results.

The proposed dependency pins and hardware compatibility remain untested. The answer makes this limitation explicit.

## Artifact verification

response.txt contains the complete substantive response including the full script.
research-notes.md contains this source/scope/nonexecution record.
The final artifact verification only reads these text files and counts bytes/lines/code fences; it does not import, compile, or execute the script.

