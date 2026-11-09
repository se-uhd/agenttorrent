import pandas as pd

# repos.csv: main dataset
# engineered_project holds the lowercase labels "true", "false" and "unclear"
# (the labels of March 2026 write "unsure" for "unclear"). pandas reads a column of
# "true" and "false" alone as booleans, so read it as text
repos = pd.read_csv("repos.csv", dtype={"engineered_project": str})

# Three populations: the sampling frame, the labeled repositories and the configured repositories
engineered_repos = repos[repos["engineered_project"] == "true"]
configured_repos = repos[repos["scanned_at"].notna()]

# Tool flags: filter repos by tool
claude_repos = configured_repos[configured_repos["claude"] == True]

# Mechanism flags: filter by configuration mechanism
repos_with_mcp = configured_repos[configured_repos["mcp"] == True]

# GitHub metadata: stars, forks, contributors, code lines, ...
popular = configured_repos[configured_repos["stargazers"] >= 1000]

# context_files.csv: context file configuration artifacts
context_files = pd.read_csv("context_files.csv")

# Git metadata: creation dates
context_files["created_at"] = pd.to_datetime(context_files["created_at"])

# AI authorship: which files were initially created by a tool
ai_created = context_files[context_files["first_commit_ai_created"] == True]

# References: context files that point to other files
references = context_files[context_files["is_reference"] == True]

# Join with repo metadata
merged = context_files.merge(
    configured_repos[["repo_name", "mainLanguage", "stargazers"]],
    on="repo_name"
)

# commits.csv: commits that credit a tool
commits = pd.read_csv("commits.csv")
commits["commit_timestamp"] = pd.to_datetime(commits["commit_timestamp"])

# Filter by tool (e.g., "Claude", "Copilot", "Cursor")
claude_commits = commits[commits["ai_tool"].str.contains("Claude")]

# The per-mechanism CSVs
skills = pd.read_csv("skills.csv") # skill definitions
subagents = pd.read_csv("subagents.csv") # subagent definitions
commands = pd.read_csv("commands.csv") # custom commands
rules = pd.read_csv("rules.csv") # rule files
settings = pd.read_csv("settings.csv") # settings files
hooks = pd.read_csv("hooks.csv") # hook configurations
mcp = pd.read_csv("mcp.csv") # MCP configurations
plugins = pd.read_csv("plugins.csv") # plugin and extension manifests
lsp = pd.read_csv("lsp.csv") # LSP server configurations

# All per-mechanism CSVs share these columns: repo_name, created_at, #commits,
# github_link, first/last_commit_sha
# Some have extra columns (e.g., skills: name, scripts, references)
skills_with_scripts = skills[skills["scripts"] == True]
agents_with_memory = subagents[subagents["memory"] == True]
