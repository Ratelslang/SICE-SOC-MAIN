#!/bin/bash
# ============================================================
# SICE SOC PORTAL — GIT SETUP
# Run ONCE from inside the Portal Hub folder.
# Sets up version control + a pre-commit health check that
# catches broken HTML (duplicate script tags, missing closing
# tags, duplicate credential blocks) before you commit, not
# after you discover the app is broken.
# ============================================================
set -e

PORTAL_DIR="/home/philip/Desktop/OPS MAIN/SOC CENTRE/SICE PORTAL HUB"
cd "$PORTAL_DIR" || { echo "ERROR: Portal directory not found."; exit 1; }

if [ -d ".git" ]; then
    echo "Git repo already initialized here. Skipping init."
else
    git init
    git config user.name "Philip Dorfling"
    git config user.email "delta6@sice.local"
    echo "Git repo initialized."
fi

# ---- .gitignore ----
cat > .gitignore << 'EOF'
# Runtime / temp files — never commit these
*.pid
*.log
__pycache__/
*.pyc
.DS_Store

# SQLite backups — these can be large and are personal data exports,
# not codebase. Back them up separately (Dropbox/MegaSync), not in git.
*.sqlite
*.db

# Editor / OS clutter
*.swp
*~
EOF

# ---- Pre-commit hook: file health check ----
mkdir -p .git/hooks
cat > .git/hooks/pre-commit << 'HOOKEOF'
#!/bin/bash
# SICE SOC — pre-commit health check
# Blocks the commit if a staged HTML file shows classic corruption
# signs: mismatched script tags, missing </html>, or a duplicated
# credentials DECLARATION (not usage).

FAILED=0

for file in $(git diff --cached --name-only --diff-filter=ACM | grep '\.html$'); do
    [ -f "$file" ] || continue

    # Count real <script> opening tags (start-of-tag, not text mentioning it)
    open_tags=$(grep -o '<script[ >]' "$file" | wc -l)
    # Count closing tags INCLUDING escaped variants used inside JS strings
    # (e.g. <\/script> written deliberately to avoid ending the outer
    # script block early when embedding HTML/print-window code).
    close_tags=$(grep -oE '<\\?/script>' "$file" | wc -l)
    if [ "$open_tags" -ne "$close_tags" ]; then
        echo "❌ $file: mismatched <script> tags ($open_tags open, $close_tags close — including escaped variants)"
        FAILED=1
    fi

    if ! grep -q '</html>' "$file"; then
        echo "❌ $file: missing </html> closing tag"
        FAILED=1
    fi

    # Only count DECLARATIONS (assignment), not .find()/usage references
    cred_count=$(grep -cE '(const|var|let)\s+(SICE_CREDENTIALS|CREDENTIALS)\s*=' "$file" || true)
    if [ "$cred_count" -gt 1 ]; then
        echo "❌ $file: credentials DECLARED $cred_count times — this is the real duplicate-block bug, fix before commit"
        FAILED=1
    fi
done

if [ "$FAILED" -eq 1 ]; then
    echo ""
    echo "COMMIT BLOCKED — fix the issues above, or use 'git commit --no-verify' to override."
    exit 1
fi

exit 0
HOOKEOF
chmod +x .git/hooks/pre-commit

echo ""
echo "Pre-commit health check installed."
echo "Staging all files for first commit..."
git add .
git commit -m "Initial commit — SICE SOC Portal Hub baseline" || echo "Nothing to commit (already committed or empty)."

echo ""
echo "DONE. Git is now tracking this folder."
echo "Daily workflow:"
echo "  git add ."
echo "  git commit -m \"describe what changed\""
echo "  git log --oneline          # see history"
echo "  git diff HEAD~1            # see what changed since last commit"
echo "  git checkout -- <file>     # revert a broken file to last commit"
