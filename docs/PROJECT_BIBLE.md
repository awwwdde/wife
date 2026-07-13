# PROJECT_BIBLE.md

> Master context for all AI assistants working on **askbrows**.

## Purpose
This document is the single source of truth for the project. Every architectural decision, document, and code change must follow it.

## Product Vision
askbrows is not just a website or CRM. It is a unified ecosystem for beauty professionals combining:
- Public Website
- CRM
- Booking Engine
- Custom Calendar
- Telegram Mini App
- Telegram Bot
- Content Platform
- Analytics

Goal: allow a master to work from one interface instead of using Telegram, DIKIDI, Gallery, Notes and other disconnected tools.

---

# Core Principles

1. Single Source of Truth
2. API First
3. Security First
4. Performance First
5. Mobile First
6. Telegram First
7. Feature-based Architecture
8. Strong Type Safety
9. Clean Architecture
10. Scalable by Design

---

# Technology Stack

Frontend
- React
- TypeScript
- Vite
- Tailwind CSS
- Framer Motion
- GSAP

Backend
- FastAPI
- SQLAlchemy 2
- Alembic
- PostgreSQL
- Redis
- aiogram
- Amazon S3 compatible storage

Infrastructure
- Docker
- Docker Compose
- Nginx

---

# Main Modules

- Website
- CRM
- Booking Engine
- Calendar Engine
- Content Engine
- Media Engine
- Notification Engine
- Review Engine
- Analytics Engine
- Telegram Bot
- Telegram Mini App

---

# Domain Model

Master
Client
Appointment
Booking
Slot
Service
WorkingHours
TimeOff
Reminder
Notification
Review
Content
Media
Publication

Definitions:
- Appointment = calendar record.
- Booking = process of creating appointment.
- Slot = available time interval.
- Content = master work entity.
- Media = original files.
- Publication = publishing content to Website or Telegram.

---

# Architecture Rules

Frontend never contains business logic.

Flow:

Client
→ React
→ REST API
→ Business Engine
→ Database

Never:

Client
→ React
→ Database

Every business feature must be implemented through an Engine.

---

# Backend Structure

backend/
- modules/
  - appointment/
  - booking/
  - client/
  - content/
  - media/
  - review/
  - settings/
- shared/
- core/
- database/
- integrations/
- workers/

Each module contains:
- router
- service
- repository
- schemas
- models
- validators
- events
- tests

---

# Frontend Structure

frontend/
- app
- pages
- widgets
- features
- entities
- shared

Business logic belongs to features/entities.

---

# Documentation Structure

docs/
- PROJECT_BIBLE.md
- ARCHITECTURE.md
- DATABASE.md
- API.md
- SECURITY.md
- TESTING.md
- CRM.md
- WEBSITE.md
- BOT.md
- MINIAPP.md
- CONTENT.md
- DESIGN_SYSTEM.md
- CHANGELOG.md

No duplicated information between documents.

---

# Telegram

Telegram is a first-class platform.

Bot responsibilities:
- reminders
- confirmations
- review requests
- publishing posts
- contact collection

Mini App:
- authentication
- booking
- client cabinet

---

# Content System

One Content entity powers:
- Portfolio
- Website
- Telegram
- Reviews
- Gallery

Never duplicate media.

---

# Performance Goals

- Lighthouse 100
- AVIF/WebP
- Lazy Loading
- Code Splitting
- Brotli
- HTTP/2
- Background Workers

---

# Security

- JWT
- HttpOnly Cookies
- Telegram hash validation
- Rate limiting
- Audit log
- Daily backups
- S3 private storage
- SQL Injection protection
- XSS protection
- CSRF protection

---

# AI Workflow

ChatGPT:
- Product architecture
- Product decisions
- Ideas
- Reviews

Gemini:
- Long documentation
- Specifications
- Business documents

Claude Code:
- Source code
- Refactoring
- Implementation
- Tests

Workflow:
1. Read PROJECT_BIBLE.md
2. Read related documentation.
3. Make changes.
4. Update documentation if architecture changes.

---

# Rules For Any AI

Always:
- preserve architecture
- preserve feature-based structure
- keep backend as source of truth
- keep OpenAPI as API contract
- write strongly typed code
- update docs with code

Never:
- move business logic into frontend
- duplicate data
- bypass engines
- introduce breaking architecture without justification
- replace chosen stack without approval
