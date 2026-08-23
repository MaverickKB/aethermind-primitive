# Scope

AetherMind is a project-local continuity primitive for AI-assisted work.

Its job is narrow: preserve the working judgment that a future agent needs before
touching the same project. It records decisions, corrections, discoveries,
uncertainty, friction, verification, and relationships between those records.

## 0.2 includes

- the AEM Light v1 project-local format;
- the Python reference engine and command line adapter;
- append-only `layers.aem`, `texture.aem`, `events.aem`, and `archive.aem`
  stores;
- layer, artifact-reference, anchor, pressure-event, supersession, and rollback
  primitives;
- explicit initialization, acknowledged writes, filtered reads, currentness,
  scoped briefs, audit reports, events, and archiving;
- the 0.1 root-first Python API and command names;
- local remote-work notes;
- examples for common agent runners.

## Boundary

AetherMind does not replace a transcript store, task tracker, project manager,
source control system, search index, or hosted memory service.

The primitive remains harness-neutral and data-local. Local project continuity
belongs beside the project source or data. Remote-work continuity can be retained in
a local remote-work store when the target filesystem should remain unchanged.

## What belongs in a layer

Useful layers are compact and consequential:

- a decision and its reason;
- a correction to an earlier assumption;
- a failure mode future agents should recognize;
- uncertainty that changes the next action;
- verification evidence that changes confidence;
- an artifact or anchor relationship;
- an explicit supersession or rollback.

Routine progress, copied transcripts, and generated logs belong elsewhere.
