pdfjsLib.GlobalWorkerOptions.workerSrc =
'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

const PDF_URL = "./pdf/document.pdf";

let pdfDoc = null;
let pageNum = 1;
let scale = 1.6;

const canvas = document.getElementById("pdfCanvas");
const ctx = canvas.getContext("2d");

function renderPage(num) {

    pdfDoc.getPage(num).then(page => {

        const viewport = page.getViewport({
            scale: scale
        });

        canvas.height = viewport.height;
        canvas.width = viewport.width;

        page.render({
            canvasContext: ctx,
            viewport: viewport
        });

        document.getElementById("pageNum").textContent = num;
    });
}

function queueRender(page) {

    if(page < 1) return;
    if(page > pdfDoc.numPages) return;

    pageNum = page;
    renderPage(pageNum);
}

pdfjsLib.getDocument(PDF_URL).promise.then(pdf => {

    pdfDoc = pdf;

    document.getElementById("pageCount").textContent =
        pdf.numPages;

    renderPage(pageNum);
});

document.getElementById("prev").onclick = () => {
    queueRender(pageNum - 1);
};

document.getElementById("next").onclick = () => {
    queueRender(pageNum + 1);
};

document.getElementById("zoomIn").onclick = () => {
    scale += 0.2;
    renderPage(pageNum);
};

document.getElementById("zoomOut").onclick = () => {

    if(scale > 0.6){
        scale -= 0.2;
        renderPage(pageNum);
    }
};

document.getElementById("fullscreen").onclick = () => {

    if(document.documentElement.requestFullscreen){
        document.documentElement.requestFullscreen();
    }
};

/*
TV Remote Support
*/

document.addEventListener("keydown", e => {

    switch(e.key){

        case "ArrowLeft":
            queueRender(pageNum - 1);
            break;

        case "ArrowRight":
            queueRender(pageNum + 1);
            break;

        case "ArrowUp":
            scale += 0.2;
            renderPage(pageNum);
            break;

        case "ArrowDown":
            if(scale > 0.6){
                scale -= 0.2;
                renderPage(pageNum);
            }
            break;

        case "Enter":
            toggleFullscreen();
            break;
    }
});

// --- NEW: Page Jump Feature ---
const pageJumpInput = document.getElementById("pageJump");

pageJumpInput.addEventListener("change", (e) => {
    let requestedPage = parseInt(e.target.value);
    
    // Check if the page exists
    if (requestedPage >= 1 && requestedPage <= pdfDoc.numPages) {
        queueRender(requestedPage);
    }
    
    // Clear the input box and remove focus so TV remote arrows work normally again
    e.target.value = ""; 
    e.target.blur(); 
});

// --- NEW: Dark Mode Feature ---
const darkModeBtn = document.getElementById("darkMode");

darkModeBtn.onclick = () => {
    canvas.classList.toggle("dark-mode");
    if (canvas.classList.contains("dark-mode")) {
        darkModeBtn.textContent = "☀ Light Mode";
    } else {
        darkModeBtn.textContent = "◑ Dark Mode";
    }
};

// --- UPDATED: Fullscreen Toggle Feature ---
// Find your existing document.getElementById("fullscreen").onclick function and REPLACE it with this:

const fullscreenBtn = document.getElementById("fullscreen");

function toggleFullscreen() {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(err => console.log(err));
    } else {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        }
    }
}

fullscreenBtn.onclick = toggleFullscreen;

// This listener detects whenever fullscreen opens or closes (even via TV remote or ESC key)
// and updates the button text accordingly.
document.addEventListener("fullscreenchange", () => {
    if (document.fullscreenElement) {
        fullscreenBtn.textContent = "⛶ Normal Screen";
    } else {
        fullscreenBtn.textContent = "⛶ Fullscreen";
    }
});
