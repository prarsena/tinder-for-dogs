import unittest

from app import app


class DogMeetupAppTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True, SECRET_KEY="test-secret")
        self.client = app.test_client()

    def test_homepage_renders(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Good dogs.", response.data)

    def test_current_profile_and_like_advance_to_next_dog(self):
        current = self.client.get("/api/current").get_json()
        self.assertEqual(current["dog"]["name"], "Milo")

        response = self.client.post(
            "/api/swipes",
            json={"dog_id": current["dog"]["id"], "direction": "like"},
        )
        result = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(result["liked"])
        self.assertEqual(result["dog"]["name"], "Luna")
        self.assertEqual(result["remaining"], 7)

    def test_breed_labels_match_reported_photos(self):
        self.client.post("/api/swipes", json={"dog_id": 1, "direction": "pass"})
        self.client.post("/api/swipes", json={"dog_id": 2, "direction": "pass"})
        peanut = self.client.get("/api/current").get_json()["dog"]
        self.assertEqual(peanut["breed"], "Pug")

        self.client.post("/api/swipes", json={"dog_id": 3, "direction": "pass"})
        maple = self.client.get("/api/current").get_json()["dog"]
        self.assertEqual(maple["breed"], "Chihuahua")

    def test_reciprocal_like_creates_match(self):
        self.client.post("/api/swipes", json={"dog_id": 1, "direction": "pass"})
        response = self.client.post(
            "/api/swipes",
            json={"dog_id": 2, "direction": "like"},
        )
        result = response.get_json()
        self.assertEqual(result["match"]["name"], "Luna")
        self.assertEqual(result["match_count"], 1)
        self.assertEqual(self.client.get("/api/matches").get_json()["count"], 1)

    def test_rejects_stale_profile_and_invalid_direction(self):
        self.client.post("/api/swipes", json={"dog_id": 1, "direction": "pass"})
        stale = self.client.post("/api/swipes", json={"dog_id": 1, "direction": "like"})
        invalid = self.client.post("/api/swipes", json={"dog_id": 2, "direction": "maybe"})
        self.assertEqual(stale.status_code, 409)
        self.assertEqual(invalid.status_code, 400)

    def test_reset_restores_first_profile_and_clears_matches(self):
        self.client.post("/api/swipes", json={"dog_id": 1, "direction": "pass"})
        self.client.post("/api/swipes", json={"dog_id": 2, "direction": "like"})
        self.client.post("/api/reset")

        current = self.client.get("/api/current").get_json()
        matches = self.client.get("/api/matches").get_json()
        self.assertEqual(current["dog"]["name"], "Milo")
        self.assertEqual(matches["count"], 0)


if __name__ == "__main__":
    unittest.main()
