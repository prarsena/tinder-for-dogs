const dogCard = document.querySelector("#dog-card");
const photo = document.querySelector("#dog-photo");
const name = document.querySelector("#dog-name");
const meta = document.querySelector("#dog-meta");
const distance = document.querySelector("#dog-distance");
const bio = document.querySelector("#dog-bio");
const tags = document.querySelector("#dog-tags");
const remainingCount = document.querySelector("#remaining-count");
const matchCount = document.querySelector("#match-count");
const matchesList = document.querySelector("#matches-list");
const statusMessage = document.querySelector("#status-message");
const passButton = document.querySelector("#pass-button");
const likeButton = document.querySelector("#like-button");
const matchDialog = document.querySelector("#match-dialog");
const matchPhoto = document.querySelector("#match-photo");
const matchTitle = document.querySelector("#match-title");
let currentDog = null;
let submitting = false;

async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "Something went wrong. Please try again.");
  }
  return data;
}

function setBusy(busy) {
  submitting = busy;
  passButton.disabled = busy || !currentDog;
  likeButton.disabled = busy || !currentDog;
}

function showDog(dog, remaining) {
  currentDog = dog;
  remainingCount.textContent = remaining;
  statusMessage.textContent = "";
  tags.replaceChildren();

  if (!dog) {
    const emptyState = document.createElement("div");
    emptyState.className = "empty-state";
    emptyState.innerHTML = `
      <span class="empty-paw" aria-hidden="true">🐾</span>
      <h3>You're all caught up!</h3>
      <p>Your next meet-cute is just around the corner.</p>
      <button class="restart-button" type="button">Start over</button>
    `;
    dogCard.replaceWith(emptyState);
    document.querySelector(".card-wrap").classList.add("is-empty");
    document.querySelector(".restart-button").addEventListener("click", resetBrowse);
    setBusy(false);
    return;
  }

  const emptyState = document.querySelector(".empty-state");
  if (emptyState) {
    emptyState.replaceWith(dogCard);
    document.querySelector(".card-wrap").classList.remove("is-empty");
  }

  photo.src = dog.photo;
  photo.alt = `${dog.name}, a ${dog.breed}`;
  photo.onerror = () => { photo.style.visibility = "hidden"; };
  photo.onload = () => { photo.style.visibility = "visible"; };
  name.textContent = `${dog.name}, ${dog.age}`;
  meta.textContent = dog.breed;
  distance.textContent = `${dog.distance} · ${dog.location}`;
  bio.textContent = dog.bio;

  for (const tag of dog.tags) {
    const chip = document.createElement("span");
    chip.className = "trait-tag";
    chip.textContent = tag;
    tags.append(chip);
  }
  setBusy(false);
}

function renderMatches(matches) {
  matchCount.textContent = matches.length;
  if (!matches.length) {
    matchesList.innerHTML = `
      <div class="empty-matches">
        <span class="empty-paw" aria-hidden="true">🐾</span>
        <p>Your new besties<br>will show up here.</p>
        <span>Keep saying hello!</span>
      </div>
    `;
    return;
  }

  matchesList.replaceChildren();
  for (const dog of matches) {
    const item = document.createElement("div");
    item.className = "match-item";
    const avatar = document.createElement("img");
    avatar.className = "match-avatar";
    avatar.src = dog.photo;
    avatar.alt = "";
    const copy = document.createElement("div");
    copy.className = "match-copy";
    const dogName = document.createElement("strong");
    dogName.textContent = dog.name;
    const dogBreed = document.createElement("span");
    dogBreed.textContent = `${dog.breed} · ${dog.distance}`;
    copy.append(dogName, dogBreed);
    const heart = document.createElement("span");
    heart.className = "match-status";
    heart.textContent = "♥";
    item.append(avatar, copy, heart);
    matchesList.append(item);
  }
}

async function loadMatches() {
  const data = await requestJson("/api/matches");
  renderMatches(data.matches);
}

async function swipe(direction) {
  if (!currentDog || submitting) return;
  setBusy(true);
  statusMessage.textContent = "";
  const dogId = currentDog.id;
  dogCard.classList.add(direction === "like" ? "swiping-right" : "swiping-left");

  try {
    const data = await requestJson("/api/swipes", {
      method: "POST",
      body: JSON.stringify({ dog_id: dogId, direction }),
    });
    await new Promise((resolve) => window.setTimeout(resolve, 210));
    dogCard.classList.remove("swiping-right", "swiping-left");
    showDog(data.dog, data.remaining);
    await loadMatches();

    if (data.match) {
      matchPhoto.src = data.match.photo;
      matchPhoto.alt = `${data.match.name}, a ${data.match.breed}`;
      matchTitle.textContent = `You and ${data.match.name} like each other`;
      matchDialog.showModal();
    }
  } catch (error) {
    dogCard.classList.remove("swiping-right", "swiping-left");
    setBusy(false);
    statusMessage.textContent = error.message;
  }
}

async function resetBrowse() {
  setBusy(true);
  try {
    await requestJson("/api/reset", { method: "POST" });
    const data = await requestJson("/api/current");
    showDog(data.dog, data.remaining);
    await loadMatches();
  } catch (error) {
    setBusy(false);
    statusMessage.textContent = error.message;
  }
}

async function start() {
  setBusy(true);
  try {
    const [current, matches] = await Promise.all([
      requestJson("/api/current"),
      requestJson("/api/matches"),
    ]);
    showDog(current.dog, current.remaining);
    renderMatches(matches.matches);
  } catch (error) {
    setBusy(false);
    statusMessage.textContent = error.message;
  }
}

passButton.addEventListener("click", () => swipe("pass"));
likeButton.addEventListener("click", () => swipe("like"));
document.querySelector("#close-match").addEventListener("click", () => matchDialog.close());
document.querySelector("#keep-browsing").addEventListener("click", () => matchDialog.close());

document.addEventListener("keydown", (event) => {
  if (matchDialog.open || event.target instanceof HTMLButtonElement) return;
  if (event.key === "ArrowLeft") swipe("pass");
  if (event.key === "ArrowRight") swipe("like");
});

document.querySelector(".save-button").addEventListener("click", (event) => {
  const button = event.currentTarget;
  const saved = button.classList.toggle("saved");
  button.textContent = saved ? "♥" : "♡";
  button.setAttribute("aria-label", saved ? "Remove saved profile" : "Save profile");
});

start();
