const cameraButton = document.getElementById("camera-button");
const uploadButton = document.getElementById("upload-button");
const calibrationButton = document.getElementById("calibracao");
const fileInput = document.getElementById("file-input");
const actionFeedback = document.getElementById("action-feedback");
const statusBadge = document.getElementById("status-badge");
const resultSeason = document.getElementById("result-season");
const resultToneDetail = document.getElementById("result-tone-detail");
const resultDescription = document.getElementById("result-description");
const resultImage = document.getElementById("result-image");
const criteriaList = document.getElementById("criteria-list");
const imgGauss = document.getElementById("img-gauss");
const imgLand = document.getElementById("img-landmarks");
const imgSeg = document.getElementById("img-segmentacao");

const setLoadingState = (isLoading, message) => {
  cameraButton.disabled = isLoading;
  uploadButton.disabled = isLoading;
  calibrationButton.disabled = isLoading;
  statusBadge.textContent = isLoading ? "Processando..." : "Analise concluida";
  actionFeedback.textContent = message;
};

const resetErrorState = (message) => {
  cameraButton.disabled = false;
  uploadButton.disabled = false;
  calibrationButton.disabled = false;
  statusBadge.textContent = "Falha na analise";
  actionFeedback.textContent = message;
};

const toBase64 = (file) =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(new Error("Nao foi possivel ler o arquivo selecionado."));
    reader.readAsDataURL(file);
  });

const renderCriteria = (criterios) => {
  const items = [];

  if (Array.isArray(criterios.partes_analisadas)) {
    items.push(`Partes analisadas: ${criterios.partes_analisadas.join(", ")}.`);
  }

  if (Array.isArray(criterios.metodo)) {
    criterios.metodo.forEach((metodo) => items.push(metodo));
  }

  if (criterios.subtom_identificado) {
    items.push(`Subtom identificado: ${criterios.subtom_identificado}.`);
  }

  criteriaList.innerHTML = "";
  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    criteriaList.appendChild(li);
  });
};

const renderResult = (resultado) => {
  resultSeason.textContent = resultado.tom_principal || "Resultado indisponivel";
  if (resultToneDetail) {
    resultToneDetail.textContent = resultado.tom_detectado || "Classificacao detalhada indisponivel.";
  }
  if (resultDescription) {
    resultDescription.textContent = resultado.informacoes_estacao || "Nao foi possivel carregar a descricao.";
  }

  if (resultado.imagem_exibicao_data_url) {
    resultImage.src = resultado.imagem_exibicao_data_url;
  } else if (resultado.imagem_exibicao_base64) {
    resultImage.src = `data:image/png;base64,${resultado.imagem_exibicao_base64}`;
  }

  if (resultado.criterios_decisao) {
    renderCriteria(resultado.criterios_decisao);
  }

  document.getElementById("resultado").scrollIntoView({ behavior: "smooth", block: "start" });
};

const renderEtapas = (etapas) => {
  if (!etapas) return;

  if (imgGauss && etapas.gaussiano) {
    imgGauss.src = "data:image/jpeg;base64," + etapas.gaussiano;
  }

  if (imgLand && etapas.landmarks) {
    imgLand.src = "data:image/jpeg;base64," + etapas.landmarks;
  }

  if (imgSeg && etapas.segmentacao){
    imgSeg.src = "data:image/jpeg;base64," + etapas.segmentacao;
  }
};

const handleApiError = async (response) => {
  let detail = "Nao foi possivel concluir a analise.";
  try {
    const data = await response.json();
    detail = data.detail || detail;
  } catch (error) {
    detail = `${detail} Tente novamente.`;
  }
  throw new Error(detail);
};

const runCameraAnalysis = async () => {
  setLoadingState(true, "Abrindo a webcam e aguardando a captura da imagem...");

  try {
    const response = await fetch("/api/analise", { method: "POST" });
    if (!response.ok) {
      await handleApiError(response);
    }

    const data = await response.json();
    renderEtapas(data.etapas);
    renderResult(data.resultado);
    setLoadingState(false, "Análise por câmera concluída com sucesso.");
  } catch (error) {
    resetErrorState(error.message);
  }
};

const runColorCheck = async (file) => {
  setLoadingState(true, "Convertendo a imagem e enviando para análise...");

  try {
    const imagemBase64 = await toBase64(file);
    const response = await fetch("/api/check_cores", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ imagem_base64: imagemBase64 }),
    });

    if (!response.ok) {
      await handleApiError(response);
    }
    setLoadingState(false, "Calibração feita !");
  } catch (error) {
    resetErrorState(error.message);
  }
};

const runUploadAnalysis = async (file) => {
  setLoadingState(true, "Convertendo a imagem e enviando para análise...");

  try {
    const imagemBase64 = await toBase64(file);
    const response = await fetch("/api/analise_upload", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ imagem_base64: imagemBase64 }),
    });

    if (!response.ok) {
      await handleApiError(response);
    }

    const data = await response.json();
    renderEtapas(data.etapas);
    renderResult(data.resultado);
    setLoadingState(false, `Analise concluida para o arquivo ${file.name}.`);
  } catch (error) {
    resetErrorState(error.message);
  }
};

let flag = null;
cameraButton.addEventListener("click", runCameraAnalysis);

uploadButton.addEventListener("click", () => {
  flag = "upload";
  fileInput.click();
});

calibrationButton.addEventListener("click", () => {
  flag = "calibracao";
  fileInput.click();
});

fileInput.addEventListener("change", async (event) => {
  const [file] = event.target.files;
  if (!file) return;

  if (flag === "calibracao") {
    await runColorCheck(file);
  } else if (flag === "upload") {
    await runUploadAnalysis(file);
  }

  fileInput.value = "";
});