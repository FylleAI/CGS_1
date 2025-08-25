# Deprecated Components Archive

This directory contains components that have been deprecated during the KBA (Knowledge Base Assistant) refactoring.

## Purpose

These files are preserved for:
- **Rollback capability**: In case we need to revert changes
- **Reference**: Understanding how the old system worked
- **Migration assistance**: Helping users transition to new KBA workflows

## Deprecated Workflows

### Newsletter Workflows
- `workflows/handlers/premium_newsletter_handler.py` - Generic premium newsletter generation
- `workflows/handlers/siebert_premium_newsletter_handler.py` - Siebert-specific newsletter with Perplexity integration
- `workflows/templates/premium_newsletter.json` - Premium newsletter template
- `workflows/templates/siebert_premium_newsletter.json` - Siebert newsletter template

### Article Workflows  
- `workflows/handlers/enhanced_article_handler.py` - Enhanced article generation with research
- `workflows/templates/enhanced_article.json` - Enhanced article template

## Migration Path

**Old System (Deprecated)**:
```python
# Content generation focused on newsletters and articles
workflow_types = [
    "premium_newsletter",
    "siebert_premium_newsletter", 
    "enhanced_article"
]
```

**New System (KBA)**:
```python
# Knowledge base ingestion and transformation focused
workflow_types = [
    "kba_ingestion",
    "kba_transformation", 
    "kba_export"
]
```

## Deprecation Status

All handlers in this archive have been marked with:
- `DEPRECATED = True` flag
- Deprecation warnings in `__init__` methods
- Updated docstrings with deprecation notices

## Removal Timeline

These components will be completely removed in a future major version release. Users should migrate to KBA workflows before then.

## Archive Date

Archived on: 2025-08-25 during KBA refactoring (Phase 1)
