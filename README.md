# pupmeet

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

Start the development server:

```bash
python app.py
```

Visit [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser. Leave the terminal running while you use the app; press `Ctrl+C` there to stop the server. Profile photos load from Unsplash and require an internet connection.

To run it again later, open a terminal in the project directory, activate the environment (`source .venv/bin/activate` on macOS/Linux, or `.venv\Scripts\activate` on Windows), then run `python app.py`.

## Tests

```bash
python -m unittest discover -s tests -v
```

This is a local demo: profiles and mutual likes are sample data stored in the signed browser session. For deployment, set a private `SECRET_KEY` environment variable and replace the sample profiles with a persistent data store.
