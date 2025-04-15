#!/bin/bash

extract_ab() {
    local FILES=$1
    local FOLDER=$2
    local OPTIONS=$3

    mkdir -p scripts/assets/$FOLDER scripts/extracted/$FOLDER
    cp -f scripts/apk/assets/AB/Android/$FILES scripts/assets/$FOLDER || :
    cp -f scripts/download/$FILES scripts/assets/$FOLDER || :
    dotnet $ARKSTUDIOCLI scripts/assets/$FOLDER $OPTIONS -o scripts/extracted/$FOLDER
}

git_commit() {
    local MODIFY=$1
    local FILES=$2
    local COMMIT_MSG=$3

    rm -f /tmp/git_commit

    if [[ "$MODIFY" == *"$FILES"* ]]; then
        git add "$FILES" || :
        if git diff --cached --quiet; then
            echo "No changes to commit."
            echo 0 | tee /tmp/git_commit
        else
            git commit -m "$COMMIT_MSG"
            echo 1 | tee /tmp/git_commit
        fi
    else
        git ls-files --others --exclude-standard $FILES -z | xargs -0 git add
        if git diff --cached --quiet; then
            echo "No changes to commit."
            echo 0 | tee /tmp/git_commit
        else
            git commit -m "$COMMIT_MSG"
            echo 1 | tee /tmp/git_commit
        fi
    fi
}
