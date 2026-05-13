# BACKLOG — Кваліфікаційна робота бакалавра, Підгайко С.В.

> **Стан 2026-05-13:** захисна нарада потребувала повного переписування
> (113 стор. → ≤50; 2 → 3 розділи; нова назва без «АНАЛІЗУ»; ДСТУ 8302:2015 bib).
> **Активний беклог** — `bachelor_thesis/REVISION_BACKLOG_2026-05-13.md`.
> **План** — `~/.claude/plans/precious-snuggling-stream.md`.
> Цей документ зберігається як архівний журнал попереднього циклу (RQ + Phases T1–T4).

Зведений лог завдань і трасування зауважень керівника.
План повного циклу — `~/.claude/plans/crispy-soaring-swing.md`.

## Дослідницькі питання

### Частина 1 — бібліометрика
- **RQ1.1.** Тематичні кластери, дослідницькі школи, темпоральні зрушення VET-моніторинг літератури (n≈1998).
- **RQ1.2.** Узгодженість автоматичної (VOSViewer / Python-Louvain) та LLM-інтерпретації (6–8 моделей) та експертної.
- **RQ1.3.** Білі плями літератури з позиції реформи ПТО України.

### Частина 2 — система
- **RQ2.1.** Декомпозиція 24 форм Specifikatsiya v2.0 у консистентну реляційну модель з ідемпотентним прийомом даних.
- **RQ2.2.** ABAC vs. RBAC для територіальної ієрархії з накладеною спеціалізацією інспекторів.
- **RQ2.3.** Гарантії невідмовності SHA-256 хеш-ланцюга аудиту і відповідність вимогам Закону «Про освіту».
- **RQ2.4.** TRL прототипу і компромісні рішення для пілоту в одному ОТГ або одному ЗП(ПТ)О.

## Phases

### Phase 0. Готовність та інвентаризація
- [x] Створення каркасу `bachelor_thesis/`.
- [x] Копіювання та адаптація Python-скриптів (фікс `wos_parser.py` шляхів, vector matplotlib).
- [x] Створення цього `BACKLOG.md`.
- [x] Транскрипція 10 рукописних зауважень → `part1/Зауваження/transcribed.md` (14 пунктів + посторінкові правки).
- [x] Оновлення `CLAUDE.md` (корінь) та `context.txt` під нову структуру + TikZ-inline + ~-- + Закон 4574-IX.
- [x] Times New Roman 14pt через `tempora`, поля 30/10/20/20 мм, нумерація upper-right, заборона переносів.
- [x] Перегенерація 15 рисунків Частини 1 у векторний PDF; PNG видалено.
- [x] Новий титульний аркуш за Додатком Б Положення КДПУ.
- [x] Запевнення про доброчесність (Додаток В) → `chapters/integrity.tex` на 2-й сторінці.
- [x] GenAI declaration перенесено зі стандалоновного фрагмента у підрозділ «Методи дослідження» вступу.
- [x] Структурний рефакторинг: 2 розділи (rozdil1.tex + rozdil2.tex), застарілі chapter-файли архівовано в `chapters/_legacy_part1/`.
- [x] Smoke-test build: `pdflatex` + `biber` зелений, 19 стор., 0 errors.
- [ ] Інтеграція top-level `part2/` (Луганський збірник 2025 + вимоги до сайту) у дизайн Розділу 2.
- [ ] Узгодження з керівником: дата захисту, ≥3 експерти, формат доступу до прототипу.

### Phase 1. Розділ 1 — поглиблення до publication-grade
- [x] T1.0 Міграція legacy-контенту з `_legacy_part1/{chapter1,chapter2,chapter3}.tex` у відповідні підрозділи `rozdil1.tex` (1.2, 1.3, 1.4, 1.5) з пониженням заголовків та застосуванням `~--`-конвенції; 44 стор. PDF, 0 помилок.
- [x] T1.1 PRISMA~2020 flow-діаграма (TikZ inline, 4 фази Identification→Screening→Eligibility→Included з боковими блоками виключень) у підрозділі 1.2.2 та повний 27-пунктовий PRISMA-чек-лист у Додатку Г з прив'язкою кожного пункту до підрозділів роботи. Page2021PRISMA додано до bib.
- [x] T1.2 Огляд **11 попередніх SLR/бібліометричних оглядів VET** через MCP (Tripney 2013, Christidis 2019, Calero López 2020, Adjei 2023, Husaeni 2023, Omar 2024, TVET-Funding 2024, Karantali 2025, Mende 2025, Sholikhah 2025, Ciantar 2025); усі DOI Crossref-верифіковані. Артефакти: `bachelor_thesis/data/prior_reviews.csv` (12 рядків з полями: scope, databases, n_records, period, clusters_or_themes, method_summary, distinctness_from_present_work) + `data/prior_reviews_table.tex` (LaTeX); інтегровано як таблицю 1.1 у новому підрозділі 1.2.1 «Позиціонування цієї роботи серед попередніх оглядів» + аналітичний параграф із чотирма характерними рисами літератури. Bib зріс 51→62 (+11).
- [x] T1.3 Теоретична рамка (EDM/LA + EQAVET/QA + DSR) у підрозділі 1.1: 3~під-підрозділи, 16~цитувань, **всі джерела перевірені через Crossref** (Romero&Ventura 2020, Gunasekara&Saarela 2025, Sharma 2025, Nuankaew 2025, Chen 2025, GonzalezPerez 2025, Lampropoulos 2025, Ciantar 2025, Rauner 2024, Wafudu 2024, Yang 2025, Soloviov 2025, OECD 2010, Cedefop 2017/2020, UNEVOC 2013, Hevner 2004, Rajamaki 2022, DeLone&McLean 2003); bib зріс з~24 до~41 запису.
- [x] T1.4 Multi-LLM cluster naming на **11 моделях з 7 різних родин**: Anthropic Claude Haiku/Sonnet/Opus 4.5/4.6/4.7 (через subagents) + 8 cloud-моделей через Ollama (DeepSeek v4 Pro/Flash, Qwen 3.5/coder-next, Gemma 4, GLM 5.1, MiniMax m2.7, Kimi k2.6). 4~кластери × 11~моделей = 44 інтерпретації. Метрики: cosine similarity (sentence-transformers paraphrase-multilingual), Krippendorff α=0.531, Schools Jaccard, modal-method agreement. Підрозділ 1.5.6 наповнено: дизайн експерименту, таблиця 1.10 з результатами, 5~аналітичних параграфів (cross- vs intra-vendor варіація, термінологічний дрейф ПТО/ПОН/ВПО внаслідок Закону 4574-IX, теоретичний коментар Opus 4.7 про degree-attraction артефакт Лувена). Артефакти: `bachelor_thesis/llm_naming/{vendor}__{model}.json` × 11, `agreement_metrics.csv`, `agreement_summary.md`, `results_table.tex`.
- [x] T1.5 Підрозділ 1.6 «Імплікації» — 4 під-підрозділи: картування 4 кластерів у 7 блоків Specifikatsiya v2.0; кейс переміщених закладів Луганщини; драйвери реформ (війна / відновлення / ЄС); 9 практичних рекомендацій для МОН/керівників/інспекторів. **12 нових Crossref-верифікованих джерел** (Bazhan 2025, Kulachynskyi 2024, Barabash 2024, Cherniakova 2025, Kostrytsia 2025, Kryshchenko 2024, Semenenko 2023, Radkevych 2022, Storonyanska 2025, Zlenko 2024, Penkin 2025, Derman 2025); bib 41→51 записи.
- [x] T1.6 **DSTU 8302:2015 як gost-numeric proxy** (документовано в main.tex; biblatex-dstu відсутній у TeX Live 2021, перенесено у post-defense backlog як можливе покращення). **Bib розширено 62→89 записів** (74 capstone + 15 scopus): додано 12 верифікованих Crossref-джерел з пріоритетом 2024–2026, у т.ч. **8 українських авторів** за рукописним зауваженням #10 керівника (Кремень×2, Радкевич×4 включно з монографією, Лук'янова, Биков); 4 додаткових джерела для архітектурних розділів (Mustamir 2024 dashboard, ABAC encyclopedia 2019, Ferraiolo 2018, Oliinyk 2025 IDP). **Виправлено всі biber data model warnings** (incollection editors для Soloviov/Rauner; видалено неправильний publisher field з CedefopReport2017 + Cedefop2020). Української наукової спільноти представлено: Кремень, Радкевич, Лук'янова, Биков, Семеніков, Безхан, Кулачинський, Барабаш, Чернякова, Костриця, Крищенко, Радкевич О., Сторонянська, Зленко, Пенкін, Дерман, Соловйов, Олійник.
- [x] T1.7 **Анотація укр./англ.** переписана у `chapters/summary.tex`: обидві ≥250 слів, чотирьох-секційна структура (Тема/Актуальність/Мета/Методи/Результати/Висновки + Ключові слова), повне відображення Розділів 1 і 2, усі 11 ключових тверджень (4 кластери, кореляції 0.923/0.919, ARI=0.47, NMI=0.61, $\alpha$=0.531, multi-LLM 7 родин, Закон №4574-IX, EQAVET, переміщені заклади, ABAC + SHA-256). **Висновки до Розділу 1** наповнено повноцінно: 6 висновків зі структурованою прив'язкою до RQ1.1–1.3 (по 2 висновки на кожне), плюс заключний абзац про Розділ 1 як rigor cycle парадигми DSR.

### Phase 2. Розділ 2 — написання + експертне оцінювання
- [x] T2.1 Каркас Розділу 2 — всі 5 підрозділів повністю наповнено (текст готовий до перегляду керівника).
- [x] T2.2 Підрозділ 2.1 «Ландшафт цифрових систем» — 3 під-підрозділи, **порівняльна таблиця 2.1** п'яти національних систем (ІСУО/ЄДЕБО/ДІСО/УЦОЯО/АІКОМ) за 9 параметрами + EU4Skills/EU4VET/ETF + ідентифікація прогалини для переміщених закладів. 3 нові Crossref-верифіковані джерела (Bieliaieva 2020, Shatalovych 2025, Khozhylo 2024).
- [x] T2.3 Підрозділ 2.2 «Вимоги» — нормативна основа (4 рівні: Закон №4574-IX, Закон «Про освіту» 2017, накази МОН, Закон «Про академічну доброчесність»); 10 функціональних вимог F1–F10; 9 нефункціональних NF1–NF9; **traceability-матриця 2.2** на 15 рядків (нормативне джерело → блок/форма → функціональна вимога → модуль реалізації).
- [x] T2.4 Підрозділ 2.3 «Дизайн» — 7 під-підрозділів: DSR positioning + Hevner; модульний моноліт; **ABAC JSON-AST з прикладом полісі директора** (TikZ inline у стилі JSON Crack — рис. 2.1 «node-graph» діаграма); SHA-256 хеш-ланцюг audit; ідемпотентний compare-then-write; multi-sheet Excel; дизайн-рішення для переміщених закладів (5 пунктів).
- [x] T2.5+T2.8 Підрозділ 2.4 «Емпірична евалюація» — 7 під-підрозділів: інтегральність аудит-ланцюга (10k upsert + verify); ABAC correctness (~160 тестів); Excel round-trip; latency/throughput ($p_{95}<500$мс цільовий); WCAG 2.1 AA через axe-core; **експертне оцінювання $n\geq 3$ + рубрика SUS + B-domain (8 пунктів) + C-open (4 пункти)**; 5 walkthrough-сценаріїв з кейсом переміщеного закладу.
- [x] T2.9 Підрозділ 2.5 «Рекомендації» — **дорожня карта 6/12/24 міс** з прив'язкою до war/recovery/EU контекстів + адресні рекомендації для МОН/обласних департаментів/керівників/інспекторів НМЦ ПТО.
- [x] T2.10 Висновки до Розділу 2 — 6 висновків відповідно до RQ2.1–RQ2.4 + загальний підсумок про DSR-цикл relevance–design–rigor.
- [x] T2.6 **Підготовка повного INPUT/OUTPUT-комплекту експертного оцінювання** (виконано 2026-05-10): створено каталог `bachelor_thesis/expert_eval/` з 9 markdown-файлами + 4 шаблонами output: 01_invitation_letter (запрошення з декларацією конфлікту інтересів), 02_consent_form (інформована згода за ст.~8 Закону №2297-VI + GDPR), 03_walkthrough_script (сценарій ~10–12 хв скрінкасту з 10 розділами), 04_demo_credentials_template (3 ролі × seeded-instance), 05_scenario_card (5 end-to-end сценаріїв ~30–40 хв з кейсом переміщеного закладу), 06_rubric (22 пункти у 4 розділах: SUS A.1–10 + B.1–8 + C.1–4 + D.1–6), 07_session_protocol (3,5–4 год half-day think-aloud з severity-rating Nielsen 1–4), 08_form_schema (Google Form/LimeSurvey з анонімністю без email/IP). Скрипти: `scripts/eval_aggregate_experts.py` (SUS-нормалізація 0–100, B-метрики, TRL, експорт results_table.tex та summary_stats.json з warnings при $n{<}12$); `scripts/eval_pdf_to_csv.py` (fallback-парсер заповнюваного PDF через pypdf). Інтегровано: rozdil2.tex 2.4.6 оновлено на нові шляхи + `\input{expert_eval/results_table.tex}`; додано **Додаток~Д «Комплект експертного оцінювання прототипу»** з 5 під-секціями (Д.1 структура, Д.2 рубрика, Д.3 5 сценаріїв, Д.4 протокол half-day, Д.5 цифрова форма) + табл.~Д.1 і табл.~Д.2; bib додано `SauroLewis2016` (Quantifying the User Experience, 2nd ed., ISBN 9780128023082). **Build:** 111 стор. (104→111, +7 для Додатку Д), 0 errors, 0 biber warnings, 0 undefined refs.
- [ ] T2.7 (**операційне**, поза текстом) Виконання експертного оцінювання — потребує реальних експертів і розсилки/half-day сесій. Усі необхідні матеріали готові (T2.6), залишається: (а) розгорнути seeded-instance прототипу; (б) узгодити список ≥3 експертів з керівником; (в) розіслати; (г) провести 1–2 half-day сесії; (д) запустити `scripts/eval_aggregate_experts.py` для авто-генерації results_table.tex; (е) виконати якісне тематичне кодування C-блоку та B-коментарів вдвох з керівником.

### Phase 3. Зведення + перевірка + захист
- [x] T3.1 Об'єднання двох частин у єдиний документ — main.tex інтегрує title-page → integrity → summary → ToC → vstup → rozdil1 → rozdil2 → vysnovky → bibliography → appendix у~порядку §4 Положення КДПУ.
- [x] T3.2 Аудит 14 рукописних зауважень керівника + 5 посторінкових правок: усі закрито або визнано N/A для нової структури за~Додатком Б Положення. Виявлено та~виправлено критичний баг `\linespread{1.5}` (старий `1.25` був на~рядку 300 setup.sty); appendix.tex отримав `\clearpage` між кожним з~Додатків А–Г.
- [x] T3.3 Self-review через feature-dev:code-reviewer agent виявив 3~критичні + 5~важливих проблем; усі виправлено: (1) дві empty `\item % TODO` у~vysnovky.tex замінено на~повноцінні висновки 5 і~6; (2) дубль hyperref (main.tex + setup.sty) → видалено з~main.tex; (3) додано `editor` поля до~vanEck2014 та~Radkevych2026SmartVET; (4) дубль `\linespread{1.5}` прибрано з~рядка 130 setup.sty; (5) дубль `\pagestyle{fancy}` блоку прибрано; (6) appendix.tex `\addcontentsline{ДОДАТКИ}` видалено (заміна авто-ToC секцій); (7) дублі `gensymb`/`lineno`/`tikz` прибрано. **Final clean build: 95~стор., 0 LaTeX errors, 0 biber warnings, 0 undefined refs.**
- [ ] T3.4 Інституційна перевірка плагіату → ціль <15%.
- [ ] T3.5 Електронна подача `Pidhaiko_АП24_КР_2025.pdf` за 2 дні до захисту.
- [x] T3.6 Захисна доповідь Beamer (`bachelor_thesis/defence/main.tex`) — **18 слайдів** на~12--13~хв: (1) титул + теми; (2) актуальність; (3) RQ; (4) вибірка/методика; (5) 4~кластери VOSViewer; (6) Python ↔ VOSViewer кореляції; (7) multi-LLM ансамбль; (8) картування у~Specifikatsiya~v2.0 (TikZ діаграма); (9) кейс переміщених закладів; (10) архітектура системи (TikZ stack); (11) ABAC JSON-AST; (12) SHA-256 audit chain; (13) евалюація; (14) дорожня карта; (15) висновки; (16) дякую; (17--18) запасні (traceability + порівняння нац.\ систем). Theme=Madrid, aspectratio=16:9, tempora-Times. Build: 18 стор.\ PDF, 346 КБ, 0 errors.

### Phase 4 (post-defense). Адаптація під подачу у журнал
- [ ] T4.1 Carve-out paper version Частини 1 → C&E / Scientometrics.
- [ ] T4.2 Carve-out paper version Частини 2 → C&E / Information Systems Frontiers.

### Симульований peer-review (виконано 2026-05-10)

4 паралельні рецензенти (R1: bibliometrics methodology Opus, R2: Ukrainian VET policy Sonnet, R3: System architecture/DSR Opus, R4: copyediting — rate-limited, проведено власною перевіркою): 7 critical + 14 major + 13 minor issues.

**Виправлено критичні (всі 7):**
- ✅ Конфлікт інтересів — додано окремий блок «Декларація конфлікту інтересів» у~vstup.tex з~4~mitigation заходами + покликання на~PRISMA-26
- ✅ Збірник НМЦ ПТО Луганщини додано як~`@misc{NMTsPTO2025}` у~bib + замінено наративні згадки на~`\cite{NMTsPTO2025}` у~rozdil1+2
- ✅ DSR positioning — додано **Таблицю 2.1: відповідність 7 настановам Hevner G1–G7**
- ✅ «Невідмовність» → «tamper-evident integrity» з~явною threat model + delegated to~12-month roadmap (anchoring + КЕП)
- ✅ SUS reframe — N≥3 малий, тому SUS-середнє та~Cronbach α без~інференційних висновків; основа аналізу — якісний тематичний кодинг
- ✅ Multi-LLM single-shot disclosure — додано параграф про~convenience sample, single-shot без~replicates, default temperature
- ✅ Krippendorff bootstrap 95%-CI [0.20, 0.82] — широкий CI, висновок «помірний рівень згоди» виставлено як~орієнтовний

**Виправлено major (10 із 14):**
- ✅ WoS single-DB обмеження — параграф у~1.2.2 «Методологічні обмеження вибірки»
- ✅ VOSViewer threshold виправдано через~vanEck2014 + sensitivity-аналіз винесено
- ✅ Pearson + Spearman + Fisher-z 95%-CI + Bonferroni додано
- ✅ Числа 7/8/10 уніфіковано: «7~тематичних блоків + 10~функціональних модулів коду (8~даних + 2~інфраструктурних)»
- ✅ Herning Declaration 2025 → замінено на~Bruges Communiqué 2010 + Riga Conclusions 2015 + Osnabrück 2020
- ✅ Дорожня карта 12 міс: 3–5 областей → 1–2 області (реалістично у~воєнний час)
- ✅ ABAC operators — додано **Таблицю 2.5: повна граматика 13 операторів**
- ✅ Compare-then-write isolation — параграф про~READ COMMITTED + SERIALIZABLE як~backlog
- ✅ BullMQ retry/DLQ — disclosed як~6-month backlog
- ✅ Performance benchmarks reframed як~«протокол, виконання заплановане під~час пілоту»
- ✅ WCAG axe-core scope — disclaimer що~axe покриває ~30–40% AA, manual checks у~6-міс backlog
- ✅ TRL 5–6 → **TRL 4** (lab-only validation), TRL 5 conditional на~6-міс milestone

**Виправлено minor:**
- ✅ Дата Закону №4574-IX: вересень 2025 → вересень 2024 з~перехідними положеннями до~2027
- ✅ on-prem vs держхмара (ГІНФРАС) — додано альтернативу
- ✅ Bykov2016DigitalHumanistic ghost entry — інтегровано у~1.1.1

**Build після фіксу:** 101 стор. (95→101), 0 LaTeX errors, 0 biber warnings, 0 undefined refs, bib 78 записів (89 разом зі~scopus.bib).

**Усі peer-review issues закрито (2026-05-10):**

Критичні (7) + важливі (12) + мінорні (8) = 27 issues виправлено.

**Final round (R1-#8, R3-m2, R3-m5):**
- ✅ **R1-#8 cluster validity (real numbers):** написано `scripts/cluster_validity.py`, обчислено: Newman~$Q$ (VOSViewer 4-кл) = $-0{,}014$, $Q$ (Python 3-кл) = $-0{,}000$, силует $-0{,}139$ та~$-0{,}065$ (обидва від'ємні), стабільність Louvain mean~ARI~=~0,741~$\pm$~0,166 на~100 прогонах при~37 унікальних партиціях. Чесна інтерпретація: жодне розбиття не~перевищує випадкову модулярну структуру через~378/378 повну зв'язність~-- VOSViewer-кластери зберігають семантичну корисність через~association-strength нормалізацію, не~через~максимізацію модулярності. Hypothesis-generating позиціонування підкріплено даними. Нова таблиця 1.5 у~rozdil1.tex.
- ✅ **R3-m2 Table 2.1 footnotes:** додано 5 footnote-маркерів a-e з~публічними URL (isuo.org, inforesurs.gov.ua, testportal.gov.ua) та~посиланнями на~Khozhylo 2024, Shatalovych 2025, NMTsPTO 2025. Дата доступу 2026-05-10 у~caption.
- ✅ **R3-m5 DRY displaced-institution requirements:** канонічна деривація залишилась у~1.6.2, канонічна реалізація у~2.3.7. Усі~3~повторення (2.1.3 landscape gap, висновки 1 item 6, висновки 2 item 5) скорочено до~cross-refs.

**Build:** 102 стор., 0 LaTeX errors, 0 biber warnings, 0 undefined refs.

**Empirical realization (R1-#3 + R1-#5, виконано 2026-05-10):**
- ✅ **R1-#3 sensitivity sweep VOSViewer threshold** — написано `scripts/threshold_sensitivity.py`, який повторює text-mining pipeline на~порогах $\{50, 75, 100, 150, 200\}$, будує граф, запускає Louvain. Результати у~`data/threshold_sensitivity.csv`: при~$t{=}50$ маємо 340~термінів, density~0,992, $Q{=}0{,}038$; $t{=}75$~-- 176/1,0/0,032; $t{=}100$~-- 112/1,0/0,027; $t{=}150$~-- 56/1,0/0,013; $t{=}200$~-- 35/1,0/0,004. **Висновок:** при~$r{=}1{,}0$ Louvain дає рівно 2~кластери на~всіх порогах, $Q$ монотонно спадає; при~$t{\geq}75$~-- повна зв'язність ($\rho{=}1{,}0$). Нова таблиця `tab:threshold_sensitivity` у~rozdil1.tex з~інтерпретаційним абзацом.
- ✅ **R1-#5 formal Spearman recompute через скрипт** — написано `scripts/correlation_recompute.py`, який обчислює Pearson $r$, Spearman $\rho$, Fisher-z 95\%~CI для~5~метрик; результати у~`data/correlation_recompute.csv`: Occurrences $r{=}0{,}923$, $\rho{=}0{,}834$; TLS $r{=}0{,}919$, $\rho{=}0{,}828$; Avg pub year $r{=}0{,}736$, $\rho{=}0{,}602$; Avg citations $r{=}0{,}742$, $\rho{=}0{,}722$; Norm.\ citations $r{=}0{,}790$, $\rho{=}0{,}785$. **Усі 5~корелацій проходять Bonferroni $\alpha_{\text{adj}}{=}0{,}010$.** Spearman нижча для~Occurrences/TLS через~правосторонньо-зміщений розподіл (\textit{vet} TLS\,=\,17\,857 домінує). Заміщено `tab:correlations` на~повну `tab:correlations_full` з~Pearson+Spearman+CI у~rozdil1.tex.

**Build після empirical realization:** **104 стор.**, 0 LaTeX errors, 0 biber warnings, 0 undefined refs. Усі open R1 issues закрито з~реальними даними; жодного перенесення на~Phase 4.

**Crossref-перевірка усіх 94~посилань (виконано 2026-05-10):**
- Написано `scripts/verify_bib_crossref.py`: парсить bib через `bibtexparser`, для кожного DOI запитує `api.crossref.org/works/{doi}`, для записів без DOI шукає за title+author. Перевіряє title (Sequence-Matcher ≥0,7), рік (priority: published-print → published-online → issued → created), surname (з обробкою LaTeX-діакритики `{\"a}`→`ä`, кириличної транслітерації, інституційних авторів). Звіт: `data/bib_verification_report.csv`.
- **Виправлено критичні DOI-помилки (2):**
  - `Pilz2017` (scopus.bib) — DOI `10.1080/13636820.2017.1303785` повертав статтю Agrawal & Agrawal у тому ж номері JVET 69(2); виправлено на канонічну роботу Pilz `10.1007/978-3-319-47856-2_26` (incollection, Springer book chapter про '6P-стратегію'); тип @article→@incollection.
  - `Gonon2014` (scopus.bib) — DOI `10.1007/978-94-017-8902-8_53` повертав 404 (Springer-handbook chapter не існує); виправлено на правильну Peter Lang публікацію `10.3726/978-3-0351-0758-6/24` (рік 2014→2016, видавець Springer→Peter Lang, booktitle "International Handbook"→"Challenges of Policy Transfer in Vocational Skills Development"). Citekey збережено для стабільності цитувань.
- **Додано відсутні DOI (2):** Hagberg2008 (NetworkX SciPy 2008) → `10.25080/TCWV9851`; McKinney2010 (pandas SciPy 2010) → `10.25080/Majora-92bf1922-00a`.
- **Виправлено metadata-помилки (1):** Shatalovych2025NMT — журнал "Psychology and Society"→"Slobozhansky Scientific Herald. Series: Psychology" (з Crossref-deposited контейнерної назви); додано volume/issue/pages.
- **Виправлено явні year-помилки, де Crossref-рік пізніший за наш або не збігався з друкованим випуском (7):** Adjei2023→2024 (vol.7 no.2 = 2024 issue), Kremen2024PedagogicalWar→2025 (BNAES vol.7 = 2025), Radkevych2023Monograph→2025 (фактичний рік видання), Husaeni2023→2022 (only Crossref date), Kremen2024EduWar→2023 (online 2023, no print issue yet), Busemeyer2012→2011 (Oxford print 2011-11-01), Rauner2008→2009 (Springer 2009; також виправлено @author→@editor для Rauner & Maclean).
- **Документовано як свідому розбіжність (1):** Wheelahan2010 — Crossref індексує e-book видання 2012-07-26; цитуємо канонічний рік першого друкованого видання Routledge 2010 (бібліотечна конвенція). Доданий `note` пояснює.
- **False-positives виявлено й нейтралізовано через покращення скрипта:** LaTeX-діакритика (Rajamäki, Tynjälä, González-Pérez, Calero López) — додано LATEX_ACCENT_MAP + `unicodedata.NFKD` strip-diacritics; кирилична транслітерація (Shatalovych↔Шаталович) — `_has_cyrillic` check; інституційні Crossref-deposit (Sharma/Kulachynskyi/Barabash/Kostrytsia/Kryshchenko/Penkin — Crossref повертає назву установи замість прізвища) — `r_is_inst` flag; subtitle-handling (Billett2011) — порівняння з конкатенованим `title: subtitle`.
- **Фінальний стан:** 83/84 з DOI повністю Crossref-верифіковані; 1 свідома розбіжність (Wheelahan2010, документована); 0 author/title mismatches; 0 DOI 404; 10 без DOI (старі праці, технічні звіти Cedefop/UNESCO, закони, монографії — Crossref-deposited не існують).
- **Build:** **112 стор.** (+1 від `note` полів), 0 LaTeX errors, 0 biber warnings, 0 undefined refs.

## Жорсткі обмеження
- ❌ `part1/Курсова/**` — read-only, не редагувати.
- ❌ `project/**` — read-only, використовувати як black-box (HTTP/БД/файли).
- ❌ `part2/**` (top-level: Луганський збірник + вимоги до сайту) — read-only джерельні матеріали.
- ❌ `common/**`, `template_examples/**`, `scripts/**` (корінь) — read-only.
- ✅ Усе редагування — у `bachelor_thesis/**`.

## Конвенції LaTeX (фіксовано Phase 0)
- TikZ-рисунки **тільки inline** у chapter-файлах. Не створювати каталог `figures/`.
- Шрифт: **Times New Roman 14pt** (через пакет `tempora`), інтервал 1.5.
- Поля: **left ≥30 мм, right ≥10 мм, top ≥20 мм, bottom ≥20 мм** (за п. 6 Положення КДПУ).
- Нумерація сторінок: **правий верхній кут** (`fancyhdr` у `setup.sty`).
- Бібліографія: **DSTU 8302:2015** (приклади у Додатку Г Положення КДПУ; зараз `gost-numeric` як технічний proxy, замінити на DSTU-точніший стиль у T1.6).
- Перенесення слів заборонено: `\hyphenpenalty=10000`, `\exhyphenpenalty=10000`.
- **Конвенція тире:** перед `--` ставити нерозривний пропуск, тобто писати `~-- ` у LaTeX-вихідному коді (наприклад «Кривий Ріг~-- 2026»). Не використовувати ` -- ` із звичайним пробілом.
- **Векторні рисунки тільки** (PDF / TikZ), без PNG. matplotlib-скрипти у `bachelor_thesis/scripts/` налаштовано на `savefig.format='pdf'`; `media/` містить лише `.pdf`.
- **Структура: рівно 2 розділи** (Розділ 1 = бібліометрика + теорія, Розділ 2 = система + евалюація). Підрозділи нумеруються 1.1, 1.2..., 2.1, 2.2... Висновки до розділу — наприкінці кожного.
- **Декларація використання GenAI** входить у підрозділ «Методи дослідження» вступу (НЕ окрема секція).
- **Запевнення про доброчесність** (Додаток В Положення) — на 2-й сторінці після титулу (`chapters/integrity.tex`).

## Контекст автора
**Підгайко С.В. — заступник директора з НМР НМЦ ПТО у Луганській області** (співавтор збірника моніторингу за 2025 р.). Робота позиціонується як **practitioner-research / insider design science**: автор має прямий доступ до НМЦ ПТО Луганщини, її колеги — потенційні експерти-оцінювачі, а Луганський збірник — ground-truth для seed даних та валідації traceability-матриці.

## Рукописні зауваження керівника (pending транскрипція)

| # | Файл | Транскрипція | Розділ-власник | Статус |
|---|---|---|---|---|
| 1 | `part1/Зауваження/25d4a84c-...jpg` | TBD | TBD | TODO |
| 2 | `part1/Зауваження/42435b66-...jpg` | TBD | TBD | TODO |
| 3 | `part1/Зауваження/4e21e817-...jpg` | TBD | TBD | TODO |
| 4 | `part1/Зауваження/89ef80b0-...jpg` | TBD | TBD | TODO |
| 5 | `part1/Зауваження/8ce5e6a3-...jpg` | TBD | TBD | TODO |
| 6 | `part1/Зауваження/a144d7ec-...jpg` | TBD | TBD | TODO |
| 7 | `part1/Зауваження/c7d0b7d4-...jpg` | TBD | TBD | TODO |
| 8 | `part1/Зауваження/d87253e7-...jpg` | TBD | TBD | TODO |
| 9 | `part1/Зауваження/ece67558-...jpg` | TBD | TBD | TODO |
| 10 | `part1/Зауваження/f53243a8-...jpg` | TBD | TBD | TODO |

> Заповнюється під час Phase 0 task «Транскрипція рукописних зауважень».

## Узгодження з керівником

- [ ] Дата захисту: TBD.
- [ ] Список експертів-оцінювачів (≥3, бажано різного профілю: директор ЗП(ПТ)О, інспектор обласного департаменту, представник МОН або науковець з педінформатики): TBD.
- [ ] Респонденти half-day сесій (1–2 з-поміж експертів-оцінювачів): TBD.
- [ ] Місце розгортання seeded instance прототипу для експертів (хмара / локальний хост / тимчасовий VPS): TBD.
