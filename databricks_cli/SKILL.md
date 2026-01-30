---
name: databricks_cli
description: Install, configure, and use the Databricks CLI to manage workspaces and resources from the terminal or scripts. Covers installation (Homebrew, WinGet, curl, source), authentication (OAuth U2M and M2M), configuration profiles, and common command groups (auth, clusters, jobs, workspace, Unity Catalog, bundle). Use when automating Databricks from the command line, setting up CLI auth, switching workspaces via profiles, or when the user mentions Databricks CLI, databricks command, or .databrickscfg.
---

# Databricks CLI

The Databricks CLI (version 0.205 and above) exposes Databricks REST APIs from the command line. Use it for workspace and account operations, automation scripts, and tooling (e.g. Databricks Connect auth, Asset Bundles).

## When to Use This Skill

Use when the user needs to:
- Install or update the Databricks CLI (Homebrew, WinGet, Chocolatey, curl, or source)
- Configure authentication (OAuth U2M or M2M, profiles)
- Run or script workspace/account operations (clusters, jobs, workspace files, Unity Catalog, etc.)
- Work with configuration profiles and `.databrickscfg`
- Troubleshoot CLI auth or profile issues

## Requirements

- **CLI version**: 0.205 or above. Legacy CLI (0.18 and below) is deprecated; see [references/REFERENCES.md](references/REFERENCES.md) for migration.
- **Auth**: OAuth U2M (interactive) or OAuth M2M (headless/CI). Personal access tokens are legacy; prefer OAuth where possible.

## Step-by-Step Setup

### 1. Install the CLI

**Linux or macOS (Homebrew):**

```bash
brew tap databricks/tap
brew install databricks
```

**Windows (WinGet):**

```bash
winget install Databricks.DatabricksCLI
```

**Linux, macOS, or WSL (curl):**

```bash
curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh
```

**Source**: Download the appropriate binary from [GitHub Releases](https://github.com/databricks/cli/releases) and extract it.

Verify: `databricks version` — must report 0.205.0 or above.

### 2. Configure Authentication

**OAuth user-to-machine (U2M)** — interactive, recommended for local use:

- **Workspace-level commands:**
  ```bash
  databricks auth login --host https://<workspace-name>.cloud.databricks.com
  ```
- **Account-level commands:**
  ```bash
  databricks auth login
  ```

The CLI opens a browser; after login it creates or updates a profile in `~/.databrickscfg` (or `%USERPROFILE%\.databrickscfg` on Windows).

**OAuth machine-to-machine (M2M)** — for scripts and CI: create a profile in `~/.databrickscfg` with `host`, `client_id`, and `client_secret` (see [OAuth M2M](https://docs.databricks.com/aws/en/dev-tools/auth/oauth-m2m)). Use `--profile <name>` or `-p <name>` when running commands.

**Databricks Connect cluster config:** use `databricks auth login --configure-cluster --host <workspace-url>` so the profile includes cluster (or serverless) settings for Databricks Connect.

### 3. Use a Profile

If you omit `--profile`, the CLI uses the `DEFAULT` profile when present. To use another profile:

```bash
databricks clusters list --profile my-workspace
```

Press Tab after `--profile` or `-p` to list profiles. To inspect a profile (no secrets): `databricks auth env --profile <name>`.

### 4. Confirm Authentication

Test the active (or chosen) profile with a simple workspace call:

```bash
databricks cluster-policies list --profile <name>
# or, if no profile given, default profile is used
databricks clusters list
```

## Common Commands and Groups

General form: `databricks <group> <command> [options] [--profile <name>]`. Get help: `databricks -h`, `databricks <group> -h`, or `databricks <group> <command> -h`.

| Use case | Example |
|----------|--------|
| Auth | `databricks auth login [--host <url>]`, `databricks auth env [--profile <name>]` |
| Clusters | `databricks clusters list`, `databricks clusters get --cluster-id <id>` |
| Jobs | `databricks jobs list`, `databricks jobs create --json '{"name":"My Job", ...}'` |
| Workspace | `databricks workspace list /Users/me`, `databricks workspace export_dir /path /local/dir` |
| Files | `databricks fs ls dbfs:/`, `databricks fs cp dbfs:/file ./local` |
| Unity Catalog | `databricks catalogs list`, `databricks schemas list --catalog-name main`, `databricks tables list --catalog-name main --schema-name default` |
| Bundles | `databricks bundle validate -t dev`, `databricks bundle deploy -t prod` |
| API | `databricks api get /api/2.0/clusters/list` |

Many commands accept `--json` for input or emit JSON. Use `--output json` when available for machine-readable output. Pipe to `jq` to filter, e.g. `databricks clusters list -o json | jq '.clusters[] | .cluster_name'`.

## Configuration Profiles

- **File**: `~/.databrickscfg` (Unix/macOS) or `%USERPROFILE%\.databrickscfg` (Windows). Override with `DATABRICKS_CONFIG_FILE`.
- **Format**: Ini-style sections `[profile-name]` with `host`, and for M2M `client_id` and `client_secret`. U2M credentials are stored by the CLI after `databricks auth login`.
- **Default**: If no `--profile` is given, the `DEFAULT` profile is used when defined.
- **Precedence**: Profile → environment variables → bundle target (when in a bundle directory). See [references/REFERENCES.md](references/REFERENCES.md) for auth order of evaluation.

## Edge Cases and Troubleshooting

| Issue | What to do |
|-------|------------|
| "Not authenticated" or 403 | Run `databricks auth login --host <workspace-url>` (or `databricks auth login` for account). For M2M, check `client_id`/`client_secret` and profile name. |
| Wrong workspace or account | Use `--profile <name>` or set `DEFAULT` in `~/.databrickscfg` to the intended host. |
| Legacy CLI (0.18 or below) | Migrate to 0.205+; see [migration guide](https://docs.databricks.com/aws/en/dev-tools/cli/migrate). New syntax and auth differ. |
| JSON in Windows CMD | Use different quoting; see [Basic usage](https://docs.databricks.com/aws/en/dev-tools/cli/usage). Prefer PowerShell or WSL for complex JSON. |
| Web terminal in workspace | CLI is available there without local auth; see [Run shell commands in Databricks web terminal](https://docs.databricks.com/aws/en/compute/web-terminal). |

## Best Practices

1. **Use OAuth**: Prefer OAuth U2M for interactive use and OAuth M2M for automation; avoid PATs for new setups.
2. **One profile per target**: Use separate profiles for dev/prod or multiple workspaces; pass `--profile` explicitly in scripts.
3. **Help and JSON**: Use `databricks <group> <command> -h` and `-o json` plus `jq` when scripting.
4. **Bundles**: For deployment and CI, use Asset Bundles (`databricks bundle`) and profile/target rather than ad-hoc CLI calls.

For install options, auth details, and command references, see [references/REFERENCES.md](references/REFERENCES.md).
