#!/usr/bin/env python3
"""Deploy dist to gh-pages using git CLI"""
import subprocess
import os
import shutil
import tempfile

os.chdir("/Users/scott/hermes room/stock-dashboard")

TMP = tempfile.mkdtemp()
repo_path = os.path.join(TMP, "repo")

# Clone main branch
subprocess.run([
    "git", "clone",
    "--branch", "main",
    "--single-branch",
    "https://github.com/lshonesntt/stock-dashboard-sc.git",
    repo_path
], check=True)

# Create orphan gh-pages branch
subprocess.run(["git", "checkout", "--orphan", "gh-pages"], cwd=repo_path, check=True)

# Remove all files from gh-pages
subprocess.run(["git", "rm", "-rf", "."], cwd=repo_path, check=True)

# Copy dist content
dist_src = "/Users/scott/hermes room/stock-dashboard/dist"
for item in os.listdir(dist_src):
    src = os.path.join(dist_src, item)
    dst = os.path.join(repo_path, item)
    if os.path.isdir(src):
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
    else:
        shutil.copy2(src, dst)

# Configure and push
subprocess.run(["git", "config", "user.email", "bot@deploy.com"], cwd=repo_path, check=True)
subprocess.run(["git", "config", "user.name", "Deploy Bot"], cwd=repo_path, check=True)
subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
subprocess.run(["git", "commit", "-m", "Deploy dist for GitHub Pages"], cwd=repo_path, check=True)

# Push gh-pages to remote
subprocess.run([
    "git", "push",
     f"https://{os.environ.get('GH_TOKEN', '')}@github.com/lshonesntt/stock-dashboard-sc.git",
     "gh-pages:gh-pages"
], check=True)

print("✅ Deployed to gh-pages successfully!")
print("   URL: https://lshonesntt.github.io/stock-dashboard-sc/")

shutil.rmtree(TMP)
