#!/bin/bash
set -euo pipefail

echo "更新日誌" > CHANGELOG.md
echo "====================" >> CHANGELOG.md

TAGS=$(git tag -l | sort -V)
LIMIT=${CHANGELOG_LIMIT:-50}

if [ -z "$TAGS" ]; then
    echo "" >> CHANGELOG.md
    echo "## Unreleased" >> CHANGELOG.md
    echo "" >> CHANGELOG.md
    git log --no-merges --pretty=format:"- %h - %s (%an, %ad)" --date=short -n "$LIMIT" >> CHANGELOG.md
    echo "" >> CHANGELOG.md
    exit 0
fi

LAST_TAG=$(echo "$TAGS" | tail -n 1)
if [ "$(git rev-list "${LAST_TAG}..HEAD" --count)" -gt 0 ]; then
    echo "" >> CHANGELOG.md
    echo "## Unreleased" >> CHANGELOG.md
    echo "" >> CHANGELOG.md
    git log "${LAST_TAG}..HEAD" --no-merges --pretty=format:"- %h - %s (%an, %ad)" --date=short >> CHANGELOG.md
    echo "" >> CHANGELOG.md
fi

PREV_TAG=""
echo "$TAGS" | while read TAG ; do
    echo "[$TAG]" >> CHANGELOG.md
    echo "----------------" >> CHANGELOG.md
    if [ "$PREV_TAG" ]
    then
        git log "$PREV_TAG..$TAG" --no-merges --pretty=format:"%h - %s (%an, %ad)" --date=short >> CHANGELOG.md
    else
        git log "$TAG" --no-merges --pretty=format:"%h - %s (%an, %ad)" --date=short >> CHANGELOG.md
    fi
    echo "" >> CHANGELOG.md
    PREV_TAG=$TAG
done
