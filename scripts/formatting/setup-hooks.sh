#!/bin/bash
# Setup git hooks for code quality

echo "🔧 Setting up git hooks for Solar Analysis API..."

# Create reports directory
mkdir -p reports

# Check if pre-commit is available
if command -v pre-commit &> /dev/null; then
    echo "📦 Using pre-commit framework..."
    
    # Install pre-commit hooks
    pre-commit install
    
    echo "✅ Pre-commit hooks installed successfully!"
    echo ""
    echo "📋 Available commands:"
    echo "  make pre-commit-run     - Run pre-commit on all files"
    echo "  make pre-commit-update  - Update pre-commit hooks"
    echo "  pre-commit run          - Run hooks manually"
    echo ""
    
else
    echo "📦 Using custom pre-commit hook..."
    
    # Create git hooks directory if it doesn't exist
    mkdir -p .git/hooks

    # Create pre-commit hook
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook that runs code quality checks

python scripts/formatting/pre-commit-hook.py
EOF

    # Make the hook executable
    chmod +x .git/hooks/pre-commit

    echo "✅ Custom git hooks installed successfully!"
    echo ""
    echo "� For better experience, install pre-commit framework:"
    echo "  pip install pre-commit"
    echo "  make pre-commit-install"
    echo ""
fi

echo "📋 General commands:"
echo "  make install-dev     - Install development tools"
echo "  make format          - Auto-format code"
echo "  make lint            - Check code quality"
echo "  make lint-report     - Generate detailed report"
echo "  make pre-commit      - Run pre-commit checks manually"
echo "  make quick-check     - Run quick style checks"
echo "  make quality-gate    - Run all quality checks"
echo ""
echo "🎉 You're all set! Git hooks will run automatically on commit."
