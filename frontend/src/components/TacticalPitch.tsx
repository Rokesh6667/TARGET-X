import React from 'react';
import type { TacticalPitchSnapshot } from '../types';

interface Props {
  snapshot: TacticalPitchSnapshot | null;
  team1Color: string;
  team2Color: string;
  showTrails?: boolean;
}

export const TacticalPitch: React.FC<Props> = ({ snapshot, team1Color, team2Color }) => {
  if (!snapshot) {
    return (
      <div className="w-full h-full min-h-[360px] flex items-center justify-center bg-pitch-dark/80 rounded-xl border border-pitch-border text-slate-500 font-mono text-sm">
        No tactical data for current frame
      </div>
    );
  }

  const { players, ball, tactical_metrics } = snapshot;

  return (
    <div className="relative w-full aspect-[100/68] bg-[#143823] rounded-xl overflow-hidden border border-emerald-900/60 shadow-2xl select-none">
      {/* Pitch grass mowing stripes */}
      <div className="absolute inset-0 flex">
        {Array.from({ length: 12 }).map((_, i) => (
          <div
            key={i}
            className={`flex-1 h-full ${i % 2 === 0 ? 'bg-[#153e27]' : 'bg-[#18462c]'}`}
          />
        ))}
      </div>

      {/* SVG Pitch Markings */}
      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 68" preserveAspectRatio="none">
        {/* Outer boundary */}
        <rect x="4" y="3" width="92" height="62" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.6" />

        {/* Halfway line */}
        <line x1="50" y1="3" x2="50" y2="65" stroke="rgba(255,255,255,0.4)" strokeWidth="0.6" />

        {/* Center circle */}
        <circle cx="50" cy="34" r="9" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.6" />
        <circle cx="50" cy="34" r="0.8" fill="rgba(255,255,255,0.6)" />

        {/* Left Penalty Area */}
        <rect x="4" y="16" width="16" height="36" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.6" />
        {/* Left 6-yard Box */}
        <rect x="4" y="24" width="6" height="20" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.6" />
        {/* Left Penalty Spot */}
        <circle cx="15" cy="34" r="0.7" fill="rgba(255,255,255,0.6)" />
        {/* Left Goal Arc */}
        <path d="M 20 28 A 9 9 0 0 1 20 40" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.6" />
        {/* Left Goal */}
        <rect x="1.5" y="29.5" width="2.5" height="9" fill="rgba(255,255,255,0.15)" stroke="rgba(255,255,255,0.5)" strokeWidth="0.5" />

        {/* Right Penalty Area */}
        <rect x="80" y="16" width="16" height="36" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.6" />
        {/* Right 6-yard Box */}
        <rect x="90" y="24" width="6" height="20" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.6" />
        {/* Right Penalty Spot */}
        <circle cx="85" cy="34" r="0.7" fill="rgba(255,255,255,0.6)" />
        {/* Right Goal Arc */}
        <path d="M 80 28 A 9 9 0 0 0 80 40" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.6" />
        {/* Right Goal */}
        <rect x="96" y="29.5" width="2.5" height="9" fill="rgba(255,255,255,0.15)" stroke="rgba(255,255,255,0.5)" strokeWidth="0.5" />

        {/* Corner Arcs */}
        <path d="M 4 5 A 2 2 0 0 0 6 3" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.6" />
        <path d="M 4 63 A 2 2 0 0 1 6 65" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.6" />
        <path d="M 94 3 A 2 2 0 0 0 96 5" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.6" />
        <path d="M 94 65 A 2 2 0 0 1 96 63" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="0.6" />

        {/* Team Centroids and Compactness Spread */}
        {tactical_metrics?.team1_centroid && (
          <g opacity="0.35">
            <circle
              cx={tactical_metrics.team1_centroid[0]}
              cy={tactical_metrics.team1_centroid[1]}
              r={tactical_metrics.team1_spatial_spread || 6}
              fill={team1Color}
              fillOpacity="0.15"
              stroke={team1Color}
              strokeWidth="0.5"
              strokeDasharray="1.5,1.5"
            />
            <circle
              cx={tactical_metrics.team1_centroid[0]}
              cy={tactical_metrics.team1_centroid[1]}
              r="1.2"
              fill={team1Color}
            />
          </g>
        )}

        {tactical_metrics?.team2_centroid && (
          <g opacity="0.35">
            <circle
              cx={tactical_metrics.team2_centroid[0]}
              cy={tactical_metrics.team2_centroid[1]}
              r={tactical_metrics.team2_spatial_spread || 6}
              fill={team2Color}
              fillOpacity="0.15"
              stroke={team2Color}
              strokeWidth="0.5"
              strokeDasharray="1.5,1.5"
            />
            <circle
              cx={tactical_metrics.team2_centroid[0]}
              cy={tactical_metrics.team2_centroid[1]}
              r="1.2"
              fill={team2Color}
            />
          </g>
        )}

        {/* Players */}
        {players.map((p) => {
          const isGk = p.role === 'goalkeeper';
          const isRef = p.team === 'Referee';
          const isTeam1 = p.team === 'Team 1' || p.team === 'Portugal';
          const playerColor = isRef ? '#FFD700' : (isGk ? '#00CED1' : (isTeam1 ? team1Color : team2Color));

          return (
            <g key={p.id} className="transition-all duration-75">
              {/* Outer Glow / Halo for Goalkeeper or Ball Carrier */}
              {isGk && (
                <circle
                  cx={p.pitch_x}
                  cy={p.pitch_y}
                  r="2.8"
                  fill="none"
                  stroke="#38bdf8"
                  strokeWidth="0.6"
                  strokeDasharray="1,1"
                />
              )}

              {/* Player Dot */}
              <circle
                cx={p.pitch_x}
                cy={p.pitch_y}
                r={isGk ? '2.0' : '1.7'}
                fill={playerColor}
                stroke="#ffffff"
                strokeWidth="0.4"
                className="filter drop-shadow"
              />

              {/* Player Number / ID text */}
              <text
                x={p.pitch_x}
                y={p.pitch_y - 2.4}
                fontSize="2.0"
                fontWeight="700"
                fill="#ffffff"
                textAnchor="middle"
                className="font-mono select-none drop-shadow"
              >
                {isRef ? 'REF' : (isGk ? 'GK' : `#${p.id}`)}
              </text>
            </g>
          );
        })}

        {/* Football */}
        {ball && (
          <g>
            {/* Pulse effect */}
            <circle
              cx={ball.pitch_x}
              cy={ball.pitch_y}
              r="2.2"
              fill="none"
              stroke="#fbbf24"
              strokeWidth="0.4"
              className="animate-ping opacity-60"
            />
            {/* Ball Marker */}
            <circle
              cx={ball.pitch_x}
              cy={ball.pitch_y}
              r="1.2"
              fill="#ffffff"
              stroke="#000000"
              strokeWidth="0.4"
            />
            <circle cx={ball.pitch_x} cy={ball.pitch_y} r="0.4" fill="#000000" />
          </g>
        )}
      </svg>

      {/* Compliance Label: Tracked Image-Space Tactical View */}
      <div className="absolute top-2 left-3 px-2 py-0.5 rounded bg-black/60 border border-white/10 text-[10px] text-slate-300 font-mono tracking-wider flex items-center gap-1.5">
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
        TRACKED IMAGE-SPACE TACTICAL VIEW
      </div>

      {/* Legend overlay */}
      <div className="absolute bottom-2 right-3 px-2.5 py-1 rounded bg-black/70 border border-white/10 text-[11px] text-slate-300 font-medium flex items-center gap-3">
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full border border-white/40" style={{ backgroundColor: team1Color }} />
          <span>Team 1</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full border border-white/40" style={{ backgroundColor: team2Color }} />
          <span>Team 2</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-yellow-400" />
          <span>Ref</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-white border border-black" />
          <span>Ball</span>
        </div>
      </div>
    </div>
  );
};
