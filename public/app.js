const homeView = document.querySelector("#homeView");
const galleryView = document.querySelector("#galleryView");
const folderGrid = document.querySelector("#folderGrid");
const imageGrid = document.querySelector("#imageGrid");
const refreshFolders = document.querySelector("#refreshFolders");
const backButton = document.querySelector("#backButton");
const reportButton = document.querySelector("#reportButton");
const reportBackButton = document.querySelector("#reportBackButton");
const galleryTitle = document.querySelector("#galleryTitle");
const galleryCount = document.querySelector("#galleryCount");
const fileInput = document.querySelector("#fileInput");
const uploadStatus = document.querySelector("#uploadStatus");
const addPhotoControl = fileInput.closest(".add-button");
const homePhotoCard = document.querySelector("#homePhotoCard");
const homePhoto = document.querySelector("#homePhoto");
const homePhotoLabel = document.querySelector("#homePhotoLabel");
const installButton = document.querySelector("#installButton");
const modeStatus = document.querySelector("#modeStatus");
const reportView = document.querySelector("#reportView");
const reportIntro = document.querySelector("#reportIntro");
const reportStats = document.querySelector("#reportStats");
const sizeReport = document.querySelector("#sizeReport");
const groupReport = document.querySelector("#groupReport");
const summaryTable = document.querySelector("#summaryTable");
const detailToggleButton = document.querySelector("#detailToggleButton");
const detailPanel = document.querySelector("#detailPanel");
const detailTable = document.querySelector("#detailTable");
const lightbox = document.querySelector("#lightbox");
const lightboxImage = document.querySelector("#lightboxImage");
const lightboxCaption = document.querySelector("#lightboxCaption");
const closeLightbox = document.querySelector("#closeLightbox");
const prevImage = document.querySelector("#prevImage");
const nextImage = document.querySelector("#nextImage");

let currentFolder = "";
let currentImages = [];
let currentImageIndex = 0;
let deferredInstallPrompt = null;
let detailVisible = false;
let catalogCache = null;
let appConfig = {
  mode: "local",
  dataSource: "api",
  readOnly: false,
  apiBaseUrl: "",
  catalogUrl: "catalog.json",
};

function formatCount(count) {
  if (count === 0) return "Nenhuma foto";
  if (count === 1) return "1 foto";
  return `${count} fotos`;
}

function setLoading(target, text) {
  target.innerHTML = `<div class="loading-state">${text}</div>`;
}

function friendlyName(name) {
  return name.replaceAll("_", " ").replace(/\.[^.]+$/, "");
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (character) => {
    const entities = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;",
    };
    return entities[character];
  });
}

function assetUrl(path) {
  return new URL(path, document.baseURI).toString();
}

function isStaticMode() {
  return appConfig.dataSource === "catalog" || appConfig.mode === "static";
}

function isReadOnlyMode() {
  return Boolean(appConfig.readOnly) || isStaticMode();
}

function apiUrl(path) {
  return `${appConfig.apiBaseUrl || ""}${path}`;
}

function applyAppMode() {
  document.body.dataset.appMode = appConfig.mode || "local";

  if (addPhotoControl) {
    addPhotoControl.hidden = isReadOnlyMode();
  }

  if (!modeStatus) return;
  if (isReadOnlyMode()) {
    modeStatus.textContent =
      "Versao online: somente visualizacao. Para adicionar ou renomear, use o app local no Docker.";
    modeStatus.hidden = false;
  } else {
    modeStatus.hidden = true;
  }
}

async function loadAppConfig() {
  try {
    const response = await fetch(assetUrl("app-config.json"));
    if (!response.ok) return;
    const config = await response.json();
    appConfig = { ...appConfig, ...config };
  } catch (error) {
    appConfig = { ...appConfig, mode: "local", dataSource: "api", readOnly: false };
  } finally {
    applyAppMode();
  }
}

async function requestJson(url, options) {
  const response = await fetch(url, options);
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.error || "Nao consegui carregar agora.");
  }
  return payload;
}

async function requestApiJson(path, options) {
  return requestJson(apiUrl(path), options);
}

async function loadCatalog() {
  if (catalogCache) return catalogCache;
  catalogCache = await requestJson(assetUrl(appConfig.catalogUrl || "catalog.json"));
  return catalogCache;
}

async function loadStaticFolders() {
  const catalog = await loadCatalog();
  return (catalog.folders || []).map((folder) => ({
    name: folder.name,
    count: folder.count,
    preview: folder.preview,
  }));
}

async function loadStaticFolder(folderName) {
  const catalog = await loadCatalog();
  return (catalog.folders || []).find((folder) => folder.name === folderName);
}

function showReadOnlyMessage() {
  uploadStatus.textContent =
    "Versao online: edicoes ficam disponiveis apenas no app local do Docker.";
}

function isStandaloneMode() {
  return window.matchMedia("(display-mode: standalone)").matches || navigator.standalone;
}

function setupPwaInstall() {
  if (!installButton || isStandaloneMode()) {
    if (installButton) installButton.hidden = true;
    return;
  }

  installButton.hidden = false;

  window.addEventListener("beforeinstallprompt", (event) => {
    event.preventDefault();
    deferredInstallPrompt = event;
    installButton.hidden = false;
  });

  window.addEventListener("appinstalled", () => {
    deferredInstallPrompt = null;
    installButton.hidden = true;
  });

  installButton.addEventListener("click", async () => {
    if (deferredInstallPrompt) {
      deferredInstallPrompt.prompt();
      const choice = await deferredInstallPrompt.userChoice;
      deferredInstallPrompt = null;
      if (choice.outcome === "accepted") installButton.hidden = true;
      return;
    }

    alert(
      "No celular, use o menu do navegador e escolha Adicionar a tela inicial. Para instalacao PWA completa pela rede local, use HTTPS ou localhost.",
    );
  });
}

function registerServiceWorker() {
  if (!("serviceWorker" in navigator) || !window.isSecureContext) return;

  window.addEventListener("load", () => {
    navigator.serviceWorker.register("sw.js").catch(() => {});
  });
}

async function loadFolders() {
  setLoading(folderGrid, "Carregando pastinhas...");
  try {
    const folders = isStaticMode()
      ? await loadStaticFolders()
      : (await requestApiJson("/api/folders")).folders || [];
    renderHomePhoto(folders);
    renderFolders(folders);
  } catch (error) {
    folderGrid.innerHTML = `<div class="empty-state">${error.message}</div>`;
  }
}

function showHome() {
  currentFolder = "";
  currentImages = [];
  fileInput.value = "";
  uploadStatus.textContent = "";
  galleryView.hidden = true;
  reportView.hidden = true;
  homeView.hidden = false;
  history.replaceState(null, "", location.pathname);
  loadFolders();
}

function renderHomePhoto(folders) {
  const folder = folders.find((item) => item.preview);
  if (!folder) {
    homePhotoCard.hidden = true;
    return;
  }

  homePhoto.onload = () => {
    homePhotoCard.hidden = false;
  };
  homePhoto.onerror = () => {
    homePhotoCard.hidden = true;
  };
  homePhoto.alt = `Previa da pasta ${folder.name}`;
  homePhoto.src = folder.preview;
  homePhotoLabel.textContent = `${folder.name} - ${formatCount(folder.count)}`;
}

function renderFolders(folders) {
  if (!folders.length) {
    folderGrid.innerHTML =
      '<div class="empty-state">Crie pastas dentro de Roupinhas para elas aparecerem aqui.</div>';
    return;
  }

  folderGrid.innerHTML = folders
    .map((folder) => {
      const folderName = escapeHtml(folder.name);
      const previewUrl = escapeHtml(folder.preview || "");
      const preview = folder.preview
        ? `<img src="${previewUrl}" alt="Previa da pasta ${folderName}" loading="eager" decoding="async" />`
        : `<div class="folder-placeholder">${escapeHtml(folder.name.slice(0, 2))}</div>`;

      return `
        <button class="folder-card" type="button" data-folder="${folderName}">
          <div class="folder-preview">${preview}</div>
          <div class="folder-info">
            <h3>${folderName}</h3>
            <p>${formatCount(folder.count)}</p>
          </div>
        </button>
      `;
    })
    .join("");
}

async function openFolder(folderName, options = {}) {
  currentFolder = folderName;
  galleryTitle.textContent = folderName;
  galleryCount.textContent = "";
  if (!options.preserveStatus) uploadStatus.textContent = "";
  imageGrid.innerHTML = "";
  homeView.hidden = true;
  reportView.hidden = true;
  galleryView.hidden = false;
  setLoading(imageGrid, "Abrindo as roupinhas...");

  try {
    const payload = isStaticMode()
      ? await loadStaticFolder(folderName)
      : await requestApiJson(`/api/folders/${encodeURIComponent(folderName)}`);
    if (!payload) throw new Error("Pasta nao encontrada.");
    currentImages = payload.images || [];
    renderImages();
    history.replaceState(null, "", `#${encodeURIComponent(folderName)}`);
  } catch (error) {
    imageGrid.innerHTML = `<div class="empty-state">${error.message}</div>`;
  }
}

function renderImages() {
  galleryCount.textContent = formatCount(currentImages.length);
  if (!currentImages.length) {
    imageGrid.innerHTML =
      '<div class="empty-state">Ainda nao tem foto nessa pastinha.</div>';
    return;
  }

  imageGrid.innerHTML = currentImages
    .map(
      (image, index) => {
        const label = escapeHtml(image.label || friendlyName(image.name));
        const url = escapeHtml(image.url);
        return `
        <article class="image-card">
          <button class="image-photo-button" type="button" data-index="${index}">
            <img src="${url}" alt="${label}" loading="lazy" />
            <span>${label}</span>
          </button>
          ${
            isReadOnlyMode()
              ? ""
              : `<div class="card-actions">
                  <button class="rename-button" type="button" data-rename-index="${index}">
                    Renomear
                  </button>
                </div>`
          }
        </article>
      `;
      },
    )
    .join("");
}

function backHome() {
  showHome();
}

async function uploadSelectedFile() {
  const file = fileInput.files[0];
  if (!file || !currentFolder) return;
  if (isReadOnlyMode()) {
    fileInput.value = "";
    showReadOnlyMessage();
    return;
  }

  uploadStatus.textContent = "Enviando foto...";
  const formData = new FormData();
  formData.append("image", file);

  try {
    await requestApiJson(`/api/folders/${encodeURIComponent(currentFolder)}/upload`, {
      method: "POST",
      body: formData,
    });
    uploadStatus.textContent = "Foto adicionada.";
    fileInput.value = "";
    await openFolder(currentFolder, { preserveStatus: true });
  } catch (error) {
    uploadStatus.textContent = error.message;
  }
}

async function openReport() {
  currentFolder = "";
  currentImages = [];
  detailVisible = false;
  detailPanel.hidden = true;
  detailToggleButton.textContent = "Ver detalhado";
  homeView.hidden = true;
  galleryView.hidden = true;
  reportView.hidden = false;
  history.replaceState(null, "", "#relatorio");
  reportIntro.textContent = "Carregando...";
  reportStats.innerHTML = "";
  sizeReport.innerHTML = "";
  groupReport.innerHTML = "";
  summaryTable.innerHTML = "";
  detailTable.innerHTML = "";

  try {
    const report = isStaticMode()
      ? (await loadCatalog()).report
      : await requestApiJson("/api/report");
    renderReport(report || {});
  } catch (error) {
    reportIntro.textContent = error.message;
  }
}

function renderStat(value, label) {
  return `
    <div class="stat-card">
      <strong>${escapeHtml(value)}</strong>
      <span>${escapeHtml(label)}</span>
    </div>
  `;
}

function renderMiniBars(items, target) {
  if (!items.length) {
    target.innerHTML = '<div class="empty-state">Sem dados.</div>';
    return;
  }

  const max = Math.max(...items.map((item) => Number(item.quantity) || 0), 1);
  target.innerHTML = items
    .map((item) => {
      const quantity = Number(item.quantity) || 0;
      const width = Math.max(4, Math.round((quantity / max) * 100));
      return `
        <div class="mini-bar">
          <span>${escapeHtml(item.name)}</span>
          <div class="mini-bar-track">
            <div class="mini-bar-fill" style="width: ${width}%"></div>
          </div>
          <strong>${quantity}</strong>
        </div>
      `;
    })
    .join("");
}

function renderTable(table, columns, rows) {
  if (!rows.length) {
    table.innerHTML = "";
    return;
  }

  const header = columns
    .map((column) => `<th scope="col">${escapeHtml(column.label)}</th>`)
    .join("");
  const body = rows
    .map(
      (row) => `
        <tr>
          ${columns.map((column) => `<td>${escapeHtml(row[column.key] || "")}</td>`).join("")}
        </tr>
      `,
    )
    .join("");

  table.innerHTML = `<thead><tr>${header}</tr></thead><tbody>${body}</tbody>`;
}

function renderReport(report) {
  const totals = report.totals || {};
  const summary = report.summary || [];
  const details = report.details || [];

  reportIntro.textContent = `${formatCount(totals.classified || 0)} classificadas em ${totals.folders || 0} pastas.`;
  reportStats.innerHTML = [
    renderStat(totals.images || 0, "imagens no disco"),
    renderStat(totals.classified || 0, "itens classificados"),
    renderStat(totals.folders || 0, "pastas"),
    renderStat(totals.groups || 0, "grupos"),
  ].join("");

  renderMiniBars(report.bySize || [], sizeReport);
  renderMiniBars(report.byGroup || [], groupReport);
  renderTable(
    summaryTable,
    [
      { key: "tamanho_pasta", label: "Tamanho" },
      { key: "grupo", label: "Grupo" },
      { key: "tipo_classificacao", label: "Tipo" },
      { key: "quantidade", label: "Qtd" },
    ],
    summary,
  );
  renderTable(
    detailTable,
    [
      { key: "arquivo", label: "Arquivo" },
      { key: "tamanho_pasta", label: "Pasta" },
      { key: "tamanho_identificado", label: "Tamanho" },
      { key: "grupo", label: "Grupo" },
      { key: "tipo_classificacao", label: "Tipo" },
      { key: "subtipo", label: "Subtipo" },
      { key: "cor_predominante", label: "Cor" },
      { key: "estampa_ou_detalhes", label: "Detalhes" },
      { key: "confianca", label: "Conf." },
    ],
    details,
  );
}

async function renameImage(index) {
  const image = currentImages[index];
  if (!image || !currentFolder) return;
  if (isReadOnlyMode()) {
    showReadOnlyMessage();
    return;
  }

  const currentLabel = image.label || friendlyName(image.name);
  const requestedName = prompt("Novo nome da foto:", currentLabel);
  if (requestedName === null) return;

  const newName = requestedName.trim();
  if (!newName) {
    uploadStatus.textContent = "Digite um nome para renomear a foto.";
    return;
  }

  uploadStatus.textContent = "Renomeando foto...";
  try {
    await requestApiJson(`/api/folders/${encodeURIComponent(currentFolder)}/rename`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        oldName: image.name,
        newName,
      }),
    });
    uploadStatus.textContent = "Foto renomeada.";
    await openFolder(currentFolder, { preserveStatus: true });
  } catch (error) {
    uploadStatus.textContent = error.message;
  }
}

function openLightbox(index) {
  const image = currentImages[index];
  if (!image) return;

  currentImageIndex = index;
  lightboxImage.src = image.url;
  lightboxImage.alt = image.label || friendlyName(image.name);
  lightboxCaption.textContent = image.label || friendlyName(image.name);
  lightbox.hidden = false;
  document.body.style.overflow = "hidden";
}

function closeLightboxView() {
  lightbox.hidden = true;
  lightboxImage.removeAttribute("src");
  document.body.style.overflow = "";
}

function moveLightbox(direction) {
  if (!currentImages.length) return;
  const nextIndex =
    (currentImageIndex + direction + currentImages.length) % currentImages.length;
  openLightbox(nextIndex);
}

folderGrid.addEventListener("click", (event) => {
  const card = event.target.closest("[data-folder]");
  if (!card) return;
  openFolder(card.dataset.folder);
});

imageGrid.addEventListener("click", (event) => {
  const renameButton = event.target.closest("[data-rename-index]");
  if (renameButton) {
    renameImage(Number(renameButton.dataset.renameIndex));
    return;
  }

  const photoButton = event.target.closest("[data-index]");
  if (!photoButton) return;
  openLightbox(Number(photoButton.dataset.index));
});

refreshFolders.addEventListener("click", loadFolders);
backButton.addEventListener("click", backHome);
reportButton.addEventListener("click", openReport);
reportBackButton.addEventListener("click", backHome);
fileInput.addEventListener("change", uploadSelectedFile);
closeLightbox.addEventListener("click", closeLightboxView);
prevImage.addEventListener("click", () => moveLightbox(-1));
nextImage.addEventListener("click", () => moveLightbox(1));
detailToggleButton.addEventListener("click", () => {
  detailVisible = !detailVisible;
  detailPanel.hidden = !detailVisible;
  detailToggleButton.textContent = detailVisible ? "Ocultar detalhado" : "Ver detalhado";
});

lightbox.addEventListener("click", (event) => {
  if (event.target === lightbox) closeLightboxView();
});

document.addEventListener("keydown", (event) => {
  if (lightbox.hidden) return;
  if (event.key === "Escape") closeLightboxView();
  if (event.key === "ArrowLeft") moveLightbox(-1);
  if (event.key === "ArrowRight") moveLightbox(1);
});

async function startApp() {
  await loadAppConfig();
  await loadFolders();
  const initialHash = decodeURIComponent(location.hash.replace(/^#/, ""));
  if (initialHash === "relatorio") {
    openReport();
    return;
  }
  if (initialHash) openFolder(initialHash);
}

setupPwaInstall();
registerServiceWorker();
startApp();
