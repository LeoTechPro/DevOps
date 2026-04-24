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

## /int Agent Execution Contract

Эти repo-local правила включают прежние machine-wide правила `/int`. `D:\int` — каталог отдельных репозиториев, а не монорепозиторий и не корень проекта.

### Область и режим
- Перед любой задачей определить точную область, репозиторий, режим (`EXECUTE`, `PLAN`, `SPEC-MUTATION`, `FINISH`) и домен.
- По умолчанию разрешены пути `/int/*`; owner-задачи также могут использовать `/home/leon/*`. Всё остальное требует письменного approval владельца.
- Перед началом работы выполнить `whoami`; предположения, влияющие на исполнение, фиксировать как `[ASSUMPTION]`.
- Остановиться и эскалировать, если неясны область, доступ, владелец, состояние локов, git state или обязательная спека.

### Приоритет правил
1. Директивы владельца
2. Доступ и безопасность
3. Контракт выполнения
4. Spec-first policy
5. Git, lock и process gates
6. Правила кодирования
7. Repo-local правила ниже

При конфликте правил следовать более приоритетному правилу и зафиксировать конфликт в handoff.

### Spec-first policy
- Изменения API, schema, contract, auth/RBAC, runtime interface и cross-repo boundaries требуют существующей approved spec до правок кода.
- В `EXECUTE` спеки можно читать, но нельзя переписывать. `SPEC-MUTATION` может менять спеки только с разрешения владельца.
- Если код и спека расходятся, сначала исправить или согласовать spec path; запрещено молча изобретать contract behavior.

### Git, Multica и lock-гейты
- Используй `$agent-issues` как источник истины для Multica issue-дисциплины, runtime `lockctl`, commit-гейты и движения worklog/status.
- Repo-local `AGENTS.md` может добавлять более строгие гейты конкретной области, но не должен дублировать полный Multica workflow.
- Push, deploy и publication требуют явного разрешения владельца или прямой команды `push/publish`.
- Работать только из чистого дерева, если владелец явно не разрешил работу поверх существующих несвязанных изменений; никогда не откатывать и не stage-ить несвязанные изменения пользователя.
### Кодирование и дисциплина изменений
- Делать минимальные точечные правки; сохранять существующую архитектуру, conventions и структуру файлов.
- Не добавлять speculative flexibility, широкие rewrites или unrelated cleanup.
- Перед исправлением воспроизвести или изучить проблему; перед завершением проверить, что запрошенный результат достигнут.
- Не менять production-состояние, не удалять данные, не reset-ить историю и не выполнять разрушительные операции без явного разрешения владельца.

### Процесс, пути и runtime
- Порядок process gates: Intake, Architecture, Implementation, Merge, QA, InfoSec, DevOps, Promotion.
- Не складывать мусор в `/int`; временные файлы должны лежать в `/int/.tmp/<ISO8601>/`.
- Переиспользуемый tooling должен жить в `/int/tools/**`.
- Канонические hosts: prod `vds.punkt-b.pro`, dev `vds.intdata.pro`.
- Канонические пользователи: `intdata` основной, `codex` runtime agent, `leon` manual-only.
- System roles и system tables Supabase нельзя менять.
- Frontend-диагностика и browser-proof по умолчанию идут через внутренний Codex Browser / Browser Use / in-app browser. Fallback только по фактическому blocker: `firefox-devtools`, затем `chrome-devtools`, затем standalone Playwright.
- Если существует repo-local или tooling machine-readable policy file, прочитай его. Если referenced machine policy file отсутствует, зафиксируй это как blocker или assumption, а не считай его доступным.
- Язык коммуникации — русский, если владелец явно не попросил иначе; фиксируй решения, blockers, verification и remaining risks.

## Политика frontend runtime
- Для сессий, стартующих из этого репозитория, default frontend-диагностика и browser-proof выполняются через внутренний Codex Browser / Browser Use / in-app browser.
- Fallback допускается только по blocker-case с явной фиксацией причины в handoff: сначала `firefox-devtools`, затем `chrome-devtools`, затем standalone Playwright.
# AGENTS — Leonid public site

## Allowed scope

- `standalone-product` личного public-content контура владельца;
- личный сайт, публичные материалы, резюме, docs/lab/edu/archive контент;
- презентационные и контентные изменения внутри этого repo;
- public-facing assets и repo-level docs, относящиеся только к сайту владельца.

## Владение источником истины

- `/int/leonid` остаётся `standalone-product` и владеет только personal/public content владельца;
- не является источником истины для family backend-core, product contracts или machine-wide tooling;
- не подменяет ownership других top-level repos в `/int`.

## What not to mutate

- не переносить сюда product-core семейства;
- не смешивать личный сайт и operational/runtime state других проектов;
- не хранить здесь machine-wide tooling как источник истины.

## Интеграционные ожидания

- сайт может ссылаться на публичные материалы и проекты владельца, но не владеет их runtime;
- любые product/runtime интеграции остаются внешними ссылками, а не ownership-переносом;
- repo остаётся вне архитектуры canonical `intdata core`.
- прямые кодовые импорты из других top-level root-контуров `/int/*` запрещены; любые связи с другими repos оформляются только через public links, public APIs/contracts, documented scripts/hooks/CLI entrypoints или иные явно согласованные boundary contracts.

## Триггеры эскалации

- попытка разместить здесь product-core или ops-runtime других проектов;
- смешение personal/public content и internal process tooling;
- решения, которые делают repo зависимым owner-контуром family backend.

## Lock и Multica gates
- Используй `$agent-issues` как источник истины для Multica issue-дисциплины, runtime `lockctl`, commit-гейты и движения worklog/status.
- Любые файловые правки в этом repo запрещены без предварительного `lockctl acquire` по конкретному файлу; после завершения лок обязательно снимается через `lockctl release-path` или `lockctl release-issue`.
- Repo-local правила ниже могут ужесточать git/commit/publish flow, но не должны дублировать полный Multica workflow.
## Разделение документации

- `README.md` хранит только документацию и инструкции по репозиторию.
- `AGENTS.md` хранит только process/rules/gates/commit-policy этого repo.
- `RELEASE.md` ведётся опционально: обновляется только по прямому запросу владельца или в задаче на подготовку релиз-коммуникации.

## Git и завершение работы

- Перед новой работой в этом git-репозитории агент обязан проверить чистоту дерева и upstream текущей ветки; при чистом дереве и валидном upstream автоматически выполняется `git pull --ff-only` без дополнительного вопроса владельцу.
- Если дерево грязное, работа ведётся поверх текущего состояния без удаления или перезаписи чужих правок; конфликты и спорные места эскалируются владельцу. Если upstream отсутствует, upstream gone или `git pull --ff-only` требует ручного решения, это фиксируется как git-блокер без auto-sync.
- Любая завершённая правка в `/int/leonid` считается незавершённой, пока в пределах текущей задачи не создан как минимум один локальный commit в этом repo.
- Перед каждым локальным commit обязательно добавить в индекс новые файлы текущего scope и повторно выполнить `git add` для уже staged путей после каждой дополнительной правки; commit по устаревшему состоянию индекса запрещён.
- Перед каждым локальным commit обновление `RELEASE.md` не требуется; по умолчанию источник истины по изменениям — git history (commit subjects/body + diff).
- Релизный пост формируется по запросу из git-истории (commit subjects/body + diff) с ручной редактурой под целевую аудиторию.
- Если в задаче явно нужен релизлог, используем только корневой `RELEASE.md`; исторический `docs/`-путь и другие альтернативные варианты не используем.
- Перед локальным commit агент обязан проверить, не устарел ли корневой `README.md`; если правка меняет описанные там команды, структуру, маршруты, интеграции или инструкции, обновление `README.md` входит в тот же commit.
- Любой push в удалённую ветку `main` допустим только при `ALLOW_MAIN_PUSH=1` и только из локальной `main`.
- Для `/int/leonid` owner-approved git-задача после локального commit и при чистом дереве должна завершаться немедленной canonical publication в `origin/main`; локальный commit без этой публикации считается промежуточным состоянием, если владелец явно не остановил задачу до push.
- Если canonical publication в `origin/main` завершилась non-zero, задача считается незавершённой до устранения причины и повторного успешного publish.
- Для каждого checkout/worktree обязателен локальный bootstrap `git config core.hooksPath .githooks`; tracked `.githooks/pre-push` включает этот guardrail только после такой настройки и не ограничивает push в `dev` или другие non-main branches.
- `git push` и прочие remote-операции остаются отдельным шагом и не выполняются автоматически без разрешения владельца или явного требования локального процесса.

## Env Policy (Strict)
- В git допускаются только шаблоны `*.env.example` и `*.example`.
- Любые `*.env` и `config/runtime/*.env` запрещены в индексе.
- Runtime-секреты хранятся только вне git (локальные env/secret-store).

## Режимы
- `EXECUTE`: реализация в пределах текущего approved scope без lifecycle-мутаций.
- `PLAN`: планирование без изменения lifecycle и без мутации спецификаций.
- `SPEC-MUTATION`: создание/изменение proposal/spec lifecycle только если задача реально меняет contracts/API/schema/capability boundaries.
- `FINISH`: closing pipeline по локальному diff, checks и handoff без расширения scope.

## Режимные границы
- `EXECUTE`: не открывать lifecycle/spec "на всякий случай"; любые мутации `openspec/**` запрещены без явного разрешения владельца.
- `PLAN`: читать только summary/headers и локальный контекст; любые мутации `openspec/**` запрещены без явного разрешения владельца.
- `SPEC-MUTATION`: применять lifecycle только если задача реально меняет contracts/API/schema/capability boundaries; любая мутация `openspec/**` допускается только по явному разрешению владельца, без самостоятельного "додумывания" несогласованных spec-деталей.
- `FINISH`: опираться только на локальный diff, результаты checks и состояние рабочей зоны; любые мутации `openspec/**` запрещены без явного разрешения владельца.

## Spec-First Policy
- Главный приоритет любой реализации — согласованная актуальная спека (OpenSpec / approved spec source-of-truth для контура).
- Если спеки нет, она неполная, противоречивая или не фиксирует API/contracts/capability boundaries, сначала нужно довести спеку до согласованного состояния и только потом приступать к реализации.
- Изменения API, RPC, schema contracts, payload shape, capability boundaries и access semantics без зафиксированной и согласованной спеки запрещены.
- Если реализация расходится со спекой, приоритет у спеки; сначала исправляется/уточняется spec source-of-truth, затем код.
- Любой owner-facing triage обязан явно ответить: какая спека является источником истины, полна ли она и разрешает ли текущую реализацию.
