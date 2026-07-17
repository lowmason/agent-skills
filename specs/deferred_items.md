# Deferred items

logs: /workarea/.claude_config/projects

=== TOTALS across 24 sessions ===
~cost (indicative per-model std rates, NO 1M-ctx premium): $3,000
  main-thread $2,149   subagents $850 (28%)
input-side tokens: 1586.5M   output: 8.39M
cache-READ share of input: 95.6%  (higher = cheaper; reads ~10x under writes, ~100x under fresh input)
output:input ratio: 0.53%  (if tiny, cost is context-read-dominated, not generation)

=== BY MODEL (by ~cost) ===
  $2,562  cacheRead   96%  out  5.46M  claude-opus-4-8
    $422  cacheRead   95%  out  2.71M  claude-sonnet-5
     $15  cacheRead   93%  out  0.22M  claude-haiku-4-5-20251001
      $0  cacheRead    0%  out  0.00M  <synthetic>

=== BY PROJECT (by ~cost) ===
  $2,183  cacheRead   96%  out  6.20M  /workarea/alt-nfp-modeling
    $525  cacheRead   96%  out  1.04M  /workarea/alt-nfp-modeling/.claude/worktrees/plan-39-qcew_in
    $231  cacheRead   96%  out  0.87M  /workarea/alt-nfp-modeling/.claude/worktrees/plan-40-multi_v
     $35  cacheRead   83%  out  0.17M  /workarea/alt-nfp-modeling/packages/nfp-model
     $14  cacheRead   98%  out  0.07M  /workarea/alt-nfp-modeling/packages/nfp-model/src/nfp_model
     $10  cacheRead   88%  out  0.04M  /workarea
      $1  cacheRead  100%  out  0.00M  /workarea/alt-nfp-modeling/.claude/worktrees/plan-40-multi_v

=== BY SKILL (by ~cost) ===
  $2,137  cacheRead   96%  out  5.75M  (none)
    $768  cacheRead   96%  out  2.01M  subagent-driven-development
     $69  cacheRead   97%  out  0.43M  writing-plans
     $13  cacheRead   95%  out  0.10M  brainstorming
      $6  cacheRead   86%  out  0.01M  bloomberg-tools
      $3  cacheRead   98%  out  0.07M  finishing-a-development-branch
      $2  cacheRead   70%  out  0.02M  deferred
      $1  cacheRead   98%  out  0.01M  bls-data-context

=== BY DAY (most recent 14 active) ===
2026-07-10      $549
2026-07-11      $471
2026-07-12      $129
2026-07-13      $553
2026-07-14      $798
2026-07-15      $320
2026-07-16      $169
2026-07-17       $10
