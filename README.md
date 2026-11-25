# puppin' up

A small Flask demo for meeting nearby dogs. Browse profiles, pass or say hello, and collect reciprocal likes in your pack.

## Run locally

You need Python 3 installed. From the project directory, create a virtual environment,
activate it, and install the app's dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows, activate the environment with `.venv\Scripts\activate` instead.

Start the development server on a non-privileged local port (such as `5000`):

```bash
PORT=5000 python app.py
```

Visit [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser. Leave the terminal running while you use the app; press `Ctrl+C` there to stop the server. Profile photos load from Unsplash and require an internet connection.

> **Why `PORT=5000` locally?** In `app.py`, the app binds to `0.0.0.0` and defaults to port `80` (`app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "80")))`) so it is publicly reachable over standard HTTP on the server:
> - `0.0.0.0` listens on all network interfaces (instead of `127.0.0.1`, which only accepts connections from the same machine).
> - Port `80` is the default HTTP port (no `:5000` needed in the URL). On Linux, ports below `1024` are privileged, so running directly on port `80` requires either `CAP_NET_BIND_SERVICE` (configured in the `systemd` service below) or `root`. Setting `PORT=5000` lets you run locally without elevated privileges.

To run it again later, open a terminal in the project directory, activate the environment (`source .venv/bin/activate` on macOS/Linux, or `.venv\Scripts\activate` on Windows), then run `PORT=5000 python app.py`.

## Server Deployment (`systemd` Background Service)

To keep the app running in the background after you log out—and have it start automatically whenever the server boots—it is configured as a `systemd` service named `tinder-for-dogs.service`.

### 1. Create the `systemd` service unit

Create `/etc/systemd/system/tinder-for-dogs.service`:

```bash
sudo tee /etc/systemd/system/tinder-for-dogs.service > /dev/null <<'EOF'
[Unit]
Description=tinder-for-dogs (pupmeet) Flask application
After=network.target

[Service]
Type=simple
User=profffesssorpeeeeteee
Group=profffesssorpeeeeteee
WorkingDirectory=/home/profffesssorpeeeeteee/tinder-for-dogs
Environment=PYTHONUNBUFFERED=1
ExecStart=/home/profffesssorpeeeeteee/tinder-for-dogs/.venv/bin/python /home/profffesssorpeeeeteee/tinder-for-dogs/app.py
AmbientCapabilities=CAP_NET_BIND_SERVICE
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
```

Key settings explained:
- `After=network.target` — Waits until networking is up before starting the app.
- `User` / `Group` — Runs the app as a regular non-root user instead of `root`.
- `WorkingDirectory` — Runs from the project directory so Flask finds `templates/` and `static/`.
- `Environment=PYTHONUNBUFFERED=1` — Flushes Python output immediately so logs appear right away in `journalctl`.
- `ExecStart` — Launches `app.py` with the virtual environment's Python interpreter (`.venv/bin/python`).
- `AmbientCapabilities=CAP_NET_BIND_SERVICE` and `CapabilityBoundingSet=CAP_NET_BIND_SERVICE` — Grants only the Linux capability needed to bind to privileged port `80`, without running the app as `root`.
- `Restart=on-failure` / `RestartSec=3` — Automatically restarts the app 3 seconds after a crash.
- `WantedBy=multi-user.target` — Ensures the service starts automatically at boot once enabled.

### 2. Enable on boot and start the service

Tell `systemd` to load the new unit file, enable it for startup on boot, and start it immediately:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now tinder-for-dogs.service
```

Verify that it is active and listening on port `80`:

```bash
sudo systemctl status tinder-for-dogs.service
curl -I http://localhost/
```

### 3. Managing the service

| Task | Command |
| --- | --- |
| Check service status | `sudo systemctl status tinder-for-dogs.service` |
| Start the service | `sudo systemctl start tinder-for-dogs.service` |
| Stop the service | `sudo systemctl stop tinder-for-dogs.service` |
| Restart the service (e.g. after code changes) | `sudo systemctl restart tinder-for-dogs.service` |
| Enable auto-start on boot | `sudo systemctl enable tinder-for-dogs.service` |
| Disable auto-start on boot | `sudo systemctl disable tinder-for-dogs.service` |
| Check whether auto-start is enabled | `systemctl is-enabled tinder-for-dogs.service` |
| Reload unit file after editing `/etc/systemd/system/tinder-for-dogs.service` | `sudo systemctl daemon-reload && sudo systemctl restart tinder-for-dogs.service` |
| View recent logs | `sudo journalctl -u tinder-for-dogs.service -n 50 --no-pager` |
| Stream live logs (`Ctrl+C` to exit) | `sudo journalctl -u tinder-for-dogs.service -f` |

## Deploying Code Changes

Running `git pull` updates the files on disk, **but it does not automatically update the running app**. Because Flask is running in non-debug mode under `systemd`, both Python code (`app.py`) and compiled Jinja2 HTML templates (`templates/*.html`) stay cached in memory until the process is restarted.

Follow these steps whenever you deploy changes to the server:

1. **Go to the project directory and check for local changes:**
   ```bash
   cd /home/profffesssorpeeeeteee/tinder-for-dogs
   git status
   ```
   *(Note: if `app.py` has uncommitted server-only edits—such as the `0.0.0.0:80` host/port change—`git pull` will succeed unless incoming commits modify those same lines. Committing those changes or configuring host/port via environment variables avoids future merge conflicts.)*

2. **Pull the latest code:**
   ```bash
   git pull
   ```

3. **Update dependencies** (if `requirements.txt` changed):
   ```bash
   .venv/bin/pip install -r requirements.txt
   ```

4. **Run the test suite** (recommended before restarting):
   ```bash
   .venv/bin/python -m unittest discover -s tests -v
   ```

5. **Restart the `systemd` service** so the running process loads the updated code and templates:
   ```bash
   sudo systemctl restart tinder-for-dogs.service
   ```

6. **Verify the deployment:**
   ```bash
   sudo systemctl status tinder-for-dogs.service --no-pager
   curl -s http://localhost/ | grep -i '<title>'
   ```
   Confirm the service shows `active (running)` with a fresh start timestamp and that `curl` returns your updated HTML. If you updated CSS or JS files under `static/` and don't see them in your browser, do a hard refresh (`Ctrl+Shift+R` or `Cmd+Shift+R`).

   If the service fails to start, inspect the logs:
   ```bash
   sudo journalctl -u tinder-for-dogs.service -n 30 --no-pager
   ```

## Tests

```bash
.venv/bin/python -m unittest discover -s tests -v
```

This is a local demo: profiles and mutual likes are sample data stored in the signed browser session. For deployment, set a private `SECRET_KEY` environment variable and replace the sample profiles with a persistent data store.
