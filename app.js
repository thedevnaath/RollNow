pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

let pdfDoc = null;
let pageNum = 1;
let scale = 1.6;

const canvas = document.getElementById("pdfCanvas");
const ctx = canvas.getContext("2d");

const homeScreen = document.getElementById("homeScreen");
const viewerScreen = document.getElementById("viewerScreen");
const fileList = document.getElementById("fileList");
const homeBtn = document.getElementById("homeBtn");

// Initialize Lucide icons on load
lucide.createIcons();

// --- Fetch the dynamic list of PDFs ---
fetch("files.json")
    .then(response => response.json())
    .then(files => {
        if(files.length === 0) {
            fileList.innerHTML = "<p style='text-align:center; color:#888;'>No PDFs found.</p>";
            return;
        }
        
        files.forEach(file => {
            const btn = document.createElement("button");
            btn.className = "file-btn";
            btn.innerHTML = `<i data-lucide="file-text"></i> <span>${file.name}</span>`;
            btn.onclick = () => openViewer(file.path);
            fileList.appendChild(btn);
        });
        
        // Render the icons for the newly created file buttons
        lucide.createIcons({ root: fileList });
    })
    .catch(err => {
        console.log("Error loading files:", err);
    });

function openViewer(url) {
    homeScreen.style.display = "none";
    viewerScreen.style.display = "block";
    
    pdfjsLib.getDocument(url).promise.then(pdf => {
        pdfDoc = pdf;
        pageNum = 1; 
        document.getElementById("pageCount").textContent = pdf.numPages;
        renderPage(pageNum);
    }).catch(err => console.log(err));
}

// Return Home logic
homeBtn.onclick = () => {
    viewerScreen.style.display = "none";
    homeScreen.style.display = "flex"; 
    pdfDoc = null;
};

function renderPage(num) {
    if(!pdfDoc) return;
    pdfDoc.getPage(num).then(page => {
        const viewport = page.getViewport({ scale: scale });
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
    if(!pdfDoc) return;
    if(page < 1) return;
    if(page > pdfDoc.numPages) return;
    pageNum = page;
    renderPage(pageNum);
}

// Button Clicks
document.getElementById("prev").onclick = () => queueRender(pageNum - 1);
document.getElementById("next").onclick = () => queueRender(pageNum + 1);
document.getElementById("zoomIn").onclick = () => { scale += 0.2; renderPage(pageNum); };
document.getElementById("zoomOut").onclick = () => { if(scale > 0.6){ scale -= 0.2; renderPage(pageNum); } };

/* TV Remote Support */
document.addEventListener("keydown", e => {
    if (viewerScreen.style.display === "none") return;

    switch(e.key){
        case "ArrowLeft": queueRender(pageNum - 1); break;
        case "ArrowRight": queueRender(pageNum + 1); break;
        case "ArrowUp": scale += 0.2; renderPage(pageNum); break;
        case "ArrowDown": if(scale > 0.6){ scale -= 0.2; renderPage(pageNum); } break;
        case "Enter": toggleFullscreen(); break;
    }
});

// Page Jump Feature
const pageJumpInput = document.getElementById("pageJump");
if(pageJumpInput) {
    pageJumpInput.addEventListener("change", (e) => {
        let requestedPage = parseInt(e.target.value);
        if (pdfDoc && requestedPage >= 1 && requestedPage <= pdfDoc.numPages) {
            queueRender(requestedPage);
        }
        e.target.value = ""; 
        e.target.blur(); 
    });
}

// Dark Mode Feature
const darkModeBtn = document.getElementById("darkMode");
if(darkModeBtn) {
    darkModeBtn.onclick = () => {
        canvas.classList.toggle("dark-mode");
        
        if (canvas.classList.contains("dark-mode")) {
            darkModeBtn.innerHTML = '<i data-lucide="sun"></i> Light Mode';
        } else {
            darkModeBtn.innerHTML = '<i data-lucide="moon"></i> Dark Mode';
        }
        
        // Refresh icons so the sun/moon render properly
        lucide.createIcons();
    };
}

// Fullscreen Toggle Feature
const fullscreenBtn = document.getElementById("fullscreen");
function toggleFullscreen() {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(err => console.log(err));
    } else {
        if (document.exitFullscreen) document.exitFullscreen();
    }
}

if(fullscreenBtn) {
    fullscreenBtn.onclick = toggleFullscreen;
    
    document.addEventListener("fullscreenchange", () => {
        if (document.fullscreenElement) {
            fullscreenBtn.innerHTML = '<i data-lucide="minimize"></i> Normal Screen';
        } else {
            fullscreenBtn.innerHTML = '<i data-lucide="maximize"></i> Fullscreen';
        }
        
        lucide.createIcons();
    });
}
