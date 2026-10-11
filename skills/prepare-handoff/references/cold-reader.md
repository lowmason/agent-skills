# Cold reader: a handoff brief

You are the fresh session this brief will start. Read the brief at
[BRIEF_PATH], then what it points you to in the repository, and nothing else:
no memory, no earlier conversation. Change nothing: this review is read-only.

Read it as the receiver would, and report what would mislead or stall you:

- **contradiction:** two parts, or a part and the artifact, that cannot both
  hold;
- **ambiguity:** a part you could act on in two ways, or a question only the
  owner can answer;
- **trap:** an instruction that would lead you into a mistake;
- **padding:** text that restates the artifact, or what the receiving skill
  already does;
- **overreach:** the sender's reading presented as the owner's words, or a
  decision that goes further than what the owner said.

Make overreach its own pass, one decision at a time. It does not stall you:
you would act on the decision as if the owner had said all of it. Take the
owner's words for the decision (its "You said" field, or its headline when the
brief keeps none apart) and set them beside what the decision asks you to do:
its steps, its done-when conditions, its scope. Go through the decision's own
text sentence by sentence, not only the lines elsewhere in the brief that
mention it, and do not stop at the first hit: a decision can overreach in
several places. For its done-when, ask where the owner's words would let you
stop, and whether the brief makes you do more before you may call it finished.
A step, condition, scope or done-when that the brief takes from an artifact (a
spec, a backlog item, an earlier plan) is the sender's reading unless the brief
shows the owner choosing it: citing the artifact accurately shows what it says,
not what the owner decided, so do not count it as the owner's stopping point.
Report each step, condition or scope that the owner's words do not carry but
the brief states as the owner's decision, as overreach, or as an ambiguity when
the owner may well have meant it.

Report each as one block, numbered from 0:

```
--- [n] contradiction | ambiguity | trap | padding | overreach
DRAFT: <the brief's text, verbatim>
PROBLEM: <what goes wrong for the receiver>
SUGGEST: <replacement text, or the question to put to the owner>
EVIDENCE: <the brief's own lines, or path:line in the repository>
```
