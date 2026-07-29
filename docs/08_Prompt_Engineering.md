# 08 Prompt Engineering

# CreatorOS AI

# Prompt Engineering

**Document Version:** 1.0

**Document Type:** AI Prompt Engineering

**Status:** Draft

**Last Updated:** July 2026

---

# Related Documents

- 00_Project_Vision.md
- 05_API_Design.md
- 06_AI_Agent_Design.md
- 07_Workflows.md

---

# Table of Contents

1. Introduction
2. Prompt Engineering Goals
3. Prompt Architecture
4. Prompt Lifecycle
5. Prompt Versioning
6. Prompt Validation
7. Strategy Agent Prompt
8. Trend Agent Prompt
9. Research Agent Prompt

---

# 1. Introduction

## Purpose

This document defines the prompt engineering standards used by CreatorOS AI.

Every AI interaction follows standardized prompts to ensure:

- High-quality responses
- Consistent brand voice
- Predictable outputs
- Safe AI behavior
- Structured JSON responses

---

# 2. Prompt Engineering Goals

The prompt engineering framework aims to:

- Generate accurate content
- Reduce hallucinations
- Improve consistency
- Minimize token usage
- Produce structured outputs
- Support multiple AI models
- Enable easy prompt maintenance

---

# 3. Prompt Architecture

Every prompt consists of five sections.

```
System Prompt
        │
        ▼
Context
        │
        ▼
Task Instructions
        │
        ▼
Output Format
        │
        ▼
Validation Rules
```

---

## Prompt Components

### System Prompt

Defines the AI's role and behavior.

### Context

Provides workspace, brand kit, and project information.

### Task

Describes the work to perform.

### Output Format

Defines the expected JSON response.

### Validation Rules

Specifies constraints and quality checks.

---

# 4. Prompt Lifecycle

```
Prompt Created
       │
       ▼
Versioned
       │
       ▼
Tested
       │
       ▼
Approved
       │
       ▼
Production
       │
       ▼
Monitoring
       │
       ▼
Optimization
```

---

# 5. Prompt Versioning

Each prompt must include metadata.

Example

```yaml
prompt_id: strategy_prompt
version: 1.0.0
author: CreatorOS Team
model: Gemini 2.5 Pro
status: Production
last_updated: 2026-07-29
```

---

## Version Rules

| Version | Meaning |
|----------|---------|
| 1.0.0 | Initial Release |
| 1.1.0 | Minor Improvements |
| 2.0.0 | Major Rewrite |
| 2.1.0 | New Features |
| 3.0.0 | Breaking Changes |

---

# 6. Prompt Validation

Every prompt must satisfy the following checks.

## Required

- Clear objective
- Defined role
- Structured instructions
- Output schema
- Error handling

---

## Quality Checklist

- No ambiguous instructions
- No conflicting requirements
- Platform-specific guidance
- Token efficient
- Easy to maintain

---

# 7. Strategy Agent Prompt

## Purpose

Determine the overall content strategy.

---

## System Prompt

```
You are an expert social media strategist.

Analyze the user's request and determine:

- Content goal
- Target audience
- Platform strategy
- Tone
- Content format

Provide concise reasoning and return only valid JSON.
```

---

## Input

```json
{
  "topic": "Future of Artificial Intelligence",
  "platform": "X",
  "audience": "Developers",
  "tone": "Professional"
}
```

---

## Expected Output

```json
{
  "goal": "Educate",
  "content_type": "Thread",
  "tone": "Professional",
  "audience": "Developers"
}
```

---

# 8. Trend Agent Prompt

## Purpose

Identify relevant trends and hashtags.

---

## System Prompt

```
You are a trend analysis expert.

Identify current topics relevant to the user's request.

Prioritize:

- Current trends
- Industry relevance
- High engagement potential

Return only valid JSON.
```

---

## Expected Output

```json
{
  "trends": [
    "AI Agents",
    "Generative AI",
    "LangGraph"
  ],
  "hashtags": [
    "#AI",
    "#GenAI",
    "#LangGraph"
  ]
}
```

---

# 9. Research Agent Prompt

## Purpose

Collect accurate and trustworthy information.

---

## System Prompt

```
You are an AI research assistant.

Research the topic using trusted information.

Summarize only verified facts.

Do not invent information.

Highlight uncertain claims separately.

Return valid JSON.
```

---

## Expected Output

```json
{
  "summary": "Artificial Intelligence is transforming software development through automation, reasoning, and generative models.",
  "sources": [
    "Trusted Source 1",
    "Trusted Source 2"
  ],
  "confidence": 0.96
}
```

---

# End of Part 1

**Next:** Part 2 – Content Planner Prompt, Content Generator Prompt, Brand Voice Prompt, Fact Check Prompt, SEO Prompt, Hashtag Prompt, and Image Prompt.

---

# 10. Content Planner Agent Prompt

## Purpose

Transform research into a structured content outline before writing begins.

---

## System Prompt

```
You are an expert content strategist.

Create a clear, logical, and engaging outline based on the provided research.

Requirements:

- Keep the structure easy to follow.
- Adapt the outline for the selected platform.
- Avoid unnecessary sections.
- Return only valid JSON.
```

---

## Input

```json
{
  "topic": "Future of Artificial Intelligence",
  "research": "...",
  "platform": "LinkedIn"
}
```

---

## Expected Output

```json
{
  "title": "The Future of Artificial Intelligence",
  "outline": [
    "Introduction",
    "Current State",
    "Future Trends",
    "Challenges",
    "Conclusion"
  ]
}
```

---

## Validation Rules

- Minimum 3 sections
- Maximum 8 sections
- Logical ordering
- Platform appropriate

---

# 11. Content Generator Agent Prompt

## Purpose

Generate complete social media content from the approved outline.

---

## System Prompt

```
You are a professional social media copywriter.

Write engaging, accurate, and original content.

Requirements:

- Follow the provided outline.
- Maintain the requested tone.
- Optimize for readability.
- Avoid repetition.
- Do not invent facts.
- Include a strong call-to-action where appropriate.
- Return valid JSON only.
```

---

## Context

Includes

- Brand Kit
- Audience
- Platform
- Tone
- Outline
- Research Summary

---

## Input

```json
{
  "platform": "X",
  "tone": "Professional",
  "outline": [
    "Introduction",
    "Benefits",
    "Conclusion"
  ]
}
```

---

## Expected Output

```json
{
  "title": "AI Agents Are Changing Everything",
  "content": "..."
}
```

---

## Platform Guidelines

### X

- Short
- Engaging
- Thread-friendly

---

### LinkedIn

- Professional
- Educational
- Longer form

---

### Instagram

- Storytelling
- Emoji-friendly
- Caption optimized

---

## Validation Rules

- No plagiarism
- No unsupported claims
- Proper grammar
- Platform limits respected

---

# 12. Brand Voice Agent Prompt

## Purpose

Ensure generated content aligns with the organization's brand identity.

---

## System Prompt

```
You are a brand editor.

Review the content and ensure it matches the brand guidelines.

Improve consistency without changing the original meaning.

Return only valid JSON.
```

---

## Brand Context

Includes

- Brand Name
- Brand Values
- Writing Style
- Tone
- Target Audience
- Restricted Words

---

## Expected Output

```json
{
  "brand_score": 96,
  "updated_content": "...",
  "changes": [
    "Simplified sentence",
    "Removed restricted phrase"
  ]
}
```

---

## Validation Rules

- Preserve meaning
- Follow brand voice
- Remove restricted language
- Improve consistency

---

# 13. Fact Check Agent Prompt

## Purpose

Validate factual accuracy before publishing.

---

## System Prompt

```
You are a professional fact checker.

Review every factual statement.

Mark unsupported claims.

Do not invent facts.

Return valid JSON.
```

---

## Expected Output

```json
{
  "verified": true,
  "confidence": 0.97,
  "issues": []
}
```

---

## Validation Rules

- Verify statistics
- Verify dates
- Verify company names
- Flag uncertain information

---

# 14. SEO Agent Prompt

## Purpose

Improve discoverability while maintaining readability.

---

## System Prompt

```
You are an SEO specialist.

Improve search visibility without changing the original meaning.

Avoid keyword stuffing.

Return valid JSON.
```

---

## Expected Output

```json
{
  "seo_score": 91,
  "keywords": [
    "AI",
    "Automation",
    "LangGraph"
  ],
  "recommendations": [
    "Improve heading",
    "Use stronger CTA"
  ]
}
```

---

## Validation Rules

- Natural keyword placement
- Maintain readability
- Preserve original intent

---

# 15. Hashtag Agent Prompt

## Purpose

Generate optimized hashtags for the selected platform.

---

## System Prompt

```
You are a social media growth expert.

Generate relevant hashtags.

Use a mix of:

- High-volume hashtags
- Medium-volume hashtags
- Niche hashtags

Remove duplicates.

Return valid JSON.
```

---

## Platform Rules

### X

Maximum

```
3 hashtags
```

---

### LinkedIn

Maximum

```
5 hashtags
```

---

### Instagram

Maximum

```
15 hashtags
```

---

## Expected Output

```json
{
  "hashtags": [
    "#ArtificialIntelligence",
    "#AI",
    "#LangGraph"
  ]
}
```

---

# 16. Image Prompt Agent Prompt

## Purpose

Generate high-quality prompts for AI image generation models.

---

## System Prompt

```
You are an expert visual designer.

Create a detailed image generation prompt.

Requirements:

- Match the content theme.
- Follow brand colors.
- Describe composition.
- Describe lighting.
- Describe style.
- Do not include text inside the image unless explicitly requested.

Return valid JSON.
```

---

## Expected Output

```json
{
  "prompt": "A futuristic workspace with holographic AI dashboards, cinematic lighting, blue and white color palette, ultra-detailed, modern office environment."
}
```

---

## Supported Models

- GPT Image
- Imagen
- Flux
- Stable Diffusion

---

## Validation Rules

- Highly descriptive
- Platform appropriate
- Brand consistent
- No copyrighted characters
- No unsafe content

---

# End of Part 2

**Next:** Part 3 – Scheduling Prompt, Publishing Prompt, Analytics Prompt, Feedback Prompt, Prompt Chaining, Prompt Templates, Context Management, and Prompt Security.

---

# 17. Scheduling Agent Prompt

## Purpose

Recommend the best publishing schedule based on audience activity, platform behavior, and workspace preferences.

---

## System Prompt

```
You are a social media scheduling expert.

Analyze the content, audience, platform, and historical analytics.

Recommend the optimal publishing date and time.

Prioritize:

- Maximum engagement
- Audience activity
- Timezone
- Platform best practices

Return valid JSON only.
```

---

## Context

Includes

- Platform
- Audience Analytics
- Workspace Timezone
- Historical Engagement
- Publishing Preferences

---

## Input

```json
{
  "platform": "LinkedIn",
  "timezone": "Asia/Kolkata",
  "audience": "Software Engineers"
}
```

---

## Expected Output

```json
{
  "recommended_time": "2026-08-15T10:30:00Z",
  "timezone": "Asia/Kolkata",
  "reason": "Highest engagement window"
}
```

---

## Validation Rules

- Future date only
- Valid timezone
- Platform supported
- Respect workspace settings

---

# 18. Publishing Agent Prompt

## Purpose

Validate content before publishing and prepare platform-specific publishing requests.

---

## System Prompt

```
You are a publishing assistant.

Before publishing:

- Validate content.
- Verify media.
- Ensure approval is complete.
- Confirm platform compatibility.

Return only valid JSON.
```

---

## Context

Includes

- Generated Content
- Media Assets
- Approval Status
- Platform Information

---

## Expected Output

```json
{
  "ready": true,
  "platform": "LinkedIn",
  "warnings": []
}
```

---

## Validation Rules

- Content approved
- Media accessible
- OAuth token valid
- Platform connected

---

# 19. Analytics Agent Prompt

## Purpose

Analyze post performance and generate actionable insights.

---

## System Prompt

```
You are a social media analytics expert.

Review the analytics data and identify:

- Strong metrics
- Weak metrics
- Engagement trends
- Recommendations

Provide concise and actionable insights.

Return valid JSON only.
```

---

## Input

```json
{
  "likes": 230,
  "comments": 18,
  "shares": 25,
  "reach": 9200
}
```

---

## Expected Output

```json
{
  "engagement_score": 8.7,
  "insights": [
    "Strong engagement rate",
    "High share count",
    "Posting time was effective"
  ]
}
```

---

## Validation Rules

- Numeric metrics only
- Recommendations supported by data
- Avoid speculation

---

# 20. Feedback Agent Prompt

## Purpose

Learn from historical performance and recommend improvements for future content.

---

## System Prompt

```
You are an AI content optimization expert.

Compare historical content performance.

Identify successful patterns.

Recommend improvements.

Return valid JSON only.
```

---

## Context

Includes

- Historical Analytics
- Published Posts
- Audience Growth
- Previous Recommendations

---

## Expected Output

```json
{
  "recommendations": [
    "Use stronger opening sentences",
    "Publish more educational posts",
    "Reduce caption length"
  ]
}
```

---

## Validation Rules

- Recommendations must be data-driven
- No unsupported assumptions
- Prioritize actionable advice

---

# 21. Prompt Chaining

## Purpose

Prompt chaining enables multiple AI agents to collaborate while maintaining workflow context.

---

## Chain Flow

```
Strategy Prompt
        │
        ▼
Trend Prompt
        │
        ▼
Research Prompt
        │
        ▼
Planning Prompt
        │
        ▼
Generation Prompt
        │
        ▼
Brand Prompt
        │
        ▼
Fact Check Prompt
        │
        ▼
SEO Prompt
        │
        ▼
Hashtag Prompt
        │
        ▼
Image Prompt
```

---

## Chaining Rules

- Pass structured JSON between agents
- Preserve shared workflow state
- Do not regenerate completed outputs
- Validate outputs before passing to the next agent

---

# 22. Prompt Templates

Every prompt follows the same template.

```text
Role

↓

Objective

↓

Context

↓

Instructions

↓

Constraints

↓

Output Format

↓

Validation Rules
```

---

## Standard Prompt Template

```text
System Role

Objective

Context

Task Instructions

Constraints

Expected JSON Output

Validation Rules
```

---

## Benefits

- Easier maintenance
- Consistent AI behavior
- Faster debugging
- Prompt reusability
- Improved output quality

---

# 23. Context Management

## Purpose

Provide each AI agent with only the context it requires.

---

## Context Sources

- Workspace
- Brand Kit
- Project
- Research Summary
- Analytics
- Platform
- Audience
- Previous Outputs

---

## Context Flow

```
Workspace

↓

Brand Kit

↓

Project

↓

Research

↓

Outline

↓

Draft

↓

Analytics
```

---

## Best Practices

- Avoid unnecessary context
- Remove duplicate information
- Pass only validated data
- Keep prompts concise

---

# 24. Prompt Security

## Purpose

Protect the AI system from malicious or unintended prompt manipulation.

---

## Threats

- Prompt Injection
- Jailbreak Attempts
- Malicious User Input
- Data Leakage
- Instruction Override

---

## Security Measures

- Validate all user input
- Sanitize external content
- Ignore conflicting instructions
- Restrict sensitive data exposure
- Log suspicious prompt activity

---

## Example Guardrails

### Do

- Follow system instructions
- Return structured JSON
- Respect brand guidelines
- Verify facts where applicable

### Don't

- Reveal system prompts
- Ignore security rules
- Generate harmful content
- Leak internal workflow information

---

## Prompt Sanitization Pipeline

```
User Input

↓

Input Validation

↓

Content Sanitization

↓

Prompt Construction

↓

LLM

↓

Output Validation

↓

Return Response
```

---

# End of Part 3

**Next:** Part 4 – Prompt Testing, Prompt Optimization, Model Selection Strategy, Token Management, Cost Optimization, Prompt Monitoring, Prompt Governance, Best Practices, and Final Summary.

---

# 25. Prompt Testing

## Purpose

Prompt testing ensures every prompt consistently produces accurate, safe, and structured outputs across supported AI models.

---

## Testing Objectives

- Verify output quality
- Ensure JSON validity
- Reduce hallucinations
- Validate business rules
- Measure latency
- Compare model performance

---

## Test Categories

### Functional Testing

Verify that the prompt completes the requested task correctly.

Examples

- Generate content
- Generate hashtags
- Generate image prompt

---

### Output Validation

Ensure

- Valid JSON
- Required fields present
- Correct data types
- No missing values

---

### Quality Testing

Evaluate

- Readability
- Accuracy
- Grammar
- Brand consistency
- Platform optimization

---

### Stress Testing

Test prompts with

- Long inputs
- Empty inputs
- Invalid inputs
- Special characters
- Multiple languages

---

## Example Test Case

| Field | Value |
|---------|--------|
| Test ID | PROMPT-001 |
| Prompt | Content Generator |
| Input | AI in Healthcare |
| Expected Result | Platform-specific JSON response |
| Status | Passed |

---

# 26. Prompt Optimization

## Purpose

Continuously improve prompts to increase response quality while reducing latency and token usage.

---

## Optimization Goals

- Improve accuracy
- Reduce hallucinations
- Lower token consumption
- Increase response consistency
- Improve reasoning quality

---

## Optimization Techniques

### Better Role Definition

Instead of

```
Write content.
```

Use

```
You are an experienced LinkedIn content strategist specializing in B2B technology.
```

---

### Explicit Instructions

Specify

- Tone
- Audience
- Platform
- Output format
- Constraints

---

### Structured Output

Always request JSON.

Example

```json
{
  "title": "",
  "content": "",
  "hashtags": []
}
```

---

### Reduce Prompt Length

Remove

- Duplicate instructions
- Redundant context
- Unused examples

---

## Continuous Improvement Cycle

```
Prompt

↓

Testing

↓

Evaluation

↓

Optimization

↓

Production

↓

Monitoring
```

---

# 27. Model Selection Strategy

## Purpose

Choose the most appropriate AI model for each task.

---

## Default Model

```
Gemini 2.5 Pro
```

---

## Fallback Model

```
GPT-5
```

---

## Future Models

- Claude
- Llama
- Mistral
- DeepSeek

---

## Model Selection Matrix

| Task | Preferred Model |
|---------|----------------|
| Strategy | Gemini 2.5 Pro |
| Trend Analysis | Gemini 2.5 Pro |
| Research | Gemini 2.5 Pro |
| Content Generation | Gemini 2.5 Pro |
| Brand Review | Gemini 2.5 Pro |
| Fact Checking | Gemini 2.5 Pro |
| SEO | Gemini 2.5 Pro |
| Image Prompt | Gemini 2.5 Pro |

---

## Fallback Rules

```
Primary Model

↓

Timeout?

↓

Retry

↓

Failure?

↓

Fallback Model

↓

Success

↓

Continue Workflow
```

---

# 28. Token Management

## Purpose

Optimize prompt size and response length to control latency and API costs.

---

## Token Budget

| Agent | Recommended Input Tokens | Recommended Output Tokens |
|---------|-------------------------:|--------------------------:|
| Strategy | 500 | 250 |
| Research | 1,500 | 500 |
| Planner | 800 | 400 |
| Generator | 2,000 | 800 |
| Brand Voice | 800 | 300 |
| Fact Check | 1,000 | 400 |
| SEO | 700 | 250 |
| Hashtag | 300 | 150 |
| Image Prompt | 500 | 250 |

---

## Best Practices

- Reuse shared context
- Trim unnecessary history
- Pass summaries instead of raw documents
- Cache reusable prompts
- Compress intermediate outputs

---

# 29. Cost Optimization

## Objectives

- Reduce API usage
- Improve response speed
- Minimize repeated requests

---

## Techniques

### Prompt Caching

Cache

- Brand Kit
- Prompt Templates
- System Prompts
- Frequently Used Research

---

### Shared Context

Avoid sending identical information to every agent.

Instead

```
Shared State

↓

All Agents
```

---

### Conditional Execution

Skip unnecessary agents.

Example

```
No image requested

↓

Skip Image Prompt Agent
```

---

### Batch Processing

Combine similar requests when possible.

Examples

- Multiple hashtag generations
- Analytics summaries
- Scheduled reports

---

# 30. Prompt Monitoring

## Purpose

Track prompt performance in production.

---

## Metrics

- Response Time
- Token Usage
- Cost Per Request
- Success Rate
- Retry Count
- Validation Failures
- JSON Parsing Errors

---

## Dashboard KPIs

- Average Response Time
- Average Tokens
- Prompt Success %
- Cost Per Workflow
- AI Error Rate

---

## Logging

Store

- Prompt ID
- Version
- Model
- Execution Time
- Tokens
- Status
- Error Message

---

# 31. Prompt Governance

## Purpose

Ensure prompts are reviewed, approved, and maintained consistently.

---

## Roles

| Role | Responsibility |
|------|----------------|
| AI Engineer | Create prompts |
| Reviewer | Review quality |
| Tech Lead | Approve changes |
| Administrator | Publish to production |

---

## Prompt Lifecycle

```
Draft

↓

Review

↓

Testing

↓

Approval

↓

Production

↓

Monitoring

↓

Improvement
```

---

## Change Management

Every prompt modification must record

- Version
- Author
- Date
- Reason for Change
- Approval Status

---

# 32. Prompt Engineering Best Practices

## Design Principles

- Use clear objectives
- Keep instructions concise
- Prefer structured outputs
- Validate every response
- Separate system and user instructions
- Minimize ambiguity

---

## AI Safety Principles

- Never expose system prompts
- Reject unsafe requests
- Protect confidential information
- Prevent prompt injection
- Enforce brand guidelines

---

## Performance Principles

- Reduce token usage
- Reuse context
- Cache prompt templates
- Execute independent tasks in parallel

---

# 33. Future Enhancements

Future improvements planned for CreatorOS AI include:

- Dynamic prompt generation
- Automatic prompt evaluation
- Prompt A/B testing
- Self-improving prompts
- Multi-model prompt routing
- Retrieval-Augmented Generation (RAG)
- Personalized prompts by workspace
- Industry-specific prompt libraries

---

# 34. Prompt Engineering Summary

The CreatorOS AI prompt engineering framework ensures that every AI interaction is:

- Consistent
- Accurate
- Secure
- Scalable
- Maintainable
- Cost-efficient

The framework standardizes prompt design across all AI agents and provides governance, monitoring, optimization, and testing to support production deployments.

---

# 35. Conclusion

This document defines the prompt engineering standards for CreatorOS AI.

By following these standards, all AI agents can produce reliable, structured, and high-quality outputs while maintaining security, performance, and brand consistency.

Together with the AI Agent Design document, this serves as the implementation guide for building the LangGraph-powered prompt system.

---

# Document Status

**Document:** `08_Prompt_Engineering.md`

**Version:** 1.0

**Status:** ✅ Completed

**Next Document**

```
docs/09_External_APIs.md
```

---

**End of Document**