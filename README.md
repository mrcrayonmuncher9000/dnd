# MinDND demo

MinDND is a local, single-host demo that connects the campaign dashboard and VTT to a Python state service. The browser screens use the same JSON-backed campaign state; dice rolls and character movement are validated and saved by the backend.

## Run the whole demo

1. Install Python 3.10 or newer. No third-party Python packages are required.
2. From the repository root, start the app:

   ```powershell
   py .\run_demo.py
   ```

   If the Python launcher is unavailable, use `python .\run_demo.py`.
3. Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in a browser. The root page opens the campaign dashboard.
4. Choose **Open** on a room, or select **Open VTT Demo** to enter the VTT. The campaign party panel and dice roller are connected to the backend.
5. Keep the terminal open while presenting. Press **Ctrl+C** there to stop the server.

The backend creates and persists demo data in `Gin/demo_state.json`. To try a fresh state without overwriting that file, set a temporary state path before starting:

```powershell
$env:MINDND_STATE_PATH = "$env:TEMP\mindnd-demo-state.json"
py .\run_demo.py
```

## Connected demo actions

- Dashboard room cards load from the campaign API.
- Create rooms from either dashboard tab and open them directly in the VTT.
- The VTT party list and room banner load from the same state.
- Dice rolls use `Gin/dice_engine.py`, are logged, and persist to the JSON state.
- Movement validates the 36-by-24 grid, occupied destinations, and the 35-foot turn limit, then records movement in the state.
- **Next Turn** resets movement availability.
- Custom map uploads remain browser-local in IndexedDB.

The server is intended for a local presentation demo, not public deployment or multi-user production hosting.

## API

- `GET /api/health` — server availability.
- `GET /api/state` — current campaign, rooms, characters, maps, and logs.
- `POST /api/rooms` — create a room.
- `POST /api/roll` — roll dice and append a dice log.
- `POST /api/move` — validate and save a character move.
- `POST /api/reset-turn` — reset per-character movement for a new turn.
- `POST /api/logs/clear` — clear campaign logs.
