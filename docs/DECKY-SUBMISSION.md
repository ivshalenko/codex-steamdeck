# Official Decky submission status

The official destination is [SteamDeckHomebrew/decky-plugin-database](https://github.com/SteamDeckHomebrew/decky-plugin-database). A new listing is a maintainer-reviewed pull request adding a plugin submodule, not an automated registration endpoint.

The current [new-plugin template](https://github.com/SteamDeckHomebrew/decky-plugin-database/blob/main/.github/PULL_REQUEST_TEMPLATE/plugin_addition.md) includes this mandatory developer confirmation:

> Generative AI was NOT used to write a majority of the code I am submitting.

Deck AI was developed with substantial Claude/Codex assistance. We cannot check this statement. A normal listing PR must not misrepresent code provenance or mark unperformed Stable/Beta/third-party tests as passed. An eligibility inquiry and a complete technical package are prepared; listing requires maintainer clarification/approval and the actual required human tests.

Technical delivery: standalone built Decky ZIP, API v2 manifest, source, Apache-2.0 and dependency notices, explicit runtime/package allowlists, regression tests, installation/remote-access documentation, and release notes. The main repository is a monorepo; a future approved store submission should use a plugin-root branch/submodule compatible with Decky's build pipeline. Store approval is not claimed by a GitHub release.
