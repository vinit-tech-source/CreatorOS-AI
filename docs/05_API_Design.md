# CreatorOS AI

# API Design

**Document Version:** 1.0

**Document Type:** API Design Specification

**Status:** Draft

**Last Updated:** July 2026

---

# Related Documents

- 00_Project_Vision.md
- 01_Requirement_Analysis.md
- 02_System_Architecture.md
- 03_Tech_Stack.md
- 04_Database_Design.md

---

# Table of Contents

1. Introduction
2. API Design Goals
3. REST API Principles
4. API Architecture
5. API Versioning
6. Authentication & Authorization
7. API Standards
8. Request Headers
9. Response Format
10. Error Handling
11. HTTP Status Codes
12. Pagination
13. Filtering
14. Sorting
15. Search
16. Rate Limiting
17. Authentication APIs

---

# 1. Introduction

## Purpose

This document defines the complete REST API specification for CreatorOS AI.

The API acts as the communication layer between the frontend, backend, AI engine, and external social media platforms.

It provides standardized interfaces for:

- User Authentication
- Organization Management
- Workspace Management
- AI Content Generation
- Publishing
- Scheduling
- Analytics
- Social Media Integration

---

## Objectives

The API should be:

- RESTful
- Secure
- Scalable
- Versioned
- Easy to Maintain
- Well Documented
- OpenAPI Compatible

---

# 2. API Design Goals

The API has been designed to satisfy the following goals.

## Security

- JWT Authentication
- OAuth Integration
- HTTPS Only
- Role Based Access Control
- Token Encryption

---

## Scalability

Support

- Multiple Organizations
- Multiple Workspaces
- Multiple Platforms
- Multiple AI Models
- Thousands of Scheduled Jobs

---

## Maintainability

- Modular Routers
- Service Layer
- Repository Layer
- OpenAPI Documentation
- Standard Response Format

---

## Performance

- Pagination
- Filtering
- Lazy Loading
- Database Indexing
- Async Processing

---

# 3. REST API Principles

CreatorOS AI follows REST architecture.

### Resource Based URLs

Good

```
/workspaces
```

Bad

```
/createWorkspace
```

---

### Stateless Requests

Every request must contain all required information.

Server sessions are not maintained.

---

### Standard HTTP Methods

| Method | Description |
|----------|------------|
| GET | Read |
| POST | Create |
| PUT | Replace |
| PATCH | Partial Update |
| DELETE | Delete |

---

### JSON Communication

All APIs accept and return JSON.

Example

```json
{
  "name":"CreatorOS"
}
```

---

### Predictable URLs

Examples

```
/api/v1/workspaces

/api/v1/projects

/api/v1/posts

/api/v1/analytics
```

---

# 4. API Architecture

```
React Frontend

↓

HTTPS Request

↓

FastAPI Router

↓

Authentication Middleware

↓

Validation

↓

Service Layer

↓

Repository Layer

↓

PostgreSQL
```

For AI APIs

```
Client

↓

FastAPI

↓

AI Service

↓

LangGraph

↓

AI Agents

↓

Gemini/OpenAI

↓

Database

↓

Response
```

---

# 5. API Versioning

Every endpoint begins with

```
/api/v1
```

Example

```
/api/v1/auth/login

/api/v1/workspaces

/api/v1/projects
```

Future versions

```
/api/v2
```

Versioning ensures backward compatibility.

---

# 6. Authentication & Authorization

## Authentication

CreatorOS AI uses

- JWT Access Token
- Refresh Token

Authentication Flow

```
Register

↓

Login

↓

Access Token

↓

Protected APIs

↓

Refresh Token

↓

Logout
```

Authorization Header

```
Authorization: Bearer <access_token>
```

---

## Authorization

RBAC (Role Based Access Control)

Roles

- Owner
- Admin
- Editor
- Viewer

Permissions

| Role | Permission |
|------|------------|
| Owner | Full Access |
| Admin | Manage Workspace |
| Editor | Create/Edit Content |
| Viewer | Read Only |

---

# 7. API Standards

## Data Format

- JSON
- UTF-8 Encoding

---

## Date Format

ISO-8601

Example

```
2026-07-28T18:30:00Z
```

---

## UUID

Primary Keys use UUID v4.

Example

```
550e8400-e29b-41d4-a716-446655440000
```

---

## Naming Convention

Use snake_case

Good

```
workspace_id

created_at

updated_at
```

Bad

```
workspaceId

createdAt
```

---

## HTTPS

Production only accepts HTTPS.

---

# 8. Common Request Headers

Required

```
Content-Type: application/json
```

Protected APIs

```
Authorization: Bearer <JWT>
```

Optional

```
Accept-Language

X-Request-ID

User-Agent
```

---

# 9. Standard Response Format

## Success Response

```json
{
  "success": true,
  "message": "Workspace created successfully.",
  "data": {}
}
```

---

## Error Response

```json
{
  "success": false,
  "error": {
    "code": "WORKSPACE_NOT_FOUND",
    "message": "Workspace does not exist."
  }
}
```

---

## Paginated Response

```json
{
  "success": true,
  "data": [],
  "pagination": {
    "page":1,
    "page_size":20,
    "total_pages":5,
    "total_records":96
  }
}
```

---

# 10. Error Handling

Every error contains

- Error Code
- Message
- HTTP Status

Example

```json
{
  "success": false,
  "error": {
    "code":"AUTH_001",
    "message":"Invalid Credentials"
  }
}
```

---

# 11. HTTP Status Codes

| Code | Meaning |
|------|---------|
|200|Success|
|201|Created|
|202|Accepted|
|204|No Content|
|400|Bad Request|
|401|Unauthorized|
|403|Forbidden|
|404|Not Found|
|409|Conflict|
|422|Validation Error|
|429|Too Many Requests|
|500|Internal Server Error|

---

# 12. Pagination

Supported Parameters

```
?page=1

&page_size=20
```

Example

```
GET /posts?page=2&page_size=25
```

---

# 13. Filtering

Examples

```
GET /posts?status=draft

GET /posts?platform=x

GET /projects?workspace_id=<uuid>
```

Multiple filters

```
GET /posts?status=published&platform=x
```

---

# 14. Sorting

Ascending

```
?sort=created_at
```

Descending

```
?sort=-created_at
```

Multiple

```
?sort=-created_at,title
```

---

# 15. Search

Global search parameter

```
?search=AI
```

Example

```
GET /posts?search=Generative AI
```

---

# 16. Rate Limiting

Default

```
100 Requests / Minute / User
```

AI Generation

```
20 Requests / Minute
```

Authentication

```
10 Login Attempts / Minute
```

Headers

```
X-RateLimit-Limit

X-RateLimit-Remaining

Retry-After
```

---

# 17. Authentication APIs

## Register User

### Endpoint

```
POST /api/v1/auth/register
```

### Description

Creates a new user account.

### Authentication

Not Required

### Request Body

```json
{
  "first_name":"John",
  "last_name":"Doe",
  "email":"john@example.com",
  "password":"StrongPassword123!"
}
```

### Success Response

HTTP 201

```json
{
  "success":true,
  "message":"User registered successfully."
}
```

### Possible Errors

- Email Already Exists
- Invalid Password
- Validation Error

---

## Login

### Endpoint

```
POST /api/v1/auth/login
```

### Request

```json
{
  "email":"john@example.com",
  "password":"StrongPassword123!"
}
```

### Response

```json
{
  "success":true,
  "data":{
    "access_token":"...",
    "refresh_token":"...",
    "expires_in":3600
  }
}
```

---

## Refresh Token

```
POST /api/v1/auth/refresh
```

Returns a new access token using a valid refresh token.

---

## Logout

```
POST /api/v1/auth/logout
```

Invalidates the current session.

---

## Current User

```
GET /api/v1/auth/me
```

Returns the authenticated user's profile.

---

## Change Password

```
PUT /api/v1/auth/change-password
```

Allows an authenticated user to update their password after verifying the current password.

---

# End of Part 1

**Next:** Part 2 – Organization APIs, Workspace APIs, Brand Kit APIs, Platform APIs, Social Account APIs, API Credential APIs, and Content Project APIs.


---

# 18. Organization APIs

Organizations represent the top-level tenant in CreatorOS AI. Each organization can contain multiple users, workspaces, and resources.

---

## Create Organization

### Endpoint

```
POST /api/v1/organizations
```

### Description

Creates a new organization.

### Authentication

Required (Owner)

### Request Body

```json
{
  "name": "OpenAI",
  "slug": "openai",
  "description": "AI Research Organization"
}
```

### Success Response

```json
{
  "success": true,
  "message": "Organization created successfully.",
  "data": {
    "id": "uuid",
    "name": "OpenAI"
  }
}
```

### Database Tables

- Organization

### Permissions

Owner

---

## List Organizations

```
GET /api/v1/organizations
```

Returns all organizations the authenticated user belongs to.

---

## Get Organization

```
GET /api/v1/organizations/{organization_id}
```

Returns organization details.

---

## Update Organization

```
PUT /api/v1/organizations/{organization_id}
```

Updates organization information.

---

## Delete Organization

```
DELETE /api/v1/organizations/{organization_id}
```

Soft deletes an organization.

---

# 19. Workspace APIs

A workspace represents a brand, client, or business unit.

One organization can contain multiple workspaces.

---

## Create Workspace

### Endpoint

```
POST /api/v1/workspaces
```

### Description

Creates a new workspace.

### Authentication

Required

### Request

```json
{
    "organization_id":"uuid",
    "name":"CreatorOS",
    "description":"AI Content Automation",
    "timezone":"Asia/Kolkata",
    "default_language":"English"
}
```

### Success

```json
{
    "success":true,
    "message":"Workspace created successfully.",
    "data":{
        "id":"uuid"
    }
}
```

### Database Tables

- Workspace

### Service

WorkspaceService

### Repository

WorkspaceRepository

---

## List Workspaces

```
GET /api/v1/workspaces
```

Supports:

- Pagination
- Search
- Sorting

---

## Get Workspace

```
GET /api/v1/workspaces/{workspace_id}
```

---

## Update Workspace

```
PUT /api/v1/workspaces/{workspace_id}
```

---

## Delete Workspace

```
DELETE /api/v1/workspaces/{workspace_id}
```

Soft delete only.

---

# 20. Brand Kit APIs

Brand Kits maintain consistent branding across generated content.

---

## Create Brand Kit

```
POST /api/v1/brand-kits
```

### Request

```json
{
    "workspace_id":"uuid",
    "brand_name":"CreatorOS",
    "primary_color":"#4F46E5",
    "secondary_color":"#06B6D4",
    "tone":"Professional",
    "voice":"Friendly",
    "website":"https://creatoros.ai"
}
```

### Response

```json
{
    "success":true,
    "message":"Brand kit created."
}
```

---

## List Brand Kits

```
GET /api/v1/brand-kits
```

---

## Get Brand Kit

```
GET /api/v1/brand-kits/{brand_kit_id}
```

---

## Update Brand Kit

```
PUT /api/v1/brand-kits/{brand_kit_id}
```

---

## Delete Brand Kit

```
DELETE /api/v1/brand-kits/{brand_kit_id}
```

Soft delete.

---

# 21. Platform APIs

Platform APIs provide available publishing platforms.

Examples

- X
- LinkedIn
- Facebook
- Instagram
- Threads

---

## List Platforms

```
GET /api/v1/platforms
```

Response

```json
{
  "success":true,
  "data":[
    {
      "id":"uuid",
      "name":"X"
    },
    {
      "id":"uuid",
      "name":"LinkedIn"
    }
  ]
}
```

---

## Get Platform

```
GET /api/v1/platforms/{platform_id}
```

---

# 22. Social Account APIs

Connect and manage social media accounts.

---

## Connect Social Account

```
POST /api/v1/social-accounts/connect
```

### Description

Starts OAuth authentication flow.

### Request

```json
{
    "workspace_id":"uuid",
    "platform_id":"uuid"
}
```

### Response

```json
{
    "authorization_url":"https://..."
}
```

---

## OAuth Callback

```
GET /api/v1/social-accounts/callback
```

Stores OAuth tokens after successful authorization.

---

## List Connected Accounts

```
GET /api/v1/social-accounts
```

---

## Get Connected Account

```
GET /api/v1/social-accounts/{account_id}
```

---

## Refresh OAuth Token

```
POST /api/v1/social-accounts/{account_id}/refresh
```

---

## Disconnect Account

```
DELETE /api/v1/social-accounts/{account_id}
```

Revokes OAuth authorization.

---

# 23. API Credential APIs

Stores encrypted API credentials for external integrations.

---

## Create Credential

```
POST /api/v1/api-credentials
```

### Request

```json
{
    "workspace_id":"uuid",
    "platform_id":"uuid",
    "access_token":"encrypted",
    "refresh_token":"encrypted"
}
```

### Response

```json
{
    "success":true,
    "message":"Credential stored securely."
}
```

---

## List Credentials

```
GET /api/v1/api-credentials
```

---

## Get Credential

```
GET /api/v1/api-credentials/{credential_id}
```

---

## Update Credential

```
PUT /api/v1/api-credentials/{credential_id}
```

---

## Delete Credential

```
DELETE /api/v1/api-credentials/{credential_id}
```

---

# 24. Content Project APIs

Content Projects organize campaigns, topics, or content plans.

---

## Create Content Project

```
POST /api/v1/projects
```

### Request

```json
{
    "workspace_id":"uuid",
    "title":"AI Marketing Campaign",
    "description":"July Campaign",
    "status":"draft"
}
```

### Success Response

```json
{
    "success":true,
    "message":"Project created successfully.",
    "data":{
        "project_id":"uuid"
    }
}
```

### Database Tables

- ContentProject

### Service

ContentProjectService

### Repository

ContentProjectRepository

---

## List Projects

```
GET /api/v1/projects
```

Supports

- Pagination
- Search
- Filtering
- Sorting

---

## Get Project

```
GET /api/v1/projects/{project_id}
```

---

## Update Project

```
PUT /api/v1/projects/{project_id}
```

---

## Delete Project

```
DELETE /api/v1/projects/{project_id}
```

Soft delete.

---

## Archive Project

```
PATCH /api/v1/projects/{project_id}/archive
```

Moves a project to archived state without deleting it.

---

## Restore Project

```
PATCH /api/v1/projects/{project_id}/restore
```

Restores an archived project.

---

# End of Part 2

**Next:** Part 3 – Generated Post APIs, AI Generation APIs, Post Version APIs, Media Asset APIs, Approval APIs, Schedule APIs, and Publishing APIs.

---

# 25. Generated Post APIs

Generated Posts are AI-generated social media posts created from Content Projects. Every generated post is linked to a workspace and project and supports versioning, scheduling, publishing, approvals, and analytics.

---

## Create Generated Post

### Endpoint

```http
POST /api/v1/posts
```

### Description

Creates a new post manually without AI.

### Authentication

Required

### Request

```json
{
  "project_id": "uuid",
  "platform_id": "uuid",
  "title": "Introducing CreatorOS AI",
  "content": "Our new AI platform helps automate social media operations.",
  "status": "draft"
}
```

### Success Response

```json
{
  "success": true,
  "message": "Post created successfully.",
  "data": {
    "post_id": "uuid"
  }
}
```

### Database Tables

- GeneratedPost

---

## List Posts

```http
GET /api/v1/posts
```

Supports

- Pagination
- Search
- Filtering
- Sorting

Example

```
GET /api/v1/posts?status=draft&page=1&page_size=20
```

---

## Get Post

```http
GET /api/v1/posts/{post_id}
```

Returns complete post information.

---

## Update Post

```http
PUT /api/v1/posts/{post_id}
```

Updates

- Title
- Content
- Hashtags
- Status
- Platform

---

## Delete Post

```http
DELETE /api/v1/posts/{post_id}
```

Soft delete.

---

## Duplicate Post

```http
POST /api/v1/posts/{post_id}/duplicate
```

Creates a copy of an existing post.

---

# 26. AI Content Generation APIs

These APIs invoke LangGraph workflows.

---

## Generate AI Post

### Endpoint

```http
POST /api/v1/ai/generate-post
```

### Description

Starts a complete AI workflow for generating a social media post.

### AI Workflow

```
Strategy Agent
      │
      ▼
Trend Agent
      │
      ▼
Research Agent
      │
      ▼
Content Planner
      │
      ▼
Content Generator
      │
      ▼
Brand Voice Agent
      │
      ▼
Fact Check Agent
      │
      ▼
SEO Agent
      │
      ▼
Hashtag Agent
      │
      ▼
Database
```

### Request

```json
{
  "workspace_id": "uuid",
  "project_id": "uuid",
  "platform_id": "uuid",
  "topic": "Future of Artificial Intelligence",
  "tone": "Professional",
  "language": "English",
  "target_audience": "Developers"
}
```

### Response

```json
{
  "success": true,
  "data": {
    "job_id": "uuid",
    "status": "processing"
  }
}
```

---

## Rewrite Content

```http
POST /api/v1/ai/rewrite
```

Rewrites existing content using AI.

---

## Improve Content

```http
POST /api/v1/ai/improve
```

Improves readability, engagement, and grammar.

---

## Summarize Content

```http
POST /api/v1/ai/summarize
```

Summarizes long-form content.

---

## Translate Content

```http
POST /api/v1/ai/translate
```

Supported Languages

- English
- Hindi
- Marathi
- Spanish
- French

---

## Generate Hashtags

```http
POST /api/v1/ai/generate-hashtags
```

Returns optimized hashtags.

---

## Generate Thread

```http
POST /api/v1/ai/generate-thread
```

Creates an X (Twitter) thread.

---

## Analyze Tone

```http
POST /api/v1/ai/analyze-tone
```

Returns

- Tone
- Confidence
- Suggestions

---

## Fact Check

```http
POST /api/v1/ai/fact-check
```

Validates generated content.

---

## Generate Image Prompt

```http
POST /api/v1/ai/image-prompt
```

Creates prompts for image-generation models.

---

# 27. Post Version APIs

Each modification creates a new version.

---

## List Versions

```http
GET /api/v1/posts/{post_id}/versions
```

Returns all versions.

---

## Get Version

```http
GET /api/v1/posts/{post_id}/versions/{version_id}
```

Returns a specific version.

---

## Restore Version

```http
POST /api/v1/posts/{post_id}/versions/{version_id}/restore
```

Restores a previous version.

---

## Compare Versions

```http
GET /api/v1/posts/{post_id}/versions/compare
```

Example

```
?from=1&to=4
```

Returns differences.

---

# 28. Media Asset APIs

Media assets include

- Images
- Videos
- Documents
- GIFs

---

## Upload Media

```http
POST /api/v1/media/upload
```

Supported Formats

- JPG
- PNG
- WEBP
- GIF
- MP4

Maximum File Size

```
50 MB
```

---

## List Media

```http
GET /api/v1/media
```

---

## Get Media

```http
GET /api/v1/media/{media_id}
```

---

## Update Media

```http
PUT /api/v1/media/{media_id}
```

Updates metadata.

---

## Delete Media

```http
DELETE /api/v1/media/{media_id}
```

Soft delete.

---

# 29. Approval APIs

Approval is required before publishing when workspace approval rules are enabled.

---

## Request Approval

```http
POST /api/v1/approvals/request
```

Creates an approval request.

---

## Approve Post

```http
POST /api/v1/approvals/{approval_id}/approve
```

Marks approval as approved.

---

## Reject Post

```http
POST /api/v1/approvals/{approval_id}/reject
```

Request

```json
{
  "reason": "Incorrect statistics."
}
```

---

## Get Approval Status

```http
GET /api/v1/approvals/{approval_id}
```

Returns

- Pending
- Approved
- Rejected

---

# 30. Schedule APIs

Schedules future publishing.

---

## Create Schedule

```http
POST /api/v1/schedules
```

Request

```json
{
  "post_id": "uuid",
  "publish_at": "2026-08-10T10:30:00Z"
}
```

---

## List Schedules

```http
GET /api/v1/schedules
```

---

## Get Schedule

```http
GET /api/v1/schedules/{schedule_id}
```

---

## Update Schedule

```http
PUT /api/v1/schedules/{schedule_id}
```

---

## Delete Schedule

```http
DELETE /api/v1/schedules/{schedule_id}
```

---

## Reschedule

```http
PATCH /api/v1/schedules/{schedule_id}
```

Changes publish date and time.

---

# 31. Publishing APIs

Publishing APIs communicate with external social media platforms.

---

## Publish Post

```http
POST /api/v1/publish
```

Publishes a draft or scheduled post immediately.

---

## Retry Publishing

```http
POST /api/v1/publish/retry
```

Retries failed publishing jobs.

---

## Publishing Logs

```http
GET /api/v1/publishing-logs
```

Supports

- Pagination
- Search
- Filtering

---

## Get Publishing Log

```http
GET /api/v1/publishing-logs/{log_id}
```

Returns

- Platform
- Publish Time
- External Post ID
- Status
- Error Message

---

## Cancel Scheduled Publishing

```http
DELETE /api/v1/publish/{schedule_id}
```

Cancels a scheduled publishing task before execution.

---

# End of Part 3

**Next:** Part 4 – Analytics APIs, AI Model APIs, AI Agent APIs, AI Job APIs, Prompt Execution APIs, Validation Rules, Error Codes, Security, API Lifecycle, OpenAPI Guidelines, Sequence Diagrams, Future APIs, and Summary.

---

# 32. Analytics APIs

Analytics APIs provide insights into post performance, audience engagement, and workspace growth.

---

## Dashboard Analytics

### Endpoint

```http
GET /api/v1/analytics/dashboard
```

### Description

Returns an overview of workspace analytics.

### Response

```json
{
  "success": true,
  "data": {
    "total_posts": 120,
    "published_posts": 95,
    "scheduled_posts": 15,
    "draft_posts": 10,
    "engagement_rate": 6.8,
    "followers": 12540
  }
}
```

---

## Post Analytics

```http
GET /api/v1/analytics/posts/{post_id}
```

Returns

- Impressions
- Reach
- Likes
- Comments
- Shares
- Saves
- Clicks
- Engagement Rate

---

## Workspace Analytics

```http
GET /api/v1/analytics/workspaces/{workspace_id}
```

Returns overall workspace statistics.

---

## Platform Analytics

```http
GET /api/v1/analytics/platforms/{platform_id}
```

Returns analytics for a specific social platform.

---

## Audience Analytics

```http
GET /api/v1/analytics/audience
```

Returns

- Age Distribution
- Gender Distribution
- Country
- City
- Active Hours

---

## Growth Analytics

```http
GET /api/v1/analytics/growth
```

Returns follower growth trends.

---

## Engagement Analytics

```http
GET /api/v1/analytics/engagement
```

Returns engagement metrics over time.

---

# 33. AI Model APIs

Manage AI models used by CreatorOS AI.

---

## List Models

```http
GET /api/v1/ai/models
```

Returns available AI models.

---

## Get Model

```http
GET /api/v1/ai/models/{model_id}
```

Returns model details.

---

## Activate Model

```http
PATCH /api/v1/ai/models/{model_id}/activate
```

Sets the selected model as active.

---

## Disable Model

```http
PATCH /api/v1/ai/models/{model_id}/disable
```

Disables an AI model.

---

# 34. AI Agent APIs

Manage LangGraph AI Agents.

---

## List Agents

```http
GET /api/v1/ai/agents
```

---

## Get Agent

```http
GET /api/v1/ai/agents/{agent_id}
```

---

## Agent Status

```http
GET /api/v1/ai/agents/{agent_id}/status
```

Returns

- Running
- Idle
- Failed
- Disabled

---

## Restart Agent

```http
POST /api/v1/ai/agents/{agent_id}/restart
```

---

# 35. AI Job APIs

AI Jobs represent asynchronous AI executions.

---

## List Jobs

```http
GET /api/v1/ai/jobs
```

Supports

- Pagination
- Filtering
- Sorting

---

## Get Job

```http
GET /api/v1/ai/jobs/{job_id}
```

Returns complete job information.

---

## Cancel Job

```http
POST /api/v1/ai/jobs/{job_id}/cancel
```

---

## Retry Job

```http
POST /api/v1/ai/jobs/{job_id}/retry
```

---

## Job Logs

```http
GET /api/v1/ai/jobs/{job_id}/logs
```

---

# 36. Prompt Execution APIs

Prompt Execution stores every prompt sent to AI models.

---

## List Prompt Executions

```http
GET /api/v1/prompt-executions
```

---

## Get Prompt Execution

```http
GET /api/v1/prompt-executions/{execution_id}
```

---

## Prompt History

```http
GET /api/v1/prompt-executions/history
```

Returns historical prompt executions.

---

# 37. Validation Rules

## User

| Field | Rule |
|------|------|
| First Name | Required |
| Last Name | Required |
| Email | Valid Email |
| Password | Minimum 8 Characters |

---

## Workspace

| Field | Rule |
|------|------|
| Name | Required |
| Description | Optional |
| Timezone | Required |

---

## Project

| Field | Rule |
|------|------|
| Title | Required |
| Description | Optional |
| Status | Draft, Active, Archived |

---

## Post

| Field | Rule |
|------|------|
| Content | Required |
| Platform | Required |
| Status | Draft, Scheduled, Published |

---

# 38. Error Codes

## Authentication

| Code | Description |
|------|-------------|
| AUTH_001 | Invalid Credentials |
| AUTH_002 | Token Expired |
| AUTH_003 | Unauthorized |

---

## User

| Code | Description |
|------|-------------|
| USER_001 | User Not Found |
| USER_002 | Email Already Exists |

---

## Workspace

| Code | Description |
|------|-------------|
| WORKSPACE_001 | Workspace Not Found |

---

## Project

| Code | Description |
|------|-------------|
| PROJECT_001 | Project Not Found |

---

## AI

| Code | Description |
|------|-------------|
| AI_001 | Model Error |
| AI_002 | Prompt Validation Failed |
| AI_003 | Agent Timeout |

---

## Publishing

| Code | Description |
|------|-------------|
| PUBLISH_001 | Publishing Failed |
| PUBLISH_002 | Platform Unavailable |

---

# 39. API Security

The API follows security best practices.

## Authentication

- JWT Authentication
- Refresh Tokens

---

## Authorization

- Role-Based Access Control (RBAC)

---

## Data Security

- HTTPS Only
- Password Hashing (Argon2)
- Encrypted OAuth Tokens
- SQL Injection Protection
- XSS Protection
- CSRF Protection
- Input Validation

---

## Logging

Every API request is logged with

- User ID
- Timestamp
- Endpoint
- HTTP Method
- IP Address
- Status Code

---

# 40. API Lifecycle

Every request follows the lifecycle below.

```
Client
    │
    ▼
FastAPI Router
    │
    ▼
Authentication Middleware
    │
    ▼
Authorization
    │
    ▼
Request Validation
    │
    ▼
Service Layer
    │
    ▼
Repository Layer
    │
    ▼
PostgreSQL
    │
    ▼
Response Formatter
    │
    ▼
Client
```

---

# 41. OpenAPI (Swagger)

CreatorOS AI uses FastAPI's automatic OpenAPI documentation.

Documentation URLs

```
/docs
```

Swagger UI

```
/redoc
```

ReDoc Documentation

Every endpoint must include

- Summary
- Description
- Tags
- Parameters
- Request Schema
- Response Schema
- Error Responses
- Authentication

---

# 42. Sequence Diagrams

## Login Flow

```
Client
   │
POST /login
   │
FastAPI
   │
Authentication Service
   │
JWT Token
   │
Response
```

---

## AI Content Generation Flow

```
Client
   │
Generate Post
   │
FastAPI
   │
LangGraph
   │
Strategy Agent
   │
Trend Agent
   │
Research Agent
   │
Content Planner
   │
Content Generator
   │
Brand Voice
   │
Fact Check
   │
SEO
   │
Hashtag
   │
Database
   │
Response
```

---

## Publishing Flow

```
Client
   │
Publish API
   │
Scheduler
   │
Social Platform API
   │
Publishing Log
   │
Analytics
   │
Response
```

---

# 43. Future APIs

The following APIs are planned for future releases.

## Notification APIs

- Email Notifications
- Push Notifications
- Slack Notifications

---

## Team Collaboration APIs

- Invite Members
- Remove Members
- Assign Roles

---

## Campaign APIs

- Campaign Management
- Campaign Analytics
- Campaign Scheduling

---

## Billing APIs

- Subscription Management
- Payment History
- Invoice Download

---

## AI Marketplace APIs

- Custom AI Agents
- Prompt Marketplace
- Plugin Integrations

---

# 44. Summary

The CreatorOS AI API follows modern RESTful principles and is designed to be:

- Secure
- Scalable
- Versioned
- Modular
- AI-Ready
- OpenAPI Compatible

The API provides complete support for:

- Authentication & Authorization
- Organization & Workspace Management
- Brand Kit Management
- Social Media Integration
- Content Project Management
- AI Content Generation
- Post Versioning
- Media Management
- Approval Workflow
- Scheduling & Publishing
- Analytics
- AI Model & Agent Management
- Prompt Execution Tracking

This API specification serves as the implementation contract between the React frontend, FastAPI backend, PostgreSQL database, LangGraph AI workflows, and external social media platforms.

---

# Document Status

**Document:** 05_API_Design.md

**Version:** 1.0

**Status:** ✅ Completed

**Next Document**

```
docs/06_AI_Agent_Design.md
```

---

**End of Document**