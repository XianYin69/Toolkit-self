#!/bin/bash

# =================================================================================================
# Script Name:   setup_git.sh
# Description:   This script automates the process of configuring Git and cloning a repository.
#                It prompts the user for their GitHub username, email, and the repository URL,
#                sets the global Git configuration, and clones the specified repository.
# Author:        Kilo Code
# Date:          2025-08-10
# =================================================================================================

# --- Banner ---
echo "========================================="
echo "        Git Setup & Repo Cloner        "
echo "========================================="
echo

# --- Prompt for User Information ---
echo "This script will help you configure Git and clone a repository."
read -p "Please enter your GitHub username: " GITHUB_USERNAME
read -p "Please enter your GitHub email: " GITHUB_EMAIL
read -p "Please enter the GitHub repository URL to clone: " REPO_URL

# --- Configure Git ---
echo
echo "Configuring Git with your credentials..."
git config --global user.name "$GITHUB_USERNAME"
git config --global user.email "$GITHUB_EMAIL"
echo "✅ Git user.name and user.email have been set globally."

# --- Clone Repository ---
echo
echo "Cloning the repository from $REPO_URL..."
if git clone "$REPO_URL"; then
    echo "✅ Repository has been successfully cloned."
else
    echo "❌ Error: Failed to clone the repository. Please check the URL and your permissions." >&2
    exit 1
fi

echo
echo "========================================="
echo "      🚀 All tasks completed! 🚀      "
echo "========================================="