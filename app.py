import os

from flask import Flask, jsonify, render_template, request, session


app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY", "local-dog-dating-demo-key"),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

DOGS = [
    {
        "id": 1,
        "name": "Milo",
        "age": 3,
        "breed": "Corgi",
        "distance": "0.8 miles away",
        "location": "Brooklyn, NY",
        "bio": "Professional sunbeam chaser. Amateur sock collector.",
        "tags": ["Big personality", "Park regular", "Treat motivated"],
        "photo": "https://images.unsplash.com/photo-1552053831-71594a27632d?auto=format&fit=crop&w=1200&q=85",
        "likes_you": False,
    },
    {
        "id": 2,
        "name": "Luna",
        "age": 2,
        "breed": "Husky mix",
        "distance": "1.2 miles away",
        "location": "Brooklyn, NY",
        "bio": "I sing in the shower and will absolutely steal your pillow.",
        "tags": ["Adventure buddy", "Chatty", "Great with dogs"],
        "photo": "https://images.unsplash.com/photo-1543466835-00a7907e9de1?auto=format&fit=crop&w=1200&q=85",
        "likes_you": True,
    },
    {
        "id": 3,
        "name": "Peanut",
        "age": 4,
        "breed": "Pug",
        "distance": "1.7 miles away",
        "location": "Cobble Hill",
        "bio": "Short legs, long list of places I want to sniff.",
        "tags": ["Cuddle expert", "City pup", "Loves brunch"],
        "photo": "https://images.unsplash.com/photo-1517849845537-4d257902454a?auto=format&fit=crop&w=1200&q=85",
        "likes_you": False,
    },
    {
        "id": 4,
        "name": "Maple",
        "age": 1,
        "breed": "Chihuahua",
        "distance": "2.1 miles away",
        "location": "Brooklyn Heights",
        "bio": "Currently accepting applications for a fetch partner.",
        "tags": ["Puppy energy", "Water lover", "Very friendly"],
        "photo": "https://images.unsplash.com/photo-1537151625747-768eb6cf92b2?auto=format&fit=crop&w=1200&q=85",
        "likes_you": True,
    },
    {
        "id": 5,
        "name": "Frankie",
        "age": 5,
        "breed": "French bulldog",
        "distance": "2.4 miles away",
        "location": "Carroll Gardens",
        "bio": "A little snort, a lot of heart. Let's split a snack.",
        "tags": ["Laid-back", "Snack enthusiast", "House trained"],
        "photo": "https://images.unsplash.com/photo-1583337130417-3346a1be7dee?auto=format&fit=crop&w=1200&q=85",
        "likes_you": False,
    },
    {
        "id": 6,
        "name": "Biscuit",
        "age": 2,
        "breed": "Beagle",
        "distance": "2.8 miles away",
        "location": "Boerum Hill",
        "bio": "Follow my nose; it usually leads to the good stuff.",
        "tags": ["Trail scout", "Foodie", "Gentle soul"],
        "photo": "https://images.unsplash.com/photo-1548199973-03cce0bbc87b?auto=format&fit=crop&w=1200&q=85",
        "likes_you": True,
    },
    {
        "id": 7,
        "name": "Olive",
        "age": 3,
        "breed": "Terrier mix",
        "distance": "3.1 miles away",
        "location": "Fort Greene",
        "bio": "Small but mighty. Looking for a plus-one at the dog park.",
        "tags": ["Playful", "City explorer", "Loves people"],
        "photo": "https://images.unsplash.com/photo-1551717743-49959800b1f6?auto=format&fit=crop&w=1200&q=85",
        "likes_you": False,
    },
    {
        "id": 8,
        "name": "Archie",
        "age": 4,
        "breed": "Shepherd mix",
        "distance": "3.6 miles away",
        "location": "Prospect Heights",
        "bio": "Equal parts good listener and enthusiastic tennis-ball retriever.",
        "tags": ["Loyal", "Ball obsessed", "Easygoing"],
        "photo": "https://images.unsplash.com/photo-1534361960057-19889db9621e?auto=format&fit=crop&w=1200&q=85",
        "likes_you": True,
    },
]


def public_dog(dog):
    return {key: value for key, value in dog.items() if key != "likes_you"}


def seen_dog_ids():
    return set(session.get("seen_dog_ids", []))


def active_dog():
    seen = seen_dog_ids()
    return next((dog for dog in DOGS if dog["id"] not in seen), None)


def match_dogs():
    matched_ids = set(session.get("matched_dog_ids", []))
    return [public_dog(dog) for dog in DOGS if dog["id"] in matched_ids]


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/current")
def current_dog():
    dog = active_dog()
    remaining = len(DOGS) - len(seen_dog_ids())
    return jsonify(
        dog=public_dog(dog) if dog else None,
        remaining=remaining,
    )


@app.get("/api/matches")
def get_matches():
    matches = match_dogs()
    return jsonify(matches=matches, count=len(matches))


@app.post("/api/swipes")
def swipe():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error="Send a JSON object with dog_id and direction."), 400

    dog_id = payload.get("dog_id")
    direction = payload.get("direction")
    if isinstance(dog_id, bool) or not isinstance(dog_id, int):
        return jsonify(error="dog_id must be an integer."), 400
    if direction not in ("like", "pass"):
        return jsonify(error="direction must be 'like' or 'pass'."), 400

    dog = active_dog()
    if dog is None:
        return jsonify(error="There are no more dogs to browse."), 409
    if dog["id"] != dog_id:
        return jsonify(error="That profile is no longer the active dog."), 409

    seen = list(session.get("seen_dog_ids", []))
    seen.append(dog_id)
    session["seen_dog_ids"] = seen

    is_match = direction == "like" and dog["likes_you"]
    if is_match:
        matched = list(session.get("matched_dog_ids", []))
        matched.append(dog_id)
        session["matched_dog_ids"] = matched

    next_dog = active_dog()
    return jsonify(
        liked=direction == "like",
        match=public_dog(dog) if is_match else None,
        dog=public_dog(next_dog) if next_dog else None,
        remaining=len(DOGS) - len(seen),
        match_count=len(match_dogs()),
    )


@app.post("/api/reset")
def reset_browse():
    session.pop("seen_dog_ids", None)
    session.pop("matched_dog_ids", None)
    return jsonify(ok=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "80")))
