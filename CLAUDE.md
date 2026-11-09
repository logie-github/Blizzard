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
- **Before every push to `main`, make sure nothing of another session's was gone over** (the user: "be sure
  that nothing else hasn't gone over"). Right before pushing: `git fetch origin main`, merge it (never rebase or
  force), then read what came in (`git log --stat <your last pushed sha>..origin/main`) and, for every file both
  you and it touched, check that the other session's recent additions are still there after the merge (a merge
  that takes only your side of a conflict, or a file rewritten from an old copy, undoes their work). Re-run the
  tests after the merge, then push; if the push is refused because `main` moved, do it all again. A
  `build-apk` run cancelled by a newer push isn't a failure: confirm the newest run that contains your commit.
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
- **A game that fails on the phone is run here first** (the user: "Do testing. Don't skip it"). Winlator's Wine is an x86_64
  build and runs natively on this machine against the downloader's own game folders under Xvfb: README, "Testing the
  Windows games here". Reproduce the failure there, read the dialogs, the `+seh`/`+relay` traces and the game's code, fix,
  and see the game run before pushing. A change to how a Windows game starts that was not run there is a guess; say so.
- **Anything run beside a game must run on its desktop.** The games run in Wine's virtual desktop (`explorer /desktop=shell,WxH`);
  a helper started with plain `wine` lands on another desktop and sees none of the game's windows. On the phone, run it through
  winhandler's `exec` (as `borderless.exe` is); on the test rig, `wine explorer /desktop=shell,WxH C:\windows\helper.exe`.
- Never commit build outputs, downloaded tools, or any game files.
