# 09 External APIs
# CreatorOS AI

# External APIs

**Document Version:** 1.0

**Document Type:** External Integration Design

**Status:** Draft

**Last Updated:** July 2026

---

# Related Documents

- 02_System_Architecture.md
- 03_Tech_Stack.md
- 05_API_Design.md
- 06_AI_Agent_Design.md
- 07_Workflows.md

---

# Table of Contents

1. Introduction
2. External API Architecture
3. Integration Principles
4. Authentication Strategies
5. Google Gemini API
6. X (Twitter) API
7. LinkedIn API

---

# 1. Introduction

## Purpose

This document defines how CreatorOS AI integrates with external services.

These APIs enable:

- AI content generation
- Social media publishing
- Trend analysis
- Research
- Analytics
- Notifications
- Media storage

---

# 2. External API Architecture

All third-party services are accessed through a dedicated Integration Layer.

```
React Frontend
        │
        ▼
FastAPI Backend
        │
        ▼
Integration Layer
        │
 ┌──────┼────────┬─────────┬──────────┐
 ▼      ▼        ▼         ▼
Gemini  X API  LinkedIn  News API
```

---

## Design Principles

- Loose coupling
- Retry support
- Timeout handling
- API versioning
- Secure credential storage
- Structured error handling

---

# 3. Integration Principles

Every external integration must provide:

- Authentication
- Validation
- Logging
- Retry logic
- Timeout handling
- Error mapping
- Monitoring

---

## Standard Request Flow

```
Client Request

↓

Service Layer

↓

Integration Layer

↓

External API

↓

Response Validation

↓

Database

↓

Client Response
```

---

# 4. Authentication Strategies

Different APIs require different authentication mechanisms.

| API | Authentication |
|------|----------------|
| Gemini | API Key |
| X | OAuth 2.0 |
| LinkedIn | OAuth 2.0 |
| Meta | OAuth 2.0 |
| Tavily | API Key |
| NewsAPI | API Key |
| Cloud Storage | Service Account / Access Key |

---

## Credential Storage

Credentials are stored securely.

Rules

- Encrypt before storage
- Never expose to frontend
- Rotate periodically
- Restrict access using RBAC

---

# 5. Google Gemini API

## Purpose

Primary AI model for all content generation workflows.

---

## Features

- Content generation
- Prompt execution
- Reasoning
- Summarization
- Translation
- Structured JSON output

---

## Authentication

```
API Key
```

---

## Base URL

```
https://generativelanguage.googleapis.com/
```

---

## Primary Use Cases

- Strategy Agent
- Research Agent
- Content Planner
- Content Generator
- Brand Voice
- Fact Check
- SEO
- Hashtag Generation
- Image Prompt Generation

---

## Request Flow

```
LangGraph

↓

Prompt Builder

↓

Gemini API

↓

JSON Response

↓

Validation

↓

Workflow State
```

---

## Error Handling

Retry

- Timeout
- Temporary Service Errors

Do Not Retry

- Invalid API Key
- Invalid Request
- Permission Denied

---

# 6. X (Twitter) API

## Purpose

Publish posts and retrieve analytics from X.

---

## Authentication

```
OAuth 2.0
```

---

## Features

- Publish Posts
- Publish Threads
- Delete Posts
- Read Analytics
- Retrieve User Information

---

## Example Endpoints

```
POST /tweets

GET /tweets

GET /users/me
```

---

## Required Permissions

- Read Tweets
- Write Tweets
- Read User Profile

---

## Retry Strategy

Retry

- Network Timeout
- HTTP 429
- Temporary Server Errors

---

## Database Tables

- SocialAccount
- APICredential
- PublishingLog

---

# 7. LinkedIn API

## Purpose

Publish professional content and retrieve engagement analytics.

---

## Authentication

```
OAuth 2.0
```

---

## Features

- Publish Posts
- Upload Images
- Retrieve Analytics
- Manage Organization Posts

---

## Example Endpoints

```
POST /ugcPosts

GET /organizationalEntityShareStatistics
```

---

## Required Permissions

- OpenID
- Profile
- Email
- Content Publishing

---

## Retry Strategy

Retry only for

- Rate Limits
- Network Failures
- Temporary Server Errors

---

# End of Part 1

Next:

- Meta Graph API
- Instagram API
- Threads API
- NewsAPI
- Tavily API
- Cloud Storage APIs
- Email APIs
- Webhook Architecture

---

# 8. Meta Graph API

## Purpose

The Meta Graph API enables publishing and analytics for Facebook Pages and Instagram Business accounts.

---

## Authentication

```
OAuth 2.0
```

---

## Features

- Publish Posts
- Upload Images
- Upload Videos
- Read Insights
- Manage Pages
- Retrieve Comments

---

## Supported Platforms

- Facebook Pages
- Instagram Business

---

## Example Endpoints

```
POST /{page-id}/feed

POST /{page-id}/photos

POST /{page-id}/videos

GET /{page-id}/insights

GET /{page-id}/posts
```

---

## Required Permissions

- pages_manage_posts
- pages_read_engagement
- pages_show_list
- instagram_basic
- instagram_content_publish

---

## Retry Strategy

Retry

- HTTP 429
- HTTP 500
- HTTP 503
- Network Timeout

Maximum

```
3 Retries
```

---

## Database Tables

- Platform
- SocialAccount
- APICredential
- PublishingLog
- AnalyticsSnapshot

---

# 9. Instagram API

## Purpose

Manage Instagram Business account publishing and analytics.

---

## Authentication

```
OAuth 2.0
```

---

## Supported Content

- Images
- Carousel Posts
- Videos
- Reels (Future)

---

## Features

- Publish Content
- Upload Media
- Read Insights
- Retrieve Profile Information

---

## Request Flow

```
CreatorOS

↓

Media Upload

↓

Instagram Media Container

↓

Publish

↓

Receive Media ID

↓

Store Publishing Log
```

---

## Analytics

Retrieve

- Reach
- Impressions
- Likes
- Comments
- Saves
- Shares
- Profile Visits

---

# 10. Threads API

## Purpose

Publish content to Threads.

---

## Authentication

```
OAuth 2.0
```

---

## Features

- Publish Thread
- Delete Post
- Read User Information
- Analytics (Future)

---

## Supported Content

- Text
- Images

---

## Retry Policy

Retry

- Rate Limit
- Timeout
- Temporary Server Error

---

# 11. NewsAPI Integration

## Purpose

Retrieve current news for research and content generation.

---

## Authentication

```
API Key
```

---

## Base URL

```
https://newsapi.org/
```

---

## AI Use Cases

- Research Agent
- Trend Agent
- Fact Check Agent

---

## Request Flow

```
Research Agent

↓

NewsAPI

↓

News Articles

↓

Summarization

↓

Workflow State
```

---

## Response Fields

- Title
- Description
- URL
- Source
- Published Date

---

## Error Handling

Retry

- Timeout
- HTTP 500

Do Not Retry

- Invalid API Key
- Invalid Parameters

---

# 12. Tavily API

## Purpose

Perform AI-optimized web search for research workflows.

---

## Authentication

```
API Key
```

---

## Features

- Web Search
- Answer Retrieval
- Source URLs
- Content Summarization

---

## AI Agents

- Research Agent
- Fact Check Agent
- Trend Agent

---

## Request Flow

```
Research Agent

↓

Tavily Search

↓

Relevant Sources

↓

Summary

↓

Workflow State
```

---

## Validation

- Remove duplicate sources
- Verify response structure
- Filter unsupported websites

---

# 13. Cloud Storage APIs

## Purpose

Store uploaded media and generated assets.

---

## Supported Providers

- AWS S3
- Google Cloud Storage
- Cloudflare R2

---

## Stored Files

- Images
- Videos
- Logos
- Documents
- AI Generated Assets

---

## Upload Flow

```
Frontend

↓

FastAPI

↓

Media Service

↓

Cloud Storage

↓

File URL

↓

Database
```

---

## Security

- Signed URLs
- Private Buckets
- File Validation
- Virus Scanning (Future)

---

## Metadata Stored

- File Name
- File Size
- MIME Type
- Upload Date
- Storage Provider
- Storage URL

---

# 14. Email Service

## Purpose

Send transactional emails.

---

## Recommended Providers

- Resend
- SendGrid
- Amazon SES

---

## Email Types

- Welcome Email
- Email Verification
- Password Reset
- Workspace Invitation
- Approval Notification
- Publishing Status
- Weekly Report

---

## Workflow

```
Application Event

↓

Email Service

↓

Template Engine

↓

Provider

↓

Recipient
```

---

## Retry Strategy

Retry

- Temporary SMTP Failure
- Provider Timeout

Maximum

```
3 Retries
```

---

# 15. Webhook Architecture

## Purpose

Receive asynchronous events from external services.

---

## Supported Webhooks

- Publishing Status
- OAuth Events
- Analytics Updates
- Media Processing
- Subscription Events

---

## Workflow

```
External Platform

↓

Webhook Endpoint

↓

Signature Verification

↓

Validation

↓

Event Processing

↓

Database Update
```

---

## Security

- HTTPS Required
- Verify Signature
- Timestamp Validation
- Replay Protection

---

## Event Logging

Store

- Event ID
- Provider
- Event Type
- Received Time
- Processing Status
- Error Details

---

# End of Part 2

**Next:** Part 3 – Notification Services, Analytics Integrations, Monitoring APIs, Payment APIs, AI Image APIs, Translation APIs, Retry Policies, Rate Limiting, and Integration Security.

---

# 16. Notification Services

## Purpose

Deliver notifications to users about important system events.

---

## Notification Channels

### Email

- Welcome Email
- Password Reset
- Approval Request
- Publishing Status
- Weekly Analytics

---

### In-App Notifications

- AI Generation Completed
- Publishing Success
- Publishing Failure
- Team Invitation
- Approval Updates

---

### Future Channels

- Push Notifications
- Slack
- Microsoft Teams
- Discord
- WhatsApp Business

---

## Notification Workflow

```
Application Event

↓

Notification Service

↓

Determine Channel

↓

Render Template

↓

Send Notification

↓

Store Delivery Status
```

---

## Retry Strategy

| Failure | Action |
|----------|---------|
| SMTP Timeout | Retry |
| API Timeout | Retry |
| Invalid Email | Don't Retry |
| Invalid Device Token | Don't Retry |

---

# 17. Analytics Integrations

## Purpose

Collect performance metrics from connected social media platforms.

---

## Supported Sources

- X Analytics
- LinkedIn Analytics
- Meta Insights
- Instagram Insights
- Threads Analytics (Future)

---

## Metrics

- Impressions
- Reach
- Likes
- Comments
- Shares
- Saves
- Clicks
- Followers
- Engagement Rate

---

## Analytics Flow

```
Scheduler

↓

Analytics Agent

↓

Platform API

↓

Normalize Data

↓

AnalyticsSnapshot

↓

Dashboard
```

---

## Refresh Frequency

| Type | Frequency |
|--------|-----------|
| Dashboard | Hourly |
| Post Analytics | Every 6 Hours |
| Reports | Daily |
| Manual Refresh | On Demand |

---

# 18. Monitoring APIs

## Purpose

Monitor health, performance, and availability of external integrations.

---

## Monitored Services

- Gemini API
- X API
- LinkedIn API
- Meta API
- Tavily
- NewsAPI
- Email Provider
- Cloud Storage

---

## Health Metrics

- Availability
- Response Time
- Error Rate
- Timeout Count
- Retry Count
- Success Rate

---

## Health Check Workflow

```
Monitoring Service

↓

Ping API

↓

Collect Metrics

↓

Store Metrics

↓

Dashboard
```

---

## Alert Conditions

- API unavailable
- Response time > 5 seconds
- Error rate > 10%
- Authentication failure
- Rate limit exceeded

---

# 19. Payment APIs (Future)

## Purpose

Support subscriptions and billing for SaaS customers.

---

## Candidate Providers

- Stripe
- Razorpay
- PayPal

---

## Features

- Subscription Management
- One-Time Payments
- Invoice Generation
- Refund Processing
- Webhook Events

---

## Payment Workflow

```
User

↓

Choose Plan

↓

Payment Gateway

↓

Payment Success

↓

Subscription Activated

↓

Database Updated
```

---

## Security

- PCI Compliance
- HTTPS Only
- Webhook Verification
- Tokenized Payments

---

# 20. AI Image Generation APIs

## Purpose

Generate images based on prompts created by the Image Prompt Agent.

---

## Supported Providers

- GPT Image
- Google Imagen
- FLUX
- Stable Diffusion

---

## Workflow

```
Image Prompt

↓

Image API

↓

Generate Image

↓

Store Image

↓

Return URL
```

---

## Output

- PNG
- JPG
- WEBP

---

## Metadata

Store

- Prompt
- Model
- Resolution
- Generation Time
- Cost
- File URL

---

# 21. Translation APIs

## Purpose

Support multilingual content generation.

---

## Languages

- English
- Hindi
- Marathi
- Spanish
- French
- German
- Japanese

---

## Candidate Providers

- Gemini
- Google Cloud Translation
- DeepL

---

## Workflow

```
Original Content

↓

Translation Service

↓

Translated Content

↓

Brand Review

↓

Return Result
```

---

## Validation

- Preserve meaning
- Maintain tone
- Preserve formatting
- Verify language code

---

# 22. Retry Policies

Every external integration follows a standardized retry strategy.

---

## Retry Matrix

| API | Retries | Backoff |
|------|---------:|---------|
| Gemini | 2 | Exponential |
| X API | 3 | Exponential |
| LinkedIn | 3 | Exponential |
| Meta | 3 | Exponential |
| Tavily | 2 | Exponential |
| NewsAPI | 2 | Exponential |
| Email | 3 | Linear |
| Cloud Storage | 2 | Exponential |

---

## Retry Flow

```
Request

↓

Failure

↓

Retry

↓

Failure

↓

Retry

↓

Failure

↓

Fallback

↓

Error Response
```

---

## Non-Retryable Errors

- Invalid Credentials
- Invalid Request
- Permission Denied
- Unsupported Endpoint
- Resource Not Found

---

# 23. Rate Limiting Strategy

## Purpose

Prevent exceeding provider quotas and improve reliability.

---

## Strategies

- Token Bucket
- Request Queue
- Exponential Backoff
- Circuit Breaker
- Request Prioritization

---

## Internal Limits

| Service | Limit |
|----------|------:|
| AI Generation | 10 concurrent jobs |
| Publishing | 5 concurrent jobs |
| Analytics Sync | 20 concurrent jobs |
| Image Generation | 5 concurrent jobs |

---

## Overflow Handling

```
Incoming Request

↓

Queue

↓

Available Worker?

↓

Yes

↓

Execute

↓

No

↓

Wait
```

---

# 24. Integration Security

## Credential Protection

Store

- OAuth Tokens
- API Keys
- Client Secrets

Encrypted using secure server-side storage.

---

## Best Practices

- Never expose secrets to frontend
- Rotate credentials regularly
- Encrypt sensitive data
- Use HTTPS
- Validate webhook signatures
- Apply least-privilege permissions

---

## Access Control

Only authorized backend services may call external APIs.

Frontend never communicates directly with third-party providers.

---

## Audit Logging

Log

- Provider
- Endpoint
- Timestamp
- Response Time
- Status Code
- Retry Count
- Error Details

---

## Security Architecture

```
Frontend

↓

FastAPI

↓

Authentication

↓

Integration Layer

↓

Secrets Manager

↓

External API
```

---

# End of Part 3

**Next:** Part 4 – Integration Layer Design, API Client Architecture, Error Mapping, Response Normalization, Configuration Management, Testing Strategy, Future Integrations, Best Practices, and Final Summary.

---

# 25. Integration Layer Design

## Purpose

The Integration Layer provides a unified interface between CreatorOS AI and all external services.

Instead of allowing business services to communicate directly with third-party APIs, every request passes through the Integration Layer.

---

## Responsibilities

- Authentication
- Request Construction
- Response Validation
- Error Handling
- Retry Logic
- Logging
- Monitoring
- Response Normalization

---

## Architecture

```
React Frontend
        │
        ▼
FastAPI
        │
        ▼
Business Service
        │
        ▼
Integration Layer
        │
 ┌──────┼────────┬─────────┬────────────┐
 ▼      ▼        ▼         ▼
Gemini  X API  LinkedIn  Meta Graph
        │
        ▼
 Response Handler
        │
        ▼
Business Service
```

---

## Advantages

- Loose Coupling
- Centralized Error Handling
- Easier Testing
- Better Security
- Reusable API Clients

---

# 26. API Client Architecture

Every external provider has its own API client.

---

## Structure

```
integration/

│

├── gemini_client.py

├── x_client.py

├── linkedin_client.py

├── meta_client.py

├── tavily_client.py

├── news_client.py

├── storage_client.py

├── email_client.py

└── base_client.py
```

---

## Base Client Responsibilities

- Authentication
- Retry Logic
- Timeout Handling
- Logging
- Rate Limiting

---

## Provider Client Responsibilities

- Provider-specific Endpoints
- Request Mapping
- Response Parsing
- Error Conversion

---

# 27. Error Mapping

Different providers return different error formats.

The Integration Layer converts them into a unified structure.

---

## Standard Error Schema

```json
{
    "success": false,
    "error": {
        "code": "EXTERNAL_API_ERROR",
        "provider": "Gemini",
        "message": "Rate limit exceeded"
    }
}
```

---

## Mapping Examples

| Provider Error | Internal Error |
|----------------|----------------|
| HTTP 429 | RATE_LIMIT_EXCEEDED |
| HTTP 401 | AUTHENTICATION_FAILED |
| HTTP 403 | PERMISSION_DENIED |
| HTTP 404 | RESOURCE_NOT_FOUND |
| HTTP 500 | INTERNAL_PROVIDER_ERROR |
| Timeout | REQUEST_TIMEOUT |

---

## Benefits

- Consistent frontend handling
- Easier debugging
- Cleaner service layer
- Simplified monitoring

---

# 28. Response Normalization

## Purpose

Convert responses from different providers into a common internal format.

---

## Example

### X API Response

```json
{
    "id": "12345",
    "text": "Hello World"
}
```

↓

### LinkedIn Response

```json
{
    "share": "abc123",
    "commentary": "Hello World"
}
```

↓

### Internal Format

```json
{
    "post_id": "12345",
    "content": "Hello World",
    "platform": "X"
}
```

---

## Advantages

- Platform-independent services
- Easier analytics
- Cleaner database schema

---

# 29. Configuration Management

All integration settings should be stored securely.

---

## Environment Variables

```env
GEMINI_API_KEY=

X_CLIENT_ID=

X_CLIENT_SECRET=

LINKEDIN_CLIENT_ID=

LINKEDIN_CLIENT_SECRET=

META_CLIENT_ID=

META_CLIENT_SECRET=

NEWS_API_KEY=

TAVILY_API_KEY=

RESEND_API_KEY=
```

---

## Configuration Rules

- Never commit secrets
- Use `.env` for development
- Use a secret manager in production
- Validate required variables during startup

---

## Future Secret Managers

- Google Secret Manager
- AWS Secrets Manager
- Azure Key Vault
- HashiCorp Vault

---

# 30. Integration Testing Strategy

## Purpose

Verify that external integrations behave correctly.

---

## Test Types

### Unit Testing

Mock external APIs.

---

### Integration Testing

Test against sandbox environments.

---

### End-to-End Testing

Test the complete workflow.

Example

```
Generate Content

↓

Publish to X

↓

Retrieve Analytics

↓

Store Database
```

---

## Mock Testing

Use mocked responses for

- Gemini
- LinkedIn
- Meta
- NewsAPI
- Tavily

---

## Failure Testing

Simulate

- Timeout
- Rate Limit
- Invalid Token
- Server Error
- Network Failure

---

# 31. Future Integrations

CreatorOS AI is designed for future extensibility.

---

## AI Providers

- OpenAI
- Anthropic Claude
- Cohere
- DeepSeek
- Mistral

---

## Social Platforms

- TikTok
- Pinterest
- YouTube Community
- Reddit
- Mastodon

---

## Productivity Platforms

- Notion
- Google Docs
- Slack
- Trello
- Jira

---

## Cloud Storage

- Dropbox
- OneDrive
- Box

---

## CRM Integrations

- HubSpot
- Salesforce
- Zoho CRM

---

# 32. External API Best Practices

## Design Principles

- Keep integrations loosely coupled
- Use dedicated API clients
- Normalize responses
- Retry only transient failures
- Validate all responses

---

## Security Principles

- Encrypt credentials
- Rotate API keys
- Validate webhook signatures
- Restrict OAuth scopes
- Never expose secrets

---

## Performance Principles

- Cache repeated requests
- Use asynchronous HTTP clients
- Batch requests when possible
- Minimize duplicate API calls

---

## Reliability Principles

- Monitor API health
- Log all failures
- Support fallback providers
- Use circuit breakers

---

# 33. Summary

The External API architecture enables CreatorOS AI to communicate securely and efficiently with AI providers, social media platforms, analytics services, cloud storage providers, and notification systems.

Key capabilities include:

- Centralized Integration Layer
- Secure Authentication
- Standardized API Clients
- Response Normalization
- Unified Error Handling
- Retry & Rate Limiting
- Monitoring & Logging
- Extensible Integration Architecture

---

# 34. Conclusion

This document defines the complete external integration strategy for CreatorOS AI.

Following these guidelines ensures that all third-party services are integrated consistently, securely, and reliably while maintaining a modular architecture that supports future expansion.

Together with the API Design, AI Agent Design, Workflow, and Prompt Engineering documents, this specification provides the implementation blueprint for all external service integrations.

---

# Document Status

**Document:** `09_External_APIs.md`

**Version:** 1.0

**Status:** ✅ Completed

**Next Document**

```
docs/10_Backend_Architecture.md
```

---

**End of Document**