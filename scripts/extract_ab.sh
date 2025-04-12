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
