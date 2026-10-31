function showPage(pageId) {
    document.querySelectorAll(".page").forEach(page => {
        page.style.display = "none";
    });

    const selectedPage = document.getElementById(pageId);
    if (selectedPage) {
        selectedPage.style.display = "block";
    }
}

function showDashboardStatus(message) {
    let status = document.getElementById("dashboardStatus");
    if (!status) {
        status = document.createElement("p");
        status.id = "dashboardStatus";
        status.setAttribute("role", "status");
        document.querySelector(".navChoose").before(status);
    }
    status.textContent = message;
}

function makeRoomCard(room) {
    const card = document.createElement("div");
    card.className = "cardContainer";

    const image = document.createElement("div");
    image.className = "cardImage";

    const title = document.createElement("div");
    title.className = "cardTitle";

    const name = document.createElement("p");
    name.textContent = room.name;

    const openLink = document.createElement("a");
    openLink.href = `../MinDND/index.html?room=${encodeURIComponent(room.id)}`;
    openLink.textContent = "Open";
    openLink.setAttribute("aria-label", `Open ${room.name}`);
    openLink.style.color = "white";

    title.append(name, openLink);
    card.append(image, title);
    return card;
}

function renderRooms(rooms) {
    const gmGrid = document.getElementById("gmRoomGrid");
    const playerGrid = document.getElementById("playerRoomGrid");
    gmGrid.replaceChildren();
    playerGrid.replaceChildren();

    rooms.forEach(room => {
        const grid = room.type === "gm" ? gmGrid : playerGrid;
        grid.append(makeRoomCard(room));
    });

    if (gmGrid.childElementCount === 0) {
        gmGrid.textContent = "No Game Master rooms yet.";
    }
    if (playerGrid.childElementCount === 0) {
        playerGrid.textContent = "No player rooms yet.";
    }
}

async function dashboardApi(path, payload) {
    const response = await fetch(path, {
        method: payload ? "POST" : "GET",
        headers: payload ? { "Content-Type": "application/json" } : undefined,
        body: payload ? JSON.stringify(payload) : undefined
    });
    const result = await response.json();
    if (!response.ok) {
        throw new Error(result.error || `Request failed (${response.status}).`);
    }
    return result;
}

async function loadDashboard() {
    try {
        const state = await dashboardApi("/api/state");
        renderRooms(state.rooms || []);
        showDashboardStatus(`${state.campaign.name} · ${state.rooms.length} rooms`);
    } catch (error) {
        console.error("Could not load campaign rooms:", error);
        showDashboardStatus("Could not connect to MinDND. Start the demo with py .\\run_demo.py.");
    }
}

document.querySelectorAll(".createButton").forEach(button => {
    const form = button.parentElement.querySelector(".roomCreateForm");
    const nameInput = form.querySelector('input[name="roomName"]');

    button.addEventListener("click", () => {
        form.style.display = "flex";
        button.style.display = "none";
        nameInput.focus();
    });

    form.querySelector(".cancelRoomCreation").addEventListener("click", () => {
        form.reset();
        form.querySelector(".roomCreateStatus").textContent = "";
        form.style.display = "none";
        button.style.display = "";
    });

    form.addEventListener("submit", async event => {
        event.preventDefault();
        const status = form.querySelector(".roomCreateStatus");
        try {
            const result = await dashboardApi("/api/rooms", {
                name: nameInput.value,
                type: form.dataset.roomType
            });
            renderRooms(result.state.rooms);
            showDashboardStatus(`${result.room.name} created.`);
            form.reset();
            form.style.display = "none";
            button.style.display = "";
        } catch (error) {
            status.textContent = error.message;
        }
    });
});

loadDashboard();
