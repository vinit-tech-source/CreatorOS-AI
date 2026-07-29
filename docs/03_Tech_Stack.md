# 03 Tech Stack

# CreatorOS AI
# Technology Stack

**Version:** 1.0

**Document Type:** Technology Stack Specification

**Status:** Draft

**Related Documents**

- 00_Project_Vision.md
- 01_Requirement_Analysis.md
- 02_System_Architecture.md

---

# 1. Purpose

This document defines the complete technology stack used in CreatorOS AI.

It explains:

- Programming languages
- Frameworks
- Libraries
- AI technologies
- Database technologies
- External integrations
- Development tools
- Deployment technologies

Each technology is selected based on scalability, maintainability, performance, and compatibility with modern AI engineering practices.

---

# 2. Technology Overview

| Layer | Technology |
|---------|------------|
| Frontend Framework | React |
| Programming Language (Frontend) | TypeScript |
| UI Styling | Tailwind CSS |
| UI Components | shadcn/ui |
| State Management | Zustand |
| Charts | Recharts |
| Backend Framework | FastAPI |
| Programming Language (Backend) | Python 3.12+ |
| Validation | Pydantic |
| AI Framework | LangChain |
| AI Workflow | LangGraph |
| Large Language Model | Gemini 2.5 / GPT-5 |
| Database | PostgreSQL |
| ORM | SQLAlchemy |
| Database Migration | Alembic |
| Authentication | JWT |
| Password Hashing | pwdlib (or bcrypt) |
| Scheduler | APScheduler |
| HTTP Client | httpx |
| Configuration | python-dotenv |
| Testing | pytest |
| Containerization | Docker |
| Version Control | Git + GitHub |

---

# 3. Frontend Technologies

## 3.1 React

### Purpose

Develop the web application using reusable components.

### Responsibilities

- User Interface
- Dashboard
- Authentication Screens
- Workspace Management
- Analytics
- Settings

### Why React?

- Component-based architecture
- Large ecosystem
- Excellent performance
- Industry standard
- Easy integration with FastAPI

---

## 3.2 TypeScript

### Purpose

Provide static typing for JavaScript.

### Why TypeScript?

- Detects errors during development
- Better IDE support
- Easier maintenance
- Improved scalability

---

## 3.3 Tailwind CSS

### Purpose

UI styling.

### Why Tailwind?

- Utility-first CSS
- Fast development
- Responsive design
- Easy customization

---

## 3.4 shadcn/ui

### Purpose

Reusable UI components.

### Examples

- Buttons
- Dialogs
- Tables
- Cards
- Dropdowns
- Navigation

### Why?

- Accessible
- Modern design
- Highly customizable

---

## 3.5 Zustand

### Purpose

Global state management.

### Stores

- User
- Authentication
- Workspace
- Theme
- Settings

### Why?

- Lightweight
- Easy to learn
- Less boilerplate than Redux

---

## 3.6 Recharts

### Purpose

Display analytics.

Examples

- Engagement charts
- Growth charts
- Platform comparison
- Performance trends

---

# 4. Backend Technologies

## 4.1 Python

### Purpose

Primary programming language.

### Why Python?

- Best AI ecosystem
- Huge community
- Rich libraries
- Rapid development

---

## 4.2 FastAPI

### Purpose

Backend framework.

### Responsibilities

- REST APIs
- Authentication
- Validation
- AI workflow triggering
- API documentation

### Why FastAPI?

- High performance
- Async support
- Automatic Swagger documentation
- Excellent typing support

---

## 4.3 Pydantic

### Purpose

Data validation.

### Responsibilities

- Request validation
- Response validation
- Configuration management

---

# 5. AI Stack

## 5.1 Large Language Model

Supported Models

- Gemini 2.5 (Default)
- GPT-5 (Optional)

### Responsibilities

- Reasoning
- Content generation
- Summarization
- Classification
- Decision making

---

## 5.2 LangChain

### Purpose

LLM integration layer.

### Responsibilities

- Prompt templates
- Tool calling
- Structured output
- LLM abstraction
- Output parsing

### Why LangChain?

- Mature ecosystem
- Easy tool integration
- Production ready

---

## 5.3 LangGraph

### Purpose

Multi-agent orchestration.

### Responsibilities

- AI workflow execution
- State management
- Agent coordination
- Retry logic
- Conditional routing

### Why LangGraph?

CreatorOS AI consists of multiple AI agents collaborating together.

LangGraph is specifically designed for building stateful multi-agent AI systems.

---

# 6. Database Technologies

## 6.1 PostgreSQL

### Purpose

Primary relational database.

Stores

- Users
- Workspaces
- Posts
- Analytics
- Scheduled Jobs
- AI Logs

### Why PostgreSQL?

- ACID compliance
- Excellent reliability
- Scalable
- Industry standard

---

## 6.2 SQLAlchemy

### Purpose

Object Relational Mapper (ORM).

Responsibilities

- Models
- CRUD Operations
- Relationships
- Queries

---

## 6.3 Alembic

### Purpose

Database migration.

Responsibilities

- Schema updates
- Version control
- Rollback support

---

# 7. Authentication

## JWT

Purpose

Secure authentication.

Responsibilities

- Login
- Access Token
- Protected APIs

---

## Password Hashing

Technology

- pwdlib (preferred)
- bcrypt (alternative)

Purpose

Securely hash passwords before storing them.

---

# 8. Scheduling

## APScheduler

### Purpose

Run background jobs.

Responsibilities

- Scheduled publishing
- Retry failed jobs
- Trigger AI workflows

---

# 9. HTTP Communication

## httpx

### Purpose

Call external APIs.

Examples

- News APIs
- Social Media APIs
- Search APIs

### Why httpx?

- Async support
- Fast
- Works well with FastAPI

---

# 10. Configuration

## python-dotenv

Purpose

Load environment variables.

Examples

- API Keys
- Database URL
- JWT Secret
- Model Configuration

---

# 11. Testing

## pytest

Purpose

Application testing.

Types

- Unit Tests
- Integration Tests
- API Tests

---

# 12. Containerization

## Docker

Purpose

Containerize the application.

Benefits

- Consistent environments
- Easy deployment
- Simplified development

---

# 13. Version Control

## Git

Purpose

Source code management.

---

## GitHub

Purpose

- Repository hosting
- Collaboration
- Pull Requests
- Issue Tracking
- CI/CD Integration

---

# 14. External Integrations

CreatorOS AI will integrate with external services such as:

## Social Media

- X API
- LinkedIn API (Future)
- Instagram Graph API (Future)
- Facebook Graph API (Future)

---

## Trend Analysis

- Google Trends

---

## News & Search

- News API
- Search APIs

---

## AI Providers

- Google Gemini API
- OpenAI API

---

# 15. Development Tools

| Tool | Purpose |
|------|----------|
| VS Code | Code Editor |
| Git | Version Control |
| GitHub | Repository |
| Docker Desktop | Containers |
| Postman / Bruno | API Testing |
| pgAdmin | PostgreSQL Management |

---

# 16. Future Technologies

These are **not required for MVP**, but may be introduced in future versions.

## Redis

- Caching
- Session Storage
- Queue Support

---

## ChromaDB

Vector database for RAG.

---

## Pinecone

Cloud vector database.

---

## Weaviate

Enterprise vector database.

---

## Celery

Distributed background jobs.

---

## Kubernetes

Container orchestration.

---

## Grafana

Monitoring dashboards.

---

## Prometheus

Metrics collection.

---

# 17. Technology Compatibility

| Component | Compatible With |
|------------|----------------|
| React | FastAPI |
| React | Tailwind CSS |
| FastAPI | PostgreSQL |
| FastAPI | SQLAlchemy |
| SQLAlchemy | PostgreSQL |
| LangChain | Gemini |
| LangChain | GPT |
| LangChain | LangGraph |
| LangGraph | FastAPI |
| Docker | Entire Application |

---

# 18. Why This Technology Stack?

The selected stack provides:

- Modern AI engineering practices
- Modular architecture
- High performance
- Excellent scalability
- Strong developer ecosystem
- Easy deployment
- Production readiness

The technologies are widely adopted in industry and are well-suited for building AI-powered web applications.

---

# 19. Summary

CreatorOS AI uses a modern full-stack architecture built with React, TypeScript, FastAPI, PostgreSQL, LangChain, LangGraph, and Docker.

The stack separates business logic from AI workflows, enabling the platform to scale from an MVP supporting X (Twitter) to a multi-platform AI-powered social media operations system.

---

# Document Status

**Phase:** 3 – Technology Stack

**Status:** Completed

**Next Document:**

docs/04_Database_Design.md