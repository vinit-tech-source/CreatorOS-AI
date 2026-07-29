# 04 Database Design

# CreatorOS AI
# Database Design

**Version:** 1.3 (Final)

**Document Type:** Database Design Document

**Status:** Completed

**Database:** PostgreSQL

**ORM:** SQLAlchemy

**Migration Tool:** Alembic

---

# 1. Purpose

This document defines the complete, production-ready relational database architecture for CreatorOS AI.

The database is designed to support:
- Multi-tenant SaaS architecture (Organizations & Users)
- Workspace and BrandKit management
- Multiple connected social media platforms
- AI workflow orchestration and agent execution
- Brand-aware content generation with versioning
- Scheduling, publishing, and approval flows
- Historical time-series analytics
- Comprehensive auditability

The design follows modern relational database best practices and is optimized for scalability, maintainability, and data integrity.

---

# 2. Design Principles

The database adheres to the following principles:
- Third Normal Form (3NF)
- ACID Compliance
- Referential Integrity (strict Foreign Keys)
- UUID Primary Keys
- Soft Deletes (where necessary)
- Audit Columns
- Future-Proof Multi-Tenant Architecture

---

# 3. Final Database Modules

```text
CreatorOS AI Database

├── Authentication
│   ├── Organization
│   ├── User
│   ├── UserSession
│   └── AuditLog
│
├── Workspace
│   ├── Workspace
│   └── BrandKit
│
├── Social Media
│   ├── Platform
│   ├── SocialAccount
│   └── APICredential
│
├── Content
│   ├── ContentProject
│   ├── GeneratedPost
│   ├── PostVersion
│   ├── MediaAsset
│   └── Approval
│
├── Publishing
│   ├── Schedule
│   └── PublishingLog
│
├── Analytics
│   └── AnalyticsSnapshot
│
└── AI
    ├── AIModel
    ├── AIAgent
    ├── AIJob
    └── PromptExecution
```

**Total Tables:** 21

---

# 4. Entity List

| Module | Tables | Count |
|--------|--------|-------|
| Authentication | Organization, User, UserSession, AuditLog | 4 |
| Workspace | Workspace, BrandKit | 2 |
| Social Media | Platform, SocialAccount, APICredential | 3 |
| Content | ContentProject, GeneratedPost, PostVersion, MediaAsset, Approval | 5 |
| Publishing | Schedule, PublishingLog | 2 |
| Analytics | AnalyticsSnapshot | 1 |
| AI | AIModel, AIAgent, AIJob, PromptExecution | 4 |
| **Total** | | **21** |

---

# 5. Authentication Module

## Organization
Supports Companies, Agencies, Teams, and Multiple creators.
- id
- name
- slug
- owner_id
- plan
- created_at
- updated_at

## User
- id
- organization_id
- full_name
- email
- password_hash
- avatar_url
- role
- is_verified
- is_active
- created_at
- updated_at
- deleted_at

## UserSession
- id
- user_id
- refresh_token
- device
- ip_address
- expires_at
- created_at

## AuditLog
- id
- user_id
- action
- entity
- entity_id
- timestamp

---

# 6. Workspace Module

## Workspace
- id
- user_id
- name
- niche
- description
- timezone
- default_language
- created_at
- updated_at
- deleted_at

## BrandKit
AI reads this before generating content to maintain brand consistency.
- id
- workspace_id
- brand_name
- tone
- writing_style
- target_audience
- primary_color
- secondary_color
- logo_url
- website
- version
- is_active
- created_at
- updated_at

---

# 7. Social Media Module

## Platform
Master data table for supported platforms (e.g., X, LinkedIn, Instagram).
- id
- name
- display_name
- icon_url
- api_version
- is_active

## SocialAccount
Connected user accounts.
- id
- workspace_id
- platform_id
- account_name
- account_id
- username
- profile_url
- status
- connected_at

## APICredential
- id
- workspace_id
- platform_id (FK)
- encrypted_access_token
- encrypted_refresh_token
- expires_at
- created_at

---

# 8. Content Module

## ContentProject
Represents an overarching AI request.
- id
- workspace_id
- created_by (FK → User.id)
- title
- description
- platform
- tone
- target_audience
- status
- created_at
- deleted_at

## GeneratedPost
- id
- project_id
- platform_id (FK)
- created_by (FK → User.id)
- ai_model
- status
- created_at
- deleted_at

## PostVersion
Supports multiple AI-generated drafts instead of overwriting a single post.
- id
- post_id
- version
- title
- content
- hashtags
- created_at

## MediaAsset
Supports Images, Videos, GIFs, Documents.
- id
- post_id
- type
- url
- mime_type
- size
- width
- height
- duration
- created_at
- deleted_at

## Approval
Useful for business workflows requiring review before publishing.
- id
- post_id
- approved_by (FK → User.id)
- status
- comment
- approved_at

---

# 9. Publishing Module

## Schedule
- id
- post_id
- scheduled_at
- timezone
- status
- retry_count
- created_at

## PublishingLog
- id
- schedule_id
- platform
- published_at
- success
- response_code
- error_message

---

# 10. Analytics Module

## AnalyticsSnapshot
Metrics captured as a timeline instead of a single overwritten record.
- id
- post_id
- platform_id (FK)
- captured_at
- impressions
- likes
- comments
- shares
- bookmarks
- profile_visits
- followers_gained
- engagement_rate

---

# 11. AI Module

## AIModel
Instead of storing model names as plain strings, normalized models for agent selection.
- id
- provider
- model_name
- version
- max_context
- is_active
- created_at

## AIAgent
First-class entity (e.g., Strategy Agent, Content Agent).
- id
- name
- description
- version
- status
- created_at

## AIJob
Represents one LangGraph execution.
- id
- workspace_id
- agent_id
- model_id (FK)
- workflow_name
- status
- started_at
- completed_at
- execution_time
- total_tokens

## PromptExecution
- id
- ai_job_id
- agent_id
- prompt_version
- input_tokens
- output_tokens
- latency_ms
- created_at

---

# 12. Final Relationships

```text
Organization
    │
    └────────────< User

User
    ├────────────< UserSession
    ├────────────< Workspace
    ├────────────< AuditLog
    ├────────────< Approval
    ├────────────< ContentProject
    └────────────< GeneratedPost

Workspace
    ├────────────< BrandKit
    ├────────────< SocialAccount
    ├────────────< APICredential
    ├────────────< ContentProject
    └────────────< AIJob

Platform
    ├────────────< SocialAccount
    ├────────────< APICredential
    ├────────────< GeneratedPost
    └────────────< AnalyticsSnapshot

ContentProject
    └────────────< GeneratedPost

GeneratedPost
    ├────────────< PostVersion
    ├────────────|| Schedule
    ├────────────< MediaAsset
    ├────────────< AnalyticsSnapshot
    └────────────|| Approval

Schedule
    └────────────< PublishingLog

AIModel
    └────────────< AIJob

AIAgent
    └────────────< AIJob

AIJob
    └────────────< PromptExecution
```

---

# 13. Primary Keys

Every table uses **UUID**.

Advantages:
- Globally unique
- Safer for distributed systems
- Harder to guess

---

# 14. Final Engineering Recommendations

1. Use **PostgreSQL ENUMs** for fields like role, status, tone, and platform where appropriate instead of unrestricted strings.
2. Add **indexes** on frequently queried columns such as `email`, `organization_id`, `workspace_id`, `platform_id`, `project_id`, `post_id`, `status`, `scheduled_at`, and `created_at`.
3. **Encrypt OAuth tokens** (`encrypted_access_token`, `encrypted_refresh_token`) at rest using an encryption library; continue hashing passwords with Argon2 (preferred) or bcrypt.
4. Define **cascading behavior** explicitly:
   - Organization → User: restrict or soft-delete based on business rules.
   - Workspace → child entities: usually cascade delete or soft delete.
5. Log tables (`PublishingLog`, `PromptExecution`, `AuditLog`) should generally be retained for auditing rather than deleted.
6. Use **audit timestamps** consistently (`created_at`, `updated_at`) on mutable entities, and `deleted_at` only where soft deletion is required.

---

# 15. Summary

This is a production-ready relational schema that balances MVP simplicity with room for future growth. It supports a multi-tenant SaaS architecture, AI agent orchestration, brand-aware content generation, content versioning, and comprehensive tracking.

This schema forms a solid foundation for implementing the backend with FastAPI, SQLAlchemy, Alembic, and PostgreSQL.

---

# Document Status

**Phase:** 4 – Database Design

**Status:** Completed

**Next Document:**

```text
docs/05_API_Design.md
```