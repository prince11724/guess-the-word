const clickSound = document.getElementById("clickSound");
const winSound = document.getElementById("winSound");
const loseSound = document.getElementById("loseSound");

function playClick() {
    clickSound.currentTime = 0;
    clickSound.play().catch(e => console.log("Click sound blocked"));
}

// auto play win/lose safely
window.onload = () => {
    const msg = document.querySelector(".msg");
    if (!msg) return;

    const text = msg.innerText.toLowerCase();

    if (text.includes("win")) {
        winSound.play().catch(()=>{});
    }

    if (text.includes("lose")) {
        loseSound.play().catch(()=>{});
    }
};
