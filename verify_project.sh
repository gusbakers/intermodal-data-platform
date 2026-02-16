#!/bin/bash
# Script to verify all project files exist

echo "🔍 Verifying project structure..."
echo ""

errors=0

# Critical files
files=(
    ".gitignore"
    "LICENSE"
    "README.md"
    "requirements.txt"
    "pytest.ini"
    "setup.py"
    "Makefile"
    ".env.example"
    "run_full_pipeline.py"
    "config/config.yaml"
    "src/__init__.py"
    "src/etl/__init__.py"
    "src/etl/extract.py"
    "src/etl/transform.py"
    "src/etl/load.py"
    "src/etl/pipeline.py"
    "src/etl/load_to_database.py"
    "src/utils/__init__.py"
    "src/utils/logger.py"
    "src/utils/config_loader.py"
    "tests/__init__.py"
    "tests/unit/test_extract.py"
    "tests/unit/test_transform.py"
    "tests/unit/test_load.py"
    "tests/unit/test_pipeline.py"
    "notebooks/01_data_exploration.ipynb"
    "notebooks/02_data_quality_report.ipynb"
    "notebooks/03_kpi_dashboard.ipynb"
    "sql/schema/01_create_tables.sql"
    "sql/schema/02_create_views.sql"
    "sql/kpis/business_kpis.sql"
    "docs/ARCHITECTURE.md"
    "docs/DATA_DICTIONARY.md"
    ".github/workflows/ci.yml"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ MISSING: $file"
        ((errors++))
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $errors -eq 0 ]; then
    echo "✅ ALL FILES PRESENT - PROJECT READY!"
    echo ""
    echo "Next steps:"
    echo "  1. Add your data: cp your_data.csv data/raw/"
    echo "  2. Run pipeline: python run_full_pipeline.py"
    echo "  3. Commit to Git: git add . && git commit -m 'Initial commit'"
else
    echo "❌ MISSING $errors FILES"
    echo "Run the missing file creation commands above"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
