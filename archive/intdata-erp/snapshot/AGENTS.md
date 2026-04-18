<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

⚠️ Сначала прочитайте [repo AGENTS.md](../../../AGENTS.md).

# AGENTS — Intelligent Data ERP

## Allowed scope

- ERP runtime/configuration, vendor integration helpers и ERP-specific docs;
- Odoo/ERPNext compose, auth/integration helpers и deploy scripts;
- standalone ERP contour, живущий вне canonical backend-core.

## Source-of-truth ownership

- `/int/erp` владеет только ERP runtime/config/docs;
- canonical backend-core, shared schema/functions/contracts живут вне repo, прежде всего в `/int/data`;
- machine-wide tooling и host overlays сюда не переносятся как source-of-truth.

## What not to mutate

- не переносить сюда ownership backend-core `/int/data`;
- не хранить реальные `.env`, секреты и mutable runtime-state в git;
- не смешивать ERP contour с ownership чужих product domains.

## Integration expectations

- ERP runtime интегрируется с canonical core и control-plane через внешние APIs/contracts;
- repo остаётся owner-репозиторием ERP deploy/docs слоя;
- ERP-specific configs и vendor adapters живут здесь, а не в shared backend-core.

## Escalation triggers

- попытка сделать `/int/erp` owner shared backend schema/contracts;
- перенос секретов и runtime-state в tracked repo;
- coupling ERP contour и machine-wide tooling как одного owner-контура.

## Lock discipline

- Любые файловые правки в этом snapshot-контуре запрещены без предварительного `lockctl acquire` по конкретному файлу.
- Источник истины по активным локам — только `lockctl`; project-local заметки не подменяют runtime truth.
- После завершения правки лок обязательно снимается через `lockctl release-path` или `lockctl release-issue`.

## Git и завершение работы

- Перед каждым локальным commit обязательно добавить в индекс новые файлы текущего scope и повторно выполнить `git add` для уже staged путей после каждой дополнительной правки; commit по устаревшему состоянию индекса запрещён.
