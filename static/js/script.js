const chatBox = document.getElementById("chatBox");
const messageInput = document.getElementById("message");
const chatForm = document.getElementById("chatForm");
const historyList = document.getElementById("historyList");
const newTripBtn = document.getElementById("newTripBtn");
const sendBtn = document.getElementById("sendBtn");

let activeHistoryId = null; // tracks which sidebar item is "selected"
let isSending = false;      // prevents double-submits

function appendMessage(text, sender) {
    const msg = document.createElement("div");
    msg.className = `msg msg--${sender}`;
    const p = document.createElement("p");
    p.textContent = text;
    msg.appendChild(p);
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
    return msg;
}

/* ---------- Typing indicator (replaces static "Thinking...") ---------- */
function appendTypingIndicator() {
    const msg = document.createElement("div");
    msg.className = "msg msg--bot";
    const p = document.createElement("p");
    p.className = "typing";
    p.innerHTML = `<span class="typing-dots"><span></span><span></span><span></span></span>`;
    msg.appendChild(p);
    chatBox.appendChild(msg);
    chatBox.scrollTop = chatBox.scrollHeight;
    return msg;
}

/* ---------- Card renderers ---------- */
function renderHotelCards(data) {
    const wrap = document.createElement("div");
    wrap.className = "card-row";
    data.hotels.forEach((hotel) => {
        const card = document.createElement("div");
        card.className = "hotel-card";
        card.innerHTML = `
            <img src="${hotel.image}" alt="${hotel.name}" class="hotel-card__img" loading="lazy">
            <div class="hotel-card__body">
                <h4>${hotel.name}</h4>
                <p class="hotel-card__price">${hotel.price}</p>
                <p class="hotel-card__rating">★ ${hotel.rating}</p>
            </div>
        `;
        wrap.appendChild(card);
    });
    chatBox.appendChild(wrap);
}

function renderFlightTimetable(data) {
    const wrap = document.createElement("div");
    wrap.className = "flight-panel";
    const rows = data.flights.map(f => `
        <div class="flight-row">
            <span class="flight-plane">✈</span>
            <span>${f.airline} · ${f.flight_no}</span>
            <span>${f.departure} → ${f.arrival}</span>
            <span>${f.duration}</span>
            <span class="flight-price">${f.price}</span>
        </div>
    `).join("");
    wrap.innerHTML = `
        <div class="flight-panel__header">
            <img src="${data.destination_image}" alt="${data.destination}" class="flight-panel__hero" loading="lazy">
            <h4>${data.origin} → ${data.destination}</h4>
        </div>
        ${rows}
    `;
    chatBox.appendChild(wrap);
}

function renderCards(cards) {
    if (!cards || cards.length === 0) return;
    cards.forEach((card) => {
        if (card.type === "hotels") renderHotelCards(card);
        if (card.type === "flights") renderFlightTimetable(card);
    });
    chatBox.scrollTop = chatBox.scrollHeight;
}

/* ---------- Sending state (disables input while waiting) ---------- */
function setSending(state) {
    isSending = state;
    messageInput.disabled = state;
    sendBtn.disabled = state;
    document.querySelectorAll(".chip").forEach(c => c.disabled = state);
}

/* ---------- Send message ---------- */
async function sendMessage(text) {
    if (isSending) return; // block double-submit

    const value = (text ?? messageInput.value).trim();
    if (value === "") return;

    // Sending a new message means we're no longer "viewing" a history item
    activeHistoryId = null;
    highlightActiveHistoryItem();

    appendMessage(value, "user");
    messageInput.value = "";
    setSending(true);

    const typing = appendTypingIndicator();

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: value })
        });

        const data = await response.json();
        typing.remove();

        if (!response.ok) {
            appendMessage(data.response || "Backend Error", "bot");
            return;
        }

        appendMessage(data.response || "No response received.", "bot");
        renderCards(data.cards);
        loadHistory(); // refresh sidebar after each exchange

    } catch (err) {
        console.error(err);
        typing.remove();
        appendMessage("Connection Failed", "bot");
    } finally {
        setSending(false);
        messageInput.focus();
    }
}

/* ---------- Chat history sidebar ---------- */
function truncate(str, max) {
    if (!str) return "";
    return str.length > max ? str.slice(0, max).trim() + "…" : str;
}

function highlightActiveHistoryItem() {
    document.querySelectorAll(".history-item").forEach(el => {
        el.classList.toggle("active", el.dataset.id === String(activeHistoryId));
    });
}

async function loadHistory() {
    try {
        const res = await fetch("/history");
        const data = await res.json();
        const rows = data.history || [];

        if (rows.length === 0) {
            historyList.innerHTML = `<p class="history-empty">No previous chats yet.</p>`;
            return;
        }

        historyList.innerHTML = "";
        rows.slice(0, 20).forEach((row) => {
            const item = document.createElement("div");
            item.className = "history-item";
            item.dataset.id = row.id;
            item.title = row.user_message;
            item.innerHTML = `
                <p class="history-item__title">${truncate(row.user_message, 40)}</p>
                <p class="history-item__snippet">${truncate(row.ai_response, 55)}</p>
            `;
            item.addEventListener("click", () => {
                chatBox.innerHTML = "";
                appendMessage(row.user_message, "user");
                appendMessage(row.ai_response, "bot");
                activeHistoryId = row.id;
                highlightActiveHistoryItem();
            });
            historyList.appendChild(item);
        });

        highlightActiveHistoryItem();
    } catch (err) {
        console.error("History load failed:", err);
        historyList.innerHTML = `<p class="history-empty">Couldn't load history.</p>`;
    }
}

/* ---------- New trip: clear the visible chat, keep history in DB ---------- */
newTripBtn.addEventListener("click", () => {
    chatBox.innerHTML = "";
    appendMessage("Hello, traveler. Where would you like to go?", "bot");
    activeHistoryId = null;
    highlightActiveHistoryItem();
});

/* ---------- Event wiring ---------- */
chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    sendMessage();
});

document.querySelectorAll(".chip").forEach((chip) => {
    chip.addEventListener("click", () => {
        const prompt = chip.dataset.prompt;
        if (!prompt) return;
        messageInput.value = prompt;
        messageInput.focus();
        // put the cursor at the end so the user can type the destination right away
        const len = messageInput.value.length;
        messageInput.setSelectionRange(len, len);
    });
});
/* ---------- Load history on page load ---------- */
loadHistory();