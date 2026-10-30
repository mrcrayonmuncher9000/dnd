const defaultVisibleUIs = [
    "campaignParty",
    "chatLogs",
    "journalNotes"
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
