from __future__ import annotations

import json
import math
import shutil
import sqlite3
from collections import defaultdict
from dataclasses import dataclass
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "archive" / "hecs" / "hecs" / "db.sqlite3"
OUT_DIR = ROOT / "hecs"


COLOR_META = {
    "start": ("Старт", "#ffffff", "#d71920", "#f2f4f0"),
    "geom": ("Геометрия", "#7a5749", "#ffffff", "#eaded8"),
    "str": ("Строки", "#7b1fa2", "#ffffff", "#ead7f1"),
    "data": ("Структуры данных", "#ff9800", "#171717", "#ffe3b0"),
    "sort": ("Сортировки", "#3f51b5", "#ffffff", "#dce2ff"),
    "graph": ("Графы", "#9e9e9e", "#171717", "#eeeeee"),
    "search": ("Поиск", "#ba68c8", "#ffffff", "#efd8f3"),
    "rec": ("Рекурсия", "#d32f2f", "#ffffff", "#f6d4d4"),
    "nums": ("Числа", "#ffeb3b", "#171717", "#fff5a6"),
    "eq": ("Уравнения", "#1976d2", "#ffffff", "#d6e8fb"),
    "dp": ("Динамическое программирование", "#8bc34a", "#17210f", "#e3f1d6"),
    "comb": ("Комбинаторика", "#69f0ae", "#10261a", "#d5fae6"),
}

SUPPLEMENTAL_REFERENCES = {
    535: [
        ("Теория", "Algorithmica", "Линейные уравнения", "https://ru.algorithmica.org/cs/algebra/linear-equations/"),
        ("Практика", "Informatics", "Линейные и квадратные уравнения", "https://informatics.msk.ru/"),
    ],
    611: [
        ("Теория", "Algorithmica", "Метод двух указателей", "https://ru.algorithmica.org/cs/two-pointers/"),
        ("Теория", "Algorithmica", "Meet-in-the-middle", "https://ru.algorithmica.org/cs/meet-in-the-middle/"),
    ],
    620: [
        ("Теория", "Algorithmica", "Префиксные суммы", "https://ru.algorithmica.org/cs/range-queries/prefix-sum/"),
        ("Практика", "Informatics", "Задачи на префиксные суммы", "https://informatics.mccme.ru/"),
    ],
    621: [
        ("Теория", "Algorithmica", "Корневые структуры", "https://ru.algorithmica.org/cs/range-queries/sqrt-structures/"),
        ("Практика", "Informatics", "Корневая эвристика и sqrt-декомпозиция", "https://informatics.mccme.ru/py-source/source/dir/348-17067"),
    ],
    622: [
        ("Теория", "Algorithmica", "Разреженная таблица", "https://ru.algorithmica.org/cs/range-queries/sparse-table/"),
        ("Теория", "CP Algorithms", "Sparse Table", "https://cp-algorithms.com/data_structures/sparse-table.html"),
    ],
    623: [
        ("Теория", "Algorithmica", "Структуры данных STL", "https://ru.algorithmica.org/cs/stl/"),
        ("Практика", "Informatics", "Множества и словари", "https://informatics.mccme.ru/"),
    ],
}


@dataclass(frozen=True)
class Theme:
    id: int
    name: str
    x: int
    y: int
    color: str


def read_data() -> tuple[list[Theme], dict[int, list[dict]], dict[int, dict], dict[int, dict]]:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    themes = [
        Theme(
            id=row["id"],
            name=row["name"],
            x=row["x"],
            y=row["y"],
            color=row["color"],
        )
        for row in con.execute("select id, name, x, y, color from themes_theme order by x, y, id")
    ]
    groups = {
        row["id"]: {"name": row["name"], "icon": row["icon"]}
        for row in con.execute("select id, name, icon from themes_referencegroup order by id")
    }
    targets = {
        row["id"]: {"name": row["name"], "color": row["color"]}
        for row in con.execute("select id, name, color from themes_referencetarget order by id")
    }
    refs: dict[int, list[dict]] = defaultdict(list)
    for row in con.execute(
        """
        select theme_id, group_id, target_id, name, href
        from themes_reference
        order by theme_id, group_id, target_id, id
        """
    ):
        refs[row["theme_id"]].append(
            {
                "group_id": row["group_id"],
                "group": groups[row["group_id"]]["name"],
                "target_id": row["target_id"],
                "target": targets[row["target_id"]]["name"],
                "target_color": targets[row["target_id"]]["color"],
                "name": row["name"],
                "href": row["href"],
            }
        )
    for theme_id, items in SUPPLEMENTAL_REFERENCES.items():
        for group, target, name, href in items:
            refs[theme_id].append(
                {
                    "group_id": 0,
                    "group": group,
                    "target_id": 0,
                    "target": target,
                    "target_color": "",
                    "name": name,
                    "href": href,
                }
            )
    return themes, refs, groups, targets


def page_url(theme_id: int | None, current_id: int | None = None) -> str:
    if theme_id is None:
        return "./" if current_id is None else "../"
    return f"{theme_id}/" if current_id is None else f"../{theme_id}/"


def category(theme: Theme) -> str:
    return COLOR_META.get(theme.color, (theme.color, "", "", ""))[0]


def color_style(theme: Theme) -> str:
    _, bg, fg, edge = COLOR_META.get(theme.color, (theme.color, "#d9ded7", "#16201b", "#edf0ea"))
    return f"--hex-bg:{bg};--hex-fg:{fg};--hex-edge:{edge};"


def neighbors(theme: Theme, by_pos: dict[tuple[int, int], Theme]) -> list[Theme]:
    offsets = [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, 1), (1, -1)]
    found = [by_pos[(theme.x + dx, theme.y + dy)] for dx, dy in offsets if (theme.x + dx, theme.y + dy) in by_pos]
    return sorted(found, key=lambda t: (t.x, t.y, t.name))


def related(theme: Theme, themes: list[Theme], refs: dict[int, list[dict]], by_pos: dict[tuple[int, int], Theme]) -> list[Theme]:
    scores: dict[int, float] = defaultdict(float)
    theme_targets = {r["target_id"] for r in refs.get(theme.id, [])}
    theme_groups = {r["group_id"] for r in refs.get(theme.id, [])}
    for other in themes:
        if other.id == theme.id:
            continue
        dist = abs(other.x - theme.x) + abs(other.y - theme.y)
        if dist:
            scores[other.id] += max(0, 5 - dist) * 0.7
        if other.color == theme.color:
            scores[other.id] += 2.5
        other_targets = {r["target_id"] for r in refs.get(other.id, [])}
        other_groups = {r["group_id"] for r in refs.get(other.id, [])}
        scores[other.id] += len(theme_targets & other_targets) * 1.7
        scores[other.id] += len(theme_groups & other_groups) * 0.8
    for n in neighbors(theme, by_pos):
        scores[n.id] += 4
    by_id = {t.id: t for t in themes}
    return [by_id[i] for i, _ in sorted(scores.items(), key=lambda item: (-item[1], by_id[item[0]].name))[:8]]


def group_refs(items: list[dict]) -> list[tuple[str, list[dict]]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for item in items:
        grouped[item["group"]].append(item)
    order = {"Задачи": 0, "Видео": 1, "Теория": 2}
    return sorted(grouped.items(), key=lambda item: (order.get(item[0], 99), item[0]))


def render_hex_map(themes: list[Theme], selected_id: int | None, current_id: int | None) -> str:
    min_x = min(t.x for t in themes)
    max_x = max(t.x for t in themes)
    min_y = min(t.y for t in themes)
    max_y = max(t.y for t in themes)
    by_pos = {(t.x, t.y): t for t in themes}
    cells: list[str] = []
    for x in range(min_x, max_x + 1):
        row_offset = "is-offset" if x % 2 else ""
        cells.append(f'<div class="hecs-row {row_offset}">')
        for y in range(min_y, max_y + 1):
            theme = by_pos.get((x, y))
            if theme is None:
                cells.append('<span class="hecs-hex hecs-hex--empty" aria-hidden="true"></span>')
                continue
            active = " is-active" if theme.id == selected_id else ""
            label = escape(theme.name)
            refs_count = len(theme_refs[theme.id])
            cells.append(
                f'<a class="hecs-hex hecs-hex--{escape(theme.color)}{active}" '
                f'style="{color_style(theme)}" href="{page_url(theme.id, current_id)}" '
                f'data-theme-card data-title="{label}" data-category="{escape(category(theme))}" '
                f'data-resources="{refs_count}" aria-label="{label}">'
                f'<span>{label}</span>'
                "</a>"
            )
        cells.append("</div>")
    return "\n".join(cells)


def resource_label(count: int) -> str:
    if count == 1:
        return "1 материал"
    if 2 <= count <= 4:
        return f"{count} материала"
    return f"{count} материалов"


def render_resources(theme: Theme, refs: dict[int, list[dict]]) -> str:
    items = refs.get(theme.id, [])
    if not items:
        return '<p class="hecs-muted">Материалы для этой темы пока не добавлены.</p>'
    sections = []
    for group_name, group_items in group_refs(items):
        links = []
        for item in group_items:
            links.append(
                '<a class="hecs-resource" target="_blank" rel="noopener" '
                f'href="{escape(item["href"], quote=True)}">'
                f'<span class="hecs-resource__target">{escape(item["target"])}</span>'
                f'<span>{escape(item["name"])}</span>'
                "</a>"
            )
        sections.append(
            '<section class="hecs-resource-group">'
            f"<h3>{escape(group_name)}</h3>"
            + "\n".join(links)
            + "</section>"
        )
    return "\n".join(sections)


def render_related(title: str, items: list[Theme], current_id: int | None) -> str:
    if not items:
        return ""
    links = [
        f'<a class="hecs-chip" href="{page_url(t.id, current_id)}" style="{color_style(t)}">{escape(t.name)}</a>'
        for t in items
    ]
    return f'<section class="hecs-related"><h3>{escape(title)}</h3><div>{"".join(links)}</div></section>'


def render_start_guide(themes: list[Theme], current_id: int | None) -> str:
    by_name = {theme.name: theme for theme in themes}
    stages = [
        ("1. База", ["START", "Проверка на простоту", "Разложение числа на простые множители", "Системы счисления"]),
        ("2. Структуры", ["Связный список", "Стек", "Очередь", "Очередь с приоритетами"]),
        ("3. Алгоритмы", ["Бинарный поиск в упорядоченном массиве", "Сортировка слиянием", "Динамическое программирование", "Поиск в ширину"]),
    ]
    blocks = []
    for title, names in stages:
        links = []
        for name in names:
            theme = by_name.get(name)
            if theme:
                links.append(f'<a href="{page_url(theme.id, current_id)}" style="{color_style(theme)}">{escape(theme.name)}</a>')
        blocks.append(f'<section><h2>{escape(title)}</h2><div>{"".join(links)}</div></section>')
    return f"""
<div class="hecs-start-guide">
  <p class="hecs-eyebrow">Навигатор</p>
  <h1>С чего начать</h1>
  <div class="hecs-start-levels">
    {"".join(blocks)}
  </div>
</div>
"""


def base_html(title: str, description: str, body: str, current_id: int | None = None) -> str:
    prefix = "../" if current_id is not None else ""
    canonical = "https://leonid.pro/hecs/" if current_id is None else f"https://leonid.pro/hecs/{current_id}/"
    return f"""<!DOCTYPE html>
<html lang="ru">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{escape(title)}</title>
    <meta name="description" content="{escape(description, quote=True)}" />
    <meta name="theme-color" content="#eef1e8" />
    <link rel="canonical" href="{canonical}" />
    <link rel="icon" type="image/svg+xml" href="{prefix}../assets/favicon.svg" />
    <link rel="stylesheet" href="{prefix}assets/hecs.css" />
  </head>
  <body>
    <a class="hecs-skip" href="#hecs-content">К содержимому</a>
    {body}
    <script src="{prefix}assets/hecs.js"></script>
  </body>
</html>
"""


def render_shell(themes: list[Theme], selected: Theme | None, topic: str, current_id: int | None) -> str:
    selected_id = selected.id if selected else None
    site_root = "../" if current_id is None else "../../"
    topic_block = f'<section class="hecs-topic">{topic}</section>' if topic else ""
    page_class = "hecs-layout is-theme" if selected else "hecs-layout is-index"
    return f"""
<header class="hecs-header">
  <a class="hecs-brand" href="{page_url(None, current_id)}">
    <span class="hecs-brand__mark">H</span>
    <span>HECS</span>
  </a>
  <nav class="hecs-topnav" aria-label="Навигация">
    <a href="{page_url(None, current_id)}">Темы</a>
    <a href="{site_root}">leonid.pro</a>
  </nav>
</header>
<main class="{page_class}" id="hecs-content">
  {topic_block}
  <section class="hecs-map-shell" aria-label="Темы HECS">
    <div class="hecs-map" role="navigation" aria-label="Темы HECS">
      {render_hex_map(themes, selected_id, current_id)}
    </div>
  </section>
</main>
"""


def render_index(themes: list[Theme], refs: dict[int, list[dict]], by_pos: dict[tuple[int, int], Theme]) -> str:
    body = render_shell(themes, None, "", None)
    return base_html(
        "HECS - карта учебных тем",
        "Статичная карта учебных тем HECS: олимпиадное программирование, графы, динамика, поиск, сортировки и геометрия.",
        body,
    )


def render_theme_page(theme: Theme, themes: list[Theme], refs: dict[int, list[dict]], by_pos: dict[tuple[int, int], Theme]) -> str:
    if theme.color == "start" or theme.name.upper() == "START":
        topic = render_start_guide(themes, theme.id)
    else:
        topic = f"""
<div class="hecs-topic-card" style="{color_style(theme)}">
  <p class="hecs-eyebrow">{escape(category(theme))} / {escape(theme.name)}</p>
  <div class="hecs-topic-links">
    {render_resources(theme, refs)}
  </div>
</div>
"""
    body = render_shell(themes, theme, topic, theme.id)
    return base_html(
        f"{theme.name} - HECS",
        f"Материалы HECS по теме {theme.name}: учебные ссылки и соседние темы на статической карте.",
        body,
        theme.id,
    )


CSS = r"""
:root {
  --ink: #151d1a;
  --text: #25312d;
  --muted: #65716b;
  --paper: #eef1e8;
  --paper-2: #f8f6ef;
  --panel: rgba(255, 255, 255, 0.86);
  --line: rgba(21, 29, 26, 0.14);
  --line-strong: rgba(21, 29, 26, 0.24);
  --shadow: 0 22px 60px rgba(21, 29, 26, 0.14);
  --body: Arial, Helvetica, sans-serif;
}

*,
*::before,
*::after {
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

body {
  margin: 0;
  min-height: 100vh;
  font-family: var(--body);
  color: var(--ink);
  background:
    linear-gradient(rgba(21, 29, 26, 0.045) 1px, transparent 1px),
    linear-gradient(90deg, rgba(21, 29, 26, 0.045) 1px, transparent 1px),
    linear-gradient(135deg, #eef1e8 0%, #f8f6ef 48%, #e5ece3 100%);
  background-size: 64px 64px, 64px 64px, auto;
}

a {
  color: inherit;
  text-decoration: none;
}

:focus-visible {
  outline: 2px solid #244e73;
  outline-offset: 4px;
}

.hecs-skip {
  position: absolute;
  left: 16px;
  top: 16px;
  z-index: 10;
  transform: translateY(-80px);
  padding: 10px 14px;
  background: var(--ink);
  color: #fff;
  border-radius: 999px;
}

.hecs-skip:focus {
  transform: translateY(0);
}

.hecs-header {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 72px;
  padding: 0 max(24px, 5vw);
  border-bottom: 1px solid var(--line);
  background: rgba(238, 241, 232, 0.88);
  backdrop-filter: blur(18px);
}

.hecs-brand,
.hecs-topnav {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  font-weight: 700;
}

.hecs-brand__mark {
  display: inline-grid;
  place-items: center;
  width: 36px;
  height: 36px;
  background: var(--ink);
  color: #fff;
  clip-path: polygon(25% 6%, 75% 6%, 100% 50%, 75% 94%, 25% 94%, 0 50%);
}

.hecs-topnav a {
  padding: 8px 12px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.48);
}

.hecs-layout {
  min-height: calc(100vh - 72px);
}

.hecs-layout.is-index {
  overflow: hidden;
}

.hecs-topic {
  width: min(1120px, calc(100% - max(32px, 10vw)));
  margin: 0 auto;
  padding: 34px 0 30px;
}

.hecs-topic-card,
.hecs-start-guide {
  --hex-bg: #fff;
  --hex-fg: #16201b;
  padding: 28px 0 20px;
  color: var(--hex-fg);
}

.hecs-topic-card .hecs-eyebrow,
.hecs-start-guide .hecs-eyebrow {
  display: inline-flex;
  min-height: 36px;
  align-items: center;
  padding: 8px 16px;
  border-radius: 999px;
  background: var(--hex-bg);
  color: var(--hex-fg);
}

.hecs-eyebrow {
  margin: 0;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--muted);
}

.hecs-map-shell {
  min-width: 0;
}

.hecs-map {
  overflow: auto;
  min-height: 620px;
  padding: 48px 36px 78px;
  background:
    radial-gradient(circle at 24px 24px, rgba(21, 29, 26, 0.055) 2px, transparent 2px),
    rgba(255, 255, 255, 0.18);
  background-size: 48px 48px;
}

.is-index .hecs-map {
  min-height: calc(100vh - 72px);
  padding-top: 70px;
}

.hecs-row {
  display: flex;
  gap: 4px;
  height: 105px;
}

.hecs-row.is-offset {
  margin-left: 65px;
}

.hecs-hex {
  --hex-bg: #fff;
  --hex-fg: #16201b;
  --hex-edge: #edf0ea;
  flex: 0 0 125px;
  width: 125px;
  height: 130px;
  position: relative;
  display: grid;
  place-items: center;
  padding: 14px;
  clip-path: polygon(50% 0, 100% 23%, 100% 77%, 50% 100%, 0 77%, 0 23%);
  background: var(--hex-bg);
  color: var(--hex-fg);
  text-align: center;
  font-family: Arial, Helvetica, sans-serif;
  font-size: 13px;
  font-weight: 400;
  line-height: 1.08;
  transition: transform 0.16s ease, filter 0.16s ease, opacity 0.16s ease, background 0.16s ease, color 0.16s ease;
}

.hecs-hex span {
  position: relative;
  z-index: 1;
  display: block;
  overflow-wrap: anywhere;
}

.hecs-hex:not(.hecs-hex--empty):hover,
.hecs-hex:not(.hecs-hex--empty):focus-visible,
.hecs-hex.is-active {
  background: #000 !important;
  color: #fff !important;
  transform: translateY(-4px);
  filter: none;
}

.hecs-hex.is-active {
  outline: 4px solid #fff;
  outline-offset: -4px;
}

.hecs-hex--empty {
  visibility: hidden;
  opacity: 0;
  background: transparent;
  pointer-events: none;
}

.hecs-resource-group {
  margin-top: 22px;
}

.hecs-resource-group h3 {
  margin: 0 0 10px;
  font-size: 15px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
}

.hecs-resource {
  display: flex;
  align-items: center;
  gap: 14px;
  margin: 8px 0;
  padding: 10px 14px;
  border: 2px solid var(--hex-bg);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.62);
  color: var(--ink);
  text-decoration: none;
  transition: background 0.16s ease, color 0.16s ease, transform 0.16s ease;
}

.hecs-resource:hover,
.hecs-resource:focus-visible {
  background: #000;
  color: #fff;
  transform: translateX(4px);
}

.hecs-resource__target {
  color: var(--muted);
  font-weight: 800;
  text-transform: uppercase;
  font-size: 12px;
}

.hecs-start-levels {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin-top: 20px;
}

.hecs-start-levels section {
  padding: 18px;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.6);
}

.hecs-start-levels h2 {
  margin: 0 0 12px;
  font-size: 20px;
}

.hecs-start-levels div {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.hecs-start-levels a {
  --hex-bg: #fff;
  --hex-fg: #16201b;
  padding: 8px 12px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: color-mix(in srgb, var(--hex-bg) 34%, #fff);
  color: var(--ink);
  font-size: 13px;
  font-weight: 800;
}

.hecs-muted {
  color: var(--muted);
}

@media (max-width: 980px) {
  .hecs-topic {
    width: calc(100% - 32px);
    padding-top: 28px;
  }

  .hecs-start-levels {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .hecs-header {
    align-items: flex-start;
    flex-direction: column;
    padding-top: 14px;
    padding-bottom: 14px;
  }

  .hecs-layout {
    min-height: calc(100vh - 104px);
  }

  .hecs-map {
    padding: 34px 18px 52px;
  }

  .hecs-row {
    height: 92px;
  }

  .hecs-row.is-offset {
    margin-left: 54px;
  }

  .hecs-hex {
    flex-basis: 108px;
    width: 108px;
    height: 112px;
    padding: 14px;
    font-size: 12px;
  }

  .hecs-resource {
    align-items: flex-start;
    flex-direction: column;
    gap: 4px;
  }
}
"""


JS = r"""
const map = document.querySelector(".hecs-map");
const activeCard = document.querySelector(".hecs-hex.is-active");

if (map && activeCard) {
  const mapBox = map.getBoundingClientRect();
  const activeBox = activeCard.getBoundingClientRect();
  map.scrollLeft += activeBox.left - mapBox.left - mapBox.width / 2 + activeBox.width / 2;
}
"""


theme_refs: dict[int, list[dict]] = {}


def main() -> None:
    global theme_refs
    themes, refs, _groups, _targets = read_data()
    theme_refs = refs
    by_pos = {(t.x, t.y): t for t in themes}

    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    (OUT_DIR / "assets").mkdir(parents=True)

    (OUT_DIR / "assets" / "hecs.css").write_text(CSS.strip() + "\n", encoding="utf-8")
    (OUT_DIR / "assets" / "hecs.js").write_text(JS.strip() + "\n", encoding="utf-8")
    data = {
        "themes": [theme.__dict__ for theme in themes],
        "references": refs,
    }
    (OUT_DIR / "assets" / "hecs-data.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    (OUT_DIR / "index.html").write_text(render_index(themes, refs, by_pos), encoding="utf-8")
    for theme in themes:
        theme_dir = OUT_DIR / str(theme.id)
        theme_dir.mkdir(parents=True)
        (theme_dir / "index.html").write_text(render_theme_page(theme, themes, refs, by_pos), encoding="utf-8")

    print(f"Generated {len(themes) + 1} HECS pages in {OUT_DIR}")


if __name__ == "__main__":
    main()
