# Blizzard launcher: working rules

- **Push edits to `main`** (the user: "always push edits to main unless it conflicts with another
  session"). Many sessions can work at once. Before pushing: fetch `origin/main`, merge it into your
  work, and look at what changed there. Where it is plainly separate additions, keep both and push to
  `main`. Where the same lines changed differently, or one change undoes another's, don't push: stop
  and tell the user. Never rebase or force-push over others' work. CI builds and releases every push
  to `main` (`blizzard-build-N`); confirm the run and the release.
- Build and run the unit tests before pushing:
  `./gradlew --init-script <maven-mirror.init.gradle> :app:testDebugUnitTest` (the init script is in
  YeaBwoi's `scripts/` when it is cloned beside this repository). Say what was tested and what wasn't:
  nothing here has run on a real phone unless the user says so.
- `README.md` is the manual: keep it current with every change.
- Reports from the app (crashes, failed installs, the launch test) arrive as GitHub issues on this
  repository once the `BLIZZ_REPORT_TOKEN` secret is set (it is). Read them with the issues tools
  before asking the user to paste anything.
- Never commit build outputs, downloaded tools, or any game files.
