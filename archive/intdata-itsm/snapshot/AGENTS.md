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

⚠️ Сначала прочитайте [корневой AGENTS.md](/int/AGENTS.md).

# AGENTS — Intelligent Data ITSM

## Allowed scope

- ITSM/Flowable service layer, BPMN/migrations и related docs;
- ITSM-specific deploy/config helpers;
- standalone runtime contour для tickets/workflows поверх внешнего backend/data-core.

## Source-of-truth ownership

- `/int/itsm` владеет ITSM/Flowable runtime-code и docs;
- canonical backend-core, shared schema/functions/contracts живут вне repo, прежде всего в `/int/data`;
- machine-wide ops/process mirrors не являются ownership этого repo.

## What not to mutate

- не переносить сюда ownership backend-core `/int/data`;
- не хранить реальные секреты, runtime-state и host overlays в git;
- не смешивать ITSM contour с ownership чужих product domains.

## Integration expectations

- repo интегрируется с `/int/data` как с внешним backend/data-core;
- workflow и ticketing integrations оформляются через публичные APIs/contracts;
- `/int/itsm` остаётся owner-репозиторием своего runtime/deploy слоя.

## Escalation triggers

- попытка сделать `/int/itsm` owner shared backend schema/contracts;
- перенос mutable runtime-state и секретов в tracked repo;
- coupling Flowable/ticketing contour и shared family backend ownership.

## Git и завершение работы

- Перед каждым локальным commit обязательно добавить в индекс новые файлы текущего scope и повторно выполнить `git add` для уже staged путей после каждой дополнительной правки; commit по устаревшему состоянию индекса запрещён.
