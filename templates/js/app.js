const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileName = document.getElementById('fileName');
const form = document.getElementById('uploadForm');
const submitBtn = document.getElementById('submitBtn');
const progressContainer = document.getElementById('progressContainer');
const progressFill = document.getElementById('progressFill');
const statusMessage = document.getElementById('statusMessage');
const resultContainer = document.getElementById('resultContainer');
const resultDetails = document.getElementById('resultDetails');
const errorContainer = document.getElementById('errorContainer');
const coldstartMsg = document.getElementById('coldstartMsg');
const coldstartText = document.getElementById('coldstartText');
let currentJobId = null;

uploadArea.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        fileName.textContent = `Arquivo selecionado: ${e.target.files[0].name}`;
        form.requestSubmit();
    }
});

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});
uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});
uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    fileInput.files = e.dataTransfer.files;
    if (fileInput.files.length > 0) {
        fileName.textContent = `Arquivo selecionado: ${fileInput.files[0].name}`;
        form.requestSubmit();
    }
});

async function safeFetchJson(url, options = {}) {
    let response;
    try {
        response = await fetch(url, options);
    } catch {
        throw { type: 'network', message: 'Servidor indisponível. Verifique sua conexão.' };
    }
    const text = await response.text();
    if (!response.ok) {
        let detail;
        try { detail = JSON.parse(text).detail; } catch {}
        throw { type: 'http', message: detail || `Erro ${response.status}`, status: response.status };
    }
    try {
        return JSON.parse(text);
    } catch {
        if (text.includes('Not Found') || text.includes('not found')) {
            throw { type: 'coldstart', message: 'Servidor iniciando...' };
        }
        throw { type: 'parse', message: 'Resposta inesperada do servidor.' };
    }
}

function showColdStart(tentativa, maxTentativas) {
    coldstartText.textContent = `Servidor iniciando... Tentativa ${tentativa}/${maxTentativas}`;
    coldstartMsg.style.display = 'block';
    progressContainer.style.display = 'block';
    progressFill.style.width = '0%';
    progressFill.textContent = '0%';
    statusMessage.textContent = `Aguardando servidor (${tentativa}/${maxTentativas})...`;
}
function hideColdStart() {
    coldstartMsg.style.display = 'none';
}

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const file = fileInput.files[0];
    if (!file) return;
    errorContainer.style.display = 'none';
    resultContainer.style.display = 'none';
    submitBtn.disabled = true;
    const formData = new FormData();
    formData.append('file', file);
    const MAX_RETRIES = 4;
    let tentativa = 0;
    while (tentativa < MAX_RETRIES) {
        tentativa++;
        showColdStart(tentativa, MAX_RETRIES);
        try {
            const data = await safeFetchJson('/upload', {
                method: 'POST',
                body: formData
            });
            hideColdStart();
            currentJobId = data.job_id;
            progressFill.style.width = '10%';
            progressFill.textContent = '10%';
            statusMessage.textContent = 'Processando arquivo...';
            pollStatus(currentJobId);
            return;
        } catch (error) {
            if (error.type === 'coldstart' && tentativa < MAX_RETRIES) {
                await new Promise(r => setTimeout(r, 3000));
                continue;
            }
            hideColdStart();
            progressContainer.style.display = 'none';
            submitBtn.disabled = false;
            showError(error.message || 'Erro ao enviar arquivo', () => {
                form.requestSubmit();
            });
            return;
        }
    }
    hideColdStart();
    progressContainer.style.display = 'none';
    submitBtn.disabled = false;
    showError('Servidor não respondeu após várias tentativas. Recarregue a página e tente novamente.', () => {
        location.reload();
    });
});

async function pollStatus(jobId) {
    try {
        const data = await safeFetchJson(`/status/${jobId}`);
        if (data.status === 'processing') {
            const progress = data.progresso || 0;
            progressFill.style.width = `${progress}%`;
            progressFill.textContent = `${progress}%`;
            statusMessage.textContent = `Processando... ${progress}%`;
            setTimeout(() => pollStatus(jobId), 500);
        } else if (data.status === 'completed') {
            progressFill.style.width = '100%';
            progressFill.textContent = '100%';
            statusMessage.textContent = 'Concluído!';
            setTimeout(() => {
                progressContainer.style.display = 'none';
                showResults(data);
                downloadFile(jobId);
            }, 500);
        } else if (data.status === 'error') {
            throw { type: 'http', message: data.error || 'Erro no processamento' };
        }
    } catch (error) {
        progressContainer.style.display = 'none';
        submitBtn.disabled = false;
        showError(error.message || 'Erro ao verificar status');
    }
}

function showResults(data) {
    const resultado = data.resultado;
    resultDetails.innerHTML = `
        <div class="result-item">
            <span>Linhas originais:</span>
            <strong>${resultado.linhas_originais}</strong>
        </div>
        <div class="result-item">
            <span>Linhas processadas:</span>
            <strong>${resultado.linhas_novo}</strong>
        </div>
        <div class="result-item">
            <span>Colunas originais:</span>
            <strong>${resultado.colunas_originais}</strong>
        </div>
        <div class="result-item">
            <span>Linhas em branco removidas:</span>
            <strong>${resultado.linhas_em_branco}</strong>
        </div>
    `;
    resultContainer.style.display = 'block';
    submitBtn.disabled = false;
}

function downloadFile(jobId) {
    const link = document.createElement("a");
    link.href = `/download/${jobId}`;
    link.download = "";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function showError(message, onRetry) {
    errorContainer.innerHTML = `❌ Erro: ${message}`;
    if (onRetry) {
        const btn = document.createElement('button');
        btn.className = 'retry-btn';
        btn.textContent = 'Tentar novamente';
        btn.onclick = onRetry;
        errorContainer.appendChild(btn);
    }
    errorContainer.style.display = 'block';
}