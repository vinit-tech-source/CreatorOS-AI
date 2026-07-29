# 02 System Architecture

# CreatorOS AI
# System Architecture

Version: 1.0

Document Type: Software Architecture Document

Status: Draft

---

# 1. Purpose

This document describes the software architecture of CreatorOS AI.

It explains how the frontend, backend, AI orchestration layer, databases, external APIs, and AI agents collaborate to automate the complete social media workflow.

The architecture is designed to be:

- Modular
- Scalable
- Maintainable
- Extensible
- Production Ready

---

# 2. Architectural Style

CreatorOS AI follows a **Modular Monolith Architecture**.

Inside the backend, it follows a **Layered Architecture**, while AI workflows are implemented using a **Multi-Agent Architecture** orchestrated by LangGraph.

The overall architecture combines:

- Modular Monolith
- Layered Architecture
- Multi-Agent Architecture
- Event-driven Scheduling

This combination provides simplicity for development while remaining scalable for future expansion.

---

# 3. Why This Architecture?

The application contains three different domains.

## Business Layer

Responsible for

- Authentication
- User Management
- Dashboard
- Workspace
- Analytics

This follows Layered Architecture.

---

## AI Layer

Responsible for

- Trend Research
- Research
- Content Generation
- Fact Checking
- Publishing

This follows Multi-Agent Architecture.

---

## Integration Layer

Responsible for

- X API
- News API
- Google Trends
- Search APIs

This isolates external services from business logic.

---

# 4. High Level Architecture

```text
                    User
                      │
                      ▼
              React Frontend
                      │
                 REST API
                      │
                      ▼
                FastAPI Backend
                      │
     ┌────────────────┼─────────────────┐
     │                │                 │
     ▼                ▼                 ▼
 Business Layer   AI Orchestrator   Scheduler
     │                │
     ▼                ▼
Repositories     LangGraph Workflow
     │                │
     ▼                ▼
 PostgreSQL      AI Agents
                      │
                      ▼
              LangChain Tools
                      │
      ┌───────────────┼────────────────┐
      ▼               ▼                ▼
 Google Trends     News API        Social APIs
```

---

# 5. Layered Architecture

The backend follows four layers.

```
Presentation Layer

↓

Business Layer

↓

Repository Layer

↓

Database Layer
```

---

## Presentation Layer

Technology

- FastAPI

Responsibilities

- REST APIs
- Authentication
- Validation
- Response Formatting

---

## Business Layer

Responsibilities

- Business Rules
- Workflow Triggering
- Scheduling
- AI Coordination

---

## Repository Layer

Responsibilities

- CRUD Operations
- SQL Queries
- Database Isolation

---

## Database Layer

Technology

- PostgreSQL

Stores

- Users
- Workspaces
- Posts
- Analytics
- Schedules

---

# 6. AI Architecture

The AI system is separated from business logic.

```
User Request

↓

LangGraph

↓

Strategy Agent

↓

Trend Agent

↓

Research Agent

↓

Content Agent

↓

Fact Check Agent

↓

Publishing Agent

↓

Analytics Agent
```

Every agent performs exactly one responsibility.

---

# 7. LangGraph Workflow

The AI workflow is state-driven.

```
Start

↓

Strategy

↓

Trend

↓

Research

↓

Content

↓

Fact Check

↓

Publish

↓

Analytics

↓

End
```

LangGraph manages:

- State
- Routing
- Retry
- Conditional Execution

---

# 8. LangChain Layer

LangChain provides

- Prompt Templates
- Tool Calling
- Structured Output
- LLM Integration
- Memory
- RAG (Future)

---

# 9. Frontend Architecture

```
Pages

↓

Layouts

↓

Components

↓

Services

↓

REST APIs
```

Pages

- Dashboard
- Workspace
- Analytics
- Settings

Components

- Cards
- Tables
- Charts
- Forms

---

# 10. Backend Structure

```
backend/

app/

api/

agents/

core/

database/

models/

prompts/

repositories/

schemas/

services/

tools/

workflows/

main.py
```

---

# 11. Data Flow

```
User

↓

React

↓

FastAPI

↓

Service Layer

↓

LangGraph

↓

Agents

↓

Tools

↓

Database

↓

Frontend
```

---

# 12. Request Lifecycle

Example

Generate Post

```
User clicks Generate

↓

FastAPI Endpoint

↓

Authentication

↓

Workspace Validation

↓

Strategy Agent

↓

Trend Agent

↓

Research Agent

↓

Content Agent

↓

Fact Check Agent

↓

Save Database

↓

Return Response
```

---

# 13. Error Handling

System handles

- API Failures
- LLM Errors
- Tool Failures
- Validation Errors
- Database Errors
- Timeout Errors

Retry logic is managed inside LangGraph where appropriate.

---

# 14. Logging

The system records

- Login Events
- AI Requests
- AI Responses
- Tool Calls
- Publishing Logs
- Errors

---

# 15. Security Layers

```
Authentication

↓

Authorization

↓

Validation

↓

Business Logic

↓

Database

↓

External APIs
```

---

# 16. Scalability

The architecture supports

- Additional AI Agents
- Additional Platforms
- Multiple Organizations
- Horizontal Scaling
- Cloud Deployment

---

# 17. Future Evolution

Future versions may introduce

- AI Image Generation
- AI Video Generation
- Voice Assistant
- Community Manager
- Campaign Manager
- Multi-Team Collaboration

The current modular design allows these capabilities to be added without major architectural changes.

---

# 18. Summary

CreatorOS AI uses a Modular Monolith architecture with Layered backend design and LangGraph-based Multi-Agent AI orchestration.

This architecture separates business logic from AI workflows, improves maintainability, simplifies testing, and provides a scalable foundation for future growth.

---

# Document Status

Phase: 2 – System Architecture

Status: Completed

Next Document:

03_Tech_Stack.md