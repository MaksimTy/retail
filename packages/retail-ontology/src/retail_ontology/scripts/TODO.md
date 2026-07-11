# TODO: Future Refactoring

## Planned Improvements

### 1. Universal Schema System
- [ ] Create a generic `SchemaRegistry` class that can load table definitions from YAML/JSON
- [ ] Support multiple data sources (not just UCI Online Retail)
- [ ] Add schema versioning and migration support
- [ ] Implement schema validation against actual database

### 2. Generic ETL Pipeline
- [ ] Extract `WarehouseEngine` into a reusable `ETLPipeline` base class
- [ ] Support configurable source-to-target column mappings
- [ ] Add support for incremental loads (CDC)
- [ ] Implement data quality rules as pluggable components

### 3. Adapter Improvements
- [ ] Add connection pooling to `DuckDBAdapter`
- [ ] Implement `PostgresAdapter` and `SnowflakeAdapter`
- [ ] Add async batch operations for better performance
- [ ] Implement query result streaming for large datasets

### 4. Configuration Management
- [ ] Move all hardcoded values to configuration files (YAML/TOML)
- [ ] Support environment-specific configs (dev/staging/prod)
- [ ] Add configuration validation at startup

### 5. Testing & Observability
- [ ] Add unit tests for schema generation
- [ ] Add integration tests for ETL pipeline
- [ ] Implement structured logging with correlation IDs
- [ ] Add metrics collection (row counts, timing, error rates)

### 6. Data Quality Framework
- [ ] Create reusable data quality rule engine
- [ ] Support Great Expectations or similar framework
- [ ] Add data profiling capabilities
- [ ] Implement automated data quality reports

---

## Notes

The current implementation is tightly coupled to the UCI Online Retail dataset. The goal is to make the warehouse builder generic enough to handle any retail/e-commerce dataset with minimal configuration changes.

**Priority**: Medium - Current implementation works for the MVP. Refactor when adding new data sources or when the codebase grows beyond maintainability.

**Estimated Effort**: 2-3 weeks for full generic implementation
