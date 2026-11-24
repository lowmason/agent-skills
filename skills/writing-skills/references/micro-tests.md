# Running a micro-test

Read this before the first rep of a micro-test or a pressure test. The five steps in SKILL.md say
what to run. This file says how to keep each rep clean and each verdict honest.

## Contents

- Isolate each rep
- Probe the isolation first
- Quarantine the scenario
- Register the rules before you read
- Score blind
- Run each model
- Cap the spend

## Isolate each rep

Start each rep in a new directory outside every repository. Give it no tools unless the test needs
them. Turn off user-level settings, instruction files and memory, so that the rep sees only the
context you planned. This is not full isolation: a rep can still know the user's name.

## Probe the isolation first

Before the first arm, run one probe rep as a pilot. Ask it what context it can see: instruction
files, memory, tools, other sessions and the user's name. An answer you did not plan for means the
setup leaks. Fix it before any scored rep.

## Quarantine the scenario

Keep every file that names the scenario or the pass rule out of each rep's reach: the spec, the
plan, the kit and earlier records. A rep that reads one is void.

## Register the rules before you read

Write down the PASS, FAIL and VOID rules, and commit them, before you read any reply. If a reply
shows a reading that the rules did not foresee, keep the registered verdict and report the counts
under both readings.

## Score blind

Grade from sheets that hide the arm. No file name, path, order or count on a sheet may show which
arm a reply came from. Unblind only after every sheet has its grade.

## Run each model

Run every arm on each model that will run the guidance, with the same number of reps on each. A
wording that binds one model can fail on another.
Name at least two models in the design itself. If the user has not said which, choose two and say so; do not leave the choice open.

## Cap the spend

Before the first rep, set a spend cap and a stop rule, for example: stop when the running total plus
the next batch's worst case would pass the cap. Record each batch's cost as you go.

## In agent-skills

The newest committed kit under `specs/baseline/*/kit/` holds the exact runner flags, the isolation
probe and the scrub.
