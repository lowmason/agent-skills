# Agent mode

Agent mode writes or rewrites text that another agent or a program must parse: prompts, tool descriptions, subagent briefs and error strings. It applies the strict rule set to all of that text. The meaning rules in SKILL.md still outrank every rule here.

## Before a rewrite: scan for six habits

1. **Synonym rotation.** Two words name one thing. Pick one word, and use it every time.
2. **Stacked filler hedges.** "It is important to note that this may potentially help." Remove the filler. Keep a real hedge at the source's confidence.
3. **Nouns made from verbs.** "Perform an analysis of the log." Use the verb: "analyze the log".
4. **Marketing adjectives.** "Seamless", "robust", "powerful". Remove the adjective, or give the measurement that earns the claim.
5. **Run-on sentences.** Two or more facts or instructions share one sentence. Split them.
6. **Soft phrasal verbs.** "Spin up", "reach out", "dive into". Use the single plain verb.

## The strict rule set

- Instructions have 20 words or fewer per sentence. Descriptions have 25 or fewer.
- Write one instruction in each sentence.
- Use the active voice, unless the actor is unknown or not relevant.
- Use no phrasal verbs ("remove", not "take off") and no semicolons.
- Keep noun clusters to 3 words or fewer.
- Drop no words. Keep the subject, the verb and the article.
- Keep modality. Never turn a hedge into a fact.
- Keep one topic in each paragraph, with 6 sentences or fewer.
- Use a numbered or bulleted list for 3 or more steps or conditions.
- Use simple tenses. Keep a compound tense where it carries current relevance or a hedge, and flag it.
- Treat the lexical rules as a direction of travel only. These rules are one word for one meaning, one part of speech for each word, verbs for actions and a glossary for domain terms. Nobody can check them without ASD's dictionary, so the output never claims dictionary compliance.

An instruction tells the reader to do something. A description says what is true. A tool description is a description, even when it names what the tool does. A step in a brief is an instruction.

## Output

- Give the rewritten text alone.
- After it, add one `Kept as-is:` line for each phrase that stayed long to keep its precision, with the reason.
- Flag each compound tense that stays, in the same way.
- When the source has a gap, flag the gap. An example is an action with no condition, or a warning with no instruction. Never fill a gap. A filled gap is a new fact.
- When the request asks for the changes, add a table with the columns Rule, Before and After.

## The linter

Run `<this-skill-dir>/scripts/ste-lint.py` on the draft for a mechanical first pass. It never flags a hedge, and a hedge must stay.
