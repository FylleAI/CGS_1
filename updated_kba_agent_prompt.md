# 🤖 PROMPT AGENT KBA REFACTORING - VERSIONE COMPLETA

## 📚 DOCUMENTI DI RIFERIMENTO OBBLIGATORI

### 🎯 STRATEGICI (LETTURA PRIORITARIA)
1. **REFACTOR_PLAN.md** - Piano master trasformazione
2. **MIGRATION_GUIDE.md** - Strategia migrazione
3. **ERROR_RECOVERY_GUIDE.md** - Procedure sicurezza Git

### 🏗️ ARCHITETTURALI (COMPRENSIONE SISTEMA)
4. **docs/architecture/clean_architecture.md** - Principi architetturali
5. **core/domain/README.md** - Layer dominio
6. **core/infrastructure/README.md** - Layer infrastruttura

### 🔧 IMPLEMENTATIVI (RIFERIMENTO CODICE)
7. **core/infrastructure/tools/rag_tool.py** - Esempio tool esistente
8. **core/application/use_cases/** - Pattern use cases
9. **api/rest/v1/endpoints/knowledge_base.py** - Pattern API

### 📊 CONFIGURAZIONE (SETUP TECNICO)
10. **pyproject.toml** - Dipendenze e configurazione
11. **supabase_schema.sql** - Schema database
12. **.env.example** - Variabili ambiente

## ⚠️ INCOERENZE RISOLTE

### 1. Naming Convention Standardizzata
```python
# STANDARD ADOTTATO: SNAKE_CASE
class WorkflowType(Enum):
    ENHANCED_ARTICLE = "enhanced_article"
    SIEBERT_NEWSLETTER = "siebert_newsletter"
    KBA_INGESTION = "kba_ingestion"          # ✅ Standardizzato
    KBA_TRANSFORMATION = "kba_transformation" # ✅ Standardizzato
    KBA_EXPORT = "kba_export"                # ✅ Standardizzato
```

### 2. Struttura Output Configurabile
```python
# SOLUZIONE: Configurazione flessibile
class KBAOutputConfig(BaseModel):
    structure_type: str = "default"  # "default" | "rag_compatible"
    
    default_structure: Dict[str, str] = {
        "overview": "00_overview.md",
        "content": "01_content.md", 
        "metadata": "02_metadata.md",
        "references": "03_references.md"
    }
    
    rag_compatible_structure: Dict[str, str] = {
        "company_info": "company_profile.md",
        "guidelines": "content_guidelines.md",
        "knowledge_base": "knowledge_base.md"
    }
```

### 3. Timeout Configuration Specifica
```python
# SOLUZIONE: Timeout differenziati per tipo workflow
class WorkflowTimeouts(BaseModel):
    standard_task_timeout: int = 30      # Task normali
    kba_extraction_timeout: int = 300    # Parsing file pesanti
    kba_transformation_timeout: int = 600 # Trasformazioni complesse
    kba_export_timeout: int = 180        # Export e validazione
```

## 🎯 ISTRUZIONI AGGIORNATE

### PRIMA DI INIZIARE
1. **Leggi** tutti i documenti strategici (1-3)
2. **Studia** architettura esistente (4-6)  
3. **Analizza** pattern implementativi (7-9)
4. **Configura** ambiente seguendo (10-12)

### DURANTE SVILUPPO
- **Rispetta** le convenzioni identificate
- **Risolvi** le incoerenze con le soluzioni proposte
- **Mantieni** compatibilità con sistema esistente
- **Documenta** ogni decisione architetturale

### VALIDAZIONE CONTINUA
- **Testa** contro use cases esistenti
- **Verifica** compatibilità API
- **Controlla** performance system
- **Valida** con script di testing disponibili