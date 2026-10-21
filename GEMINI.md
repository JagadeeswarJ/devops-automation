# Agent & IDE Operational Rules

## 1. Direct Disk Writes Only (Avoid Diff-Review Reverts)
- **Do NOT use IDE diff-staging tools (`write_to_file` / `replace_file_content`) when editing or creating project files.** The IDE's pending Review buffer can automatically revert unaccepted changes at the end of a turn.
- **Direct Disk Writes**: Always write and patch project files directly to disk via Python or PowerShell inside `run_command` (using UTF-8 encoding). Changes persist immediately on the filesystem without triggering the Review rollback glitch.
- *Note*: Artifacts in the agent brain directory (`brain/<conversation-id>/...`) are exempt and follow standard artifact creation.

## 2. Windows PowerShell Constraints
- **Directory Changes**: Never issue `cd` commands in `run_command`; always set the execution folder using the `Cwd` parameter.
- **Maven Wrapper**: Use `.\mvnw.cmd` instead of `./mvnw` or `mvnw`.
- **UTF-8 Encoding**: Configure UTF-8 output (`sys.stdout.reconfigure(encoding="utf-8")`) in all inline Python scripts executed via PowerShell.

## 3. Backend Lifecycle Utilities
Always use the dedicated batch utility scripts located in `microservices/` to manage the backend lifecycle:
- **Clean targets**: `microservices\0-delete-targets.bat` (force deletes all target folders)
- **Rebuild JARs**: `microservices\0-rebuild-jars.bat` (parallel clean packaging for all microservices)
- **Start all services**: `microservices\2-start-all-services.bat` (parallel background launch)
- **Stop all services**: `microservices\3-stop-all-services.bat --no-pause` (terminates processes by port mapping)

## 4. Code & Git Conventions
- **Comments**: Do not write comments everywhere. Rarely write comments, only when the function name itself does not explain everything it does and the distinction is critical.
- **Git Safety**: Do not commit or stage anything to git. Use git strictly for inspecting changes (read-only) when needed.
