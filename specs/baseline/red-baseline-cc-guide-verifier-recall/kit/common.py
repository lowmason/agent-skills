'''Paths, limits, prompts and the packet table that plan 102's verifier-recall
kit shares (build.py, run.py, and Task 7's fixtures.py and grade.py). Every
value comes from plan 102: PC2, PC9, the Pre-registration and Task 6's
Interfaces block.

R and KIT are module attributes, and k_dir() reads HOME when it is called,
so the tests move all three to a temporary folder. Every module reads them
through this module at call time, never through a copy made at import.'''
import json
import os
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent  # this folder: probe.txt and vr-probe.md (Task 8)
REPO = Path(__file__).resolve().parents[4]  # the repo root
R = Path('/private/tmp/vr102')  # the rep root: R/<rid>/ while rep <rid> runs, then empty again

# Task 7 imports packets, state, settle, probe_checks and probes from here.
# Appended, so a kit module always wins over a module of the same name there.
if str(REPO / 'build' / 'cc_guide') not in sys.path:
    sys.path.append(str(REPO / 'build' / 'cc_guide'))


def k_dir() -> Path:
    '''$K, the kit's scratch folder: plan.json, arms, fixtures, results, homes.'''
    return Path(os.environ['HOME']) / '.cache' / 'agent-skills' / 'scratch' / 'vr102'


# PC9, by packet kind: the --max-budget-usd cap in USD, and the timeout in seconds.
CAPS = {'audit': 10, 'files': 4, 'probe': 1}
TIMEOUTS = {'audit': 60 * 60, 'files': 20 * 60, 'probe': 10 * 60}
BG_CEILING_MS = 4_200_000  # 70 minutes, above the audit timeout (spec D2)
MAX_SPARES = 2  # per packet and arm (PC9)

# V3's markers: a hit in the verifier's injected context is traced by hand.
MARKERS = ('deniedModels', 'availableModels', 'effortLevel', 'README.md:89')

# D5: the tools that reach another session. The probe's init record listed
# them, and a name-only deny rule takes a tool off a session's list. Denying
# them stops a rep calling out, but not another session messaging the rep:
# grade.py's V9 voids a rep whose records hold a peer origin.
CROSS_SESSION_TOOLS = ('ListAgents', 'SendMessage', 'PushNotification', 'RemoteTrigger')

# PC2's --settings, as D5 amends it: no session in a rep has a usable Bash
# tool or a cross-session tool, no Read under the home folder, and Read, Grep
# and Glob stay inside the working folder.
SETTINGS = json.dumps({'permissions': {'deny': ['Bash', 'Read(~/**)', *CROSS_SESSION_TOOLS],
                                       'blockReadsOutsideWorkingDirectories': True}})

# .claude/skills/cc-guide/SKILL.md, "Dispatch, save, settle" step 1's prompt, verbatim.
DISPATCH = ('Mode: {mode}. Packet: {packet}. Read its index.json first, then follow your contract '
            'and return only the report.')
# The main session's prompt (Rep layout): step 1's dispatch, then the report as the reply.
MAIN = ('Call the Agent tool exactly once, with subagent_type cc-guide-verifier, model sonnet, and exactly '
        'this prompt:\n\n{dispatch}\n\nMake no other tool call. When the agent has returned, reply with its '
        'report, unchanged, and nothing else.')

# The Pre-registration's packet table. A master is a path under
# ~/.cache/agent-skills/; Task 7 copies it to $K/fixtures/ and never writes to it.
PACKETS = {
    'audit': {'master': 'cc-guide/packets/20261013T113847-audit', 'mode': 'audit', 'reps': 5},
    'readme': {'master': 'cc-guide/packets/20261013T121854-files/hooks__README.md', 'mode': 'files', 'reps': 3},
    'precision': {'master': 'scratch/vr102/masters/precision/skills__writing-skills__SKILL.md', 'mode': 'files',
                  'reps': 3},
}
PROBE = 'probe'  # the probe rep's packet name: it has no packet copy
ARMS = ('control', 'changed')
CANARY_FIELD = '{canary}'  # probe.txt's placeholder for $K/canary.txt's absolute path


def kind(packet: str) -> str:
    '''The kind that sets a rep's cap and timeout: audit, files or probe.'''
    return PROBE if packet == PROBE else PACKETS[packet]['mode']


def fixture(packet: str, arm: str) -> Path:
    '''The packet copy that a rep of this packet and arm reads (Task 7 writes it).'''
    return k_dir() / 'fixtures' / (f'audit-{arm}' if packet == 'audit' else packet)


def docs_fixture() -> Path:
    '''The copy of the 2.1.296 docs snapshot that audit and probe reps get.'''
    return k_dir() / 'fixtures' / 'docs'
