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
            if(document.documentElement.requestFullscreen){
                document.documentElement.requestFullscreen();
            }
            break;
    }
});
