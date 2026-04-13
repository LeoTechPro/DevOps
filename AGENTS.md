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

## Browser Runtime Inheritance
- Для сессий, стартующих из этого репозитория, default frontend-диагностика и browser-proof выполняются через dedicated Firefox DevTools MCP runtime с persistent profiles.
- Канонический policy, runtime layout и fallback-ограничения задаются только в `/int/AGENTS.md` (раздел `Frontend Browser Runtime Policy`) и наследуются без локальной переинтерпретации.
- Attach к owner Chrome допустим только как documented fallback по blocker-case с явной фиксацией причины в handoff.
# AGENTS — Leonid public site

## Allowed scope

- `standalone-product` личного public-content контура владельца;
- личный сайт, публичные материалы, резюме, docs/lab/edu/archive контент;
- презентационные и контентные изменения внутри этого repo;
- public-facing assets и repo-level docs, относящиеся только к сайту владельца.

## Source-of-truth ownership

- `/int/leonid` остаётся `standalone-product` и владеет только personal/public content владельца;
- не является source-of-truth для family backend-core, product contracts или machine-wide tooling;
- не подменяет ownership других top-level repos в `/int`.

## What not to mutate

- не переносить сюда product-core семейства;
- не смешивать личный сайт и operational/runtime state других проектов;
- не хранить здесь machine-wide tooling как source-of-truth.

## Integration expectations

- сайт может ссылаться на публичные материалы и проекты владельца, но не владеет их runtime;
- любые product/runtime интеграции остаются внешними ссылками, а не ownership-переносом;
- repo остаётся вне архитектуры canonical `intdata core`.
- прямые кодовые импорты из других top-level root-контуров `/int/*` запрещены; любые связи с другими repos оформляются только через public links, public APIs/contracts, documented scripts/hooks/CLI entrypoints или иные явно согласованные boundary contracts.

## Escalation triggers

- попытка разместить здесь product-core или ops-runtime других проектов;
- смешение personal/public content и internal process tooling;
- решения, которые делают repo зависимым owner-контуром family backend.

## Lock discipline

- Любые файловые правки в `/int/leonid` запрещены без предварительного `lockctl acquire` по конкретному файлу.
- Источник истины по активным локам — только `lockctl`; project-local заметки не подменяют runtime truth.
- После завершения правки лок обязательно снимается через `lockctl release-path` или `lockctl release-issue`.

## Docs split

- `README.md` хранит только документацию и инструкции по репозиторию.
- `AGENTS.md` хранит только process/rules/gates/commit-policy этого repo.
- `RELEASE.md` ведётся опционально: обновляется только по прямому запросу владельца или в задаче на подготовку релиз-коммуникации.

## Git и завершение работы

- Перед новой работой в этом git-репозитории агент обязан проверить чистоту дерева и upstream текущей ветки; при clean tree и валидном upstream автоматически выполняется `git pull --ff-only` без дополнительного вопроса владельцу.
- Если дерево грязное, работа ведётся поверх текущего состояния без удаления или перезаписи чужих правок; конфликты и спорные места эскалируются владельцу. Если upstream отсутствует, upstream gone или `git pull --ff-only` требует ручного решения, это фиксируется как git-блокер без auto-sync.
- Любая завершённая правка в `/int/leonid` считается незавершённой, пока в пределах текущей задачи не создан как минимум один локальный commit в этом repo.
- Перед каждым локальным commit обязательно добавить в индекс новые файлы текущего scope и повторно выполнить `git add` для уже staged путей после каждой дополнительной правки; commit по устаревшему состоянию индекса запрещён.
- Перед каждым локальным commit обновление `RELEASE.md` не требуется; по умолчанию source-of-truth изменений — git history (commit subjects/body + diff).
- Релизный пост формируется по запросу из git-истории (commit subjects/body + diff) с ручной редактурой под целевую аудиторию.
- Если в задаче явно нужен релизлог, используем только корневой `RELEASE.md`; исторический `docs/`-путь и другие альтернативные варианты не используем.
- Перед локальным commit агент обязан проверить, не устарел ли корневой `README.md`; если правка меняет описанные там команды, структуру, маршруты, интеграции или инструкции, обновление `README.md` входит в тот же commit.
- Любой push в удалённую ветку `main` допустим только при `ALLOW_MAIN_PUSH=1` и только из локальной `main`.
- Для `/int/leonid` owner-approved git-задача после локального commit и при clean tree должна завершаться немедленной canonical publication в `origin/main`; локальный commit без этой публикации считается промежуточным состоянием, если владелец явно не остановил задачу до push.
- Если canonical publication в `origin/main` завершилась non-zero, задача считается незавершённой до устранения причины и повторного успешного publish.
- Для каждого checkout/worktree обязателен локальный bootstrap `git config core.hooksPath .githooks`; tracked `.githooks/pre-push` включает этот guardrail только после такой настройки и не ограничивает push в `dev` или другие non-main branches.
- `git push` и прочие remote-операции остаются отдельным шагом и не выполняются автоматически без owner approval или явного требования локального процесса.

## Env Policy (Strict)
- В git допускаются только шаблоны `*.env.example` и `*.example`.
- Любые `*.env` и `config/runtime/*.env` запрещены в индексе.
- Runtime-секреты хранятся только вне git (локальные env/secret-store).

## Spec-First Policy
- Главный приоритет любой реализации — согласованная актуальная спека (OpenSpec / approved spec source-of-truth для контура).
- Если спеки нет, она неполная, противоречивая или не фиксирует API/contracts/capability boundaries, сначала нужно довести спеку до согласованного состояния и только потом приступать к реализации.
- Изменения API, RPC, schema contracts, payload shape, capability boundaries и access semantics без зафиксированной и согласованной спеки запрещены.
- Если реализация расходится со спекой, приоритет у спеки; сначала исправляется/уточняется spec-source-of-truth, затем код.
- Любой owner-facing triage обязан явно ответить: какая спека является source-of-truth, полна ли она и разрешает ли текущую реализацию.
