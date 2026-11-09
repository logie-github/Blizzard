# Blizzard launcher: working rules

- **Always merge into `main`** (the user: "always merge unless it contradicts other sessions, then
  decide automatically which one to merge first so it doesn't mess up changes"). Many sessions can work
  at once. When a change is done, fetch `origin/main`, merge it into your work, and look at what changed
  there. Where it is plainly separate additions, keep both and push to `main`; do not wait to be asked.
  Never rebase or force-push over others' work. CI builds and releases every push to `main`
  (`blizzard-build-N`); confirm the run and the release.
  **When sessions contradict** (the same lines changed differently, or one change undoes another's),
  decide the order yourself, without asking: merge first the work that is finished, tested and
  pushed, and that the others build on or touch least (the smaller, more foundational change); the
  other session then merges `main` into its work, keeps both changes, and re-runs the tests before
  it pushes. Where both changes cannot stand together even then, keep the one merged first, adapt
  the later one to it, and say so in the commit message; never drop or overwrite the other
  session's work to make a merge go through.
- Build and run the unit tests before pushing:
  `./gradlew --init-script <maven-mirror.init.gradle> :app:testDebugUnitTest` (the init script is in
  YeaBwoi's `scripts/` when it is cloned beside this repository). Say what was tested and what wasn't:
  nothing here has run on a real phone unless the user says so.
- `README.md` is the manual: keep it current with every change.
- Reports from the app (crashes, failed installs, the launch test) arrive as GitHub issues on this
  repository once the `BLIZZ_REPORT_TOKEN` secret is set (it is). Read them with the issues tools
  before asking the user to paste anything.
- **A change that needs a game installed again forces it** (the user: "if a game update requires a true install, force
  it"). Each importer has a `recipe` number (`GameImporter.recipe`); raise it whenever the install itself changes (what
  is downloaded, which version, what is written into the archives). The app then installs that game again by itself at
  the next start or Play (saves kept, as a reset), without asking. Never raise it for a change that an installed game
  plays fine without.
- Never commit build outputs, downloaded tools, or any game files.
