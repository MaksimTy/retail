# Questions & Clarifications

## Retail Ontology Platform - Open Questions

This document captures questions and clarifications needed for the Retail Ontology Platform implementation.

---

## Questions for Clarification

### 1. OpenRouter Structured Output Implementation

**Question**: The architecture plan mentions using `instructor` library for structured output with OpenRouter, but the current implementation in `packages/retail-ontology/src/retail_ontology/llm/openrouter.py` may not be fully implemented.

**Details**:
- Is the `instructor` library integration complete?
- Are there any specific model requirements for structured output?
- Should we add fallback to non-structured output if instructor fails?

**Status**: ⚠️ Needs clarification

---

### 2. Authentication Implementation

**Question**: The API documentation mentions API key authentication, but the current implementation may not have this feature.

**Details**:
- Should authentication be implemented in the MVP?
- What authentication method should be used? (API key, JWT, OAuth?)
- Should there be different auth levels (admin, user, read-only)?

**Status**: ⚠️ Needs clarification

---

### 3. Snowflake Adapter Status

**Question**: The architecture diagram shows Snowflake adapter as "future", but it's listed in the package structure.

**Details**:
- Should we document this as a future feature?
- Is there a timeline for Snowflake support?
- Should we create a placeholder implementation?

**Status**: ⚠️ Needs clarification

---

### 4. Docker Images

**Question**: The deployment guide references Docker images, but no Dockerfiles exist in the project.

**Details**:
- Should Dockerfiles be created for each package?
- What base image should be used?
- Should we use multi-stage builds?

**Status**: ⚠️ Needs clarification

---

### 5. CI/CD Pipeline

**Question**: The implementation plan mentions GitHub Actions, but no workflow files exist.

**Details**:
- What CI/CD tools should be used? (GitHub Actions, GitLab CI, etc.)
- Should we include automated testing and publishing?
- What are the branch protection rules?

**Status**: ⚠️ Needs clarification

---

### 6. Data Pipeline Idempotency

**Question**: The ETL pipeline should be idempotent, but this needs verification.

**Details**:
- Can the warehouse be rebuilt multiple times safely?
- Should we implement incremental updates?
- How should we handle schema changes?

**Status**: ⚠️ Needs clarification

---

### 7. Query Validation Rules

**Question**: The query engine validation needs more specific rules.

**Details**:
- What validation rules should be applied?
- Should we validate against actual data or just schema?
- How should ambiguous queries be handled?

**Status**: ⚠️ Needs clarification

---

### 8. Rate Limiting Implementation

**Question**: The API documentation mentions rate limiting, but implementation details are missing.

**Details**:
- What rate limits should be applied?
- Should limits be per-user or per-API-key?
- Should we use Redis for distributed rate limiting?

**Status**: ⚠️ Needs clarification

---

### 9. Conversation Context Persistence

**Question**: The conversation context should persist across sessions.

**Details**:
- Should context be stored in memory, database, or file?
- How long should conversation history be retained?
- Should we implement conversation export/import?

**Status**: ⚠️ Needs clarification

---

### 10. Error Handling Strategy

**Question**: Error handling needs to be consistent across all components.

**Details**:
- Should we use custom exception classes?
- How should errors be logged and reported?
- Should we implement error recovery mechanisms?

**Status**: ⚠️ Needs clarification

---

## Missing Documentation

### 1. OpenAPI/Swagger Documentation

The API documentation mentions OpenAPI, but no auto-generated docs exist.

**Action**: Create OpenAPI schema and Swagger UI

### 2. Architecture Decision Records (ADRs)

No ADRs document architectural decisions.

**Action**: Create ADRs for major decisions

### 3. Contributing Guide

No contributing guide exists.

**Action**: Create CONTRIBUTING.md

### 4. Changelog

No changelog exists.

**Action**: Create CHANGELOG.md

### 5. Code Examples

Limited code examples in documentation.

**Action**: Add more practical examples

---

## Recommendations

### High Priority

1. **Create Dockerfiles** for each package
2. **Implement authentication** in API
3. **Add CI/CD workflows** for testing and publishing
4. **Create OpenAPI documentation** for API

### Medium Priority

1. **Document Snowflake adapter** as future feature
2. **Add rate limiting** to API
3. **Implement conversation persistence**
4. **Create ADRs** for architectural decisions

### Low Priority

1. **Add more code examples**
2. **Create changelog**
3. **Add contributing guide**

---

## Next Steps

1. Review and answer the questions above
2. Update documentation based on answers
3. Create missing documentation files
4. Implement missing features

---

## Document History

| Date | Version | Changes |
|------|---------|---------|
| 2024-01-15 | 0.1.0 | Initial questions list |
