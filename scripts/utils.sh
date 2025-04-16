#!/bin/bash

extract_ab() {
  local FILES=$1
  local FOLDER=$2
  local OPTIONS=$3

  mkdir -p scripts/temp/assets/$FOLDER scripts/temp/extracted/$FOLDER
  cp -f scripts/temp/apk/assets/AB/Android/$FILES scripts/temp/assets/$FOLDER || :
  cp -f scripts/temp/download/$FILES scripts/temp/assets/$FOLDER || :
  dotnet $ARKSTUDIOCLI scripts/temp/assets/$FOLDER $OPTIONS -o scripts/temp/extracted/$FOLDER
}

git_commit() {
  local MODIFY=$1
  local FOLDER=$2
  local COMMIT_MSG=$3

  rm -f /tmp/git_commit

  if [[ "$MODIFY" == *"$FOLDER"* ]]; then
    git add $FOLDER || :
    if git diff --cached --quiet; then
      echo "No changes to commit."
      echo 0 | tee /tmp/git_commit
    else
      git commit -m "$COMMIT_MSG"
      echo 1 | tee /tmp/git_commit
    fi
  else
    git ls-files --others --exclude-standard $FOLDER -z | xargs -0 git add
    if git diff --cached --quiet; then
      echo "No changes to commit."
      echo 0 | tee /tmp/git_commit
    else
      git commit -m "$COMMIT_MSG"
      echo 1 | tee /tmp/git_commit
    fi
  fi
}
