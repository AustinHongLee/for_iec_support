#!/bin/bash
echo "更新日誌" > CHANGELOG.md
echo "====================" >> CHANGELOG.md
git tag -l | sort -V | while read TAG ; do
    echo "[$TAG]" >> CHANGELOG.md
    echo "----------------" >> CHANGELOG.md
    if [ $PREV_TAG ]
    then
        git log $PREV_TAG..$TAG --no-merges --pretty=format:"%h - %s (%an, %ad)" --date=short >> CHANGELOG.md
    else
        git log $TAG --no-merges --pretty=format:"%h - %s (%an, %ad)" --date=short >> CHANGELOG.md
    fi
    echo "" >> CHANGELOG.md
    PREV_TAG=$TAG
done
