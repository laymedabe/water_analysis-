"use client";

export default function WaterBackground() {
  return (
    <div className="water-background-scene" aria-hidden="true">
      {/* Expanding Water Ripples */}
      <div className="water-ripple ripple-1"></div>
      <div className="water-ripple ripple-2"></div>
      <div className="water-ripple ripple-3"></div>

      {/* Floating Realistic Water Droplets */}
      <div className="water-droplet droplet-1">
        <svg viewBox="0 0 32 44" fill="none" className="droplet-svg">
          <path
            d="M16 2 C16 2, 2 18, 2 28 C2 35.73, 8.27 42, 16 42 C23.73 42, 30 35.73, 30 28 C30 18, 16 2, 16 2 Z"
            fill="url(#waterDropGrad1)"
            stroke="rgba(255, 255, 255, 0.4)"
            strokeWidth="0.75"
          />
          <ellipse cx="11" cy="24" rx="3.5" ry="6" transform="rotate(-28 11 24)" fill="rgba(255, 255, 255, 0.85)" />
          <circle cx="21" cy="31" r="1.5" fill="rgba(255, 255, 255, 0.6)" />
          <defs>
            <radialGradient id="waterDropGrad1" cx="35%" cy="38%" r="65%">
              <stop offset="0%" stopColor="rgba(224, 242, 254, 0.85)" />
              <stop offset="45%" stopColor="rgba(56, 189, 248, 0.45)" />
              <stop offset="85%" stopColor="rgba(14, 116, 144, 0.35)" />
              <stop offset="100%" stopColor="rgba(3, 105, 161, 0.6)" />
            </radialGradient>
          </defs>
        </svg>
      </div>

      <div className="water-droplet droplet-2">
        <svg viewBox="0 0 32 44" fill="none" className="droplet-svg">
          <path
            d="M16 2 C16 2, 2 18, 2 28 C2 35.73, 8.27 42, 16 42 C23.73 42, 30 35.73, 30 28 C30 18, 16 2, 16 2 Z"
            fill="url(#waterDropGrad2)"
            stroke="rgba(255, 255, 255, 0.35)"
            strokeWidth="0.75"
          />
          <ellipse cx="11" cy="24" rx="3" ry="5.5" transform="rotate(-28 11 24)" fill="rgba(255, 255, 255, 0.8)" />
          <circle cx="20" cy="30" r="1.3" fill="rgba(255, 255, 255, 0.5)" />
          <defs>
            <radialGradient id="waterDropGrad2" cx="30%" cy="35%" r="70%">
              <stop offset="0%" stopColor="rgba(240, 249, 255, 0.9)" />
              <stop offset="50%" stopColor="rgba(56, 189, 248, 0.5)" />
              <stop offset="100%" stopColor="rgba(2, 132, 199, 0.65)" />
            </radialGradient>
          </defs>
        </svg>
      </div>

      <div className="water-droplet droplet-3">
        <svg viewBox="0 0 32 44" fill="none" className="droplet-svg">
          <path
            d="M16 2 C16 2, 2 18, 2 28 C2 35.73, 8.27 42, 16 42 C23.73 42, 30 35.73, 30 28 C30 18, 16 2, 16 2 Z"
            fill="url(#waterDropGrad3)"
            stroke="rgba(255, 255, 255, 0.3)"
            strokeWidth="0.75"
          />
          <ellipse cx="11" cy="24" rx="2.5" ry="4.5" transform="rotate(-28 11 24)" fill="rgba(255, 255, 255, 0.75)" />
          <defs>
            <radialGradient id="waterDropGrad3" cx="35%" cy="35%" r="65%">
              <stop offset="0%" stopColor="rgba(240, 249, 255, 0.8)" />
              <stop offset="55%" stopColor="rgba(14, 165, 233, 0.4)" />
              <stop offset="100%" stopColor="rgba(12, 74, 110, 0.5)" />
            </radialGradient>
          </defs>
        </svg>
      </div>

      <div className="water-droplet droplet-4">
        <svg viewBox="0 0 32 44" fill="none" className="droplet-svg">
          <path
            d="M16 2 C16 2, 2 18, 2 28 C2 35.73, 8.27 42, 16 42 C23.73 42, 30 35.73, 30 28 C30 18, 16 2, 16 2 Z"
            fill="url(#waterDropGrad1)"
            stroke="rgba(255, 255, 255, 0.35)"
            strokeWidth="0.75"
          />
          <ellipse cx="11" cy="24" rx="3.5" ry="6" transform="rotate(-28 11 24)" fill="rgba(255, 255, 255, 0.8)" />
        </svg>
      </div>

      <div className="water-droplet droplet-5">
        <svg viewBox="0 0 32 44" fill="none" className="droplet-svg">
          <path
            d="M16 2 C16 2, 2 18, 2 28 C2 35.73, 8.27 42, 16 42 C23.73 42, 30 35.73, 30 28 C30 18, 16 2, 16 2 Z"
            fill="url(#waterDropGrad2)"
            stroke="rgba(255, 255, 255, 0.3)"
            strokeWidth="0.75"
          />
          <ellipse cx="11" cy="24" rx="2" ry="4" transform="rotate(-28 11 24)" fill="rgba(255, 255, 255, 0.85)" />
        </svg>
      </div>

      <div className="water-droplet droplet-6">
        <svg viewBox="0 0 32 44" fill="none" className="droplet-svg">
          <path
            d="M16 2 C16 2, 2 18, 2 28 C2 35.73, 8.27 42, 16 42 C23.73 42, 30 35.73, 30 28 C30 18, 16 2, 16 2 Z"
            fill="url(#waterDropGrad3)"
            stroke="rgba(255, 255, 255, 0.35)"
            strokeWidth="0.75"
          />
          <ellipse cx="11" cy="24" rx="2.8" ry="5" transform="rotate(-28 11 24)" fill="rgba(255, 255, 255, 0.8)" />
        </svg>
      </div>

      {/* Rising Ambient Water Bubbles */}
      <div className="water-bubble bubble-1"></div>
      <div className="water-bubble bubble-2"></div>
      <div className="water-bubble bubble-3"></div>
      <div className="water-bubble bubble-4"></div>
      <div className="water-bubble bubble-5"></div>
      <div className="water-bubble bubble-6"></div>
      <div className="water-bubble bubble-7"></div>
      <div className="water-bubble bubble-8"></div>
    </div>
  );
}
