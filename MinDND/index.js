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
    if (elmnt.classList.contains("movementRangeWindow")) {
        elmnt.style.transform = "none";
    }
}

let highestZIndex = 1000;

document.querySelectorAll(".popupUI").forEach(popup => {
    restoreUIPosition(popup);
    dragElement(popup);
});

document.getElementById("openMovementRange").addEventListener("click", () => {
    openUI("movementRangeWindow");
    document.getElementById("movementFeet").focus();
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

        if (elmnt.classList.contains("movementRangeWindow")) {
            elmnt.style.transform = "none";
        }
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
    let selectedMapCharacterId = null;
    let movementFeet = null;
    const mapWidth = 36;
    const mapHeight = 24;

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

        renderTabletop(state, activeRoom);

        const partyList = document.getElementById("partyCharacterList");
        partyList.replaceChildren();
        const roomCharacters = getRoomCharacters(state, activeRoom);
        roomCharacters.forEach(character => {
            const member = document.createElement("div");
            member.className = "memberName";
            member.setAttribute("role", "button");
            member.setAttribute("tabindex", "0");
            member.setAttribute("aria-label", `Select ${character.name} for movement`);
            const photo = document.createElement("div");
            photo.className = "memberPhoto";
            photo.textContent = character.name.slice(0, 1);
            const details = document.createElement("p");
            const position = character.position;
            details.textContent =
                `${character.name} | ${character.role} · ${character.class_name} · ` +
                `(${position.x}, ${position.y})${character.has_moved ? " · moved" : ""}`;
            member.append(photo, details);
            const selectForMovement = () => {
                if (character.has_moved) {
                    document.getElementById("mapMoveStatus").textContent =
                        `${character.name} has already moved this turn. Reset Turn to move again.`;
                    return;
                }
                selectedMapCharacterId = character.id;
                movementFeet = null;
                document.getElementById("movementFeet").value = "";
                renderTabletop(state, activeRoom);
                openUI("movementRangeWindow");
                document.getElementById("movementFeet").focus();
            };
            member.addEventListener("click", selectForMovement);
            member.addEventListener("keydown", event => {
                if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    selectForMovement();
                }
            });
            partyList.append(member);
        });

        ["moveCharacter", "diceCharacter"].forEach(selectId => {
            const select = document.getElementById(selectId);
            if (!select) {
                return;
            }
            const previousValue = select.value;
            select.replaceChildren();
            const availableCharacters = selectId === "diceCharacter"
                ? state.characters
                : roomCharacters;
            availableCharacters.forEach(character => {
                const option = document.createElement("option");
                option.value = character.id;
                option.textContent = character.name;
                if (selectId === "moveCharacter" && character.has_moved) {
                    option.disabled = true;
                    option.textContent += " (moved)";
                }
                select.append(option);
            });
            if (availableCharacters.some(character => character.id === previousValue)) {
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

    function getRoomCharacters(state, room) {
        const roomCharacterIds = room?.characters || [];
        const characters = roomCharacterIds.length
            ? state.characters.filter(character => roomCharacterIds.includes(character.id))
            : state.characters.filter(character => character.role === "player");
        return characters;
    }

    function renderTabletop(state, room) {
        const tokenLayer = document.getElementById("mapTokens");
        const rangeCircle = document.getElementById("movementRangeCircle");
        const status = document.getElementById("mapMoveStatus");
        const characters = getRoomCharacters(state, room);
        tokenLayer.replaceChildren();

        if (!characters.some(character =>
            character.id === selectedMapCharacterId && !character.has_moved
        )) {
            selectedMapCharacterId = characters.find(character => !character.has_moved)?.id || null;
        }

        const selectedCharacter = characters.find(
            character => character.id === selectedMapCharacterId
        );
        if (selectedCharacter && movementFeet !== null) {
            const start = selectedCharacter.turn_start_position || selectedCharacter.position;
            rangeCircle.setAttribute("cx", String(start.x + 0.5));
            rangeCircle.setAttribute("cy", String(start.y + 0.5));
            rangeCircle.setAttribute("r", String(movementFeet));
            rangeCircle.style.display = "block";
        } else {
            rangeCircle.style.display = "none";
        }

        characters.forEach(character => {
            const token = document.createElement("button");
            token.type = "button";
            token.className = `mapToken ${character.role}`;
            token.classList.toggle("selected", character.id === selectedMapCharacterId);
            token.style.left = `${((character.position.x + 0.5) / mapWidth) * 100}%`;
            token.style.top = `${((character.position.y + 0.5) / mapHeight) * 100}%`;
            token.textContent = character.name.slice(0, 1);
            token.title = `${character.name} · ${character.role} · (${character.position.x}, ${character.position.y})${character.has_moved ? " · moved this turn" : ""}`;
            token.setAttribute("aria-label", token.title);
            token.disabled = character.has_moved;
            token.addEventListener("click", event => {
                event.stopPropagation();
                selectedMapCharacterId = character.id;
                movementFeet = null;
                document.getElementById("movementFeet").value = "";
                renderTabletop(state, room);
                status.textContent = `${character.name} selected. Enter a movement range up to 35 feet.`;
                openUI("movementRangeWindow");
                document.getElementById("movementFeet").focus();
            });
            tokenLayer.append(token);
        });

        if (characters.length === 0) {
            status.textContent = "No player characters are assigned to this room yet.";
        } else {
            const selected = characters.find(character => character.id === selectedMapCharacterId);
            status.textContent = selected
                ? movementFeet === null
                    ? `${selected.name} selected. Enter a movement range up to 35 feet, then click a destination.`
                    : `${selected.name}: ${movementFeet} ft range shown from the turn-start square. Click an unoccupied square inside it. Each square counts as 1 foot.`
                : "All characters have moved this turn. Reset Turn to move again.";
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

    document.getElementById("movementRangeForm").addEventListener("submit", event => {
        event.preventDefault();
        const input = document.getElementById("movementFeet");
        const feet = Number(input.value);
        const character = lastDemoState?.characters.find(
            item => item.id === selectedMapCharacterId
        );
        const status = document.getElementById("mapMoveStatus");

        if (!Number.isInteger(feet) || feet < 1 || feet > 35) {
            status.textContent = "Movement range must be a whole number from 1 to 35 feet.";
            return;
        }
        if (!character || character.has_moved) {
            status.textContent = "Select a character that has not moved this turn.";
            return;
        }

        movementFeet = feet;
        renderTabletop(lastDemoState, stateRoom(lastDemoState));
        closeUI("movementRangeWindow");
    });

    function stateRoom(state) {
        const requestedRoom = new URLSearchParams(window.location.search).get("room");
        return state.rooms.find(room => room.id === requestedRoom) || state.rooms[0];
    }

    document.getElementById("tabletopMap").addEventListener("click", async event => {
        if (!lastDemoState || !selectedMapCharacterId) {
            return;
        }
        if (movementFeet === null) {
            document.getElementById("mapMoveStatus").textContent =
                "Enter a movement range and select Show Range before choosing a destination.";
            return;
        }

        const bounds = event.currentTarget.getBoundingClientRect();
        const map = event.currentTarget;
        const x = Math.floor(
            ((event.clientX - bounds.left - map.clientLeft) / map.clientWidth) * mapWidth
        );
        const y = Math.floor(
            ((event.clientY - bounds.top - map.clientTop) / map.clientHeight) * mapHeight
        );
        const status = document.getElementById("mapMoveStatus");

        try {
            const state = await demoApi("/api/move", {
                character_id: selectedMapCharacterId,
                x,
                y,
                max_distance: movementFeet
            });
            movementFeet = null;
            document.getElementById("movementFeet").value = "";
            renderDemoState(state);
        } catch (error) {
            status.textContent = error.message;
        }
    });

    async function resetMapTurn() {
        try {
            renderDemoState(await demoApi("/api/reset-turn", {}));
            movementFeet = null;
            document.getElementById("movementFeet").value = "";
            renderTabletop(lastDemoState, stateRoom(lastDemoState));
            document.getElementById("mapMoveStatus").textContent =
                "Turn reset. Select a character, enter a movement range, then click a destination.";
        } catch (error) {
            document.getElementById("mapMoveStatus").textContent = error.message;
        }
    }

    document.getElementById("resetMapTurn").addEventListener("click", resetMapTurn);
    const existingResetTurn = document.getElementById("resetTurn");
    if (existingResetTurn) {
        existingResetTurn.addEventListener("click", resetMapTurn);
    }

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
