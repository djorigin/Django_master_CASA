#!/bin/bash

# Django-Safe Black Formatter Script
# This script runs Black with Django-friendly settings

echo "🐍 Running Django-safe code formatting..."

# Run Black with Django-friendly options
echo "📝 Formatting Python files..."
black . \
    --line-length 88 \
    --target-version py311 \
    --skip-string-normalization \
    --exclude '/(migrations|venv|\.venv|staticfiles|media|__pycache__|\.git)/' \
    --verbose

# Check for any syntax errors after formatting
echo "🔍 Checking for syntax errors..."
python -m py_compile $(find . -name "*.py" -not -path "./venv/*" -not -path "./.venv/*" -not -path "./migrations/*")

if [ $? -eq 0 ]; then
    echo "✅ All files formatted successfully with no syntax errors!"
else
    echo "❌ Syntax errors found after formatting. Please review the changes."
    exit 1
fi

# Optional: Run Django system check
echo "🔧 Running Django system check..."
python manage.py check --deploy

if [ $? -eq 0 ]; then
    echo "✅ Django system check passed!"
else
    echo "⚠️  Django system check found issues. Please review."
fi

echo "🎉 Code formatting completed!"