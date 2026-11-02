# Сервисы для отбора статей по ИИ

Собрано 2026-10-22 по итогам исследования «как решать, что читать из arXiv».
Подробности и источники: https://claude.ai/artifact/HxWw1e53hdkJ4UiRxBeiSC

## 🔎 Ленты и ранжирование

| Сервис | Как ранжирует | Ссылка |
|---|---|---|
| Hugging Face Daily Papers | Отбор вручную (AK) + заявки авторов + голоса сообщества | https://huggingface.co/papers |
| Hugging Face Trending Papers | Популярность + привязка к коду на GitHub; заменил Papers with Code | https://huggingface.co/papers/trending |
| alphaXiv | Активность обсуждений (лайки, комментарии); формула не опубликована | https://www.alphaxiv.org |
| arxiv-sanity-lite (Karpathy) | Похожие на ваши метки, простой классификатор по аннотациям | https://arxiv-sanity-lite.com |
| Scholar Inbox (Тюбинген) | Личная модель по вашим оценкам; точность ~78%, AUC 0,87 | https://www.scholar-inbox.com |
| Semantic Scholar Research Feeds | Похожие на сохранённые вами статьи, ежедневные письма | https://www.semanticscholar.org/faq/what-are-research-feeds |
| Connected Papers | Граф общих ссылок и совместных цитирований | https://www.connectedpapers.com |
| Google Scholar Alerts | Оповещения по ключевым словам и авторам | https://scholar.google.com/scholar_alerts |
| arXiv email / RSS | Ежедневная рассылка по разделам, без ранжирования | https://info.arxiv.org/help/subscribe.html |
| Hacker News | Голоса; доля статей arXiv на главной сильно упала | https://news.ycombinator.com |
| ~~Papers with Code~~ | Закрыт в июле 2025 | — |

## 🤖 Оценка статей с помощью ИИ

| Сервис | Что делает | Ссылка |
|---|---|---|
| gpt_paper_assistant (tatsu-lab) | Список авторов + отсечка по h-индексу + оценка ИИ 1–10 за релевантность и новизну | https://github.com/tatsu-lab/gpt_paper_assistant |
| Фильтр arXiv одним промптом (Quickchat) | ИИ выбирает 3 статьи в день из рассылки arXiv | https://quickchat.ai/post/one-prompt-arxiv-filter.md |
| Stanford Agentic Reviewer | ИИ-рецензия; согласие с людьми ~0,42, как у людей между собой | https://paperreview.ai/tech-overview |
| AI Scientist reviewer (Sakana) | ИИ-рецензент «принять/отклонить»; ~70% против 73% у людей, склонен отклонять | https://arxiv.org/abs/2408.06292 |
| Paper Espresso | Сводки и тренды по популярным статьям arXiv (исследовательский проект) | https://arxiv.org/abs/2604.04562 |

## 📬 Рассылки с ручным отбором

| Рассылка | Фокус | Ссылка |
|---|---|---|
| Davis Summarizes Papers (Blalock) | 600 статей в неделю → 10–20: понимание глубокого обучения, прирост в зрении и текстах | https://dblalock.substack.com |
| Import AI (Jack Clark) | Передний край ИИ и его последствия | https://importai.substack.com |
| Interconnects (Nathan Lambert) | Открытые модели, дообучение, «без хайпа» | https://www.interconnects.ai |
| Ahead of AI (Sebastian Raschka) | Обзоры статей по большим языковым моделям | https://magazine.sebastianraschka.com |
| The Batch (deeplearning.ai) | Еженедельные новости и раздел исследований | https://www.deeplearning.ai/the-batch/ |
| Latent Space | Практичный список чтения для инженеров ИИ | https://www.latent.space/p/2025-papers |
| State of AI Report (Air Street) | Ежегодный обзор + проверка прошлых прогнозов | https://www.stateof.ai |
| a16z AI Canon | Подборка ключевых работ для новичков | https://a16z.com/2023/05/25/ai-canon/ |
