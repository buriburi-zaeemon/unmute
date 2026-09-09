/**
 * Unmute - High Performance Client Application Logic
 * Low-latency real-time video pipeline with binary WebSocket streaming,
 * in-flight flow control, interactive 3D hand skeleton visualizer, animated sign guide,
 * color-coded 5-finger anatomy, and responsive Practice Studio.
 */

// ================= HAND SKELETON CONNECTIONS REFERENCE =================
const HAND_CONNECTIONS = [
  [0, 1], [1, 2], [2, 3], [3, 4],        // Thumb (indices 0..3)
  [0, 5], [5, 6], [6, 7], [7, 8],        // Index (indices 4..7)
  [5, 9], [9, 10], [10, 11], [11, 12],   // Middle (indices 8..11)
  [9, 13], [13, 14], [14, 15], [15, 16], // Ring (indices 12..15)
  [13, 17], [17, 18], [18, 19], [19, 20],// Pinky (indices 16..19)
  [0, 17]                                // Palm base (index 20)
];

// ================= 5-FINGER UNIQUE COLOR PALETTE =================
const FINGER_COLORS = {
  thumb: "#ff9f1c",   // Neon Amber / Gold
  index: "#00f0ff",   // Electric Cyan
  middle: "#20bf6b",  // Emerald Green
  ring: "#9b5de5",    // Royal Purple
  pinky: "#f72585",   // Hot Pink / Magenta
  palm: "rgba(220, 235, 255, 0.65)" // Ice Silver
};

// 21-element joint color mapping
const JOINT_COLORS = [
  "#e2e8f0", // 0: Wrist
  FINGER_COLORS.thumb, FINGER_COLORS.thumb, FINGER_COLORS.thumb, FINGER_COLORS.thumb,       // 1-4: Thumb
  FINGER_COLORS.index, FINGER_COLORS.index, FINGER_COLORS.index, FINGER_COLORS.index,       // 5-8: Index
  FINGER_COLORS.middle, FINGER_COLORS.middle, FINGER_COLORS.middle, FINGER_COLORS.middle,   // 9-12: Middle
  FINGER_COLORS.ring, FINGER_COLORS.ring, FINGER_COLORS.ring, FINGER_COLORS.ring,           // 13-16: Ring
  FINGER_COLORS.pinky, FINGER_COLORS.pinky, FINGER_COLORS.pinky, FINGER_COLORS.pinky       // 17-20: Pinky
];

// Bone connection colors matching the 21 bones
const CONNECTION_COLORS = [
  // Thumb: [0, 1], [1, 2], [2, 3], [3, 4]
  FINGER_COLORS.thumb, FINGER_COLORS.thumb, FINGER_COLORS.thumb, FINGER_COLORS.thumb,
  // Index: [0, 5], [5, 6], [6, 7], [7, 8]
  FINGER_COLORS.palm, FINGER_COLORS.index, FINGER_COLORS.index, FINGER_COLORS.index,
  // Middle: [5, 9], [9, 10], [10, 11], [11, 12]
  FINGER_COLORS.palm, FINGER_COLORS.middle, FINGER_COLORS.middle, FINGER_COLORS.middle,
  // Ring: [9, 13], [13, 14], [14, 15], [15, 16]
  FINGER_COLORS.palm, FINGER_COLORS.ring, FINGER_COLORS.ring, FINGER_COLORS.ring,
  // Pinky: [13, 17], [17, 18], [18, 19], [19, 20]
  FINGER_COLORS.palm, FINGER_COLORS.pinky, FINGER_COLORS.pinky, FINGER_COLORS.pinky,
  // Palm base: [0, 17]
  FINGER_COLORS.palm
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

// ================= INSTANT FALLBACK SIGN GUIDE MAP =================
// Comprehensive anatomical dictionary so Practice Studio and Inspector never show blank/generic text
const FALLBACK_SIGN_GUIDE = {
  "A": {
    sign: "A", category: "Alphabet",
    description: "Form a solid fist with all four fingers curled tightly. Rest the thumb straight upright along the outer side of the index finger.",
    tips: "Keep the thumb vertical along the index knuckle; do not fold it across the front fingers.",
    keypoints: [
      { finger: "Thumb", state: "Upright along index side" },
      { finger: "Index", state: "Curled tightly into fist" },
      { finger: "Middle", state: "Curled tightly into fist" },
      { finger: "Ring", state: "Curled tightly into fist" },
      { finger: "Pinky", state: "Curled tightly into fist" }
    ]
  },
  "B": {
    sign: "B", category: "Alphabet",
    description: "Hold all four fingers straight upright and glued together. Fold the thumb flat across the palm.",
    tips: "Keep upright fingers pressed together with zero gap, and tuck the thumb comfortably across your palm.",
    keypoints: [
      { finger: "Thumb", state: "Folded flat across palm" },
      { finger: "Index", state: "Straight upright (together)" },
      { finger: "Middle", state: "Straight upright (together)" },
      { finger: "Ring", state: "Straight upright (together)" },
      { finger: "Pinky", state: "Straight upright (together)" }
    ]
  },
  "C": {
    sign: "C", category: "Alphabet",
    description: "Curve all four fingers and thumb into an open, smooth 'C' arc like holding a cup.",
    tips: "Oppose the curved thumb to the arched fingers to form a clearly defined circular silhouette.",
    keypoints: [
      { finger: "Thumb", state: "Curved forward and upward" },
      { finger: "Index", state: "Curved downward in arc" },
      { finger: "Middle", state: "Curved downward in arc" },
      { finger: "Ring", state: "Curved downward in arc" },
      { finger: "Pinky", state: "Curved downward in arc" }
    ]
  },
  "D": {
    sign: "D", category: "Alphabet",
    description: "Extend index finger straight toward the ceiling. Curl middle, ring, and pinky down to touch the thumb tip, creating a circular loop.",
    tips: "Form an 'O' ring with middle, ring, pinky, and thumb, leaving the index finger pointing vertically.",
    keypoints: [
      { finger: "Thumb", state: "Touching middle & ring tips" },
      { finger: "Index", state: "Pointing straight upright" },
      { finger: "Middle", state: "Curled touching thumb" },
      { finger: "Ring", state: "Curled touching thumb" },
      { finger: "Pinky", state: "Curled touching thumb" }
    ]
  },
  "E": {
    sign: "E", category: "Alphabet",
    description: "Curl all four fingertips tightly downward so they rest along the top edge of the thumb tucked underneath.",
    tips: "Keep knuckles high with fingertips curled tightly downward against the thumb.",
    keypoints: [
      { finger: "Thumb", state: "Bent horizontally below tips" },
      { finger: "Index", state: "Curled down resting on thumb" },
      { finger: "Middle", state: "Curled down resting on thumb" },
      { finger: "Ring", state: "Curled down resting on thumb" },
      { finger: "Pinky", state: "Curled down resting on thumb" }
    ]
  },
  "F": {
    sign: "F", category: "Alphabet",
    description: "Touch the tips of thumb and index finger to form a round circle; extend middle, ring, and pinky straight up and fanned apart.",
    tips: "Similar to the universal 'OK' gesture; keep the remaining three fingers open and upright.",
    keypoints: [
      { finger: "Thumb", state: "Pinched touching index tip" },
      { finger: "Index", state: "Pinched touching thumb tip" },
      { finger: "Middle", state: "Straight upright fanned" },
      { finger: "Ring", state: "Straight upright fanned" },
      { finger: "Pinky", state: "Straight upright fanned" }
    ]
  },
  "G": {
    sign: "G", category: "Alphabet",
    description: "Extend index finger and thumb horizontally to the side parallel to each other like a small pinch caliper.",
    tips: "Point index finger horizontally with thumb parallel; curl middle, ring, and pinky into the palm.",
    keypoints: [
      { finger: "Thumb", state: "Extended parallel sideways" },
      { finger: "Index", state: "Extended parallel sideways" },
      { finger: "Middle", state: "Curled into palm" },
      { finger: "Ring", state: "Curled into palm" },
      { finger: "Pinky", state: "Curled into palm" }
    ]
  },
  "H": {
    sign: "H", category: "Alphabet",
    description: "Extend index and middle fingers straight horizontally side-by-side pointing sideways; thumb folded over ring.",
    tips: "Lock index and middle fingers tightly together pointing horizontally.",
    keypoints: [
      { finger: "Thumb", state: "Folded over ring finger" },
      { finger: "Index", state: "Extended horizontal sideways" },
      { finger: "Middle", state: "Extended horizontal sideways" },
      { finger: "Ring", state: "Curled into palm" },
      { finger: "Pinky", state: "Curled into palm" }
    ]
  },
  "I": {
    sign: "I", category: "Alphabet",
    description: "Extend pinky finger straight upright. Curl index, middle, and ring into a fist with thumb locked across.",
    tips: "Only the small pinky finger stands tall; keep all other fingers firmly closed.",
    keypoints: [
      { finger: "Thumb", state: "Folded across knuckles" },
      { finger: "Index", state: "Curled tightly into fist" },
      { finger: "Middle", state: "Curled tightly into fist" },
      { finger: "Ring", state: "Curled tightly into fist" },
      { finger: "Pinky", state: "Pointing straight upright" }
    ]
  },
  "J": {
    sign: "J", category: "Alphabet",
    description: "Hold the 'I' handshape (pinky up) and trace a curving 'J' swooping motion in the air with your wrist.",
    tips: "Start upright with the pinky and carve downward and inward in a smooth tracing motion.",
    keypoints: [
      { finger: "Thumb", state: "Folded across knuckles" },
      { finger: "Index", state: "Curled into fist" },
      { finger: "Middle", state: "Curled into fist" },
      { finger: "Ring", state: "Curled into fist" },
      { finger: "Pinky", state: "Upright tracing 'J' arc" }
    ]
  },
  "K": {
    sign: "K", category: "Alphabet",
    description: "Index finger points straight up, middle finger angles slightly forward, and thumb tip rests at the base of middle finger.",
    tips: "Place thumb tip between the base knuckles of index and middle fingers; middle finger tilts slightly forward.",
    keypoints: [
      { finger: "Thumb", state: "Placed between index & middle" },
      { finger: "Index", state: "Straight upright" },
      { finger: "Middle", state: "Angled slightly forward" },
      { finger: "Ring", state: "Curled into palm" },
      { finger: "Pinky", state: "Curled into palm" }
    ]
  },
  "L": {
    sign: "L", category: "Alphabet",
    description: "Extend thumb horizontally and index finger vertically to form a sharp 90-degree right angle 'L'.",
    tips: "Lock thumb fully horizontal and index finger vertical; curl remaining three fingers tightly into the palm.",
    keypoints: [
      { finger: "Thumb", state: "Extended 90° horizontal" },
      { finger: "Index", state: "Extended 90° vertical" },
      { finger: "Middle", state: "Curled into palm" },
      { finger: "Ring", state: "Curled into palm" },
      { finger: "Pinky", state: "Curled into palm" }
    ]
  },
  "M": {
    sign: "M", category: "Alphabet",
    description: "Tuck thumb underneath index, middle, and ring fingers, peeking out between ring and pinky fingers.",
    tips: "Think of the three humps of 'M'—drape index, middle, and ring fingers over the tucked thumb.",
    keypoints: [
      { finger: "Thumb", state: "Tucked under 3 fingers" },
      { finger: "Index", state: "Curled over thumb" },
      { finger: "Middle", state: "Curled over thumb" },
      { finger: "Ring", state: "Curled over thumb" },
      { finger: "Pinky", state: "Curled on side" }
    ]
  },
  "N": {
    sign: "N", category: "Alphabet",
    description: "Tuck thumb underneath index and middle fingers, peeking out between middle and ring fingers.",
    tips: "Think of the two humps of 'N'—drape index and middle fingers over the tucked thumb.",
    keypoints: [
      { finger: "Thumb", state: "Tucked under 2 fingers" },
      { finger: "Index", state: "Curled over thumb" },
      { finger: "Middle", state: "Curled over thumb" },
      { finger: "Ring", state: "Curled into palm" },
      { finger: "Pinky", state: "Curled into palm" }
    ]
  },
  "O": {
    sign: "O", category: "Alphabet",
    description: "Touch all four fingertips to the thumb tip to create a smooth circular 'O' shape.",
    tips: "Form a circular aperture with all fingertips touching the thumb tip, resembling looking through a lens.",
    keypoints: [
      { finger: "Thumb", state: "Curved touching all tips" },
      { finger: "Index", state: "Curved touching thumb tip" },
      { finger: "Middle", state: "Curved touching thumb tip" },
      { finger: "Ring", state: "Curved touching thumb tip" },
      { finger: "Pinky", state: "Curved touching thumb tip" }
    ]
  },
  "P": {
    sign: "P", category: "Alphabet",
    description: "Form the 'K' finger shape (thumb between index and middle) but tilt wrist downward so index points forward/down.",
    tips: "Hold the 'K' handshape and tilt the hand downward from the wrist.",
    keypoints: [
      { finger: "Thumb", state: "Placed between index & middle" },
      { finger: "Index", state: "Pointing forward/down" },
      { finger: "Middle", state: "Pointing downward" },
      { finger: "Ring", state: "Curled into palm" },
      { finger: "Pinky", state: "Curled into palm" }
    ]
  },
  "Q": {
    sign: "Q", category: "Alphabet",
    description: "Same caliper handshape as 'G' (index and thumb parallel) but tilted downward toward the floor.",
    tips: "Point index finger and thumb straight down like picking up a coin.",
    keypoints: [
      { finger: "Thumb", state: "Pointing downward parallel" },
      { finger: "Index", state: "Pointing downward parallel" },
      { finger: "Middle", state: "Curled into palm" },
      { finger: "Ring", state: "Curled into palm" },
      { finger: "Pinky", state: "Curled into palm" }
    ]
  },
  "R": {
    sign: "R", category: "Alphabet",
    description: "Extend index and middle fingers upright and cross middle finger tightly over the front of index finger.",
    tips: "Cross your fingers for good luck! Middle finger crosses over index; thumb folds across ring.",
    keypoints: [
      { finger: "Thumb", state: "Folded across ring finger" },
      { finger: "Index", state: "Extended upright crossed" },
      { finger: "Middle", state: "Crossed over index finger" },
      { finger: "Ring", state: "Curled into palm" },
      { finger: "Pinky", state: "Curled into palm" }
    ]
  },
  "S": {
    sign: "S", category: "Alphabet",
    description: "Clench all four fingers into a tight fist and wrap the thumb horizontally across the front knuckles.",
    tips: "Lock the thumb horizontally across the center of the fist, distinct from 'A' where thumb is alongside.",
    keypoints: [
      { finger: "Thumb", state: "Wrapped across front knuckles" },
      { finger: "Index", state: "Curled tightly into fist" },
      { finger: "Middle", state: "Curled tightly into fist" },
      { finger: "Ring", state: "Curled tightly into fist" },
      { finger: "Pinky", state: "Curled tightly into fist" }
    ]
  },
  "T": {
    sign: "T", category: "Alphabet",
    description: "Tuck thumb tip between index and middle fingers, with only the index finger curled over the thumb.",
    tips: "Only index finger drapes over thumb tip; middle, ring, and pinky remain in a fist.",
    keypoints: [
      { finger: "Thumb", state: "Tucked under index finger" },
      { finger: "Index", state: "Curled over thumb tip" },
      { finger: "Middle", state: "Curled tightly into fist" },
      { finger: "Ring", state: "Curled tightly into fist" },
      { finger: "Pinky", state: "Curled tightly into fist" }
    ]
  },
  "U": {
    sign: "U", category: "Alphabet",
    description: "Extend index and middle fingers straight upright, glued side-by-side with zero gap between them.",
    tips: "Keep index and middle fingers pressed tightly together; thumb folds across the ring finger.",
    keypoints: [
      { finger: "Thumb", state: "Folded across ring finger" },
      { finger: "Index", state: "Straight upright (glued together)" },
      { finger: "Middle", state: "Straight upright (glued together)" },
      { finger: "Ring", state: "Curled into palm" },
      { finger: "Pinky", state: "Curled into palm" }
    ]
  },
  "V": {
    sign: "V", category: "Alphabet",
    description: "Extend index and middle fingers straight upright and spread them apart in a clear 'V' shape.",
    tips: "Separate index and middle fingers like the classic peace sign; thumb folds over ring finger.",
    keypoints: [
      { finger: "Thumb", state: "Folded across ring finger" },
      { finger: "Index", state: "Straight upright (spread apart)" },
      { finger: "Middle", state: "Straight upright (spread apart)" },
      { finger: "Ring", state: "Curled into palm" },
      { finger: "Pinky", state: "Curled into palm" }
    ]
  },
  "W": {
    sign: "W", category: "Alphabet",
    description: "Extend index, middle, and ring fingers straight upright and spread evenly; thumb holds pinky tip down.",
    tips: "Spread the three middle fingers evenly to form the letter 'W'; keep thumb holding pinky down.",
    keypoints: [
      { finger: "Thumb", state: "Holding pinky tip down" },
      { finger: "Index", state: "Straight upright spread" },
      { finger: "Middle", state: "Straight upright spread" },
      { finger: "Ring", state: "Straight upright spread" },
      { finger: "Pinky", state: "Curled down under thumb" }
    ]
  },
  "X": {
    sign: "X", category: "Alphabet",
    description: "Form a fist and bend only the top joints of index finger into a distinct hooked claw.",
    tips: "Curl the index finger like a pirate's hook while keeping remaining fingers closed.",
    keypoints: [
      { finger: "Thumb", state: "Folded across ring finger" },
      { finger: "Index", state: "Bent into hooked claw" },
      { finger: "Middle", state: "Curled into palm" },
      { finger: "Ring", state: "Curled into palm" },
      { finger: "Pinky", state: "Curled into palm" }
    ]
  },
  "Y": {
    sign: "Y", category: "Alphabet",
    description: "Extend thumb and pinky finger outward as far as possible; curl index, middle, and ring into palm.",
    tips: "Like the 'hang loose' surfer gesture; keep thumb and pinky extended wide laterally.",
    keypoints: [
      { finger: "Thumb", state: "Extended wide laterally" },
      { finger: "Index", state: "Curled into palm" },
      { finger: "Middle", state: "Curled into palm" },
      { finger: "Ring", state: "Curled into palm" },
      { finger: "Pinky", state: "Extended wide laterally" }
    ]
  },
  "Z": {
    sign: "Z", category: "Alphabet",
    description: "Extend index finger forward and trace a crisp zigzag 'Z' in the air with the fingertip.",
    tips: "Use your extended index finger like a stylus to draw a 'Z' directly in front of your chest.",
    keypoints: [
      { finger: "Thumb", state: "Holding middle & ring down" },
      { finger: "Index", state: "Pointing tracing 'Z' trajectory" },
      { finger: "Middle", state: "Curled into palm" },
      { finger: "Ring", state: "Curled into palm" },
      { finger: "Pinky", state: "Curled into palm" }
    ]
  },
  "I LOVE YOU": {
    sign: "I LOVE YOU", category: "Phrase",
    description: "Extend thumb, index, and pinky fingers simultaneously; keep middle and ring fingers curled into the palm.",
    tips: "Combines the letters 'I', 'L', and 'Y' into one iconic gesture.",
    keypoints: [
      { finger: "Thumb", state: "Extended laterally" },
      { finger: "Index", state: "Straight upright" },
      { finger: "Middle", state: "Curled into palm" },
      { finger: "Ring", state: "Curled into palm" },
      { finger: "Pinky", state: "Straight upright" }
    ]
  },
  "PEACE": {
    sign: "PEACE", category: "Phrase",
    description: "Extend index and middle fingers straight upright in an open 'V' shape; curl ring and pinky under thumb.",
    tips: "Classic peace sign; keep index and middle separated and palm facing forward.",
    keypoints: [
      { finger: "Thumb", state: "Folded across ring finger" },
      { finger: "Index", state: "Straight upright (spread)" },
      { finger: "Middle", state: "Straight upright (spread)" },
      { finger: "Ring", state: "Curled into palm" },
      { finger: "Pinky", state: "Curled into palm" }
    ]
  },
  "OKAY": {
    sign: "OKAY", category: "Phrase",
    description: "Touch index fingertip and thumb tip together in an 'O' loop; extend middle, ring, and pinky straight up.",
    tips: "Keep the three upright fingers fanned out neatly with palm facing forward.",
    keypoints: [
      { finger: "Thumb", state: "Pinching index fingertip" },
      { finger: "Index", state: "Pinching thumb fingertip" },
      { finger: "Middle", state: "Straight upright" },
      { finger: "Ring", state: "Straight upright" },
      { finger: "Pinky", state: "Straight upright" }
    ]
  },
  "THUMBS UP": {
    sign: "THUMBS UP", category: "Phrase",
    description: "Make a firm fist and point the thumb straight upward toward the sky.",
    tips: "Ensure knuckles face sideways and thumb points straight toward the ceiling.",
    keypoints: [
      { finger: "Thumb", state: "Pointing straight upward" },
      { finger: "Index", state: "Curled into tight fist" },
      { finger: "Middle", state: "Curled into tight fist" },
      { finger: "Ring", state: "Curled into tight fist" },
      { finger: "Pinky", state: "Curled into tight fist" }
    ]
  },
  "STOP": {
    sign: "STOP", category: "Phrase",
    description: "Hold all five fingers fully extended with open flat palm facing forward directly toward the camera.",
    tips: "Universal stop handshape; keep fingers comfortably spread with palm pushed forward.",
    keypoints: [
      { finger: "Thumb", state: "Extended outward" },
      { finger: "Index", state: "Extended straight upright" },
      { finger: "Middle", state: "Extended straight upright" },
      { finger: "Ring", state: "Extended straight upright" },
      { finger: "Pinky", state: "Extended straight upright" }
    ]
  },
  "HELLO": {
    sign: "HELLO", category: "Phrase",
    description: "Open flat hand positioned near the temple, then saluted slightly outward and forward.",
    tips: "Friendly wave / salute motion; open hand with fingers together moving outward.",
    keypoints: [
      { finger: "Thumb", state: "Extended alongside palm" },
      { finger: "Index", state: "Straight upright flat" },
      { finger: "Middle", state: "Straight upright flat" },
      { finger: "Ring", state: "Straight upright flat" },
      { finger: "Pinky", state: "Straight upright flat" }
    ]
  },
  "THANK YOU": {
    sign: "THANK YOU", category: "Phrase",
    description: "Flat hand starts with fingertips touching the chin/lips, then gently moves outward toward the other person.",
    tips: "Extend flat hand forward with palm facing slightly upward.",
    keypoints: [
      { finger: "Thumb", state: "Extended alongside palm" },
      { finger: "Index", state: "Straight upright flat" },
      { finger: "Middle", state: "Straight upright flat" },
      { finger: "Ring", state: "Straight upright flat" },
      { finger: "Pinky", state: "Straight upright flat" }
    ]
  },
  "YES": {
    sign: "YES", category: "Phrase",
    description: "Make an 'S' fist and nod it up and down from the wrist like a head nodding yes.",
    tips: "Hold a firm fist and tilt the wrist down and back up.",
    keypoints: [
      { finger: "Thumb", state: "Folded across knuckles" },
      { finger: "Index", state: "Curled into fist" },
      { finger: "Middle", state: "Curled into fist" },
      { finger: "Ring", state: "Curled into fist" },
      { finger: "Pinky", state: "Curled into fist" }
    ]
  },
  "NO": {
    sign: "NO", category: "Phrase",
    description: "Snap index and middle fingertips down onto the thumb tip like a closing bird's beak.",
    tips: "Quick closing tap of index + middle onto thumb tip.",
    keypoints: [
      { finger: "Thumb", state: "Tapping index & middle tips" },
      { finger: "Index", state: "Tapping thumb tip" },
      { finger: "Middle", state: "Tapping thumb tip" },
      { finger: "Ring", state: "Curled into palm" },
      { finger: "Pinky", state: "Curled into palm" }
    ]
  },
  "PLEASE": {
    sign: "PLEASE", category: "Phrase",
    description: "Flat open palm rubs in a gentle clockwise circle over the center of your chest.",
    tips: "Keep fingers together with palm flat facing the chest.",
    keypoints: [
      { finger: "Thumb", state: "Extended alongside palm" },
      { finger: "Index", state: "Straight upright flat" },
      { finger: "Middle", state: "Straight upright flat" },
      { finger: "Ring", state: "Straight upright flat" },
      { finger: "Pinky", state: "Straight upright flat" }
    ]
  },
  "0": {
    sign: "0", category: "Number",
    description: "Curved open oval with all fingertips touching the thumb tip, identical to letter 'O'.",
    tips: "Form an oval zero aperture with all finger pads touching thumb pad.",
    keypoints: [
      { finger: "Thumb", state: "Curved touching tips" },
      { finger: "Index", state: "Curved touching thumb" },
      { finger: "Middle", state: "Curved touching thumb" },
      { finger: "Ring", state: "Curved touching thumb" },
      { finger: "Pinky", state: "Curved touching thumb" }
    ]
  },
  "1": {
    sign: "1", category: "Number",
    description: "Index finger pointing straight up; thumb curls over remaining curled fingers.",
    tips: "Only index finger points up; palm faces forward.",
    keypoints: [
      { finger: "Thumb", state: "Holding curled fingers" },
      { finger: "Index", state: "Straight upright" },
      { finger: "Middle", state: "Curled into palm" },
      { finger: "Ring", state: "Curled into palm" },
      { finger: "Pinky", state: "Curled into palm" }
    ]
  },
  "2": {
    sign: "2", category: "Number",
    description: "Index and middle fingers extended straight upright in a 'V' shape; palm facing forward.",
    tips: "Identical to 'V' handshape; index and middle fingers spread.",
    keypoints: [
      { finger: "Thumb", state: "Holding ring & pinky" },
      { finger: "Index", state: "Straight upright (spread)" },
      { finger: "Middle", state: "Straight upright (spread)" },
      { finger: "Ring", state: "Curled into palm" },
      { finger: "Pinky", state: "Curled into palm" }
    ]
  },
  "3": {
    sign: "3", category: "Number",
    description: "Thumb, index, and middle fingers extended; ring and pinky curled into palm.",
    tips: "ASL 3 uses thumb, index, and middle, unlike the common European gesture.",
    keypoints: [
      { finger: "Thumb", state: "Extended outward" },
      { finger: "Index", state: "Straight upright" },
      { finger: "Middle", state: "Straight upright" },
      { finger: "Ring", state: "Curled into palm" },
      { finger: "Pinky", state: "Curled into palm" }
    ]
  },
  "4": {
    sign: "4", category: "Number",
    description: "All four fingers extended straight upright and spread slightly; thumb folded flat across palm.",
    tips: "Thumb tucks firmly across the palm while four fingers stand tall.",
    keypoints: [
      { finger: "Thumb", state: "Folded flat across palm" },
      { finger: "Index", state: "Straight upright" },
      { finger: "Middle", state: "Straight upright" },
      { finger: "Ring", state: "Straight upright" },
      { finger: "Pinky", state: "Straight upright" }
    ]
  },
  "5": {
    sign: "5", category: "Number",
    description: "All five fingers extended wide with open palm facing forward.",
    tips: "Identical to 'STOP' handshape with fingers spread comfortably.",
    keypoints: [
      { finger: "Thumb", state: "Extended outward" },
      { finger: "Index", state: "Straight upright" },
      { finger: "Middle", state: "Straight upright" },
      { finger: "Ring", state: "Straight upright" },
      { finger: "Pinky", state: "Straight upright" }
    ]
  },
  "6": {
    sign: "6", category: "Number",
    description: "Thumb touches pinky fingertip; index, middle, and ring fingers extended straight up.",
    tips: "Remember: 6 touches pinky (smallest finger).",
    keypoints: [
      { finger: "Thumb", state: "Touching pinky fingertip" },
      { finger: "Index", state: "Straight upright" },
      { finger: "Middle", state: "Straight upright" },
      { finger: "Ring", state: "Straight upright" },
      { finger: "Pinky", state: "Touching thumb fingertip" }
    ]
  },
  "7": {
    sign: "7", category: "Number",
    description: "Thumb touches ring fingertip; index, middle, and pinky fingers extended straight up.",
    tips: "Remember: 7 touches ring finger.",
    keypoints: [
      { finger: "Thumb", state: "Touching ring fingertip" },
      { finger: "Index", state: "Straight upright" },
      { finger: "Middle", state: "Straight upright" },
      { finger: "Ring", state: "Touching thumb fingertip" },
      { finger: "Pinky", state: "Straight upright" }
    ]
  },
  "8": {
    sign: "8", category: "Number",
    description: "Thumb touches middle fingertip; index, ring, and pinky fingers extended straight up.",
    tips: "Remember: 8 touches middle finger.",
    keypoints: [
      { finger: "Thumb", state: "Touching middle fingertip" },
      { finger: "Index", state: "Straight upright" },
      { finger: "Middle", state: "Touching thumb fingertip" },
      { finger: "Ring", state: "Straight upright" },
      { finger: "Pinky", state: "Straight upright" }
    ]
  },
  "9": {
    sign: "9", category: "Number",
    description: "Thumb touches index fingertip (pinched circle); middle, ring, and pinky fingers extended straight up.",
    tips: "Identical to letter 'F' and 'OKAY' handshape; 9 touches index finger.",
    keypoints: [
      { finger: "Thumb", state: "Touching index fingertip" },
      { finger: "Index", state: "Touching thumb fingertip" },
      { finger: "Middle", state: "Straight upright" },
      { finger: "Ring", state: "Straight upright" },
      { finger: "Pinky", state: "Straight upright" }
    ]
  }
};

// ================= 3D CANONICAL LANDMARK GENERATOR =================
// Produces full 3D coordinates [x, y, z] for canonical ASL handshapes
function getCanonicalLandmarks(sign) {
  const s = (sign || "A").toUpperCase().trim();
  
  // Base 3D coordinates (x: 0..1, y: 0..1, z: centered depth [-0.5..0.5])
  const wrist = [0.50, 0.84, 0.0];
  const mcps = [
    [0.40, 0.72, 0.02], // Thumb CMC (1)
    [0.42, 0.52, 0.0],  // Index MCP (5)
    [0.50, 0.50, 0.0],  // Middle MCP (9)
    [0.58, 0.52, 0.0],  // Ring MCP (13)
    [0.65, 0.56, 0.0]   // Pinky MCP (17)
  ];

  function buildFinger(mcpIdx, type, spreadDx = 0) {
    const mcp = mcps[mcpIdx];
    const mx = mcp[0], my = mcp[1], mz = mcp[2];

    if (type === "up") {
      const sx = spreadDx;
      return [
        [mx, my, mz],
        [mx + sx * 0.3, my - 0.12, mz - 0.01],
        [mx + sx * 0.7, my - 0.24, mz - 0.02],
        [mx + sx * 1.0, my - 0.36, mz - 0.03]
      ];
    } else if (type === "curl") {
      return [
        [mx, my, mz],
        [mx, my + 0.03, mz + 0.07],
        [mx, my + 0.08, mz + 0.13],
        [mx, my + 0.12, mz + 0.15]
      ];
    } else if (type === "hook") {
      return [
        [mx, my, mz],
        [mx, my - 0.10, mz + 0.03],
        [mx + 0.05, my - 0.06, mz + 0.10],
        [mx + 0.04, my + 0.02, mz + 0.12]
      ];
    } else if (type === "touch_thumb") {
      return [
        [mx, my, mz],
        [mx - 0.04, my - 0.07, mz + 0.05],
        [mx - 0.08, my - 0.04, mz + 0.08],
        [0.38, 0.54, 0.10]
      ];
    } else if (type === "cross") {
      return [
        [mx, my, mz],
        [mx + 0.04, my - 0.12, mz + 0.04],
        [mx + 0.07, my - 0.24, mz + 0.06],
        [mx + 0.08, my - 0.36, mz + 0.07]
      ];
    } else if (type === "side") {
      return [
        [mx, my, mz],
        [mx - 0.10, my, mz],
        [mx - 0.20, my, mz],
        [mx - 0.28, my, mz]
      ];
    } else if (type === "down") {
      return [
        [mx, my, mz],
        [mx, my + 0.12, mz + 0.05],
        [mx, my + 0.24, mz + 0.08],
        [mx, my + 0.34, mz + 0.10]
      ];
    } else if (type === "curve") {
      return [
        [mx, my, mz],
        [mx - 0.04, my - 0.08, mz + 0.07],
        [mx - 0.08, my - 0.04, mz + 0.13],
        [mx - 0.10, my + 0.02, mz + 0.15]
      ];
    }
    return [[mx, my, mz], [mx, my - 0.1, mz], [mx, my - 0.2, mz], [mx, my - 0.3, mz]];
  }

  function buildThumb(type) {
    if (type === "side_up") { // A
      return [[0.40, 0.72, 0.02], [0.36, 0.62, 0.03], [0.35, 0.52, 0.04], [0.35, 0.42, 0.05]];
    } else if (type === "flat_across") { // B, E, 4
      return [[0.40, 0.72, 0.02], [0.46, 0.68, 0.06], [0.52, 0.66, 0.08], [0.56, 0.65, 0.09]];
    } else if (type === "extended_left") { // L, Y, ILY, STOP, 3
      return [[0.38, 0.72, 0.02], [0.28, 0.68, 0.03], [0.18, 0.65, 0.04], [0.08, 0.65, 0.04]];
    } else if (type === "thumbs_up") { // THUMBS UP
      return [[0.38, 0.70, 0.02], [0.34, 0.56, 0.03], [0.32, 0.42, 0.05], [0.30, 0.26, 0.06]];
    } else if (type === "thumbs_down") { // THUMBS DOWN, Q
      return [[0.38, 0.70, 0.02], [0.38, 0.80, 0.04], [0.38, 0.90, 0.06], [0.38, 0.98, 0.08]];
    } else if (type === "pinch_index") { // F, OKAY, 9
      return [[0.40, 0.72, 0.02], [0.38, 0.62, 0.05], [0.38, 0.54, 0.08], [0.38, 0.54, 0.09]];
    } else if (type === "curve_c") { // C
      return [[0.38, 0.72, 0.02], [0.30, 0.68, 0.06], [0.26, 0.60, 0.11], [0.28, 0.52, 0.14]];
    } else if (type === "curve_o") { // O, 0
      return [[0.38, 0.72, 0.02], [0.38, 0.62, 0.06], [0.42, 0.54, 0.10], [0.45, 0.50, 0.12]];
    } else if (type === "tuck_1") { // T
      return [[0.40, 0.72, 0.02], [0.44, 0.60, 0.05], [0.44, 0.50, 0.07], [0.45, 0.44, 0.09]];
    } else if (type === "tuck_2") { // N
      return [[0.40, 0.72, 0.02], [0.48, 0.60, 0.05], [0.52, 0.52, 0.07], [0.53, 0.46, 0.09]];
    } else if (type === "tuck_3") { // M
      return [[0.40, 0.72, 0.02], [0.52, 0.60, 0.05], [0.58, 0.54, 0.07], [0.60, 0.48, 0.09]];
    } else if (type === "across_knuckles") { // S, I, J
      return [[0.40, 0.72, 0.02], [0.46, 0.64, 0.08], [0.52, 0.62, 0.11], [0.56, 0.62, 0.12]];
    } else if (type === "between_k") { // K, P
      return [[0.40, 0.72, 0.02], [0.44, 0.60, 0.04], [0.46, 0.48, 0.06], [0.46, 0.38, 0.08]];
    } else if (type === "side_horiz") { // G
      return [[0.38, 0.70, 0.02], [0.30, 0.68, 0.03], [0.20, 0.66, 0.04], [0.12, 0.65, 0.04]];
    } else if (type === "touch_pinky") { // 6
      return [[0.40, 0.72, 0.02], [0.48, 0.65, 0.06], [0.56, 0.60, 0.09], [0.62, 0.58, 0.11]];
    } else if (type === "touch_ring") { // 7
      return [[0.40, 0.72, 0.02], [0.46, 0.62, 0.06], [0.52, 0.54, 0.09], [0.54, 0.50, 0.11]];
    } else if (type === "touch_middle") { // 8
      return [[0.40, 0.72, 0.02], [0.44, 0.60, 0.06], [0.48, 0.52, 0.09], [0.48, 0.48, 0.11]];
    }
    // Default folded
    return [[0.40, 0.72, 0.02], [0.44, 0.65, 0.06], [0.48, 0.62, 0.09], [0.50, 0.60, 0.10]];
  }

  let thumbT = "folded", idxT = "curl", midT = "curl", ringT = "curl", pnkT = "curl";
  let idxSpread = 0, midSpread = 0, ringSpread = 0, pnkSpread = 0;

  switch (s) {
    case "A": thumbT = "side_up"; break;
    case "B": thumbT = "flat_across"; idxT = midT = ringT = pnkT = "up"; break;
    case "C": thumbT = "curve_c"; idxT = midT = ringT = pnkT = "curve"; break;
    case "D": thumbT = "touch_thumb"; idxT = "up"; midT = ringT = pnkT = "touch_thumb"; break;
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

  const lms = [wrist];
  lms.push(...buildThumb(thumbT));
  lms.push(...buildFinger(1, idxT, idxSpread));
  lms.push(...buildFinger(2, midT, midSpread));
  lms.push(...buildFinger(3, ringT, ringSpread));
  lms.push(...buildFinger(4, pnkT, pnkSpread));

  return lms;
}

// Neutral relaxed open hand pose for transition animations
function getNeutralHandLandmarks() {
  const wrist = [0.50, 0.84, 0.0];
  const thumb = [
    [0.40, 0.72, 0.02],
    [0.34, 0.65, 0.03],
    [0.28, 0.60, 0.04],
    [0.22, 0.56, 0.05]
  ];
  const index = [
    [0.42, 0.52, 0.0],
    [0.40, 0.40, 0.0],
    [0.38, 0.28, 0.0],
    [0.36, 0.16, 0.0]
  ];
  const middle = [
    [0.50, 0.50, 0.0],
    [0.50, 0.38, 0.0],
    [0.50, 0.26, 0.0],
    [0.50, 0.14, 0.0]
  ];
  const ring = [
    [0.58, 0.52, 0.0],
    [0.60, 0.40, 0.0],
    [0.62, 0.28, 0.0],
    [0.64, 0.16, 0.0]
  ];
  const pinky = [
    [0.65, 0.56, 0.0],
    [0.69, 0.45, 0.0],
    [0.72, 0.35, 0.0],
    [0.75, 0.24, 0.0]
  ];
  return [wrist, ...thumb, ...index, ...middle, ...ring, ...pinky];
}

// Linear interpolation between two 3D landmark sets
function interpolate3DLandmarks(lmsA, lmsB, t) {
  if (!lmsA || !lmsB) return lmsB || lmsA;
  const clampedT = Math.max(0, Math.min(1, t));
  return lmsA.map((ptA, i) => {
    const ptB = lmsB[i] || ptA;
    return [
      ptA[0] + (ptB[0] - ptA[0]) * clampedT,
      ptA[1] + (ptB[1] - ptA[1]) * clampedT,
      (ptA[2] || 0) + ((ptB[2] || 0) - (ptA[2] || 0)) * clampedT
    ];
  });
}

// ================= 3D INTERACTIVE SKELETON RENDERER =================
// Renders canonical landmarks with true 3D perspective rotation, depth foreshortening, and unique 5-finger color coding
function renderReferenceSkeleton(canvas, signNameOrLms, options = {}) {
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const w = canvas.width;
  const h = canvas.height;

  ctx.clearRect(0, 0, w, h);

  let lms;
  let signName = "";
  if (typeof signNameOrLms === "string") {
    signName = signNameOrLms;
    lms = getCanonicalLandmarks(signNameOrLms);
  } else if (Array.isArray(signNameOrLms)) {
    lms = signNameOrLms;
    signName = options.signName || "";
  }
  if (!lms || lms.length < 21) return;

  const scale = options.scale || 0.84;
  const cx = w / 2;
  const cy = h / 2 + (options.offsetY || 8);
  const yaw = options.yaw || 0.0;     // Y-axis rotation (radians)
  const pitch = options.pitch || 0.0; // X-axis rotation (radians)

  // Camera perspective parameters
  const camDist = 1.8;
  const cosY = Math.cos(yaw);
  const sinY = Math.sin(yaw);
  const cosP = Math.cos(pitch);
  const sinP = Math.sin(pitch);

  // 3D rotation & perspective projection for each landmark
  const projPts = lms.map((pt, i) => {
    // Center point relative to palm center (0.50, 0.55, 0.0)
    const x0 = (pt[0] - 0.50);
    const y0 = (pt[1] - 0.55);
    const z0 = (pt[2] !== undefined ? pt[2] : 0.0);

    // 1. Rotate around Y axis (yaw)
    const x1 = x0 * cosY + z0 * sinY;
    const z1 = -x0 * sinY + z0 * cosY;
    const y1 = y0;

    // 2. Rotate around X axis (pitch)
    const y2 = y1 * cosP - z1 * sinP;
    const z2 = y1 * sinP + z1 * cosP;
    const x2 = x1;

    // 3. Perspective projection
    const fov = camDist / (camDist + z2);
    const px = cx + x2 * w * scale * fov;
    const py = cy + y2 * h * scale * fov;

    return {
      x: px,
      y: py,
      z: z2,
      fov: fov,
      idx: i
    };
  });

  // Base line thickness & glow
  const baseLineWidth = options.lineWidth || 3.5;
  const baseTipRadius = options.tipRadius || 6.5;
  const baseJointRadius = options.jointRadius || 3.8;

  // 1. Draw Glowing 3D Bone Connections with Finger-Specific Colors
  HAND_CONNECTIONS.forEach(([startIdx, endIdx], connIdx) => {
    const p1 = projPts[startIdx];
    const p2 = projPts[endIdx];
    if (!p1 || !p2) return;

    const avgFov = (p1.fov + p2.fov) / 2;
    const connColor = CONNECTION_COLORS[connIdx] || FINGER_COLORS.palm;

    ctx.save();
    ctx.lineWidth = Math.max(1.5, baseLineWidth * avgFov);
    ctx.strokeStyle = connColor;
    ctx.shadowColor = connColor;
    ctx.shadowBlur = (options.glowBlur !== undefined ? options.glowBlur : 10) * avgFov;
    ctx.lineCap = "round";

    ctx.beginPath();
    ctx.moveTo(p1.x, p1.y);
    ctx.lineTo(p2.x, p2.y);
    ctx.stroke();
    ctx.restore();
  });

  // 2. Draw 3D Landmark Joints & Glowing Fingertip Indicators
  // Sort joints back-to-front by depth (z) so closer joints draw on top
  const sortedIndices = projPts.map((p, idx) => idx).sort((a, b) => projPts[a].z - projPts[b].z);

  sortedIndices.forEach(idx => {
    const pt = projPts[idx];
    const isTip = [4, 8, 12, 16, 20].includes(idx);
    const jointColor = JOINT_COLORS[idx] || "#00f0ff";

    ctx.save();
    if (isTip) {
      // Fingertip Node: Outer glow aura with vibrant finger color + white core pip
      const r = Math.max(3, baseTipRadius * pt.fov);
      ctx.shadowColor = jointColor;
      ctx.shadowBlur = 12 * pt.fov;
      ctx.fillStyle = jointColor;

      ctx.beginPath();
      ctx.arc(pt.x, pt.y, r, 0, 2 * Math.PI);
      ctx.fill();

      // Inner white pip for crisp contrast
      ctx.shadowBlur = 0;
      ctx.fillStyle = "#ffffff";
      ctx.beginPath();
      ctx.arc(pt.x, pt.y, r * 0.45, 0, 2 * Math.PI);
      ctx.fill();
    } else {
      // Inner Joint Node
      const r = Math.max(2, baseJointRadius * pt.fov);
      ctx.shadowBlur = 0;
      ctx.fillStyle = jointColor;

      ctx.beginPath();
      ctx.arc(pt.x, pt.y, r, 0, 2 * Math.PI);
      ctx.fill();

      // Subtle edge ring
      ctx.lineWidth = 1;
      ctx.strokeStyle = "rgba(255, 255, 255, 0.4)";
      ctx.stroke();
    }
    ctx.restore();
  });

  // 3. Motion Indicator Trajectory for Dynamic Signs (J, Z, etc.)
  const upperSign = signName.toUpperCase().trim();
  if (["J", "Z", "HELLO", "THANK YOU", "YES", "NO", "PLEASE"].includes(upperSign)) {
    ctx.save();
    ctx.strokeStyle = "#ffe600";
    ctx.fillStyle = "#ffe600";
    ctx.lineWidth = 2.2;
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    if (upperSign === "J") {
      ctx.arc(w * 0.72, h * 0.65, 20 * scale, 0, Math.PI * 0.8);
    } else if (upperSign === "Z") {
      ctx.moveTo(w * 0.35, h * 0.25);
      ctx.lineTo(w * 0.65, h * 0.25);
      ctx.lineTo(w * 0.35, h * 0.45);
      ctx.lineTo(w * 0.65, h * 0.45);
    } else {
      ctx.moveTo(w * 0.25, h * 0.22);
      ctx.lineTo(w * 0.75, h * 0.22);
    }
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.restore();
  }
}

class UnmuteApp {
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

    // Modal Inspector & 3D Interactive Visualizer
    this.inspectorModal = document.getElementById("sign-inspector-modal");
    this.modalCloseBtn = document.getElementById("modal-close-btn");
    this.modalSignTitle = document.getElementById("modal-sign-title");
    this.modalSignCategory = document.getElementById("modal-sign-category");
    this.modalSignCanvas = document.getElementById("modal-sign-canvas");
    this.modalSignDesc = document.getElementById("modal-sign-desc");
    this.modalSignTips = document.getElementById("modal-sign-tips");
    this.btnModalPractice = document.getElementById("btn-modal-practice");
    this.btnViewPracticeGuide = document.getElementById("btn-view-practice-guide");
    this.btnModalAnimToggle = document.getElementById("btn-modal-anim-toggle");
    this.modalViewPresetBtns = document.querySelectorAll(".view-preset-btn[data-view]");
    this.modalCanvasWrapper = document.querySelector(".canvas-3d-wrapper");
    this.modalKeypointsList = document.getElementById("modal-keypoints-list");
    this.activeInspectedSign = null;

    // 3D Perspective & Animated Guide State
    this.modalYaw = 0.0;
    this.modalPitch = 0.0;
    this.isModalDragging = false;
    this.modalDragLastX = 0;
    this.modalDragLastY = 0;
    this.modalAnimActive = false;
    this.modalAnimStartTime = 0;
    this.modalAnimReqId = null;

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

    // Modal Inspector & Practice Guide Buttons
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
    if (this.btnViewPracticeGuide) {
      this.btnViewPracticeGuide.addEventListener("click", () => {
        if (this.currentPracticeItem) {
          this.openInspectorModal(this.currentPracticeItem);
        }
      });
    }

    // Initialize 3D Orbit Drag and Animation Controls
    this.initModal3DControls();

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

    const dictItem = (this.dictionaryData || []).find(d => d.sign === targetSign);
    const fallbackItem = FALLBACK_SIGN_GUIDE[targetSign];
    if (this.practiceTargetDesc) {
      if (dictItem) {
        this.practiceTargetDesc.textContent = `${dictItem.description} (Tip: ${dictItem.tips})`;
      } else if (fallbackItem) {
        this.practiceTargetDesc.textContent = `${fallbackItem.description} (Tip: ${fallbackItem.tips})`;
      } else {
        this.practiceTargetDesc.textContent = `Form the sign for '${targetSign}' clearly in front of the camera.`;
      }
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

    // Determine match score for target with canonical aliases
    let matchScore = 0;
    const target = this.currentPracticeItem;
    const pred = data.predicted_sign;

    const SIGN_ALIASES = {
      "PEACE": ["PEACE", "V", "2"],
      "V": ["V", "PEACE", "2"],
      "2": ["2", "V", "PEACE"],
      "OKAY": ["OKAY", "F", "9"],
      "F": ["F", "OKAY", "9"],
      "9": ["9", "F", "OKAY"],
      "STOP": ["STOP", "5", "B"],
      "5": ["5", "STOP"],
      "B": ["B", "4"],
      "4": ["4", "B"],
      "D": ["D", "1"],
      "1": ["1", "D"],
      "O": ["O", "0"],
      "0": ["0", "O"],
      "THUMBS UP": ["THUMBS UP", "A", "YES"]
    };

    const targetAliases = SIGN_ALIASES[target] || [target];

    if (targetAliases.includes(pred)) {
      matchScore = Math.round(data.confidence * 100);
    } else {
      const topList = data.top_predictions || [];
      const matchCandidate = topList.find(p => targetAliases.includes(p.label));
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

  // ================= 3D INTERACTIVE CONTROLS & ANIMATION =================
  initModal3DControls() {
    // 3D Angle Preset Buttons (Front, Side, Top, Isometric Orbit)
    if (this.modalViewPresetBtns) {
      this.modalViewPresetBtns.forEach(btn => {
        btn.addEventListener("click", () => {
          this.modalViewPresetBtns.forEach(b => b.classList.remove("active"));
          btn.classList.add("active");
          const view = btn.dataset.view;
          if (view === "front") {
            this.modalYaw = 0.0;
            this.modalPitch = 0.0;
          } else if (view === "side") {
            this.modalYaw = 1.35;
            this.modalPitch = 0.10;
          } else if (view === "top") {
            this.modalYaw = 0.0;
            this.modalPitch = 1.45;
          } else if (view === "isometric") {
            this.modalYaw = 0.65;
            this.modalPitch = 0.40;
          }
          this.redrawModal3D();
        });
      });
    }

    // Animation Formation Toggle
    if (this.btnModalAnimToggle) {
      this.btnModalAnimToggle.addEventListener("click", () => this.toggleModalAnimation());
    }

    // Mouse & Touch 360° Drag Orbit Handlers
    const targetEl = this.modalCanvasWrapper || this.modalSignCanvas;
    if (targetEl) {
      const onStart = (clientX, clientY) => {
        this.isModalDragging = true;
        this.modalDragLastX = clientX;
        this.modalDragLastY = clientY;
      };

      const onMove = (clientX, clientY) => {
        if (!this.isModalDragging) return;
        const dx = clientX - this.modalDragLastX;
        const dy = clientY - this.modalDragLastY;
        this.modalDragLastX = clientX;
        this.modalDragLastY = clientY;

        this.modalYaw += dx * 0.012;
        this.modalPitch = Math.max(-1.45, Math.min(1.45, this.modalPitch + dy * 0.012));

        if (this.modalViewPresetBtns) {
          this.modalViewPresetBtns.forEach(b => b.classList.remove("active"));
        }
        this.redrawModal3D();
      };

      const onEnd = () => {
        this.isModalDragging = false;
      };

      targetEl.addEventListener("mousedown", e => {
        e.preventDefault();
        onStart(e.clientX, e.clientY);
      });
      window.addEventListener("mousemove", e => {
        if (this.isModalDragging) onMove(e.clientX, e.clientY);
      });
      window.addEventListener("mouseup", onEnd);

      targetEl.addEventListener("touchstart", e => {
        if (e.touches && e.touches.length === 1) {
          onStart(e.touches[0].clientX, e.touches[0].clientY);
        }
      }, { passive: true });
      window.addEventListener("touchmove", e => {
        if (this.isModalDragging && e.touches && e.touches.length === 1) {
          onMove(e.touches[0].clientX, e.touches[0].clientY);
        }
      }, { passive: true });
      window.addEventListener("touchend", onEnd);
    }
  }

  redrawModal3D() {
    if (!this.modalSignCanvas || !this.activeInspectedSign) return;
    renderReferenceSkeleton(this.modalSignCanvas, this.activeInspectedSign, {
      scale: 0.90,
      lineWidth: 4,
      tipRadius: 7,
      jointRadius: 4.5,
      glowBlur: 14,
      yaw: this.modalYaw,
      pitch: this.modalPitch
    });
  }

  toggleModalAnimation() {
    this.modalAnimActive = !this.modalAnimActive;
    if (!this.btnModalAnimToggle) return;

    if (this.modalAnimActive) {
      this.btnModalAnimToggle.classList.add("active");
      this.btnModalAnimToggle.textContent = "⏸ Pause";
      this.modalAnimStartTime = performance.now();
      this.startModalAnimLoop();
    } else {
      this.btnModalAnimToggle.classList.remove("active");
      this.btnModalAnimToggle.textContent = "▶ Animate";
      if (this.modalAnimReqId) cancelAnimationFrame(this.modalAnimReqId);
      this.redrawModal3D();
    }
  }

  startModalAnimLoop() {
    if (!this.activeInspectedSign) return;
    const targetLms = getCanonicalLandmarks(this.activeInspectedSign);
    const neutralLms = getNeutralHandLandmarks();

    const animStep = (timestamp) => {
      if (!this.modalAnimActive || !this.inspectorModal || this.inspectorModal.style.display === "none") {
        this.modalAnimActive = false;
        if (this.btnModalAnimToggle) {
          this.btnModalAnimToggle.classList.remove("active");
          this.btnModalAnimToggle.textContent = "▶ Animate";
        }
        return;
      }

      const elapsed = timestamp - this.modalAnimStartTime;
      const cycleTime = 2600; // 2.6s total loop
      const cyclePos = elapsed % cycleTime;
      const transTime = 1800; // 1.8s forming from neutral, 0.8s hold at target

      let progress = 1.0;
      if (cyclePos < transTime) {
        const rawT = cyclePos / transTime;
        // Smooth cubic ease-in-out
        progress = rawT < 0.5 ? 4 * rawT * rawT * rawT : 1 - Math.pow(-2 * rawT + 2, 3) / 2;
      }

      const currentLms = interpolate3DLandmarks(neutralLms, targetLms, progress);

      if (this.modalSignCanvas) {
        renderReferenceSkeleton(this.modalSignCanvas, currentLms, {
          signName: this.activeInspectedSign,
          scale: 0.90,
          lineWidth: 4,
          tipRadius: 7,
          jointRadius: 4.5,
          glowBlur: 14,
          yaw: this.modalYaw,
          pitch: this.modalPitch
        });
      }

      this.modalAnimReqId = requestAnimationFrame(animStep);
    };

    this.modalAnimReqId = requestAnimationFrame(animStep);
  }

  // ================= SIGN INSPECTOR MODAL =================
  openInspectorModal(itemOrSign) {
    if (!this.inspectorModal) return;

    let sign = "";
    let category = "Alphabet";
    let description = "";
    let tips = "";
    let keypoints = null;

    if (typeof itemOrSign === "string") {
      sign = itemOrSign.toUpperCase().trim();
      const fromDict = (this.dictionaryData || []).find(d => d.sign === sign);
      const fromFallback = FALLBACK_SIGN_GUIDE[sign];

      category = (fromDict && fromDict.category) || (fromFallback && fromFallback.category) || (sign.length === 1 ? "Alphabet" : "Phrase");
      description = (fromDict && fromDict.description) || (fromFallback && fromFallback.description) || `Standard ASL sign formation for '${sign}'.`;
      tips = (fromDict && fromDict.tips) || (fromFallback && fromFallback.tips) || "Practice steady hand placement in front of the camera.";
      keypoints = fromFallback ? fromFallback.keypoints : null;
    } else if (itemOrSign && typeof itemOrSign === "object") {
      sign = (itemOrSign.sign || "").toUpperCase().trim();
      const fromFallback = FALLBACK_SIGN_GUIDE[sign];
      category = itemOrSign.category || (fromFallback && fromFallback.category) || "Alphabet";
      description = itemOrSign.description || (fromFallback && fromFallback.description) || "";
      tips = itemOrSign.tips || (fromFallback && fromFallback.tips) || "";
      keypoints = fromFallback ? fromFallback.keypoints : null;
    }

    this.activeInspectedSign = sign;

    if (this.modalSignTitle) {
      this.modalSignTitle.textContent = sign.length === 1 ? `Letter '${sign}'` : `Sign: ${sign}`;
    }
    if (this.modalSignCategory) this.modalSignCategory.textContent = category;
    if (this.modalSignDesc) this.modalSignDesc.textContent = description;
    if (this.modalSignTips) this.modalSignTips.textContent = `💡 ${tips}`;

    // Reset 3D view angles to front
    this.modalYaw = 0.0;
    this.modalPitch = 0.0;
    if (this.modalViewPresetBtns) {
      this.modalViewPresetBtns.forEach(b => {
        b.classList.toggle("active", b.dataset.view === "front");
      });
    }

    // Stop ongoing animation if active
    if (this.modalAnimActive) {
      this.modalAnimActive = false;
      if (this.modalAnimReqId) cancelAnimationFrame(this.modalAnimReqId);
    }
    if (this.btnModalAnimToggle) {
      this.btnModalAnimToggle.classList.remove("active");
      this.btnModalAnimToggle.textContent = "▶ Animate";
    }

    // Render Color-Coded 5-Finger Keypoint Badges
    if (this.modalKeypointsList) {
      this.modalKeypointsList.innerHTML = "";
      const defaultKeypoints = [
        { finger: "Thumb", state: "Positioned per sign" },
        { finger: "Index", state: "Positioned per sign" },
        { finger: "Middle", state: "Positioned per sign" },
        { finger: "Ring", state: "Positioned per sign" },
        { finger: "Pinky", state: "Positioned per sign" }
      ];
      const kps = keypoints || (FALLBACK_SIGN_GUIDE[sign] && FALLBACK_SIGN_GUIDE[sign].keypoints) || defaultKeypoints;
      const fingerColorMap = {
        "Thumb": FINGER_COLORS.thumb,
        "Index": FINGER_COLORS.index,
        "Middle": FINGER_COLORS.middle,
        "Ring": FINGER_COLORS.ring,
        "Pinky": FINGER_COLORS.pinky
      };

      kps.forEach(kp => {
        const color = fingerColorMap[kp.finger] || "#00f0ff";
        const tag = document.createElement("span");
        tag.className = "kpoint-tag";
        tag.style.borderLeft = `3px solid ${color}`;
        tag.innerHTML = `<strong style="color: ${color};">${kp.finger}:</strong> ${kp.state}`;
        this.modalKeypointsList.appendChild(tag);
      });
    }

    this.inspectorModal.style.display = "flex";
    this.redrawModal3D();
  }

  closeInspectorModal() {
    if (this.inspectorModal) {
      this.inspectorModal.style.display = "none";
    }
    if (this.modalAnimActive) {
      this.modalAnimActive = false;
      if (this.modalAnimReqId) cancelAnimationFrame(this.modalAnimReqId);
    }
    if (this.btnModalAnimToggle) {
      this.btnModalAnimToggle.classList.remove("active");
      this.btnModalAnimToggle.textContent = "▶ Animate";
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
        // If practice challenge is currently active, sync description from loaded dictionary
        if (this.currentPracticeItem && this.practiceTargetDesc) {
          const dictItem = this.dictionaryData.find(d => d.sign === this.currentPracticeItem);
          if (dictItem) {
            this.practiceTargetDesc.textContent = `${dictItem.description} (Tip: ${dictItem.tips})`;
          }
        }
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
  // ================= THEME INITIALIZATION =================
  const themeToggleBtn = document.getElementById("theme-toggle-btn");
  const themeIcon = document.getElementById("theme-icon");
  const rootElement = document.documentElement; // <html> tag
  
  // Load saved theme (default to light)
  const savedTheme = localStorage.getItem("unmute-theme") || "light";
  if (savedTheme === "dark") {
    rootElement.setAttribute("data-theme", "dark");
    if (themeIcon) themeIcon.textContent = "☀️";
  } else {
    rootElement.removeAttribute("data-theme");
    if (themeIcon) themeIcon.textContent = "🌙";
  }

  // Toggle Listener
  if (themeToggleBtn) {
    themeToggleBtn.addEventListener("click", () => {
      if (rootElement.getAttribute("data-theme") === "dark") {
        rootElement.removeAttribute("data-theme");
        localStorage.setItem("unmute-theme", "light");
        themeIcon.textContent = "🌙";
      } else {
        rootElement.setAttribute("data-theme", "dark");
        localStorage.setItem("unmute-theme", "dark");
        themeIcon.textContent = "☀️";
      }
    });
  }

  window.app = new UnmuteApp();
});
