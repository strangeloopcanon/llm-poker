#!/bin/bash

set -e  # Exit immediately if any command fails

# Default to patch version bump if no argument is provided
BUMP_TYPE=${1:-patch}

# Extract current version from setup.py
CURRENT_VERSION=$(grep 'version="' setup.py | head -1 | sed -E 's/.*version="([^"]+)".*/\1/')
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"

# Bump version based on argument
if [[ "$BUMP_TYPE" == "major" ]]; then
    NEW_VERSION="$((MAJOR + 1)).0.0"
elif [[ "$BUMP_TYPE" == "minor" ]]; then
    NEW_VERSION="$MAJOR.$((MINOR + 1)).0"
else
    NEW_VERSION="$MAJOR.$MINOR.$((PATCH + 1))"
fi

# Update version in setup.py
sed -i '' "s/version=\"$CURRENT_VERSION\"/version=\"$NEW_VERSION\"/" setup.py

echo "📌 Version bumped: $CURRENT_VERSION → $NEW_VERSION"

# Commit and tag the version in Git
git add setup.py
git commit -m "Release v$NEW_VERSION"
git tag "v$NEW_VERSION"

echo "🚀 Cleaning old builds..."
rm -rf build/ dist/ *.egg-info

echo "🛠 Building new distribution..."
python -m build  # Instead of python setup.py sdist bdist_wheel

echo "📦 Uploading to PyPI..."
twine upload dist/*

echo "✅ Release complete: v$NEW_VERSION"
