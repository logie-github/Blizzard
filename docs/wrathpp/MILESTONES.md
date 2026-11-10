# Wrath++ milestones and gates

## Decision gates

| Gate | Question | State (2026-11-10) |
|---|---|---|
| A | Does the pinned source client build, boot and show the glue screens? | build: CI probe added, see TEST_RESULTS.md; boot: **untested** (needs the user's 3.3.5a data on Windows/Wine) |
| B | Does it run the Alternative HD data and connect to a disposable Wrath++ server without harming either? | **untested** (server side ready: isolated realm, live-tested server) |
| C | Does an independent sixth property visibly change a model in preview and in the world? | **blocked**: needs the `Component.GeosRenderPrep` seam (CLIENT_PROBE.md); protocol/state side done |
| D | Does the server persist and broadcast it across a restart? | **passed, server side**: live test with a protocol client (TEST_RESULTS.md); not yet with the real client |
| E | Does the client run in the app's Android runtime? | **untested** |

## Phases

| Phase | Content | State |
|---|---|---|
| 0 Inventory | repo audit, pins, hazards, licensing | done (SOURCE_AUDIT.md); Legion 7.3.5 data inventory **not done** (LEGION_OPTIONS_735.md) |
| 1 Client engine proof | build, boot, HD data, connect | build probe only |
| 2 Isolated infrastructure | realm 5 / 8087 / `*_wrathpp`, own paths, guards, rollback | `ctl.sh` done and tested; Wrath++ server/client **packages** and the **Android app entry** not started |
| 3 Vertical slice | registry → client state → preview → payload → DB → world → observer → relog/restart | registry, payload, DB, world, observer, restart: done on the server and in the Lua mod; **preview and in-world drawing: not done** (Gate C) |
| 4 Generalized compositor | texture layers, attachments, constraints | protocol carries the kinds; nothing drawn |
| 5 Legion creator UI | adapted 7.3.5 layout on the WrathPP_* API | not started |
| 6 Races | one race/sex at a time from the verified inventory | not started |
| 7 Android release | experimental installer, rollback | not started |

## Next highest-value slice

1. Run the client probe; fix whatever stops the pinned client from building with MSVC 2022 on the
   runner (or move the runner to the toolchain the client was last built with).
2. Write the `Component.GeosRenderPrep` seam as patches to core, SDK and client
   (`realm/warcraft/wrathpp/patches/{core,client}`), built by the probe; extend the Lua mod to apply
   `GeosetsFor` through it.
3. On a Windows or Wine machine with the user's 3.3.5a data: boot (Gate A), connect to the Wrath++
   server, and show that changing horns alone changes the preview, the character list, the world
   and a second client's view, and survives a restart (acceptance of the first real feature).
4. Inventory one race/sex from the user's 7.3.5 client and replace the seed registry rows.
