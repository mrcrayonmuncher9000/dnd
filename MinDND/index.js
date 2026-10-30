const defaultVisibleUIs = [
    "campaignParty"
];

const uiCheckboxes = document.querySelectorAll(
    ".settingInput input[data-ui]"
);

function loadUISettings() {

    const savedSettings = localStorage.getItem("uiVisibility");

    const visibleUIs = savedSettings
        ? JSON.parse(savedSettings)
        : defaultVisibleUIs;

    uiCheckboxes.forEach(checkbox => {

        const uiID = checkbox.dataset.ui;
        const ui = document.getElementById(uiID);

        const isVisible = visibleUIs.includes(uiID);

        checkbox.checked = isVisible;

        if (ui) {
            ui.classList.toggle("visible", isVisible);
        }

    });

}

function saveUISettings() {

    const visibleUIs = [];

    uiCheckboxes.forEach(checkbox => {

        const uiID = checkbox.dataset.ui;
        const ui = document.getElementById(uiID);

        if (checkbox.checked) {
            visibleUIs.push(uiID);
        }

        if (ui) {
            ui.classList.toggle("visible", checkbox.checked);
        }

    });

    localStorage.setItem(
        "uiVisibility",
        JSON.stringify(visibleUIs)
    );

}

document.getElementById("saveSettings").addEventListener(
    "click",
    saveUISettings
);

loadUISettings();

document.getElementById("restoreSettings").addEventListener(
    "click",
    () => {

        uiCheckboxes.forEach(checkbox => {

            checkbox.checked = defaultVisibleUIs.includes(
                checkbox.dataset.ui
            );

        });

        saveUISettings();

    }
);

const buttons = document.querySelectorAll(
    "#assetManager .controlButton"
);

const assetUIs = document.querySelectorAll(".assetUI");

buttons.forEach(button => {
    button.addEventListener("click", () => {

        const target = button.dataset.target;
        const selectedUI = document.getElementById(target);

        // Check if the selected UI is already open
        const isOpen = selectedUI?.classList.contains("active");

        // Close all asset UIs
        assetUIs.forEach(ui => {
            ui.classList.remove("active");
        });

        // If it wasn't open, open it
        if (selectedUI && !isOpen) {
            selectedUI.classList.add("active");
        }

    });
});

function showContent(section) {
            // Hide all content
            document.querySelectorAll('.ADcontent').forEach(content => {
                content.classList.remove('active');
            });

            // Show selected content
            document.getElementById(section).classList.add('active');
        }

document.querySelectorAll(".popupUI").forEach(popup => {
    const minBtn = popup.querySelector(".minBtn");

    if (!minBtn) return;

    minBtn.addEventListener("click", () => {
        const isMinimized = popup.classList.toggle("minimized");

        if (isMinimized) {
            popup.dataset.originalHeight = popup.style.height;
            popup.style.height = "fit-content";
        } else {
            popup.style.height = popup.dataset.originalHeight || "";
        }

        minBtn.innerHTML = isMinimized
            ? '<i class="fa-solid fa-plus"></i>'
            : '<i class="fa-solid fa-minus"></i>';
    });
});

function openUI(id) {

    const ui = document.getElementById(id);
    if (!ui) return;

    ui.classList.add("visible");

}

function closeUI(id) {

    const ui = document.getElementById(id);
    if (!ui) return;

    ui.classList.remove("visible");

}

function saveUIPosition(elmnt) {
    const id = elmnt.id;
    if (!id) return;

    localStorage.setItem(`ui-position-${id}`, JSON.stringify({
        left: elmnt.style.left,
        top: elmnt.style.top
    }));
}

function restoreUIPosition(elmnt) {
    const id = elmnt.id;
    if (!id) return;

    const saved = localStorage.getItem(`ui-position-${id}`);
    if (!saved) return;

    const position = JSON.parse(saved);

    elmnt.style.left = position.left;
    elmnt.style.top = position.top;
}

let highestZIndex = 1000;

document.querySelectorAll(".popupUI").forEach(popup => {
    restoreUIPosition(popup);
    dragElement(popup);
});

function dragElement(elmnt) {
    const header = elmnt.querySelector(".header");
    if (!header) return;

    let startX = 0;
    let startY = 0;
    let startLeft = 0;
    let startTop = 0;
    let dragging = false;

    header.addEventListener("pointerdown", (e) => {
        // Ignore clicks on window controls
        if (e.target.closest("button")) return;
        if (e.button !== 0) return;

        const rect = elmnt.getBoundingClientRect();

        startX = e.clientX;
        startY = e.clientY;
        startLeft = rect.left;
        startTop = rect.top;
        dragging = true;

        elmnt.style.left = `${rect.left}px`;
        elmnt.style.top = `${rect.top}px`;
        elmnt.style.zIndex = ++highestZIndex;

        header.setPointerCapture(e.pointerId);
        e.preventDefault();
    });

    header.addEventListener("pointermove", (e) => {
        if (!dragging) return;

        elmnt.style.left =
            `${startLeft + e.clientX - startX}px`;

        elmnt.style.top =
            `${startTop + e.clientY - startY}px`;
    });

    function stopDragging() {
        if (!dragging) return;

        dragging = false;
        saveUIPosition(elmnt);
    }

    header.addEventListener("pointerup", stopDragging);
    header.addEventListener("pointercancel", stopDragging);
}

    const customMapForm = document.getElementById("customMapForm");
    const customMapGrid = document.getElementById("customMapGrid");
    const customMapStatus = document.getElementById("customMapStatus");
    const customMapName = document.getElementById("customMapName");
    const customMapFile = document.getElementById("customMapFile");
    const customMapDatabaseName = "mindnd-custom-maps";
    let customMapObjectUrls = [];

    function openCustomMapDatabase() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(customMapDatabaseName, 1);

            request.onupgradeneeded = () => {
                request.result.createObjectStore("maps", { keyPath: "id" });
            };
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    async function useCustomMapStore(mode, operation) {
        const database = await openCustomMapDatabase();

        return new Promise((resolve, reject) => {
            const transaction = database.transaction("maps", mode);
            const request = operation(transaction.objectStore("maps"));
            let result;

            request.onsuccess = () => {
                result = request.result;
            };
            request.onerror = () => {
                database.close();
                reject(request.error);
            };
            transaction.oncomplete = () => {
                database.close();
                resolve(result);
            };
            transaction.onerror = () => {
                database.close();
                reject(transaction.error);
            };
            transaction.onabort = () => {
                database.close();
                reject(transaction.error);
            };
        });
    }

    function setCustomMapStatus(message) {
        customMapStatus.textContent = message;
    }

    async function renderCustomMaps() {
        const maps = await useCustomMapStore("readonly", store => store.getAll());

        customMapObjectUrls.forEach(url => URL.revokeObjectURL(url));
        customMapObjectUrls = [];
        customMapGrid.replaceChildren();

        if (maps.length === 0) {
            const emptyState = document.createElement("p");
            emptyState.className = "mapEmptyState";
            emptyState.textContent = "Your custom maps will appear here.";
            customMapGrid.append(emptyState);
            return;
        }

        maps.sort((first, second) => second.createdAt - first.createdAt);
        maps.forEach(map => {
            const card = document.createElement("div");
            card.className = "cardContainer";

            const preview = document.createElement("img");
            preview.className = "cardImage customMapPreview";
            preview.alt = `${map.name} map preview`;
            const objectUrl = URL.createObjectURL(map.image);
            customMapObjectUrls.push(objectUrl);
            preview.src = objectUrl;

            const header = document.createElement("div");
            header.className = "cardHeader";

            const name = document.createElement("p");
            name.textContent = map.name;

            const options = document.createElement("div");
            options.className = "cardOptions";

            const deleteButton = document.createElement("button");
            deleteButton.type = "button";
            deleteButton.setAttribute("aria-label", `Remove ${map.name}`);
            deleteButton.innerHTML = '<i class="fa-solid fa-trash"></i>';
            deleteButton.addEventListener("click", async () => {
                try {
                    await useCustomMapStore("readwrite", store => store.delete(map.id));
                    await renderCustomMaps();
                    setCustomMapStatus(`${map.name} removed.`);
                } catch (error) {
                    console.error("Could not remove custom map:", error);
                    setCustomMapStatus("Could not remove this map. Please try again.");
                }
            });

            options.append(deleteButton);
            header.append(name, options);
            card.append(preview, header);
            customMapGrid.append(card);
        });
    }

    customMapForm.addEventListener("submit", async event => {
        event.preventDefault();

        const name = customMapName.value.trim();
        const image = customMapFile.files[0];

        if (!name || !image) {
            setCustomMapStatus("Enter a map name and choose an image.");
            return;
        }

        if (!image.type.startsWith("image/")) {
            setCustomMapStatus("Choose a valid image file for your map.");
            return;
        }

        try {
            await useCustomMapStore("readwrite", store => store.add({
                id: crypto.randomUUID(),
                name,
                image,
                createdAt: Date.now()
            }));
            customMapForm.reset();
            await renderCustomMaps();
            setCustomMapStatus(`${name} added to your map gallery.`);
        } catch (error) {
            console.error("Could not save custom map:", error);
            setCustomMapStatus("Could not save this map in browser storage. Please try another image.");
        }
    });

    renderCustomMaps().catch(error => {
        console.error("Could not load custom maps:", error);
        setCustomMapStatus("Could not load saved maps from browser storage.");
    });

    let activeDie = 20;
    let lastDemoState = null;

    async function demoApi(path, payload) {
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

    function renderDemoState(state) {
        lastDemoState = state;
        const requestedRoom = new URLSearchParams(window.location.search).get("room");
        const activeRoom = state.rooms.find(room => room.id === requestedRoom) || state.rooms[0];
        const campaignBanner = document.getElementById("campaignBanner");
        campaignBanner.textContent = activeRoom
            ? `${state.campaign.name} · ${activeRoom.name}`
            : state.campaign.name;
        document.title = `${state.campaign.name} | MinDND VTT`;

        const partyList = document.getElementById("partyCharacterList");
        partyList.replaceChildren();
        state.characters.forEach(character => {
            const member = document.createElement("div");
            member.className = "memberName";
            const photo = document.createElement("div");
            photo.className = "memberPhoto";
            photo.textContent = character.name.slice(0, 1);
            const details = document.createElement("p");
            const position = character.position;
            details.textContent =
                `${character.name} | ${character.role} · ${character.class_name} · ` +
                `(${position.x}, ${position.y})${character.has_moved ? " · moved" : ""}`;
            member.append(photo, details);
            partyList.append(member);
        });

        ["moveCharacter", "diceCharacter"].forEach(selectId => {
            const select = document.getElementById(selectId);
            const previousValue = select.value;
            select.replaceChildren();
            state.characters.forEach(character => {
                const option = document.createElement("option");
                option.value = character.id;
                option.textContent = character.name;
                if (selectId === "moveCharacter" && character.has_moved) {
                    option.disabled = true;
                    option.textContent += " (moved)";
                }
                select.append(option);
            });
            if (state.characters.some(character => character.id === previousValue)) {
                select.value = previousValue;
            }
        });

        const diceLogs = document.getElementById("diceLogList");
        diceLogs.replaceChildren();
        const logs = state.logs.filter(entry => entry.type === "dice").slice().reverse();
        if (logs.length === 0) {
            const emptyMessage = document.createElement("p");
            emptyMessage.className = "diceLog";
            emptyMessage.textContent = "No dice rolls yet.";
            diceLogs.append(emptyMessage);
        } else {
            logs.forEach(entry => {
                const line = document.createElement("p");
                line.className = "diceLog";
                line.textContent = entry.message;
                diceLogs.append(line);
            });
        }
    }

    async function refreshDemoState() {
        try {
            const state = await demoApi("/api/state");
            renderDemoState(state);
            document.getElementById("campaignBanner").removeAttribute("title");
        } catch (error) {
            console.error("Could not load campaign state:", error);
            document.getElementById("campaignBanner").textContent =
                "Backend unavailable. Start the demo with py .\\run_demo.py.";
        }
    }

    document.querySelectorAll(".diceButton").forEach(button => {
        button.setAttribute("aria-pressed", String(Number(button.dataset.die) === activeDie));
        button.addEventListener("click", () => {
            activeDie = Number(button.dataset.die);
            document.querySelectorAll(".diceButton").forEach(dieButton => {
                dieButton.setAttribute(
                    "aria-pressed",
                    String(Number(dieButton.dataset.die) === activeDie)
                );
            });
        });
    });

    document.getElementById("rollDice").addEventListener("click", async () => {
        const status = document.getElementById("diceRollStatus");
        status.textContent = "Rolling...";
        try {
            const result = await demoApi("/api/roll", {
                character_id: document.getElementById("diceCharacter").value,
                dice_type: activeDie,
                quantity: Number(document.getElementById("diceQuantity").value),
                modifier: Number(document.getElementById("diceModifier").value),
                attribute: document.getElementById("diceAttribute").value,
                advantage: document.getElementById("diceAdvantage").value
            });
            status.textContent = result.log_message;
            await refreshDemoState();
        } catch (error) {
            status.textContent = error.message;
        }
    });

    document.getElementById("resetDice").addEventListener("click", () => {
        activeDie = 20;
        document.querySelector('.diceButton[data-die="20"]').click();
        document.getElementById("diceQuantity").value = "1";
        document.getElementById("diceModifier").value = "0";
        document.getElementById("diceAttribute").value = "None";
        document.getElementById("diceAdvantage").value = "None";
        document.getElementById("diceRollStatus").textContent = "";
    });

    document.getElementById("moveForm").addEventListener("submit", async event => {
        event.preventDefault();
        const status = document.getElementById("moveStatus");
        try {
            const state = await demoApi("/api/move", {
                character_id: document.getElementById("moveCharacter").value,
                x: Number(document.getElementById("moveX").value),
                y: Number(document.getElementById("moveY").value)
            });
            renderDemoState(state);
            status.textContent = "Move saved to the campaign state.";
        } catch (error) {
            status.textContent = error.message;
        }
    });

    document.getElementById("resetTurn").addEventListener("click", async () => {
        try {
            renderDemoState(await demoApi("/api/reset-turn", {}));
            document.getElementById("moveStatus").textContent =
                "Turn reset. Characters can move again.";
        } catch (error) {
            document.getElementById("moveStatus").textContent = error.message;
        }
    });

    document.getElementById("clearDiceLogs").addEventListener("click", async () => {
        try {
            renderDemoState(await demoApi("/api/logs/clear", {}));
            document.getElementById("diceRollStatus").textContent = "Dice history cleared.";
        } catch (error) {
            document.getElementById("diceRollStatus").textContent = error.message;
        }
    });

    refreshDemoState();
    window.setInterval(() => {
        if (!document.hidden) {
            refreshDemoState();
        }
    }, 5000);
