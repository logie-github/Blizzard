# Idea board

Ideas that are not being built now. Each says what it is, why, and what is unknown.

## A World of Warcraft realm without a server process

The 3.3.5a client has no offline mode, so a solo game still runs MariaDB, the auth server and the world server on the phone. A leaner way, cheapest first:

1. **One process, no MariaDB:** the world server built as a library inside the app, an embedded database instead of MariaDB, the auth step folded in. Saves two processes and the database's memory and SQL round trips; the game rules still run in full.
2. **In-process transport:** a Winsock shim in Wine so the client talks to the server library through shared memory, with the encryption left out on both ends. Saves little next to the game logic.
3. **Direct calls from the client:** patch the client's send and receive functions to call the game logic with no protocol at all. Fastest and leanest; a large, fragile reverse-engineering project.
4. **Simulate less** (works with any of the above): only the areas near the player active, slower ticks when idle, fewer or no playerbots, fewer map and update threads, quieter logging and database saves.

Unknown: how the phone's CPU time splits between the Winlator client, the world server, MariaDB and the auth server. Measure first (a CPU and memory readout per process in the realm's Checks report) before choosing.
