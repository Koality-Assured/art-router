# Worktree delegation verification

Status: Active  
Last updated: 2026-08-31  
Scope: art-router delegated mutating work

## Environment quirk

A delegated documentation specialist may write scoped files into the primary checkout even when the prompt names an isolated worktree. Treat primary untracked or modified files as recoverable user work; do not overwrite them during cherry-pick.

## Recovery strategy

After every mutating sidecar returns, inspect `git status --short` on primary and in the claimed worktree. Compare any unexpected primary files byte-for-byte with the specialist branch before staging, removing, or cherry-picking. Preserve identical scoped files through the normal branch commit; investigate any mismatch before continuing.

## Critical success factor

Isolation claims reduce overlap risk but are not proof of write location. Parent-side status, content, and post-merge worktree checks remain mandatory.
