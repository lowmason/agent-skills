---
# cc-guide: rules.rules-files rules.hierarchy @2.1.302
---

# Plain technical English

- Write prose for people about 80% of the way to ASD-STE100 Simplified Technical English.
- Put the main point first. Write one idea in each sentence.
- Aim for 20 words or fewer. Split a sentence above 25 words when the meaning allows.
- Use the active voice when the actor is known.
- Use one name for each thing. Define an unfamiliar term once.
- Do not use semicolons. Do not stack more than 3 nouns.
- Use numbered lists for steps, bullets for separate items and tables only for comparisons.
- Keep paragraphs to 6 sentences or fewer. Do not break a clear sentence only to cut words.
- At the first mention in a reply or a document, give a labeled item's plain meaning beside its label. If the meaning is not available, look it up or say that it is unknown. Never invent it.
- Leave code, commands, identifiers, paths, URLs, API fields and quoted errors unchanged.
- Change existing text only when the user asks.

This rule covers chat replies, Markdown and plain-text documents written for people, commit messages, and PR and issue text. It does not cover code files (comments included), config files, data, quoted text, or agent-facing text: prompts, subagent dispatches, `SKILL.md` and agent or command files, and handoff briefs. When another instruction fixes a format or an exact wording, follow that instruction, and shape only the free prose around it.

To rewrite a text or a document, to write text for an agent reader, or to apply strict STE, use the write-with-asd-ste100 skill.
