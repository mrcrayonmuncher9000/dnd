
let selectedDice = 6; // Default dice: D6

document.querySelectorAll(".diceButton").forEach(button => {
    button.addEventListener("click", function () {
        selectedDice = Number(this.id.substring(1));

        console.log("Selected dice: D" + selectedDice);
    });
});

function rollDice() {
    const diceCount = Number(document.getElementById("diceCount").value);
    const diceModifier = Number(document.getElementById("diceModifier").value);
    const diceLog = document.getElementById("diceLog");
    const values = [];

    if (diceCount < 1 || !Number.isInteger(diceCount)) {
        alert("Please enter a valid number of dice.");
        return;
    }

    for (let i = 0; i < diceCount; i++) {
        const value = Math.floor(Math.random() * selectedDice) + 1;
        values.push(value);
    }

    const total = values.reduce((sum, value) => sum + value, 0) + diceModifier;

    diceLog.innerHTML = `
        <p>D${selectedDice}: [${values.join(", ")}]</p>
        <p>Modifier: ${diceModifier}</p>
        <p>Total: ${total}</p>
    `;

    console.log("Rolls:", values);
    console.log("Total:", total);
}
