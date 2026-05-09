# План реалізації кваліфікаційної роботи бакалавра — Підгайко С.В.

## Context

Кваліфікаційна робота бакалавра з теми «Розробка інформаційно-аналітичної системи моніторингу й аналізу освітньої діяльності закладів професійної освіти» (керівник — С.О. Семеріков, КДПУ, 014.09 Середня освіта (Інформатика)).

**Поточний стан (станом на 2026-05-09):**
- **Частина 1 (бібліометрична основа)** — чернетка курсової: ~583 рядки LaTeX (≈12–15 стор.), 9 Python-скриптів, набір з 1998 публікацій WoS (1997–2025), VOSViewer карта на 4 кластери. Методологічно цілісна, але у форматі methods-paper без теоретичної рамки, без порівняння з попередніми бібліометричними оглядами та без практичних рекомендацій для України.
- **Частина 2 (системна розробка)** — розділ дисертації **відсутній**, але прототип `project/` доведений до v1.0.0: 8 даних-модулів закривають усі 24 форми Specifikatsiya v2.0, ABAC з JSON-AST, ауді́т із SHA-256 хеш-ланцюгом, ідемпотентні compare-then-write сервіси, 110 тест-файлів (≈14k LOC). Бракує емпіричної валідації, нормативного traceability, порівняння з ІСУО/ЄДЕБО/АІКОМ.

**Ціль плану:** довести обидві частини до рівня, що дозволить **після захисту** подати обидві статті (Частина 1 та Частина 2) у топ-журнали (цільовий орієнтир — Computers & Education або співмірні). Це означає: глибина аналізу, теоретична рамка, емпіричне підтвердження та практичні рекомендації мають вже бути на journal-grade рівні; жорстке форматування під конкретний журнал — після захисту окремою задачею. Кожна частина автономна, з власним набором дослідницьких питань, грунтується на чинній нормативній базі ПТО України (Закон «Про освіту» 2017, Закон «Про професійну (професійно-технічну) освіту» 1998 з останніми редакціями, Specifikatsiya v2.0, DSTU 8302:2015) і теоретично відповідає state-of-the-art (learning analytics, educational data mining, information systems for educational governance).

**Уточнення керівника (2026-05-09):**
- На реальне пілотне впровадження часу немає → емпірична секція Частини 2 будується на синтетичних бенчмарках + **експертному оцінюванні щонайменше 3 експертами** + 1–2 поглиблених half-day сесіях. Усі **input/output матеріали** для експертного оцінювання мають бути підготовлені заздалегідь (форма доступу до прототипу, рубрика, шаблон протоколу, шаблон зведення).
- Multi-LLM cluster naming експеримент масштабується: комерційні — Claude Haiku, Sonnet, Opus (через Anthropic API); відкриті — через Ollama (локально) та OpenRouter (хмара). Дає 6–8 моделей різного класу для повноцінного inter-model agreement аналізу.
- Реальна подача обох статей запланована **після захисту** — план передбачає окремий post-defense backlog для journal-format adaptation, але робота над текстом та аналізом ведеться вже на journal-grade рівні.

**Жорсткі обмеження по файлах:**
- ❌ **Не змінювати** `part1/Курсова/**` — оригінал курсової зберігається як есть. Натомість створюється **новий каталог `bachelor_thesis/`** у корені репозиторію, куди копіюється все необхідне для подальшого вдосконалення (LaTeX каркас, бібліографія, медіа). Усе редагування Частини 1 ведеться там.
- ❌ **Не змінювати** `project/**` — у роботі використовується винятково в режимі **read-only**. Бенчмарки, скрипти експорту метрик, axe-core repor-runner-и — усе живе зовні (наприклад у `bachelor_thesis/scripts/`) і працює з `project/` як з black-box (REST API, БД, файли).
- ✅ Можна змінювати/створювати: `bachelor_thesis/**`, `scripts/**` (зовні project/), `BACKLOG.md`, `context.txt`, `CLAUDE.md`, `part1/Зауваження/transcribed.md`.

**Тематичні наголоси (додано на запит керівника):**
- **Нормативна основа ПТО — лише Закон України «Про професійну освіту» №4574-IX** ([zakon.rada.gov.ua/laws/show/4574-20](https://zakon.rada.gov.ua/laws/show/4574-20)) — новий, заміщує застарілий Закон 1998 р. «Про професійно-технічну освіту». Закон 1998 р. **не цитується** як чинний; може згадуватись виключно у контексті історичної ретроспективи.
- **Воєнний контекст:** робота явно враховує специфіку **переміщених закладів П(ПТ)О** — насамперед Луганської (й суміжних) областей, що евакуйовані до інших регіонів України; як це впливає на моніторинг (територіальна ABAC прив'язка, дублікати юридична-vs-фактична адреса, статус «евакуйований» у формах звітності, специфіка обліку контингенту, що може фізично знаходитися за межами області де діє ЗО).
- **Драйвери реформ ПТО** позиціонуються як: (а) потреби воєнного часу — швидка перепідготовка кадрів для оборонної промисловості, відновлення критичних професій; (б) повоєнне відновлення — реконструкція інфраструктури, інтеграція ветеранів, ВПО; (в) зовнішнє фінансування / гармонізація з ЄС — EU4Skills, EQAVET, Європейська рамка кваліфікацій (EQF), наближення до Copenhagen Process.
- **Джерела 2025–2026 рр.** — пріоритет надавати найсвіжішим публікаціям, нормативним актам, звітам ЄФО/ETF, ОЕСР, World Bank, Cedefop, EU4Skills, EU4VET; шукати україномовні джерела через `https://zakon.rada.gov.ua`, `https://mon.gov.ua`, `https://er.knu.ua`, монографії 2025–2026 рр.

**Формальні обмеження КДПУ (з `common/2025 КР.pdf`):** ≥50 стор. основного тексту + додатки, Times New Roman 12pt, 1.5 інтервал, поля 30/10/10/10 мм, бібліографія DSTU 8302:2015, анотація укр./англ., плагіат <15–20%, захист 10–15 хв.

**Рекомендації керівника, що мають бути виконані:**
1. Багато-LLM (≥3) порівняльний аналіз кластеризації ключових слів VET-моніторингу (Claude / Gemini / Grok / ChatGPT) — обіцяно ще 2025-12-14.
2. Багаторівневий моніторинг (заняття → курс → система; реальний час vs. артефакти) має бути формалізований.
3. Обидві частини мають орієнтуватися на підтримку **управлінських рішень**, а не описовий аналіз.
4. DSTU 8302 у бібліографії, кореляція Time New Roman / форматування, рукописні зауваження `part1/Зауваження/*.jpg` мають бути закриті.

---

## Дослідницькі питання

### Частина 1 — «Bibliometric mapping of VET monitoring research and its implications for Ukrainian VET reform»

- **RQ1.1.** Які тематичні кластери, дослідницькі школи та темпоральні зрушення характеризують глобальну літературу з моніторингу професійної освіти 1997–2025 (n≈1998)?
- **RQ1.2.** Наскільки автоматизована кластеризація (VOSViewer; Python: text-mining + Louvain) та LLM-інтерпретація (Claude / Gemini / Grok / ChatGPT) збігаються між собою та з експертною інтерпретацією?
- **RQ1.3.** Які білі плями (методології, географії, стейкхолдери) існують у глобальній літературі та як їх читати з позиції реформи ПТО України?

### Частина 2 — «Design and evaluation of an information-analytical monitoring system for Ukrainian VET institutions»

- **RQ2.1.** Як декомпозувати 24 форми Specifikatsiya v2.0 у консистентну реляційну модель з ідемпотентним прийомом даних та крос-формовими інваріантами, щоб обмежити false-positive-відмови у чернетках звітів?
- **RQ2.2.** Яка декларативна модель доступу (ABAC vs. RBAC) адекватна територіальній ієрархії «область → район → громада → заклад» з накладеною спеціалізацією інспекторів і чи можна її формально верифікувати?
- **RQ2.3.** Які гарантії невідмовності (audit immutability) забезпечує SHA-256 хеш-ланцюг записів аудиту і як це співвідноситься з вимогами Закону «Про освіту» щодо доказовості освітніх даних?
- **RQ2.4.** На якому рівні зрілості (TRL) знаходиться прототип і які компромісні рішення треба ухвалити для пілотного впровадження в одному ОТГ або одному ЗП(ПТ)О?

---

## Реалізація — Частина 1 (бібліометрика)

### Створення `bachelor_thesis/` (нова папка, не редагувати `part1/Курсова/`)

```
bachelor_thesis/
  Makefile               (адаптовано з template_examples/2/Makefile: make, make clean, make clean-all)
  main.tex               скопійовано з part1/Курсова/main.tex
  setup.sty              скопійовано та адаптовано (DSTU 8302:2015, Times New Roman 12pt)
  capstone.bib, scopus.bib  скопійовано та розширено
  chapters/
    [скопійовано все з part1/Курсова/chapters/ + нові файли:]
    chapter4_implications.tex   новий
    chapter_displaced.tex       новий — переміщені заклади Луганщини як кейс
    chapter_war_recovery.tex    новий — драйвери реформ
  media/                 скопійовано всі рисунки + нові
  data/                  робоча копія (symlinks або копії) релевантних файлів з part1/Дані/
  scripts/               робочі копії аналітичних скриптів (адаптовано шляхи)
  llm_naming/            multi-LLM artifacts (промпти, відповіді, метрики)
```

### Що зберігається з курсової у режимі read-only джерела
- `part1/Курсова/` залишається без змін як **законсервована чернетка** — використовується лише для порівняння та як reference.
- `scripts/` (корінь) — використовується лише для читання як reference; робочі скрипти, що адаптуються під нові шляхи, копіюються у `bachelor_thesis/scripts/`.
- Python-pipeline (копія у `bachelor_thesis/scripts/`):
  - **Виправити шлях** у новій копії `wos_parser.py` (зараз `ROOT_DIR` шукає `savedrecs.txt` у корені — дані живуть у `part1/Дані/`); ввести `DATA_DIR = bachelor_thesis/data` з symlinks на `part1/Дані/`.
  - Додати `bachelor_thesis/scripts/requirements.txt` (pandas, numpy, scipy, scikit-learn, matplotlib, networkx, python-louvain, sentence-transformers, krippendorff, ollama-python, anthropic).
  - Винести thesaurus у `bachelor_thesis/data/thesaurus.tsv` для відтворюваності.

### Що додати

1. **PRISMA 2020 flow-diagram + checklist** (PRISMA сумісний з бібліометричним SLR; включити у методологію + Додаток).
2. **Теоретична рамка** (новий підрозділ у chapter1 або окремий розділ): зведення трьох ліній — (а) educational data mining/learning analytics (Romero & Ventura, 2020+), (б) quality assurance в TVET (Cedefop/EQAVET, OECD), (в) інформаційні системи educational governance (DeLone & McLean reuse, design science research). Це створить лінзу для інтерпретації кластерів і обґрунтує перехід до Частини 2.
3. **Multi-LLM comparative naming experiment** (виконує обіцянку керівника від 2025-12-14):
   - Промпт: 4 кластери з VOSViewer (TLS, occurrences, top-keywords) → попросити кожну модель назвати кластери, дати короткий опис, ідентифікувати домінуючу методологію та провідні школи.
   - **Скоп моделей:**
     - Anthropic API: `claude-haiku-4-5`, `claude-sonnet-4-6`, `claude-opus-4-7` (3 рівні «потужності» в межах одного провайдера — controls for vendor bias)
     - Ollama локально: `llama3.3:70b` або `llama3.1:8b`, `qwen2.5:32b`, `gemma2:27b`, `deepseek-r1:32b` (3–4 моделі різних шкіл)
     - OpenRouter: 1–2 frontier моделі для крос-перевірки (наприклад gpt-oss варіанти, mistral-large)
   - Метрики: (а) cosine similarity назв через sentence-transformers (intra-Claude vs. intra-OS vs. cross-vendor); (б) Krippendorff α між експертом та кожною моделлю; (в) Adjusted Rand Index якщо моделі переприсвоюють ключові слова до кластерів; (г) якісний аналіз дрейфу — які кластери стабільні, які різняться між моделями.
   - **Дослідницький внесок:** показати, що навіть всередині одного вендора (Claude Haiku→Opus) є помітна варіація в інтерпретаціях; крос-вендорна варіація вища; це обґрунтовує необхідність ансамблевого підходу до бібліометричної інтерпретації.
   - Скрипт-артефакт: `scripts/llm_cluster_naming.py` (через `mcp__academic-search` для контексту літератури + кожен LLM-провайдер). Результати — `part1/Дані/llm_cluster_naming/{model}.json`, зведений метричний звіт `agreement_metrics.csv`.
4. **Прив'язка до попередніх оглядів**: систематично знайти через `mcp__academic-search__search_by_topic` та `mcp__plugin_pubmed_PubMed__search_articles` усі бібліометричні / SLR огляди VET monitoring 2010–2025, побудувати порівняльну таблицю «огляд × роки × кластери × n × фокус» (мінімум 8–12 попередніх оглядів) і позиціонуватися щодо них.
5. **Розширення бібліографії** до 70–90 джерел (зараз 32) з акцентом на пост-2020 публікації; забезпечити, що кожен висновок підкріплений ≥2 джерелами.
6. **Розділ «Implications for Ukrainian VET reform»** (новий, ~6–8 стор.):
   - Картування 4 кластерів у структуру Специфікації v2.0 (форми 1.1–7.1) — який кластер яку групу форм інформує.
   - Прив'язка до Закону «Про професійну освіту» №4574-IX (ст. про моніторинг, державний нагляд, забезпечення якості).
   - Практичні рекомендації під 3 групи стейкхолдерів: (а) МОН/обласні департаменти освіти; (б) керівники ЗП(ПТ)О, у т.ч. **переміщених закладів Луганщини** (особливості моніторингу контингенту, що фізично роззосереджений; облік ВПО серед здобувачів освіти; евакуйована матеріально-технічна база); (в) інспектори.

7. **Розділ «Контекст реформ ПТО: воєнний час, повоєнне відновлення, гармонізація з ЄС»** (новий, ~5–6 стор., `chapter_war_recovery.tex`):
   - **Воєнний контекст:** швидка перепідготовка для оборонної промисловості (зварники, оператори БПЛА, кібербезпека); потреби евакуйованих закладів; виклики дистанційного моніторингу за умов цифрової нерівності.
   - **Повоєнне відновлення:** реконструкція інфраструктури ПТО; інтеграція ветеранів та ВПО у програми перепідготовки; критичні професії для відновлення (будівельники, енергетики, медики).
   - **Зовнішнє фінансування / ЄС:** EU4Skills, ETF (European Training Foundation) рекомендації 2024–2026, наближення до EQAVET, Copenhagen Process, EQF mapping; наслідки для національного моніторингу (тривалентність даних: МОН, ETF, donor reports).
   - Зв'язок з 4 бібліометричними кластерами: кластер 1 (Системи/політика) безпосередньо пов'язаний з гармонізацією EQAVET; кластер 2 (Студентські результати) — з відстеженням реінтеграції ветеранів/ВПО; кластери 3–4 (Педагогічна практика / Когнітивні навички) — з перепідготовкою кадрів для критичних галузей.
   - Джерела: пріоритет 2025–2026 рр.; шукати через `mcp__academic-search`, ETF звіти, MON/MES накази, Cedefop briefings.
7. **Розділ обмежень** (extended): мовне зміщення (English-only, виключений ukrainian VET), single-database (WoS), часовий зріз, межі автоматизованої інтерпретації LLM.
8. **Перевід на DSTU 8302:2015** (заміна стилю biblatex + перевірка усіх записів `scopus.bib` + `capstone.bib`).
9. **Анотація** укр./англ. (200–250 слів кожна) — обов'язкова за регламентом КДПУ.

### Цільовий обсяг
~35–40 стор. як розділ + ~8–10 стор. додатків (PRISMA, тезаурус, LLM-промпти/відповіді, повна порівняльна таблиця оглядів, кейс переміщених закладів Луганщини).

### Артефакти (усе в `bachelor_thesis/`, оригінал курсової не чіпається)
- Текст: `bachelor_thesis/chapters/{vstup,chapter1,chapter2,chapter3,chapter4_implications,chapter_displaced,chapter_war_recovery,vysnovky,appendix}.tex`.
- Дані: `bachelor_thesis/llm_naming/{model}.json` + `agreement_metrics.csv` + `prompts.md`; `bachelor_thesis/data/thesaurus.tsv`; `bachelor_thesis/data/prior_reviews.csv`.
- Код: `bachelor_thesis/scripts/llm_cluster_naming.py`, `bachelor_thesis/scripts/prior_reviews_table.py`, `bachelor_thesis/scripts/requirements.txt`, адаптована копія `wos_parser.py` тощо.

---

## Реалізація — Частина 2 (система)

### `project/` — суворо read-only
- Архітектура, схема, ABAC, аудит, Excel-pipeline — заморожені на v1.0.0; жодних правок коду, тестів, документації, конфігів усередині `project/`.
- Бенчмарки і скрипти експорту метрик живуть **зовні**: `bachelor_thesis/scripts/perf_bench.ts`, `bachelor_thesis/scripts/audit_verify_runner.ts`, `bachelor_thesis/scripts/abac_matrix_exporter.ts` — кожен звертається до `project/` як до black-box (HTTP API на порту 3000, БД через psql, файли через mount).
- Якщо потрібен новий тест-сценарій — пишемо його зовні і запускаємо через `npm exec` або тимчасову копію `project/`-а у sandbox; результати зберігаємо у `bachelor_thesis/perf/`.
- Traceability-матриця (форма Specifikatsiya v2.0 → код модуля → файл/функція) живе у `bachelor_thesis/traceability.csv` — будується читанням `project/src/`.

### Розділ дисертації (новий) — підкаталог `bachelor_thesis/part2/`

```
bachelor_thesis/
  part2/
    main.tex                 (окремий buildable документ; поділяє setup.sty з Частиною 1)
    chapters/
      vstup.tex              введення Частини 2 + RQ2.1–2.4
      chapter1_landscape.tex українські системи моніторингу (ІСУО, ЄДЕБО, ДІСО, УЦОЯО, АІКОМ) + EU4Skills цифрові ініціативи: функції, прогалини, чому жодна не закриває потреби обласного моніторингу ПТО, особливо для переміщених закладів
      chapter2_requirements.tex переклад Specifikatsiya v2.0 + чинного законодавства (Закон України «Про професійну освіту» №4574-IX, Закон «Про освіту» 2017, накази МОН) у функціональні/нефункціональні вимоги; traceability-матриця (форма → поле → стаття закону → бізнес-правило → модуль коду)
      chapter3_design.tex    архітектура: модульний моноліт, ABAC JSON-AST, hash-chained audit, ідемпотентні compare-then-write, multi-sheet Excel; design science research positioning (Hevner et al. 2004; оновити свіжими 2024–2026 джерелами); порівняння з альтернативами (мікросервіси, SPA, RBAC); специфічні дизайн-рішення для переміщених закладів (поле «фактична адреса» ≠ «юридична адреса», статус «евакуйований», ABAC-полісі для ВПО-здобувачів)
      chapter4_evaluation.tex евалюація: (а) audit-chain integrity (формальна перевірка через `audit.verify()`); (б) ABAC correctness (матриця role × action × resource, no-bypass invariants); (в) Excel round-trip fidelity; (г) latency/throughput benchmarks на 1k синтетичних закладах; (д) WCAG 2.1 AA звіт; (е) **експертне оцінювання ≥3 експертами** (SUS + домен-специфічні пункти); (є) сценарний walkthrough; (ж) кейс переміщеного закладу
      chapter5_recommendations.tex рекомендації для МОН/обласних департаментів/ЗП(ПТ)О щодо впровадження + дорожня карта 6/12/24 міс. з прив'язкою до пріоритетів воєнного / повоєнного / EU4Skills контекстів
      vysnovky.tex           висновки + майбутні роботи (інтеграції з ЄДЕБО, КЕП-підпис, ML-передбачення відрахувань, інтеграція з ETF reporting)
      appendix.tex           ABAC policy DSL grammar; SQL DDL виборки; traceability-матриця у повному обсязі; e2e a11y-звіт axe-core; рубрика експертного оцінювання + анонімізовані відповіді
    figures/                 архітектурні діаграми (PlantUML/TikZ): C4-context, C4-container, ER-діаграми по модулях, ABAC sequence diagram, audit hash-chain timeline
    perf/                    `perf_report.json`, `axe_report.json` — згенеровані бенчмарками
    expert_eval/             (детально нижче)
```

### Емпіричні твердження, які можна довести без real-world пілоту
- Audit chain integrity на 10k синтетичних upsert (через існуючий тест Phase 3a Task 24).
- ABAC correctness через 100% покриття матриці role × action × resource (вже існує в `tests/modules/*/policies.test.ts`).
- Excel round-trip fidelity (skip-gated тести, треба зняти skip).
- Latency p50/p95/p99 на 1 area, 50 institutions, 1000 students per institution (написати `scripts/perf_bench.ts` + Artillery або k6).
- WCAG 2.1 AA: повний axe-core run на всіх 8 модулях (вже частково є).

### Експертне оцінювання — повний input/output комплект

Усе в `bachelor_thesis/part2/expert_eval/`. Підготовка матеріалів — окремий **Phase 2 task T2.6**, виконується **до** розсилки.

**INPUT (що надається експертам):**
1. `01_invitation_letter.docx` — лист-запрошення, опис мети дослідження, очікувані витрати часу (~60–90 хв), обіцянка анонімізації, NDA-light disclaimer.
2. `02_consent_form.pdf` — інформована згода (українською), згідно з вимогами Закону про академічну доброчесність та GDPR-аналогів.
3. `03_walkthrough_video.mp4` (~10–12 хв) — записаний скрінкаст усіх ключових екранів та сценаріїв системи (директор → інспектор → державний службовець).
4. `04_demo_credentials.txt` — облікові дані для running instance (seeded data: 1 oblast, 3 rayons, 10 hromadas, 5 institutions з різним статусом включно з 1 «евакуйованим»). URL інстансу + 3 акаунти різних ролей.
5. `05_scenario_card.pdf` — 5 типових сценаріїв з кроками: (a) заповнення форми 6.1 директором; (b) імпорт 5-аркушевого Excel-шаблону `students.xlsx`; (c) інспекторська перевірка; (d) обласне зведення; (e) аудит-trail після конфлікту даних.
6. `06_rubric.pdf` — оцінкова рубрика (детально нижче).

**INSTRUMENT — рубрика `06_rubric.pdf`:**
- **Розділ A — System Usability Scale** (10 стандартних пунктів, 5-point Likert).
- **Розділ B — Domain-specific (Ukrainian VET monitoring)** — 8 пунктів, 5-point Likert + free-text:
  - B1. Відповідність полів формам Specifikatsiya v2.0.
  - B2. Зрозумілість крос-формових warnings (наприклад, sum location ≠ contingent).
  - B3. Адекватність ролей та територіальної прив'язки.
  - B4. Придатність для управлінських рішень обласного департаменту.
  - B5. Готовність обліковувати специфіку **переміщених закладів** (юридична vs. фактична адреса, статус «евакуйований»).
  - B6. Готовність обліковувати ВПО та ветеранів серед здобувачів.
  - B7. Очікувана надійність аудит-trail для офіційних звітів.
  - B8. Імовірність впровадження у вашій установі.
- **Розділ C — Open feedback** (вільний текст, 4 пункти):
  - C1. Що було найзручнішим.
  - C2. Що викликало найбільші труднощі.
  - C3. Що бракує для впровадження.
  - C4. Як би ви оцінили готовність до пілоту (TRL 1–9 self-assessment).
- **Розділ D — Метадані респондента** (анонімізована позиція, регіон, стаж, чи представляє переміщений заклад).

**OUTPUT (куди експерти записують відповіді):**
- **Цифровий шлях (recommended):** Google Form / LimeSurvey з пунктами рубрики; результати автоматично експортуються у `bachelor_thesis/part2/expert_eval/raw_responses_<expert_code>.csv`. Шаблон форми та посилання — `expert_eval/form_template.md`.
- **Альтернативний шлях:** заповнюваний PDF `06_rubric_fillable.pdf` → email → конвертація у CSV вручну скриптом `bachelor_thesis/scripts/eval_pdf_to_csv.py`.

**Half-day session output:**
- `09_deep_session_<expert_code>_notes.md` — нотатки спостерігача (формат: timestamp · крок сценарію · поведінка · вербалізація · severity 1–4).
- `10_deep_session_<expert_code>_audio.mp3` (опційно, з дозволу).

**АНАЛІЗ — pipeline і артефакти:**
- `bachelor_thesis/scripts/eval_aggregate.py` зводить усі CSV у `responses_anonymized.csv`, обчислює SUS score (mean, SD, 95% CI), Cronbach α для domain-specific розділу, тематичний кодинг C-feedback.
- Звіт: `bachelor_thesis/part2/expert_eval/summary.md` — числові метрики + якісний кодинг + мапа проблем на модулі коду.
- LaTeX інтеграція: chapter4_evaluation посилається на табличні підсумки (`\input{expert_eval/results_table.tex}`, експортується скриптом).

### Сценарний walkthrough (підкріплення експертної секції)
- Документування 5–7 типових end-to-end сценаріїв з seeded даними (включно з кейсом переміщеного закладу Луганщини). Слугує і як референс для експертів (`05_scenario_card.pdf`), і як ілюстративний матеріал у chapter4_evaluation.

### Цільовий обсяг
Розділ Частини 2 ~30–35 стор. + додатки.

---

## Cross-cutting

### Нормативне підґрунтя (обов'язковий «floor»)
- **Закон України «Про професійну освіту» №4574-IX** ([zakon.rada.gov.ua/laws/show/4574-20](https://zakon.rada.gov.ua/laws/show/4574-20)) — **єдиний** чинний закон про ПТО для цитування. Закон 1998 р. «Про професійно-технічну освіту» **не цитується** як чинний; згадка лише у контексті історичної ретроспективи перебігу реформи.
- Закон «Про освіту» (2017, ред. 2024+) — ст. 48–49 (моніторинг якості освіти), ст. 42 (державний нагляд).
- Закон України «Про академічну доброчесність» №4742-IX (2024) — `common/закон.txt` — задекларувати дотримання, розкрити використання GenAI.
- DSTU 8302:2015 — бібліографічне оформлення.
- Накази МОН про моніторингові форми (Specifikatsiya v2.0).
- Положення КДПУ про кваліфікаційні роботи (`common/2025 КР.pdf`).
- ETF (European Training Foundation), Cedefop briefings 2024–2026, EU4Skills документи — для контексту гармонізації.

Кожна частина має окрему секцію «Нормативно-правова основа» з посиланнями на конкретні статті. Усі посилання на статті закону №4574-IX перевіряються через офіційне джерело zakon.rada.gov.ua перед фіналізацією тексту.

### Tooling

| Інструмент | Де використовується | Коли |
|---|---|---|
| `mcp__academic-search` (`search_by_topic`, `search_papers`, `fetch_paper_details`) | пошук попередніх SLR з VET monitoring; набирання бібліографії | Phase 1 |
| `mcp__arxiv-latex-mcp` (`search`, `get_paper_section`) | пошук методологічних робіт з bibliometrics, EDM, learning analytics, DSR | Phase 1, Phase 2 |
| `mcp__plugin_pubmed_PubMed__search_articles` | додаткова перевірка літератури (vocational training має пересічні теми у health workforce виданнях) | Phase 1 |
| `mcp__huggingface-skills:hf-cli` + `huggingface-papers` | пошук релевантних AI/EDM статей; завантаження embedding-моделей для cosine similarity | Phase 1 |
| `mcp__plugin_context7_context7__query-docs` | актуальна документація (Drizzle, Fastify, BullMQ) для chapter3 design-розділу — щоб посилання на API було поточним | Phase 2 |
| **Anthropic API** (Haiku/Sonnet/Opus) | LLM cluster naming — 3 «рівні потужності» одного вендора | Phase 1 |
| **Ollama** (локально) | LLM cluster naming — 3–4 відкритих моделей (Llama 3.x, Qwen 2.5, Gemma 2, DeepSeek-R1) для крос-вендорного порівняння | Phase 1 |
| **OpenRouter** | 1–2 frontier моделей для cross-check; інші вільні моделі за потреби | Phase 1 |
| Skill: `superpowers:writing-plans` | формалізація під-планів кожного розділу перед написанням | continuous |
| Skill: `superpowers:brainstorming` | розкрутка наративу для нових розділів (chapter4_implications, chapter5_recommendations) | пер-розділ |
| Skill: `superpowers:test-driven-development` | додаткові benchmark-тести у `project/tests/perf/` | Phase 2 |
| Skill: `superpowers:dispatching-parallel-agents` | паралельне написання незалежних розділів (наприклад chapter1+chapter2 Частини 2) | Phase 2 |
| Skill: `code-review:code-review` | фінальний reviewer-pass перед захистом | Phase 3 |
| Skill: `superpowers:verification-before-completion` | перед кожним merge у master — збірка PDF, перевірка citations | continuous |
| `/loop` | довгі ETL-кроки: LLM cluster naming на 6–8 моделях × 4 кластерах × 3 повтори (рандомізація для variance estimation) | Phase 1 |

### Інтеграція superpowers / planning mode
- Кожен великий блок (Частина 1 розширення, Частина 2 написання) виконувати через `superpowers:subagent-driven-development` з paralelní роботою агентів на під-розділах, де це доречно.
- Перед кожним розділом — короткий `superpowers:brainstorming` сесія для уточнення наративу.
- Перед інтеграцією — `superpowers:verification-before-completion` (запуск збірки LaTeX, підрахунок сторінок, перевірка цитувань через `biber --validate-datamodel`).

---

## Фази та контрольні точки

План спроектовано в **зусиллях**, а не жорстких датах (точну дату захисту буде уточнено з керівником). Орієнтовно: 5 фаз, кожна закривається конкретним milestone.

### Phase 0. Готовність та інвентаризація
- [ ] OCR/ручна транскрипція 10 рукописних зауважень `part1/Зауваження/*.jpg` → `part1/Зауваження/transcribed.md` (з прив'язкою до сторінок курсової).
- [ ] Зведений `BACKLOG.md` у корені: пункт ↔ зауваження ↔ розділ-власник ↔ статус.
- [ ] Виправлення шляхів у `scripts/wos_parser.py` + smoke-test усіх 9 скриптів.
- [ ] Узгодження з керівником: дата захисту, склад експертів (≥3 для оцінювання + 1–2 для half-day), формат доступу до прототипу для експертів.
- **Контрольна точка:** chat-узгодження з керівником, оновлений `context.txt`.

### Phase 1. Частина 1 — поглиблення до publication-grade
- [ ] T1.1 PRISMA flow + checklist.
- [ ] T1.2 Огляд попередніх SLR через `mcp__academic-search` + `mcp__arxiv-latex-mcp` + `mcp__plugin_pubmed_PubMed` → порівняльна таблиця ≥8 оглядів.
- [ ] T1.3 Теоретична рамка (EDM/LA, EQAVET, DSR) — новий підрозділ chapter1.
- [ ] T1.4 Multi-LLM cluster naming експеримент: код `scripts/llm_cluster_naming.py`, прогон через 6–8 моделей (3 Claude + 3–4 Ollama + 1–2 OpenRouter), метрики agreement, інтерпретація.
- [ ] T1.5 Розділ «Implications for Ukrainian VET» з картуванням у форми Specifikatsiya v2.0.
- [ ] T1.6 Перехід на DSTU 8302:2015 + розширення bib до 70–90 джерел.
- [ ] T1.7 Анотація укр./англ., оновлений вступ, висновки.
- **Контрольна точка:** Частина 1 чорнова збірка ~30 стор., `pdflatex` + `biber` без warnings, перегляд керівником.

### Phase 2. Частина 2 — написання розділу + експертне оцінювання
- [ ] T2.1 Створення каркасу `bachelor_thesis/part2/` з власним `main.tex` + спільним `setup.sty`.
- [ ] T2.2 Глава 1 «Landscape» — порівняльна таблиця ІСУО/ЄДЕБО/ДІСО/УЦОЯО/АІКОМ + EU4Skills контекст; окрема підсекція про переміщені заклади.
- [ ] T2.3 Глава 2 «Requirements» з traceability-матрицею (стаття Закону №4574-IX → форма Specifikatsiya v2.0 → модуль коду).
- [ ] T2.4 Глава 3 «Design» — DSR positioning, C4-діаграми, ABAC DSL grammar, audit chain proof-sketch, дизайн-рішення для переміщених закладів та ВПО-здобувачів.
- [ ] T2.5 Бенчмарки (зовні від `project/`): `bachelor_thesis/scripts/perf_bench.ts` + axe-core report + audit `verify()` 10k upsert run; результати у `bachelor_thesis/part2/perf/`.
- [ ] T2.6 **Підготовка повного INPUT/OUTPUT-комплекту експертного оцінювання** (інвайт, consent, walkthrough-відео, demo credentials, scenario card, рубрика, Google Form / fillable PDF, шаблон протоколу half-day сесії).
- [ ] T2.7 Розсилка експертам, моніторинг збору відповідей (≥3), проведення 1–2 half-day сесій, агрегація результатів через `bachelor_thesis/scripts/eval_aggregate.py`.
- [ ] T2.8 Глава 4 «Evaluation» — звести синтетичні бенчмарки + експертні дані + сценарні walkthrough + кейс переміщеного закладу.
- [ ] T2.9 Глава 5 «Recommendations» + дорожня карта 6/12/24 міс. з прив'язкою до воєнний/повоєнний/EU контекстів.
- [ ] T2.10 Висновки + додатки (рубрика, анонімізовані відповіді, traceability-матриця) + анотація.
- **Контрольна точка:** Частина 2 чорнова збірка ~30–35 стор., axe-core report у додатку, зведений expert-eval звіт у chapter4, `project/` залишається інтактним.

### Phase 3. Зведення + перевірка + захист
- [ ] T3.1 Об'єднання двох частин у єдиний документ або скоординовані `main.tex` файли зі спільним змістом, анотацією, висновками.
- [ ] T3.2 Закриття всіх рукописних зауважень з `BACKLOG.md`.
- [ ] T3.3 Self-review через `code-review:code-review` (LaTeX) + `superpowers:requesting-code-review` (код).
- [ ] T3.4 Інституційна перевірка плагіату → ціль <15%.
- [ ] T3.5 Електронна подача `Pidhaiko_АП24_КР_2025.pdf` за 2 дні до захисту.
- [ ] T3.6 Захисна доповідь 12–13 хв + слайди (~18 слайдів: 7 на Частину 1, 7 на Частину 2, 1 вступ + 1 висновки + 2 запасних).
- **Контрольна точка:** успішний захист.

### Phase 4 (post-defense, опційно). Адаптація під подачу у журнал
- [ ] T4.1 Carve-out paper version Частини 1: скоротити нормативний UA-floor розділ, посилити methodological novelty (multi-LLM agreement), переформатувати під Computers & Education або Scientometrics; LaTeX → шаблон журналу.
- [ ] T4.2 Carve-out paper version Частини 2: позиціонувати як design science research case study, посилити evaluation секцію (можливо додати реальний пілот, якщо встигаємо), переформатувати під Computers & Education або Information Systems Frontiers.
- **Контрольна точка:** обидва manuscripts submitted.

---

## Verification (як зрозуміти, що готово)

### Частина 1
- LaTeX збірка `pdflatex main.tex && biber main && pdflatex main.tex × 2` — без помилок та warning'ів про missing references.
- ≥30 стор. основного тексту, ≥70 джерел у бібліографії, у тому числі ≥10 пост-2023 публікацій.
- PRISMA-діаграма у chapter1 + чек-лист у додатку.
- `scripts/llm_cluster_naming.py` запускається, дає 4 JSON-файли + метричний звіт; результати інтерпретовано в chapter3.
- Розділ «Implications» картує 4 кластери на ≥10 форм Specifikatsiya v2.0 з конкретними рекомендаціями для 3 груп стейкхолдерів.
- Анотація укр./англ. ≥200 слів кожна.
- Самотест: відкрити `main.pdf`, перевірити що цитування `\cite{*}` усі резолвляться, рисунки нумеруються згідно з GOST/DSTU.

### Частина 2
- LaTeX збірка `part2/main.tex` без помилок.
- ≥30 стор. основного тексту, traceability-матриця покриває всі 24 форми Specifikatsiya v2.0.
- Бенчмарк-звіт `part2/perf_report.json` з p50/p95/p99 latency для 5 типових сценаріїв.
- Audit `verify()` запущено на 10k upsert — інтегральний хеш збігається.
- ABAC матриця тестів зелена (`cd project && npm test -- abac`).
- axe-core e2e suite green (`cd project && npm run test:e2e`).
- Recommendations chapter містить дорожню карту 6/12/24 міс. з конкретними кроками впровадження.

### Зведена робота
- `pdflatex` зведеного документа дає PDF ≥60 стор. основного тексту + додатки.
- Bibliografía DSTU 8302:2015 verified.
- Плагіат <15% за інституційною перевіркою.
- Захисна доповідь у Beamer 12–13 хв з покриттям обох частин.
- Чек-лист 10 рукописних зауважень керівника закритий у `BACKLOG.md`.

---

## Критичні файли (що буде створюватися/правитися)

**Створити (у новому каталозі `bachelor_thesis/`):**
- `bachelor_thesis/Makefile` — `make`, `make clean`, `make clean-all` (адаптовано з `template_examples/2/Makefile`).
- `bachelor_thesis/main.tex`, `bachelor_thesis/setup.sty`, `bachelor_thesis/capstone.bib`, `bachelor_thesis/scopus.bib` — копія з `part1/Курсова/` + адаптації (DSTU 8302:2015, Times New Roman 12pt, 1.5 інтервал).
- `bachelor_thesis/chapters/{vstup,chapter1,chapter2,chapter3,chapter4_implications,chapter_displaced,chapter_war_recovery,vysnovky,appendix}.tex` — копії існуючих + нові розділи.
- `bachelor_thesis/media/` — копії рисунків + нові.
- `bachelor_thesis/data/{thesaurus.tsv,prior_reviews.csv}` + symlinks/copies на потрібні файли з `part1/Дані/`.
- `bachelor_thesis/llm_naming/{model}.json` (по одному на модель) + `agreement_metrics.csv` + `prompts.md`.
- `bachelor_thesis/scripts/{wos_parser.py,llm_cluster_naming.py,prior_reviews_table.py,perf_bench.ts,audit_verify_runner.ts,abac_matrix_exporter.ts,eval_aggregate.py,eval_pdf_to_csv.py,requirements.txt}`.
- `bachelor_thesis/part2/main.tex`, `bachelor_thesis/part2/chapters/*.tex`, `bachelor_thesis/part2/figures/*.tex`.
- `bachelor_thesis/part2/perf/{perf_report.json,axe_report.json,audit_verify.log}`.
- `bachelor_thesis/part2/expert_eval/{01_invitation_letter.docx,02_consent_form.pdf,03_walkthrough_video.mp4,04_demo_credentials.txt,05_scenario_card.pdf,06_rubric.pdf,06_rubric_fillable.pdf,form_template.md,raw_responses_*.csv,deep_session_*_notes.md,responses_anonymized.csv,results_table.tex,summary.md}`.
- `bachelor_thesis/traceability.csv` — нормативно-функціональна матриця.

**Створити (у корені):**
- `BACKLOG.md` — перелік пунктів зауважень + RQ + контрольних точок.
- `part1/Зауваження/transcribed.md` — текстова транскрипція рукописних правок (єдине, що додається в `part1/Зауваження/`).

**Правити (поза `part1/Курсова/` та `project/`):**
- `context.txt` — додати інформацію про нову структуру `bachelor_thesis/` та узгодження дати захисту.
- `CLAUDE.md` (корінь) — додати посилання на план і `bachelor_thesis/`, відобразити жорсткі обмеження «`part1/Курсова/` та `project/` read-only».

**Не чіпати (read-only):**
- `part1/Курсова/**` — оригінал зберігається.
- `part1/Дані/**`, `part1/Транскрипти/**`, `part1/Зауваження/*.jpg` — read-only джерела.
- `project/**` — read-only прототип.
- `common/2025 КР.pdf`, `common/закон.txt` — read-only нормативка.
- `template_examples/**` — read-only зразки.
- `scripts/**` (корінь) — read-only джерело; робочі копії живуть у `bachelor_thesis/scripts/`.

---

## Існуючі утиліти/функції до повторного використання

- `scripts/wos_parser.py:14–96` (read-only джерело) — `parse_wos`, `load_savedrecs`, `load_merged`, `load_vosviewer_map`, `setup_matplotlib`. Скопіювати у `bachelor_thesis/scripts/wos_parser.py` та адаптувати шляхи; не дублювати логіку.
- `scripts/comparison.py` (read-only) — інфраструктура CSV+LaTeX експорту; пере-використати ідіоми у новому `bachelor_thesis/scripts/prior_reviews_table.py`.
- `project/src/modules/audit/service.ts` (read-only, чорна скринька) — викликати `audit.verify()` зовні через HTTP API або через `npm exec` тимчасової копії; не переписувати.
- `project/tests/modules/*/policies.test.ts` (read-only) — матриця ABAC уже є; читати зовні і конвертувати у LaTeX-таблицю через `bachelor_thesis/scripts/abac_matrix_exporter.ts`.
- `template_examples/2/Makefile` — read-only зразок; **скопіювати** (не змінювати оригінал) і адаптувати у `bachelor_thesis/Makefile`.
- `part1/Курсова/main.tex`, `setup.sty`, `chapters/*.tex` — read-only джерело; **скопіювати** у `bachelor_thesis/` як стартову точку.

---

## Відкриті питання (узгоджено 2026-05-09)

1. ✅ Реальне пілотування — не плануємо. Замість цього — формальне експертне оцінювання ≥3 експертами + 1–2 half-day сесії.
2. ✅ Реальна подача обох частин у журнали — після захисту, в окрему фазу (Phase 4).
3. ✅ Multi-LLM скоп: Claude Haiku/Sonnet/Opus + відкриті моделі через Ollama + OpenRouter (загалом 6–8 моделей).
4. ⏳ Точну дату захисту узгодити з керівником на старті Phase 0.
5. ⏳ Склад експертів-оцінювачів (3+ людини) узгодити з керівником на початку Phase 2.
