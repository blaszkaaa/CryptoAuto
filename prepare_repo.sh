#!/usr/bin/env bash
# Helper to initialize a repo and push to GitHub (edit remote URL first)
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin $1
git push -u origin main
if [ -z "$1" ]; then
  REMOTE="git@github.com:blaszkaaa/CryptoAuto.git"
else
  REMOTE="$1"
fi

git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin $REMOTE
git push -u origin main
