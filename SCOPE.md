# Scope

AetherMind is a continuity primitive for AI-assisted work.

Its job is narrow: preserve the small amount of working judgment that future agents need before they touch the same project again. That includes decisions, corrections, uncertainty, friction, verification, and local salience. It is not a transcript store, a task log, a project manager, or a general memory product.

## Product intent

AetherMind gives any agent a common way to write durable continuity beside the work it is doing.

The primitive should be:

- write-first: real work records layers; read/status commands are diagnostic;
- data-local: local project work writes beside the project data/source;
- harness-neutral: the substrate is not tied to Codex, Claude Code, Grok Build, or any other agent runner;
- format-first: the AEM format is the contract; the Python package is the first reference implementation;
- low ceremony: an agent that can run shell commands can initialize a store, write a layer, and validate it.

## v0.1.0 includes

The first public release includes only the pieces needed to prove that primitive:

- AEM v1 format specification;
- Python reference library;
- installed CLI;
- local store initialization;
- layer writing;
- local remote-work notes for customer/remote systems;
- store validation, status, inspect, export, and import commands;
- basic integration recipes for agent runners.

## v0.1.0 does not include

These are intentionally out of scope for the primitive release:

- hosted sync or cloud storage;
- account systems, licensing, billing, or paid product enforcement;
- application-specific identity, salience, orchestration, or coordination infrastructure;
- private evaluation artifacts, generated evidence bundles, or session notes;
- harness-specific architecture or required plugins;
- MCP as the primary adoption path;
- a Node wrapper or language-specific duplicate clients;
- writing `.aethermind/` onto customer or remote systems by default.

## Local and remote boundary

For local project work, `.aethermind/` belongs beside the project source or data being worked.

For customer or remote work, continuity is still written, but by default it is written to a local remote-work store. The remote target is metadata. The primitive should not leave `.aethermind/` artifacts on systems where the operator may not own the persistence policy.

## What belongs in a layer

Good layers are dense and load-bearing:

- a decision and why it matters;
- a correction to a wrong assumption;
- a failure mode future agents must not repeat;
- uncertainty that changes the next step;
- verification evidence that affects confidence;
- a pointer to what should be checked first next time.

Bad layers are noise:

- routine progress logs;
- copied chat transcripts;
- long status reports;
- generated evidence output;
- private operational notes that do not belong in a public project store.

The primitive should make useful continuity cheap without turning the repository into a low-signal archive.
