import pandas as pd

pd.set_option("display.width", 120)
pd.set_option("display.max_columns", 10)

# Run this script in the directory of the downloaded release, after extracting repos.csv.7z and
# commits.csv.7z with `7z x <archive>`. The flag columns hold TRUE and FALSE.

# repos.csv: the sampled GitHub repositories with their metadata and the label of whether each
# hosts an engineered software project ("true", "false" or "unclear"). pandas reads a column of
# "true" and "false" alone as booleans, so read the label as text. The configured repositories,
# those with a configuration artifact, have a scan date and a flag per tool and mechanism.
repos = pd.read_csv("repos.csv", dtype={"engineered_project": str})
engineered_repos = repos[repos["engineered_project"] == "true"]
configured_repos = repos[repos["scanned_at"].notna()]

# Which agents do engineered software projects configure, and in which languages?
tools = ["claude", "copilot", "cursor", "gemini", "codex", "opencode", "no_specific_tool"]
uses_tool = configured_repos[tools].eq(True)
print(f"{len(configured_repos):,} of {len(engineered_repos):,} engineered projects are configured")
print(uses_tool.mean().sort_values(ascending=False))
languages = configured_repos["mainLanguage"].value_counts().index[:5]
print(uses_tool.groupby(configured_repos["mainLanguage"]).mean().loc[languages].round(2))

# context_files.csv: one row per context file, such as CLAUDE.md or AGENTS.md, with its commit
# history. Do agents co-author their own instructions? first_commit_ai_created says whether
# the commit that created the file credits a tool, and first_commit_ai_tool names the tool.
# AGENTS.md is the file that several tools read, so which tools write it?
context_files = pd.read_csv("context_files.csv")
names = context_files["context_file"].value_counts().index[:4]
top_files = context_files[context_files["context_file"].isin(names)]
print(top_files.groupby("context_file")["first_commit_ai_created"].apply(lambda s: s.eq(True).mean()))
agents_md = context_files[context_files["context_file"] == "AGENTS.md"]
print(agents_md["first_commit_ai_tool"].str.split(",").explode().value_counts())

# imports.csv: one row per import in a configuration artifact, such as @docs/style.md in a
# CLAUDE.md, with the file that it reaches. How many imports reach no file, and which
# configuration artifacts do the others reach? depth counts the hops of a chain of imports.
imports = pd.read_csv("imports.csv")
print(imports["target_status"].value_counts(normalize=True))
print(imports.loc[imports["target_status"] == "found", "target_category"].value_counts())
print(imports["depth"].value_counts().sort_index())

# planning-documents.csv: the specs, plans and task lists that spec-driven development
# frameworks and the tools' planning features write. Which frameworks do projects use?
planning = pd.read_csv("planning-documents.csv")
planning["created_at"] = pd.to_datetime(planning["created_at"], utc=True)
print(planning.groupby("framework").agg(repositories=("repo_name", "nunique"),
                                        first_document=("created_at", "min"))
      .sort_values("repositories", ascending=False).head(8))

# commits.csv: the commits that credit a tool. attributions says how each commit credits each
# tool: from the tool's account, as a reviewer, with the tool's standard trailer, or by a
# project's convention. How many commits credit each tool per month, and in which form?
commits = pd.read_csv("commits.csv", usecols=["repo_name", "commit_timestamp", "ai_tool",
                                              "attributions"])
commits["month"] = pd.to_datetime(commits["commit_timestamp"], utc=True).dt.strftime("%Y-%m")
per_tool = commits.assign(tool=commits["ai_tool"].str.split(",")).explode("tool")
print(per_tool.groupby(["month", "tool"]).size().unstack(fill_value=0).tail(6))
print(commits["attributions"].str.split(";").explode().value_counts().head(10))

# The other mechanisms have one CSV each, such as skills.csv, hooks.csv and mcp.csv, with the
# creation date and the number of commits of each file, and other_commits.csv lists the commits
# that credit a tool outside the six. repos_data.7z contains the configuration artifacts, and
# imported_files.7z the files that they import. How many skills have a scripts directory?
skills = pd.read_csv("skills.csv")
print(f"{skills['scripts'].eq(True).mean():.0%} of the skills have a scripts directory")
