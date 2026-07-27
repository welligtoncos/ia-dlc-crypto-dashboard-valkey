# Design da Aplicação — Consolidado (revisão)

Arquitetura BFF + Valkey triplo papel (cache, série, broker Celery) + worker/beat + Angular cards + Terraform AWS.

**Invalidado do design anterior:** `MarketIndicatorsService`, `/api/indicators`, tabela, Compose com frontend.

**Válido agora:** `pipeline.py`, `/api/dashboard`, `CardMoeda`, Celery, Compose valkey+backend+worker+beat.

Ver: `components.md`, `component-methods.md`, `services.md`, `component-dependency.md`.
