/**
 * SignBridge - High Performance Client Application Logic
 * Low-latency real-time video pipeline with binary WebSocket streaming,
 * in-flight flow control, canonical hand skeleton visualizers, and responsive Practice Studio.
 */

// ================= HAND SKELETON CONNECTIONS REFERENCE =================
const HAND_CONNECTIONS = [
  [0, 1], [1, 2], [2, 3], [3, 4],        // Thumb
  [0, 5], [5, 6], [6, 7], [7, 8],        // Index
  [5, 9], [9, 10], [10, 11], [11, 12],   // Middle
  [9, 13], [13, 14], [14, 15], [15, 16], // Ring
  [13, 17], [17, 18], [18, 19], [19, 20],// Pinky
  [0, 17]                                // Palm base
];

// ================= TOAST HELPER =================
function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  if (!container) return;
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  const icon = type === "success" ? "✅" : (type === "error" ? "❌" : "ℹ️");
  toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// ================= CANONICAL LANDMARK GENERATOR =================
function getCanonicalLandmarks(sign) {
  const s = sign.toUpperCase().trim();
  
  // Base hand dimensions (centered in 0.0 - 1.0 space)
  const wrist = [0.50, 0.84];
  const mcps = [
    [0.40, 0.72], // Thumb CMC (1)
    [0.42, 0.52], // Index MCP (5)
    [0.50, 0.50], // Middle MCP (9)
    [0.58, 0.52], // Ring MCP (13)
    [0.65, 0.56], // Pinky MCP (17)
  ];

  // Helper to build a finger's 4 joints [MCP, PIP, DIP, TIP]
  function buildFinger(mcpIdx, type, spreadDx = 0, angleDeg = 0) {
    const mcp = mcps[mcpIdx];
    const mx = mcp[0];
    const my = mcp[1];

    if (type === "up") {
      const sx = spreadDx;
      return [
        [mx, my],
        [mx + sx * 0.3, my - 0.12],
        [mx + sx * 0.7, my - 0.24],
        [mx + sx * 1.0, my - 0.36]
      ];
    } else if (type === "curl") {
      return [
        [mx, my],
        [mx, my + 0.04],
        [mx, my + 0.10],
        [mx, my + 0.14]
      ];
    } else if (type === "hook") {
      return [
        [mx, my],
        [mx, my - 0.10],
        [mx + 0.05, my - 0.06],
        [mx + 0.04, my + 0.02]
      ];
    } else if (type === "touch_thumb") {
      return [
        [mx, my],
        [mx - 0.04, my - 0.08],
        [mx - 0.08, my - 0.04],
        [0.38, 0.54] // touches thumb
      ];
    } else if (type === "cross") {
      return [
        [mx, my],
        [mx + 0.04, my - 0.12],
        [mx + 0.07, my - 0.24],
        [mx + 0.08, my - 0.36]
      ];
    } else if (type === "side") {
      return [
        [mx, my],
        [mx - 0.10, my],
        [mx - 0.20, my],
        [mx - 0.28, my]
      ];
    } else if (type === "down") {
      return [
        [mx, my],
        [mx, my + 0.12],
        [mx, my + 0.24],
        [mx, my + 0.34]
      ];
    } else if (type === "curve") {
      return [
        [mx, my],
        [mx - 0.04, my - 0.08],
        [mx - 0.08, my - 0.04],
        [mx - 0.10, my + 0.02]
      ];
    }
    return [[mx, my], [mx, my - 0.1], [mx, my - 0.2], [mx, my - 0.3]];
  }

  function buildThumb(type) {
    if (type === "side_up") { // A
      return [[0.40, 0.72], [0.36, 0.62], [0.35, 0.52], [0.35, 0.42]];
    } else if (type === "flat_across") { // B
      return [[0.40, 0.72], [0.46, 0.68], [0.52, 0.66], [0.56, 0.65]];
    } else if (type === "extended_left") { // L, Y, ILY
      return [[0.38, 0.72], [0.28, 0.68], [0.18, 0.65], [0.08, 0.65]];
    } else if (type === "thumbs_up") { // THUMBS UP
      return [[0.38, 0.70], [0.34, 0.56], [0.32, 0.42], [0.30, 0.26]];
    } else if (type === "thumbs_down") { // THUMBS DOWN
      return [[0.38, 0.70], [0.38, 0.80], [0.38, 0.90], [0.38, 0.98]];
    } else if (type === "pinch_index") { // F, OKAY, 9
      return [[0.40, 0.72], [0.38, 0.62], [0.38, 0.54], [0.38, 0.54]];
    } else if (type === "curve_c") { // C
      return [[0.38, 0.72], [0.30, 0.68], [0.26, 0.60], [0.28, 0.52]];
    } else if (type === "curve_o") { // O, 0
      return [[0.38, 0.72], [0.38, 0.62], [0.42, 0.54], [0.45, 0.50]];
    } else if (type === "tuck_1") { // T
      return [[0.40, 0.72], [0.44, 0.60], [0.44, 0.50], [0.45, 0.44]];
    } else if (type === "tuck_2") { // N
      return [[0.40, 0.72], [0.48, 0.60], [0.52, 0.52], [0.53, 0.46]];
    } else if (type === "tuck_3") { // M
      return [[0.40, 0.72], [0.52, 0.60], [0.58, 0.54], [0.60, 0.48]];
    } else if (type === "across_knuckles") { // S
      return [[0.40, 0.72], [0.46, 0.64], [0.52, 0.62], [0.56, 0.62]];
    } else if (type === "between_k") { // K, P
      return [[0.40, 0.72], [0.44, 0.60], [0.46, 0.48], [0.46, 0.38]];
    } else if (type === "side_horiz") { // G
      return [[0.38, 0.70], [0.30, 0.68], [0.20, 0.66], [0.12, 0.65]];
    } else if (type === "touch_pinky") { // 6
      return [[0.40, 0.72], [0.48, 0.65], [0.56, 0.60], [0.62, 0.58]];
    } else if (type === "touch_ring") { // 7
      return [[0.40, 0.72], [0.46, 0.62], [0.52, 0.54], [0.54, 0.50]];
    } else if (type === "touch_middle") { // 8
      return [[0.40, 0.72], [0.44, 0.60], [0.48, 0.52], [0.48, 0.48]];
    }
    // Default folded
    return [[0.40, 0.72], [0.44, 0.65], [0.48, 0.62], [0.50, 0.60]];
  }

  // Define per sign finger configurations
  let thumbT = "folded", idxT = "curl", midT = "curl", ringT = "curl", pnkT = "curl";
  let idxSpread = 0, midSpread = 0, ringSpread = 0, pnkSpread = 0;

  switch (s) {
    case "A": thumbT = "side_up"; break;
    case "B": thumbT = "flat_across"; idxT = midT = ringT = pnkT = "up"; break;
    case "C": thumbT = "curve_c"; idxT = midT = ringT = pnkT = "curve"; break;
    case "D": thumbT = "touch_index"; idxT = "up"; midT = ringT = pnkT = "touch_thumb"; break;
    case "E": thumbT = "flat_across"; idxT = midT = ringT = pnkT = "curl"; break;
    case "F": thumbT = "pinch_index"; idxT = "touch_thumb"; midT = ringT = pnkT = "up"; midSpread = -0.04; ringSpread = 0.0; pnkSpread = 0.04; break;
    case "G": thumbT = "side_horiz"; idxT = "side"; break;
    case "H": thumbT = "folded"; idxT = "side"; midT = "side"; break;
    case "I": thumbT = "across_knuckles"; pnkT = "up"; break;
    case "J": thumbT = "across_knuckles"; pnkT = "up"; break;
    case "K": thumbT = "between_k"; idxT = "up"; midT = "up"; idxSpread = -0.06; midSpread = 0.04; break;
    case "L": thumbT = "extended_left"; idxT = "up"; break;
    case "M": thumbT = "tuck_3"; break;
    case "N": thumbT = "tuck_2"; break;
    case "O": thumbT = "curve_o"; idxT = midT = ringT = pnkT = "touch_thumb"; break;
    case "P": thumbT = "between_k"; idxT = "side"; midT = "down"; break;
    case "Q": thumbT = "thumbs_down"; idxT = "down"; break;
    case "R": thumbT = "folded"; idxT = "cross"; midT = "up"; break;
    case "S": thumbT = "across_knuckles"; break;
    case "T": thumbT = "tuck_1"; break;
    case "U": thumbT = "folded"; idxT = "up"; midT = "up"; break;
    case "V": case "PEACE": thumbT = "folded"; idxT = "up"; midT = "up"; idxSpread = -0.08; midSpread = 0.08; break;
    case "W": thumbT = "folded"; idxT = "up"; midT = "up"; ringT = "up"; idxSpread = -0.08; midSpread = 0.0; ringSpread = 0.08; break;
    case "X": thumbT = "folded"; idxT = "hook"; break;
    case "Y": thumbT = "extended_left"; pnkT = "up"; pnkSpread = 0.12; break;
    case "Z": thumbT = "folded"; idxT = "up"; break;
    case "I LOVE YOU": thumbT = "extended_left"; idxT = "up"; pnkT = "up"; pnkSpread = 0.08; break;
    case "THUMBS UP": thumbT = "thumbs_up"; break;
    case "THUMBS DOWN": thumbT = "thumbs_down"; break;
    case "STOP": case "5": thumbT = "extended_left"; idxT = midT = ringT = pnkT = "up"; idxSpread = -0.08; midSpread = -0.02; ringSpread = 0.04; pnkSpread = 0.10; break;
    case "0": thumbT = "curve_o"; idxT = midT = ringT = pnkT = "touch_thumb"; break;
    case "1": thumbT = "folded"; idxT = "up"; break;
    case "2": thumbT = "folded"; idxT = "up"; midT = "up"; idxSpread = -0.06; midSpread = 0.06; break;
    case "3": thumbT = "extended_left"; idxT = "up"; midT = "up"; idxSpread = -0.04; midSpread = 0.04; break;
    case "4": thumbT = "flat_across"; idxT = midT = ringT = pnkT = "up"; idxSpread = -0.08; midSpread = -0.02; ringSpread = 0.04; pnkSpread = 0.10; break;
    case "6": thumbT = "touch_pinky"; idxT = midT = ringT = "up"; pnkT = "touch_thumb"; break;
    case "7": thumbT = "touch_ring"; idxT = midT = pnkT = "up"; ringT = "touch_thumb"; break;
    case "8": thumbT = "touch_middle"; idxT = ringT = pnkT = "up"; midT = "touch_thumb"; break;
    case "9": case "OKAY": thumbT = "pinch_index"; idxT = "touch_thumb"; midT = ringT = pnkT = "up"; break;
    case "HELLO": case "THANK YOU": case "YES": case "NO": case "PLEASE":
      thumbT = "extended_left"; idxT = midT = ringT = pnkT = "up"; break;
    default:
      thumbT = "side_up"; idxT = "up"; midT = "up"; ringT = "up"; pnkT = "up";
  }

  // Assemble full 21 landmarks
  const lms = [wrist];
  lms.push(...buildThumb(thumbT));
  lms.push(...buildFinger(1, idxT, idxSpread));
  lms.push(...buildFinger(2, midT, midSpread));
  lms.push(...buildFinger(3, ringT, ringSpread));
  lms.push(...buildFinger(4, pnkT, pnkSpread));

  return lms;
}

// ================= CANONICAL SKELETON RENDERER =================
function renderReferenceSkeleton(canvas, signName, options = {}) {
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const w = canvas.width;
  const h = canvas.height;

  ctx.clearRect(0, 0, w, h);

  const lms = getCanonicalLandmarks(signName);
  if (!lms || lms.length < 21) return;

  const scale = options.scale || 0.82;
  const cx = w / 2;
  const cy = h / 2 + (options.offsetY || 8);

  // Transform coordinates relative to canvas center
  const pts = lms.map(p => {
    return [
      cx + (p[0] - 0.50) * w * scale,
      cy + (p[1] - 0.55) * h * scale
    ];
  });

  // 1. Draw Glowing Bone Connections
  ctx.lineWidth = options.lineWidth || 3;
  ctx.strokeStyle = options.boneColor || "rgba(0, 240, 255, 0.9)";
  ctx.shadowColor = options.glowColor || "#00f0ff";
  ctx.shadowBlur = options.glowBlur || 10;

  for (const [startIdx, endIdx] of HAND_CONNECTIONS) {
    const p1 = pts[startIdx];
    const p2 = pts[endIdx];
    if (p1 && p2) {
      ctx.beginPath();
      ctx.moveTo(p1[0], p1[1]);
      ctx.lineTo(p2[0], p2[1]);
      ctx.stroke();
    }
  }

  // 2. Draw Landmark Joints & Highlighted Fingertips
  ctx.shadowBlur = 0;
  pts.forEach((pt, idx) => {
    ctx.beginPath();
    if ([4, 8, 12, 16, 20].includes(idx)) {
      // Fingertip Nodes (Hot Pink / Magenta)
      ctx.fillStyle = options.tipColor || "#f72585";
      ctx.arc(pt[0], pt[1], options.tipRadius || 5.5, 0, 2 * Math.PI);
      ctx.fill();
      ctx.lineWidth = 1.5;
      ctx.strokeStyle = "#ffffff";
      ctx.stroke();
    } else {
      // Inner Joints (Electric Cyan)
      ctx.fillStyle = options.jointColor || "#00f0ff";
      ctx.arc(pt[0], pt[1], options.jointRadius || 3.5, 0, 2 * Math.PI);
      ctx.fill();
    }
  });

  // 3. Optional Motion Indicator Arrow for Dynamic Signs (J, Z, HELLO, etc.)
  if (["J", "Z", "HELLO", "THANK YOU", "YES", "NO", "PLEASE"].includes(signName.toUpperCase())) {
    ctx.strokeStyle = "#ffe600";
    ctx.fillStyle = "#ffe600";
    ctx.lineWidth = 2;
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    if (signName.toUpperCase() === "J") {
      ctx.arc(w * 0.72, h * 0.65, 20, 0, Math.PI * 0.8);
    } else if (signName.toUpperCase() === "Z") {
      ctx.moveTo(w * 0.35, h * 0.25);
      ctx.lineTo(w * 0.65, h * 0.25);
      ctx.lineTo(w * 0.35, h * 0.45);
      ctx.lineTo(w * 0.65, h * 0.45);
    } else {
      ctx.moveTo(w * 0.25, h * 0.25);
      ctx.lineTo(w * 0.75, h * 0.25);
    }
    ctx.stroke();
    ctx.setLineDash([]);
  }
}

// ================= MAIN APPLICATION CONTROLLER =================
class SignBridgeApp {
  constructor() {
    this.activeTab = "camera-tab";
    this.isCameraRunning = false;
    this.ws = null;
    this.stream = null;
    
    // Performance & Flow Control
    this.isFrameInFlight = false;
    this.lastFrameSendTime = 0;
    this.minFrameIntervalMs = 30; // ~30 FPS network rate
    this.lastFrameTime = performance.now();
    this.frameCount = 0;
    this.fps = 0;

    // Active Render State
    this.latestLandmarks = null;
    this.hasHands = false;

    // Practice Studio State
    this.practiceScoreVal = 0;
    this.currentPracticeItem = null;
    this.practiceHoldStart = 0;
    this.isPracticeSuccess = false;
    this.practiceCtx = null;

    // Sentence Composer State
    this.composedSentence = "";
    this.lastCommittedSign = "";
    this.lastCommittedTime = 0;
    this.activeConfidenceThreshold = 0.50; // default 50% for effortless recognition

    this.initDOMElements();
    this.setupEventListeners();
    this.initDictionary();
    this.initCustomGestures();
  }

  initDOMElements() {
    this.tabButtons = document.querySelectorAll(".tab-btn");
    this.tabContents = document.querySelectorAll(".tab-content");

    // Camera Mode
    this.video = document.getElementById("webcam-video");
    this.canvas = document.getElementById("landmark-canvas");
    this.ctx = this.canvas.getContext("2d");
    this.toggleSkeleton = document.getElementById("toggle-skeleton");
    this.toggleMirror = document.getElementById("toggle-mirror");
    this.btnCameraToggle = document.getElementById("btn-camera-toggle");
    this.camToggleIcon = document.getElementById("cam-toggle-icon");
    this.cameraPlaceholder = document.getElementById("camera-placeholder");
    this.btnStartCameraPrompt = document.getElementById("btn-start-camera-prompt");
    this.sensitivitySlider = document.getElementById("sensitivity-slider");
    this.sensitivityVal = document.getElementById("sensitivity-val");

    if (this.sensitivitySlider) {
      this.sensitivitySlider.value = 50;
      if (this.sensitivityVal) this.sensitivityVal.textContent = "50%";
    }

    // Telemetry & Sentence
    this.hudFps = document.querySelector("#hud-fps .val");
    this.hudLatency = document.querySelector("#hud-latency .val");
    this.hudHand = document.querySelector("#hud-hand .val");
    this.badgeSign = document.getElementById("badge-sign");
    this.badgeConf = document.getElementById("badge-conf");
    this.badgeConfFill = document.getElementById("badge-conf-fill");
    this.badgeType = document.getElementById("badge-type");
    this.floatingBadge = document.getElementById("floating-sign-badge");
    this.composedTextEl = document.getElementById("composed-text");
    this.activeLetterBadge = document.getElementById("active-letter-badge");
    this.activeLetterConf = document.getElementById("active-letter-conf");
    this.confidenceList = document.getElementById("confidence-list");

    // Actions
    this.btnTts = document.getElementById("btn-tts");
    this.btnCopy = document.getElementById("btn-copy");
    this.btnClear = document.getElementById("btn-clear");
    this.btnAddSpace = document.getElementById("btn-add-space");
    this.btnBackspace = document.getElementById("btn-backspace");
    this.btnPeriod = document.getElementById("btn-period");

    // Video Mode
    this.uploadDropzone = document.getElementById("upload-dropzone");
    this.videoFileInput = document.getElementById("video-file-input");
    this.btnBrowseVideo = document.getElementById("btn-browse-video");
    this.processingPanel = document.getElementById("processing-panel");
    this.videoProcBar = document.getElementById("video-proc-bar");
    this.videoProcPct = document.getElementById("video-proc-pct");
    this.procStatusMsg = document.getElementById("proc-status-msg");
    this.videoPreviewWrapper = document.getElementById("video-preview-wrapper");
    this.uploadedVideoPlayer = document.getElementById("uploaded-video-player");
    this.overlaySubText = document.getElementById("overlay-sub-text");
    this.videoPlayerActions = document.getElementById("video-player-actions");
    this.btnUploadAnother = document.getElementById("btn-upload-another");
    this.btnSpeakVideoTranscript = document.getElementById("btn-speak-video-transcript");
    this.videoFullTranscript = document.getElementById("video-full-transcript");
    this.segmentsList = document.getElementById("segments-list");
    this.btnExportSrt = document.getElementById("btn-export-srt");
    this.btnExportVtt = document.getElementById("btn-export-vtt");
    this.btnExportJson = document.getElementById("btn-export-json");

    // Practice Studio
    this.practiceTargetLetter = document.getElementById("practice-target-letter");
    this.practiceTargetName = document.getElementById("practice-target-name");
    this.practiceTargetDesc = document.getElementById("practice-target-desc");
    this.practiceMatchPct = document.getElementById("practice-match-pct");
    this.practiceMatchBar = document.getElementById("practice-match-bar");
    this.practiceScore = document.getElementById("practice-score");
    this.btnSkipChallenge = document.getElementById("btn-skip-challenge");
    this.btnNextChallenge = document.getElementById("btn-next-challenge");
    this.practiceTargetCanvas = document.getElementById("practice-target-canvas");
    this.practiceVideo = document.getElementById("practice-video");
    this.practiceCanvas = document.getElementById("practice-canvas");
    if (this.practiceCanvas) {
      this.practiceCtx = this.practiceCanvas.getContext("2d");
    }
    this.practiceFeedbackBanner = document.getElementById("practice-feedback-banner");

    // Modal Inspector
    this.inspectorModal = document.getElementById("sign-inspector-modal");
    this.modalCloseBtn = document.getElementById("modal-close-btn");
    this.modalSignTitle = document.getElementById("modal-sign-title");
    this.modalSignCategory = document.getElementById("modal-sign-category");
    this.modalSignCanvas = document.getElementById("modal-sign-canvas");
    this.modalSignDesc = document.getElementById("modal-sign-desc");
    this.modalSignTips = document.getElementById("modal-sign-tips");
    this.btnModalPractice = document.getElementById("btn-modal-practice");
    this.activeInspectedSign = null;

    // Custom Trainer
    this.customGestureName = document.getElementById("custom-gesture-name");
    this.customVideo = document.getElementById("custom-video");
    this.customCanvas = document.getElementById("custom-canvas");
    this.recordCountdown = document.getElementById("record-countdown");
    this.recordingMeter = document.getElementById("recording-meter");
    this.recordSamplesCount = document.getElementById("record-samples-count");
    this.recordProgressBar = document.getElementById("record-progress-bar");
    this.btnStartRecord = document.getElementById("btn-start-record");
    this.btnTrainCustom = document.getElementById("btn-train-custom");
    this.btnRefreshCustom = document.getElementById("btn-refresh-custom");
    this.customTable = document.getElementById("custom-table");

    // Dictionary
    this.dictSearchInput = document.getElementById("dict-search-input");
    this.filterPills = document.querySelectorAll(".filter-pill");
    this.dictGrid = document.getElementById("dict-grid");

    this.activeJobId = null;
    this.videoSegments = [];
    this.customSamplesRecorded = [];
    this.dictionaryData = [];
  }

  setupEventListeners() {
    this.tabButtons.forEach(btn => {
      btn.addEventListener("click", () => this.switchTab(btn.dataset.tab));
    });

    this.btnCameraToggle.addEventListener("click", () => this.toggleCamera());
    this.btnStartCameraPrompt.addEventListener("click", () => this.startCamera());

    this.toggleMirror.addEventListener("change", (e) => {
      const isMirrored = e.target.checked;
      this.video.classList.toggle("mirrored", isMirrored);
      this.canvas.classList.toggle("mirrored", isMirrored);
    });

    this.sensitivitySlider.addEventListener("input", (e) => {
      this.activeConfidenceThreshold = e.target.value / 100;
      this.sensitivityVal.textContent = `${e.target.value}%`;
    });

    this.btnTts.addEventListener("click", () => this.speakComposedText());
    this.btnCopy.addEventListener("click", () => this.copyComposedText());
    this.btnClear.addEventListener("click", () => this.clearComposedText());
    this.btnAddSpace.addEventListener("click", () => this.appendChar(" "));
    this.btnBackspace.addEventListener("click", () => this.backspace());
    this.btnPeriod.addEventListener("click", () => this.appendChar(". "));

    this.uploadDropzone.addEventListener("click", () => this.videoFileInput.click());
    this.btnBrowseVideo.addEventListener("click", (e) => {
      e.stopPropagation();
      this.videoFileInput.click();
    });
    this.videoFileInput.addEventListener("change", (e) => this.handleVideoSelected(e));

    ["dragenter", "dragover"].forEach(evt => {
      this.uploadDropzone.addEventListener(evt, (e) => {
        e.preventDefault();
        this.uploadDropzone.classList.add("dragover");
      });
    });
    ["dragleave", "drop"].forEach(evt => {
      this.uploadDropzone.addEventListener(evt, (e) => {
        e.preventDefault();
        this.uploadDropzone.classList.remove("dragover");
      });
    });
    this.uploadDropzone.addEventListener("drop", (e) => {
      const files = e.dataTransfer.files;
      if (files.length > 0) this.uploadVideoFile(files[0]);
    });

    this.btnUploadAnother.addEventListener("click", () => this.resetVideoMode());
    this.btnSpeakVideoTranscript.addEventListener("click", () => {
      this.speakText(this.videoFullTranscript.textContent);
    });

    this.btnExportSrt.addEventListener("click", () => this.downloadSubtitle("srt"));
    this.btnExportVtt.addEventListener("click", () => this.downloadSubtitle("vtt"));
    this.btnExportJson.addEventListener("click", () => this.downloadSubtitle("json"));

    this.btnSkipChallenge.addEventListener("click", () => this.nextPracticeChallenge());
    this.btnNextChallenge.addEventListener("click", () => this.nextPracticeChallenge());

    // Modal Inspector
    if (this.modalCloseBtn) {
      this.modalCloseBtn.addEventListener("click", () => this.closeInspectorModal());
    }
    if (this.inspectorModal) {
      this.inspectorModal.addEventListener("click", (e) => {
        if (e.target === this.inspectorModal) this.closeInspectorModal();
      });
    }
    if (this.btnModalPractice) {
      this.btnModalPractice.addEventListener("click", () => {
        if (this.activeInspectedSign) {
          const sign = this.activeInspectedSign;
          this.closeInspectorModal();
          this.switchTab("practice-tab");
          this.setPracticeChallenge(sign);
        }
      });
    }

    this.btnStartRecord.addEventListener("click", () => this.startCustomRecording());
    this.btnTrainCustom.addEventListener("click", () => this.saveCustomGesture());
    this.btnRefreshCustom.addEventListener("click", () => this.initCustomGestures());

    this.dictSearchInput.addEventListener("input", () => this.filterDictionary());
    this.filterPills.forEach(pill => {
      pill.addEventListener("click", () => {
        this.filterPills.forEach(p => p.classList.remove("active"));
        pill.classList.add("active");
        this.filterDictionary();
      });
    });

    this.uploadedVideoPlayer.addEventListener("timeupdate", () => this.updateVideoSubtitleOverlay());
  }

  // ================= TAB MANAGEMENT =================
  switchTab(tabId) {
    this.activeTab = tabId;
    this.tabButtons.forEach(b => b.classList.toggle("active", b.dataset.tab === tabId));
    this.tabContents.forEach(c => c.classList.toggle("active", c.id === tabId));

    if (tabId === "camera-tab") {
      this.bindStreamToElement(this.video, this.canvas);
      if (!this.isCameraRunning) this.startCamera();
    } else if (tabId === "practice-tab") {
      this.startPracticeCamera();
      if (!this.currentPracticeItem) this.nextPracticeChallenge();
    } else if (tabId === "custom-tab") {
      this.startCustomCamera();
    }
  }

  bindStreamToElement(videoEl, canvasEl) {
    if (!videoEl) return;
    if (this.stream && videoEl.srcObject !== this.stream) {
      videoEl.srcObject = this.stream;
      videoEl.play().catch(() => {});
      if (canvasEl) {
        canvasEl.width = videoEl.videoWidth || 640;
        canvasEl.height = videoEl.videoHeight || 480;
      }
    }
  }

  // ================= LIVE CAMERA & WEBSOCKET STREAMING =================
  async startCamera() {
    if (this.isCameraRunning && this.stream) {
      this.bindStreamToElement(this.video, this.canvas);
      return;
    }
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 640 }, height: { ideal: 480 }, frameRate: { ideal: 30 } },
        audio: false,
      });
      this.video.srcObject = this.stream;
      this.video.onloadedmetadata = () => {
        this.video.play();
        this.canvas.width = this.video.videoWidth || 640;
        this.canvas.height = this.video.videoHeight || 480;
        this.isCameraRunning = true;
        this.cameraPlaceholder.style.display = "none";
        this.camToggleIcon.textContent = "⏹️";
        this.initWebSocket();
        this.startStreamingLoop();
      };
    } catch (err) {
      console.error("Camera access error:", err);
      showToast("Could not access camera. Please allow camera permissions.", "error");
    }
  }

  stopCamera() {
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
      this.stream = null;
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.isCameraRunning = false;
    this.cameraPlaceholder.style.display = "flex";
    this.camToggleIcon.textContent = "▶️";
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
  }

  toggleCamera() {
    if (this.isCameraRunning) this.stopCamera();
    else this.startCamera();
  }

  initWebSocket() {
    const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${proto}//${window.location.host}/ws/live-stream`;
    
    try {
      this.ws = new WebSocket(wsUrl);
      this.ws.binaryType = "blob";

      this.ws.onopen = () => {
        const statusEl = document.getElementById("server-status");
        if (statusEl) {
          statusEl.className = "status-indicator online";
          statusEl.querySelector(".status-label").textContent = "AI Live (WebSocket)";
        }
        this.isFrameInFlight = false;
      };

      this.ws.onmessage = (event) => {
        const roundTripLatency = Math.round(performance.now() - this.lastFrameSendTime);
        if (this.hudLatency) this.hudLatency.textContent = `${roundTripLatency}ms`;
        this.isFrameInFlight = false;

        try {
          const data = JSON.parse(event.data);
          this.handlePredictionResult(data);
        } catch (e) {
          console.error("Error parsing WS message:", e);
        }
      };

      this.ws.onclose = () => {
        const statusEl = document.getElementById("server-status");
        if (statusEl) {
          statusEl.className = "status-indicator";
          statusEl.querySelector(".status-label").textContent = "Reconnecting...";
        }
        this.isFrameInFlight = false;
        if (this.isCameraRunning) {
          setTimeout(() => this.initWebSocket(), 1500);
        }
      };
    } catch (e) {
      console.error(e);
    }
  }

  startStreamingLoop() {
    const offscreen = document.createElement("canvas");
    const offCtx = offscreen.getContext("2d");
    offscreen.width = 256;
    offscreen.height = 192;

    const render = (now) => {
      if (!this.isCameraRunning || this.activeTab !== "camera-tab") return;

      this.frameCount++;
      if (now - this.lastFrameTime >= 1000) {
        this.fps = this.frameCount;
        this.frameCount = 0;
        this.lastFrameTime = now;
        if (this.hudFps) this.hudFps.textContent = `${this.fps} FPS`;
      }

      this.drawLandmarks();

      const timeSinceLastSend = now - this.lastFrameSendTime;
      if (this.ws && this.ws.readyState === WebSocket.OPEN && !this.isFrameInFlight && timeSinceLastSend >= this.minFrameIntervalMs) {
        this.isFrameInFlight = true;
        this.lastFrameSendTime = now;

        offCtx.drawImage(this.video, 0, 0, offscreen.width, offscreen.height);
        offscreen.toBlob((blob) => {
          if (blob && this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(blob);
          } else {
            this.isFrameInFlight = false;
          }
        }, "image/jpeg", 0.50);
      }

      requestAnimationFrame(render);
    };

    requestAnimationFrame(render);
  }

  handlePredictionResult(data) {
    if (!data.has_hands) {
      this.hasHands = false;
      this.latestLandmarks = null;
      if (this.hudHand) this.hudHand.textContent = "None";
      this.floatingBadge.style.display = "none";
      this.activeLetterBadge.textContent = "_";
      this.activeLetterConf.textContent = "0%";
      return;
    }

    this.hasHands = true;
    this.latestLandmarks = data.landmarks || null;
    if (this.hudHand) this.hudHand.textContent = data.handedness || "Right";

    const sign = data.predicted_sign;
    const conf = data.confidence || 0.0;
    const isStable = data.is_stable;
    const signType = data.sign_type || "alphabet";

    if (sign && sign !== "UNKNOWN" && conf >= 0.35) {
      this.floatingBadge.style.display = "block";
      this.badgeSign.textContent = sign;
      this.badgeConf.textContent = `${Math.round(conf * 100)}%`;
      this.badgeConfFill.style.width = `${Math.round(conf * 100)}%`;
      this.badgeType.textContent = signType.toUpperCase();

      this.activeLetterBadge.textContent = sign;
      this.activeLetterConf.textContent = `${Math.round(conf * 100)}%`;

      if (data.top_predictions && data.top_predictions.length > 0) {
        this.renderConfidenceList(data.top_predictions);
      }

      if (isStable && conf >= this.activeConfidenceThreshold) {
        this.accumulateSign(sign, signType);
      }
    }
  }

  drawLandmarks() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    if (!this.toggleSkeleton.checked || !this.latestLandmarks) return;

    const w = this.canvas.width;
    const h = this.canvas.height;
    const lms = this.latestLandmarks;

    this.ctx.lineWidth = 3.5;
    this.ctx.strokeStyle = "rgba(0, 240, 255, 0.9)";
    this.ctx.shadowColor = "#00f0ff";
    this.ctx.shadowBlur = 8;

    for (const [startIdx, endIdx] of HAND_CONNECTIONS) {
      const p1 = lms[startIdx];
      const p2 = lms[endIdx];
      if (p1 && p2) {
        this.ctx.beginPath();
        this.ctx.moveTo(p1[0] * w, p1[1] * h);
        this.ctx.lineTo(p2[0] * w, p2[1] * h);
        this.ctx.stroke();
      }
    }

    this.ctx.shadowBlur = 0;
    lms.forEach((lm, idx) => {
      const x = lm[0] * w;
      const y = lm[1] * h;

      this.ctx.beginPath();
      if ([4, 8, 12, 16, 20].includes(idx)) {
        this.ctx.fillStyle = "#f72585";
        this.ctx.arc(x, y, 6.5, 0, 2 * Math.PI);
        this.ctx.fill();
        this.ctx.lineWidth = 2;
        this.ctx.strokeStyle = "#ffffff";
        this.ctx.stroke();
      } else {
        this.ctx.fillStyle = "#00f0ff";
        this.ctx.arc(x, y, 4, 0, 2 * Math.PI);
        this.ctx.fill();
      }
    });
  }

  renderConfidenceList(predictions) {
    const items = this.confidenceList.querySelectorAll(".confidence-item");
    predictions.slice(0, 3).forEach((pred, i) => {
      if (items[i]) {
        const label = pred.label || pred["label"] || "-";
        const pct = Math.round((pred.confidence || pred["confidence"] || 0) * 100);
        items[i].querySelector(".conf-label").textContent = label;
        items[i].querySelector(".conf-pct").textContent = `${pct}%`;
        items[i].querySelector(".progress-bar").style.width = `${pct}%`;
      }
    });
  }

  // ================= SENTENCE COMPOSITION & ACCUMULATOR =================
  accumulateSign(sign, signType) {
    const now = Date.now();
    if (sign === this.lastCommittedSign && now - this.lastCommittedTime < 1100) {
      return;
    }

    this.lastCommittedSign = sign;
    this.lastCommittedTime = now;

    if (sign === "SPACE") {
      this.appendChar(" ");
    } else if (sign === "BACKSPACE" || sign === "CLEAR") {
      this.backspace();
    } else if (signType === "phrase") {
      if (this.composedSentence && !this.composedSentence.endsWith(" ")) {
        this.composedSentence += " ";
      }
      this.composedSentence += sign + " ";
      this.updateSentenceUI();
    } else {
      this.appendChar(sign);
    }
  }

  appendChar(char) {
    if (this.composedSentence === "Show a sign to begin translating...") {
      this.composedSentence = "";
    }
    this.composedSentence += char;
    this.updateSentenceUI();
  }

  backspace() {
    if (this.composedSentence.length > 0) {
      this.composedSentence = this.composedSentence.slice(0, -1);
      this.updateSentenceUI();
    }
  }

  clearComposedText() {
    this.composedSentence = "";
    this.updateSentenceUI();
    showToast("Translation cleared", "info");
  }

  updateSentenceUI() {
    const display = this.composedSentence || "Show a sign to begin translating...";
    this.composedTextEl.textContent = display;
    const words = this.composedSentence.trim().split(/\s+/).filter(Boolean);
    const counter = document.getElementById("stat-words-count");
    if (counter) counter.textContent = `Words: ${words.length}`;
  }

  speakComposedText() {
    if (!this.composedSentence || this.composedSentence === "Show a sign to begin translating...") {
      showToast("No translated text to read yet!", "error");
      return;
    }
    this.speakText(this.composedSentence);
  }

  speakText(text) {
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.95;
      utterance.pitch = 1.0;
      window.speechSynthesis.speak(utterance);
      showToast("Speaking translation 🔊", "success");
    } else {
      showToast("Text-to-speech is not supported on this browser.", "error");
    }
  }

  copyComposedText() {
    if (!this.composedSentence) {
      showToast("Nothing to copy!", "error");
      return;
    }
    navigator.clipboard.writeText(this.composedSentence).then(() => {
      showToast("Copied to clipboard! 📋", "success");
    });
  }

  // ================= VIDEO FILE UPLOAD & SUBTITLES =================
  handleVideoSelected(e) {
    const file = e.target.files[0];
    if (file) this.uploadVideoFile(file);
  }

  async uploadVideoFile(file) {
    this.uploadDropzone.style.display = "none";
    this.processingPanel.style.display = "flex";
    this.videoProcBar.style.width = "0%";
    this.videoProcPct.textContent = "0%";
    this.procStatusMsg.textContent = "Uploading video file to server...";

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("/api/upload-video", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Upload failed");

      const data = await response.json();
      this.activeJobId = data.job_id;
      showToast(`Video uploaded: ${file.name}`, "success");
      this.pollVideoProgress(data.job_id);
    } catch (err) {
      console.error(err);
      showToast("Failed to upload video file.", "error");
      this.resetVideoMode();
    }
  }

  async pollVideoProgress(jobId) {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`/api/video-status/${jobId}`);
        if (!res.ok) return;
        const data = await res.json();

        const pct = Math.round(data.progress || 0);
        this.videoProcBar.style.width = `${pct}%`;
        this.videoProcPct.textContent = `${pct}%`;
        this.procStatusMsg.textContent = data.status_message || "Analyzing video frames...";

        if (data.status === "completed") {
          clearInterval(interval);
          this.loadVideoResult(jobId);
        } else if (data.status === "failed") {
          clearInterval(interval);
          showToast(`Processing error: ${data.error}`, "error");
          this.resetVideoMode();
        }
      } catch (e) {
        clearInterval(interval);
      }
    }, 500);
  }

  async loadVideoResult(jobId) {
    try {
      const res = await fetch(`/api/video-result/${jobId}`);
      if (!res.ok) throw new Error("Failed to get result");

      const data = await res.json();
      this.videoSegments = data.segments || [];

      this.processingPanel.style.display = "none";
      this.videoPreviewWrapper.style.display = "block";
      this.videoPlayerActions.style.display = "flex";

      this.uploadedVideoPlayer.src = `/api/video-file/${jobId}`;
      this.uploadedVideoPlayer.load();

      this.videoFullTranscript.textContent = data.full_transcript || "(No gestures detected)";
      this.renderSegmentsList(this.videoSegments);

      showToast("Translation complete! 🎬", "success");
    } catch (err) {
      console.error(err);
      showToast("Error retrieving video results.", "error");
    }
  }

  renderSegmentsList(segments) {
    this.segmentsList.innerHTML = "";
    if (!segments || segments.length === 0) {
      this.segmentsList.innerHTML = '<div class="empty-segments-state">No sign gestures identified in this clip.</div>';
      return;
    }

    segments.forEach(seg => {
      const row = document.createElement("div");
      row.className = "segment-row";
      row.innerHTML = `
        <span class="segment-time">${seg.start_time_srt.slice(3, 8)}</span>
        <span class="segment-text">${seg.text}</span>
        <span class="segment-conf">${Math.round(seg.confidence * 100)}%</span>
      `;
      row.addEventListener("click", () => {
        this.uploadedVideoPlayer.currentTime = seg.start_time;
        this.uploadedVideoPlayer.play();
      });
      this.segmentsList.appendChild(row);
    });
  }

  updateVideoSubtitleOverlay() {
    const curTime = this.uploadedVideoPlayer.currentTime;
    const activeSeg = this.videoSegments.find(s => curTime >= s.start_time && curTime <= s.end_time);

    if (activeSeg) {
      this.overlaySubText.textContent = activeSeg.text;
      this.overlaySubText.style.display = "inline-block";
    } else {
      this.overlaySubText.style.display = "none";
    }
  }

  resetVideoMode() {
    this.uploadDropzone.style.display = "block";
    this.processingPanel.style.display = "none";
    this.videoPreviewWrapper.style.display = "none";
    this.videoPlayerActions.style.display = "none";
    this.uploadedVideoPlayer.pause();
    this.uploadedVideoPlayer.src = "";
    this.videoFullTranscript.textContent = "Upload a video to see translation transcript.";
    this.segmentsList.innerHTML = '<div class="empty-segments-state">No segments detected yet.</div>';
    this.videoFileInput.value = "";
    this.activeJobId = null;
  }

  downloadSubtitle(format) {
    if (!this.activeJobId) {
      showToast("No processed video available to export.", "error");
      return;
    }
    window.location.href = `/api/export-subtitles/${this.activeJobId}?format=${format}`;
  }

  // ================= PRACTICE STUDIO =================
  async startPracticeCamera() {
    if (this.stream) {
      this.bindStreamToElement(this.practiceVideo, this.practiceCanvas);
      this.startPracticeLoop();
      return;
    }
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 640 }, height: { ideal: 480 }, frameRate: { ideal: 30 } },
        audio: false,
      });
      this.isCameraRunning = true;
      this.bindStreamToElement(this.practiceVideo, this.practiceCanvas);
      this.startPracticeLoop();
    } catch (err) {
      console.error("Practice camera access error:", err);
      showToast("Please allow camera access for Practice Studio.", "error");
    }
  }

  setPracticeChallenge(targetSign) {
    this.isPracticeSuccess = false;
    this.practiceHoldStart = 0;
    this.currentPracticeItem = targetSign;

    if (this.practiceTargetLetter) this.practiceTargetLetter.textContent = targetSign;
    if (this.practiceTargetName) {
      this.practiceTargetName.textContent = targetSign.length === 1 ? `Letter '${targetSign}'` : `Sign: ${targetSign}`;
    }

    const dictItem = this.dictionaryData.find(d => d.sign === targetSign);
    if (this.practiceTargetDesc) {
      this.practiceTargetDesc.textContent = dictItem 
        ? `${dictItem.description} (Tip: ${dictItem.tips})` 
        : "Form the sign clearly in front of the camera.";
    }

    if (this.practiceMatchPct) this.practiceMatchPct.textContent = "0%";
    if (this.practiceMatchBar) this.practiceMatchBar.style.width = "0%";
    if (this.practiceFeedbackBanner) this.practiceFeedbackBanner.textContent = `Form sign '${targetSign}' in camera view`;

    // Render Canonical Reference Skeleton on Target Canvas
    if (this.practiceTargetCanvas) {
      renderReferenceSkeleton(this.practiceTargetCanvas, targetSign, { scale: 0.85 });
    }
  }

  nextPracticeChallenge() {
    const alphabets = "ABCDEFGHIKLMNOPQRSTUVWXY".split("");
    const phrases = ["THANK YOU", "HELLO", "YES", "NO", "PLEASE", "I LOVE YOU", "PEACE", "OKAY", "THUMBS UP", "STOP"];
    const pool = [...alphabets, ...phrases];
    const target = pool[Math.floor(Math.random() * pool.length)];

    this.setPracticeChallenge(target);
  }

  startPracticeLoop() {
    const tempCanvas = document.createElement("canvas");
    const tempCtx = tempCanvas.getContext("2d");
    tempCanvas.width = 256;
    tempCanvas.height = 192;

    let isEvaluating = false;

    const loop = async () => {
      if (this.activeTab !== "practice-tab") return;

      if (!isEvaluating && this.currentPracticeItem && !this.isPracticeSuccess && this.practiceVideo.readyState >= 2) {
        isEvaluating = true;
        tempCtx.drawImage(this.practiceVideo, 0, 0, tempCanvas.width, tempCanvas.height);
        const base64Data = tempCanvas.toDataURL("image/jpeg", 0.50);

        try {
          const res = await fetch("/api/predict-frame", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              image_base64: base64Data,
              session_id: "practice_studio_session"
            }),
          });

          if (res.ok) {
            const data = await res.json();
            this.evaluatePracticeMatch(data);
          }
        } catch (e) {}

        isEvaluating = false;
      }

      requestAnimationFrame(loop);
    };

    requestAnimationFrame(loop);
  }

  evaluatePracticeMatch(data) {
    if (!this.practiceCtx) {
      if (this.practiceCanvas) this.practiceCtx = this.practiceCanvas.getContext("2d");
      else return;
    }

    this.practiceCtx.clearRect(0, 0, this.practiceCanvas.width, this.practiceCanvas.height);

    if (!data.has_hands || !this.currentPracticeItem) {
      this.practiceMatchPct.textContent = "0%";
      this.practiceMatchBar.style.width = "0%";
      this.practiceFeedbackBanner.textContent = "Hold hand inside camera view";
      this.practiceHoldStart = 0;
      return;
    }

    // Determine match score for target
    let matchScore = 0;
    const target = this.currentPracticeItem;
    const pred = data.predicted_sign;

    if (pred === target) {
      matchScore = Math.round(data.confidence * 100);
    } else {
      const topList = data.top_predictions || [];
      const matchCandidate = topList.find(p => p.label === target);
      if (matchCandidate) {
        matchScore = Math.round(matchCandidate.confidence * 100);
      }
    }

    // Draw Skeleton on Practice Canvas (Neon Green if >=60%, Cyan otherwise)
    if (data.landmarks) {
      this.drawPracticeLandmarks(data.landmarks, matchScore >= 60);
    }

    this.practiceMatchPct.textContent = `${matchScore}%`;
    this.practiceMatchBar.style.width = `${matchScore}%`;

    // Match verification threshold (60%)
    if (matchScore >= 60) {
      const now = performance.now();
      if (!this.practiceHoldStart) this.practiceHoldStart = now;

      const holdDuration = now - this.practiceHoldStart;
      this.practiceFeedbackBanner.textContent = `🎯 Great match! Hold for verification... (${matchScore}%)`;

      if (holdDuration >= 700 && !this.isPracticeSuccess) {
        this.isPracticeSuccess = true;
        this.practiceFeedbackBanner.textContent = `🎉 Perfect! Challenge Complete (+10 pts)!`;
        this.practiceScoreVal += 10;
        this.practiceScore.textContent = this.practiceScoreVal;
        showToast(`Correct! +10 Points (${target}) 🌟`, "success");

        setTimeout(() => this.nextPracticeChallenge(), 1400);
      }
    } else {
      this.practiceHoldStart = 0;
      if (pred && pred !== "UNKNOWN") {
        this.practiceFeedbackBanner.textContent = `Detected: '${pred}' (Target: '${target}')`;
      } else {
        this.practiceFeedbackBanner.textContent = `Target sign: '${target}'`;
      }
    }
  }

  drawPracticeLandmarks(landmarks, isMatched = false) {
    if (!this.practiceCtx || !landmarks) return;
    const w = this.practiceCanvas.width;
    const h = this.practiceCanvas.height;

    this.practiceCtx.lineWidth = 3.5;
    this.practiceCtx.strokeStyle = isMatched ? "rgba(16, 185, 129, 0.95)" : "rgba(0, 240, 255, 0.9)";
    this.practiceCtx.shadowColor = isMatched ? "#10b981" : "#00f0ff";
    this.practiceCtx.shadowBlur = 10;

    for (const [startIdx, endIdx] of HAND_CONNECTIONS) {
      const p1 = landmarks[startIdx];
      const p2 = landmarks[endIdx];
      if (p1 && p2) {
        this.practiceCtx.beginPath();
        this.practiceCtx.moveTo(p1[0] * w, p1[1] * h);
        this.practiceCtx.lineTo(p2[0] * w, p2[1] * h);
        this.practiceCtx.stroke();
      }
    }

    this.practiceCtx.shadowBlur = 0;
    landmarks.forEach((lm, idx) => {
      const x = lm[0] * w;
      const y = lm[1] * h;

      this.practiceCtx.beginPath();
      if ([4, 8, 12, 16, 20].includes(idx)) {
        this.practiceCtx.fillStyle = isMatched ? "#ffe600" : "#f72585";
        ctxCircle(this.practiceCtx, x, y, 6.5);
      } else {
        this.practiceCtx.fillStyle = isMatched ? "#10b981" : "#00f0ff";
        ctxCircle(this.practiceCtx, x, y, 4);
      }
    });

    function ctxCircle(ctx, x, y, r) {
      ctx.arc(x, y, r, 0, 2 * Math.PI);
      ctx.fill();
    }
  }

  // ================= SIGN INSPECTOR MODAL =================
  openInspectorModal(item) {
    if (!this.inspectorModal) return;
    this.activeInspectedSign = item.sign;

    this.modalSignTitle.textContent = item.sign.length === 1 ? `Letter '${item.sign}'` : `Sign: ${item.sign}`;
    this.modalSignCategory.textContent = item.category;
    this.modalSignDesc.textContent = item.description;
    this.modalSignTips.textContent = `💡 ${item.tips}`;

    this.inspectorModal.style.display = "flex";

    // Draw high-resolution reference skeleton
    if (this.modalSignCanvas) {
      renderReferenceSkeleton(this.modalSignCanvas, item.sign, {
        scale: 0.90,
        lineWidth: 4,
        tipRadius: 7,
        jointRadius: 4.5,
        glowBlur: 14
      });
    }
  }

  closeInspectorModal() {
    if (this.inspectorModal) {
      this.inspectorModal.style.display = "none";
    }
  }

  // ================= CUSTOM GESTURE TRAINER =================
  async startCustomCamera() {
    if (this.stream) {
      this.bindStreamToElement(this.customVideo, this.customCanvas);
      return;
    }
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 640 }, height: { ideal: 480 }, frameRate: { ideal: 30 } },
        audio: false,
      });
      this.isCameraRunning = true;
      this.bindStreamToElement(this.customVideo, this.customCanvas);
    } catch (e) {
      console.error(e);
    }
  }

  async startCustomRecording() {
    const name = this.customGestureName.value.trim();
    if (!name || name.length < 2) {
      showToast("Please enter a gesture name (at least 2 letters)", "error");
      return;
    }

    this.btnStartRecord.disabled = true;
    this.customSamplesRecorded = [];
    this.recordCountdown.style.display = "block";

    for (let count = 3; count > 0; count--) {
      this.recordCountdown.textContent = count;
      await new Promise(r => setTimeout(r, 800));
    }
    this.recordCountdown.style.display = "none";
    this.recordingMeter.style.display = "block";

    const tempCanvas = document.createElement("canvas");
    const tempCtx = tempCanvas.getContext("2d");
    tempCanvas.width = 256;
    tempCanvas.height = 192;

    const totalSamplesNeeded = 30;

    for (let i = 0; i < totalSamplesNeeded; i++) {
      tempCtx.drawImage(this.customVideo, 0, 0, tempCanvas.width, tempCanvas.height);
      const b64 = tempCanvas.toDataURL("image/jpeg", 0.55);

      try {
        const res = await fetch("/api/predict-frame", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ image_base64: b64 }),
        });

        if (res.ok) {
          const data = await res.json();
          if (data.has_hands && data.landmarks) {
            this.customSamplesRecorded.push(data.landmarks);
          }
        }
      } catch (e) {}

      const pct = Math.round(((i + 1) / totalSamplesNeeded) * 100);
      this.recordProgressBar.style.width = `${pct}%`;
      this.recordSamplesCount.textContent = `${this.customSamplesRecorded.length} / ${totalSamplesNeeded}`;
      await new Promise(r => setTimeout(r, 60));
    }

    this.btnStartRecord.disabled = false;
    if (this.customSamplesRecorded.length >= 10) {
      this.btnTrainCustom.disabled = false;
      showToast(`Captured ${this.customSamplesRecorded.length} frames! Click Train & Save.`, "success");
    } else {
      showToast("Hand was not clearly detected in enough frames. Please retry.", "error");
    }
  }

  async saveCustomGesture() {
    const name = this.customGestureName.value.trim().toUpperCase();
    if (!name || this.customSamplesRecorded.length < 5) return;

    try {
      const res = await fetch("/api/custom-gesture/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          gesture_name: name,
          landmarks_batch: this.customSamplesRecorded,
        }),
      });

      if (res.ok) {
        showToast(`Gesture '${name}' trained and saved! ⚡`, "success");
        this.customGestureName.value = "";
        this.btnTrainCustom.disabled = true;
        this.recordingMeter.style.display = "none";
        this.initCustomGestures();
      }
    } catch (e) {
      showToast("Failed to save custom gesture.", "error");
    }
  }

  async initCustomGestures() {
    try {
      const res = await fetch("/api/custom-gesture/list");
      if (res.ok) {
        const data = await res.json();
        this.renderCustomTable(data.gestures || []);
      }
    } catch (e) {}
  }

  renderCustomTable(gestures) {
    this.customTable.innerHTML = "";
    if (gestures.length === 0) {
      this.customTable.innerHTML = '<div class="table-empty">No custom gestures recorded yet. Record one to test!</div>';
      return;
    }

    gestures.forEach(g => {
      const row = document.createElement("div");
      row.className = "custom-row";
      row.innerHTML = `
        <span class="custom-name">${g.name}</span>
        <span class="custom-samples">${g.samples_count} samples</span>
        <button class="action-btn danger" data-name="${g.name}">🗑️ Delete</button>
      `;
      row.querySelector("button").addEventListener("click", async () => {
        await fetch(`/api/custom-gesture/${g.name}`, { method: "DELETE" });
        showToast(`Deleted ${g.name}`, "info");
        this.initCustomGestures();
      });
      this.customTable.appendChild(row);
    });
  }

  // ================= ASL DICTIONARY & GUIDE =================
  async initDictionary() {
    try {
      const res = await fetch("/api/dictionary");
      if (res.ok) {
        const data = await res.json();
        this.dictionaryData = data.dictionary || [];
        this.renderDictionary(this.dictionaryData);
      }
    } catch (e) {
      console.error(e);
    }
  }

  renderDictionary(items) {
    this.dictGrid.innerHTML = "";
    items.forEach(item => {
      const card = document.createElement("div");
      card.className = "dict-card";
      card.innerHTML = `
        <div class="dict-card-top">
          <span class="dict-sign-title">${item.sign}</span>
          <span class="dict-cat-tag">${item.category}</span>
        </div>
        <div class="dict-visualizer-box">
          <canvas class="dict-visualizer-canvas" width="130" height="130" data-sign="${item.sign}"></canvas>
          <span class="dict-vis-overlay-hint">Click to Inspect</span>
        </div>
        <p class="dict-desc">${item.description}</p>
        <p class="dict-tip">💡 ${item.tips}</p>
      `;

      // Click card to open full-screen inspector modal
      card.addEventListener("click", () => this.openInspectorModal(item));

      this.dictGrid.appendChild(card);

      // Render the canonical skeleton on the card's canvas
      const canvasEl = card.querySelector(".dict-visualizer-canvas");
      if (canvasEl) {
        renderReferenceSkeleton(canvasEl, item.sign, {
          scale: 0.82,
          lineWidth: 2.5,
          tipRadius: 4.5,
          jointRadius: 3,
          glowBlur: 6
        });
      }
    });
  }

  filterDictionary() {
    const query = (this.dictSearchInput.value || "").toLowerCase().trim();
    const activeFilterBtn = document.querySelector(".filter-pill.active");
    const activeCat = activeFilterBtn ? activeFilterBtn.dataset.filter : "all";

    const filtered = this.dictionaryData.filter(item => {
      const matchesQuery = item.sign.toLowerCase().includes(query) || item.description.toLowerCase().includes(query);
      const matchesCat = activeCat === "all" || item.category === activeCat;
      return matchesQuery && matchesCat;
    });

    this.renderDictionary(filtered);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  window.app = new SignBridgeApp();
});
