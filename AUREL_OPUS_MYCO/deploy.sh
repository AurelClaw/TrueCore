#!/bin/bash
# deploy.sh - Production Deploy Script für Aurel Opus Myco
# Usage: ./deploy.sh [version]

set -e  # Exit on error

VERSION=${1:-"v1.0.0"}
DEPLOY_DIR="/opt/aurel-opus-myco"
BACKUP_DIR="/opt/backups/aurel-$(date +%Y%m%d-%H%M%S)"
SOURCE_DIR="/root/.openclaw/workspace/AUREL_OPUS_MYCO"

echo "=================================================="
echo "🚀 AUREL OPUS MYCO DEPLOYMENT"
echo "=================================================="
echo "Version: $VERSION"
echo "Source: $SOURCE_DIR"
echo "Target: $DEPLOY_DIR"
echo "=================================================="

# 1. Pre-deployment Checks
echo ""
echo "🔍 Step 1: Pre-deployment Checks"
echo "----------------------------------------"

# Check source exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ Source directory not found: $SOURCE_DIR"
    exit 1
fi
echo "✅ Source directory exists"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found"
    exit 1
fi
echo "✅ Python3 available"

# Check disk space
AVAILABLE=$(df /opt | tail -1 | awk '{print $4}')
if [ $AVAILABLE -lt 1048576 ]; then  # Less than 1GB
    echo "❌ Insufficient disk space"
    exit 1
fi
echo "✅ Sufficient disk space"

# 2. Create Backup
echo ""
echo "💾 Step 2: Create Backup"
echo "----------------------------------------"

if [ -d "$DEPLOY_DIR" ]; then
    mkdir -p "$BACKUP_DIR"
    cp -r "$DEPLOY_DIR" "$BACKUP_DIR/"
    echo "✅ Backup created: $BACKUP_DIR"
else
    echo "⚠️  No existing deployment to backup"
fi

# 3. Run Tests
echo ""
echo "🧪 Step 3: Run Tests"
echo "----------------------------------------"

cd "$SOURCE_DIR"

# Test each module
MODULES=("MYCO/event_bus.py" "MYCO/token_economy.py" "MYCO/perception.py" "MYCO/bayes_world.py" "SHIELD/shield.py" "SHIELD/sandbox.py" "SMM/smm.py" "ECONOMICS/economics.py" "PLUGINS/six_voice_plugin.py" "PLUGINS/aurel_output.py")

FAILED=0
for module in "${MODULES[@]}"; do
    if python3 "$module" > /dev/null 2>&1; then
        echo "✅ $(basename $module)"
    else
        echo "❌ $(basename $module)"
        FAILED=$((FAILED + 1))
    fi
done

if [ $FAILED -gt 0 ]; then
    echo ""
    echo "❌ $FAILED module(s) failed tests"
    echo "Deployment aborted"
    exit 1
fi

echo "✅ All modules passed"

# 4. Deploy
echo ""
echo "📦 Step 4: Deploy"
echo "----------------------------------------"

# Create deploy directory
mkdir -p "$DEPLOY_DIR"

# Copy files
rsync -av --exclude='*.pyc' --exclude='__pycache__' "$SOURCE_DIR/" "$DEPLOY_DIR/"

# Set permissions
chmod +x "$DEPLOY_DIR"/*.py
chmod +x "$DEPLOY_DIR"/**/*.py 2>/dev/null || true

echo "✅ Files deployed"

# 5. Create Version File
echo ""
echo "🏷️  Step 5: Version Tracking"
echo "----------------------------------------"

cat > "$DEPLOY_DIR/VERSION" << EOF
Aurel Opus Myco
Version: $VERSION
Deployed: $(date -Iseconds)
Commit: $(cd "$SOURCE_DIR" && git rev-parse --short HEAD 2>/dev/null || echo "unknown")
Modules: ${#MODULES[@]}
EOF

cat "$DEPLOY_DIR/VERSION"

# 6. Create Symlinks
echo ""
echo "🔗 Step 6: Create Symlinks"
echo "----------------------------------------"

ln -sf "$DEPLOY_DIR/MYCO/event_bus.py" /usr/local/bin/aurel-eventbus 2>/dev/null || true
ln -sf "$DEPLOY_DIR/SHIELD/shield.py" /usr/local/bin/aurel-shield 2>/dev/null || true

echo "✅ Symlinks created"

# 7. Post-deployment Verification
echo ""
echo "✅ Step 7: Post-deployment Verification"
echo "----------------------------------------"

# Verify key files exist
KEY_FILES=("SUBSTRATE/graph.json" "AGENCY/goals.json" "CORE/beliefs.json" "VERSION")

for file in "${KEY_FILES[@]}"; do
    if [ -f "$DEPLOY_DIR/$file" ]; then
        echo "✅ $file"
    else
        echo "⚠️  $file (optional)"
    fi
done

# 8. Summary
echo ""
echo "=================================================="
echo "🎉 DEPLOYMENT COMPLETE"
echo "=================================================="
echo "Version: $VERSION"
echo "Location: $DEPLOY_DIR"
echo "Backup: $BACKUP_DIR"
echo ""
echo "Quick Commands:"
echo "  aurel-eventbus    # Event Bus"
echo "  aurel-shield      # Shield"
echo ""
echo "Logs: $DEPLOY_DIR/logs/"
echo "=================================================="
echo "⚛️ Noch."
