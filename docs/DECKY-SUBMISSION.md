# Official Decky submission status

**Declined on 3 November 2026.** [Eligibility issue #1178](https://github.com/SteamDeckHomebrew/decky-plugin-database/issues/1178) is closed.

A Decky organization member [explained the decision](https://github.com/SteamDeckHomebrew/decky-plugin-database/issues/1178#issuecomment-6607400046): the project falls under both the restriction on plugins that are shells for LLM access and the restriction on plugins developed mostly by LLMs. This is a store-admission decision; it is not a legal ruling about independent distribution.

Deck AI was developed with substantial Claude/Codex assistance. The [new-plugin template](https://github.com/SteamDeckHomebrew/decky-plugin-database/blob/main/.github/PULL_REQUEST_TEMPLATE/plugin_addition.md) asks developers to confirm that generative AI did not write a majority of submitted code. We cannot truthfully make that confirmation. No normal listing PR, pending approval or exception is claimed.

Distribution remains independent through GitHub Releases and manual installation. The `decky-store-candidate` branch is retained as standalone source for reference, not as an accepted or pending store entry. A future store submission would require an applicable policy change or an explicit maintainer invitation.

Independent device, Stable/Beta and physical-control tests remain technical release-candidate checks; passing them would not reverse the store decision. See [RELEASE-CHECKLIST.md](RELEASE-CHECKLIST.md).
