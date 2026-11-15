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
- **A one-line patch note with every change** (the user: "Start leaving one line patch notes in the update when you update
  the version. Put this only in the games, settings, gear button menu"). Each change that reaches `main` adds one file to
  `notes/` (`YYYY-MM-DD-what.txt`, one line in plain words for the player: `notes/README.md`). CI's release step puts the
  lines added since the previous release into the new release (`scripts/release-notes.sh`), and the app shows them only on
  Settings' Games page (the gear button, `PatchNotes`): never in a popup, the update banner or anywhere else. Never edit or
  remove a released note.
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
  a helper started with plain `wine` lands on another desktop and sees none of the game's windows. On the phone every Windows
  game is started by the session's keeper (`borderless.exe`, `tools/borderless`: Winlator patch 0009's `exec_wrapper`), which is
  where such work belongs; on the test rig, `wine explorer /desktop=shell,WxH C:\windows\helper.exe`.
- **Winlator is changed only through `patches/winlator`.** `app/winlator` is git-ignored: `scripts/prepare-winlator.sh` checks
  out Winlator's commit into `build/winlator-app`, applies `patches/winlator/NNNN-*.patch` and copies the result. An edit made
  only in `app/winlator` builds here and never ships (builds 178 to 180 said Warcraft III's clicks were fixed, and held nothing
  of it). Commit the change in `build/winlator-app`, `git format-patch -1` it into `patches/winlator`, and check the whole
  series applies to a clean checkout.
- **A fault in a game's clicks or keys is reproduced on Winlator's own X server** (`tools/xrig/README.md`: the server in a unit
  test, the phone's Wine connected to it), where the phone's input differs from Xvfb: pointer grabs, the stretch, which window
  gets the event. A change to the input path, the keeper or Winlator's server is run there before it is pushed.
- Never commit build outputs, downloaded tools, or any game files.

## Wrath++: the whole Shadowlands creator, every option, every race (the user's standing rule)

The user (14 November 2026): "We are using 3.3.5 modified client. It allows for more options because we are using the
shadowlands character creator. So all of this shit needs to be available and I should NOT have to keep repeating this
over and over."

- Wrath++ is **not stock 3.3.5**: it is the 3.3.5a client run through WarcraftXL's runtime with Wrath++'s own native mod
  (`client-mod/wrathpp-native`), its appearance add-on (`client-mod/wrathpp`), its realm module
  (`mod-wrathpp-customization`, the extended appearance protocol and registry) and the Shadowlands character creator
  (`app/src/main/assets/wrathpp/WrathppCreate.lua`). Its limits are what those can be made to do, not the stock client's.
- **Every option Shadowlands' creator has for a race and sex is available in Wrath++ and seen in the game**, per character:
  every race and both sexes (the Blood Elf man included), every category and option (Face, Hair, Accessories, Body,
  Markings: scars, paints, tattoos, horns, ears, vines, jewellery, makeup, face shape, Upright, the lot), and Wrath++'s own
  body options (Shape, Style, Density) for every race's women with every shape. "3.3.5 keeps five numbers" is never the
  end of it: what the five numbers can't carry goes through the extended appearance (registry categories, stored per
  character by the realm) and is drawn by the native mod (geosets, texture layers, extra models, bones) or by displays.
- An option greyed as "Not drawn yet", a race left on the old look, a shape only some races have or an animation that
  falls back to standing is **unfinished work, not an answer**. Never present it as done; list what is left and keep
  working through it (task #19 and the body options' races). Don't ask the user whether to wire something the creator
  shows: wire it.
