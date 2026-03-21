⚠️ Сначала прочитайте [корневой AGENTS.md](/int/AGENTS.md).

# AGENTS — Leonid public site

## Allowed scope

- личный сайт, публичные материалы, docs/lab/edu/archive;
- контентные и презентационные изменения внутри этого repo.

## Source-of-truth ownership

- `/int/leonid` владеет только личным/public content владельца;
- не является source-of-truth для family backend-core, ops-tooling и product contracts.

## What not to mutate

- не переносить сюда product-core семейства;
- не смешивать личный сайт и operational/runtime state других проектов;
- не описывать здесь canonical ownership чужих репозиториев как локальный source-of-truth.

## Integration expectations

- repo изолирован от canonical `intdata core`;
- любые ссылки на семейство продуктов носят справочный/публичный характер.

## Escalation triggers

- задача просит использовать repo как storage для чужого product-core;
- изменения затрагивают секреты, runtime-state или другие внешние контуры;
- публичный контент подменяется внутренней эксплуатационной документацией.
