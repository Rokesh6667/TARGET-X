import React, { useState, useRef, useEffect } from 'react';

interface Props {
  heatmaps: {
    grid_dimensions: { width: number; height: number };
    team1_heatmap: number[][];
    team2_heatmap: number[][];
    player_heatmaps: Record<string, number[][]>;
  } | null;
  team1Color: string;
  team2Color: string;
}

export const HeatmapView: React.FC<Props> = ({ heatmaps }) => {
  const [selectedMode, setSelectedMode] = useState<'team1' | 'team2' | 'player'>('team1');
  const [selectedPlayer, setSelectedPlayer] = useState<string>('');
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  const playerKeys = React.useMemo(
    () => (heatmaps?.player_heatmaps ? Object.keys(heatmaps.player_heatmaps) : []),
    [heatmaps]
  );
  const activePlayer = selectedPlayer || (playerKeys.length > 0 ? playerKeys[0] : '');

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !heatmaps) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let grid: number[][] = [];
    if (selectedMode === 'team1') {
      grid = heatmaps.team1_heatmap;
    } else if (selectedMode === 'team2') {
      grid = heatmaps.team2_heatmap;
    } else if (selectedMode === 'player' && activePlayer) {
      grid = heatmaps.player_heatmaps[activePlayer] || [];
    }

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (!grid || grid.length === 0) return;

    const rows = grid.length;
    const cols = grid[0].length;
    const cellW = canvas.width / cols;
    const cellH = canvas.height / rows;

    // Draw heat cells with alpha blending
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const val = grid[r][c];
        if (val > 0.05) {
          // Heat color scale: Blue -> Cyan -> Green -> Yellow -> Red
          const hue = (1.0 - val) * 240; // 240 (blue) to 0 (red)
          ctx.fillStyle = `hsla(${hue}, 100%, 50%, ${Math.min(0.85, val * 1.2)})`;
          ctx.fillRect(c * cellW, r * cellH, cellW + 1, cellH + 1);
        }
      }
    }
  }, [heatmaps, selectedMode, activePlayer]);

  if (!heatmaps) {
    return (
      <div className="p-8 text-center text-slate-500 font-mono text-sm">
        Heatmap data unavailable. Run analysis to compute spatial movement density.
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      {/* Mode Selectors */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex rounded-lg bg-pitch-dark p-1 border border-pitch-border text-xs">
          <button
            onClick={() => setSelectedMode('team1')}
            className={`px-3 py-1.5 rounded-md font-medium transition ${
              selectedMode === 'team1' ? 'bg-cyan-600 text-white shadow' : 'text-slate-400 hover:text-white'
            }`}
          >
            Team 1 Heatmap
          </button>
          <button
            onClick={() => setSelectedMode('team2')}
            className={`px-3 py-1.5 rounded-md font-medium transition ${
              selectedMode === 'team2' ? 'bg-cyan-600 text-white shadow' : 'text-slate-400 hover:text-white'
            }`}
          >
            Team 2 Heatmap
          </button>
          <button
            onClick={() => setSelectedMode('player')}
            className={`px-3 py-1.5 rounded-md font-medium transition ${
              selectedMode === 'player' ? 'bg-cyan-600 text-white shadow' : 'text-slate-400 hover:text-white'
            }`}
          >
            Individual Player
          </button>
        </div>

        {selectedMode === 'player' && playerKeys.length > 0 && (
          <select
            value={activePlayer}
            onChange={(e) => setSelectedPlayer(e.target.value)}
            className="px-3 py-1.5 rounded-lg bg-pitch-dark border border-pitch-border text-xs text-white focus:outline-none focus:border-cyan-400"
          >
            {playerKeys.map((k) => (
              <option key={k} value={k}>
                {k.replace('player_', 'Player #')}
              </option>
            ))}
          </select>
        )}
      </div>

      {/* Heatmap Canvas over Pitch */}
      <div className="relative w-full aspect-[100/68] bg-[#0c2215] rounded-xl overflow-hidden border border-emerald-900/60 shadow-xl">
        {/* Pitch boundary and lines watermark */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none opacity-30" viewBox="0 0 100 68">
          <rect x="4" y="3" width="92" height="62" fill="none" stroke="#ffffff" strokeWidth="0.6" />
          <line x1="50" y1="3" x2="50" y2="65" stroke="#ffffff" strokeWidth="0.6" />
          <circle cx="50" cy="34" r="9" fill="none" stroke="#ffffff" strokeWidth="0.6" />
          <rect x="4" y="16" width="16" height="36" fill="none" stroke="#ffffff" strokeWidth="0.6" />
          <rect x="80" y="16" width="16" height="36" fill="none" stroke="#ffffff" strokeWidth="0.6" />
        </svg>

        <canvas
          ref={canvasRef}
          width={800}
          height={544}
          className="absolute inset-0 w-full h-full mix-blend-screen"
        />

        {/* Legend */}
        <div className="absolute bottom-2 left-3 px-2.5 py-1 rounded bg-black/70 border border-white/10 text-[11px] text-slate-300 flex items-center gap-2">
          <span>Density:</span>
          <div className="w-24 h-2 rounded bg-gradient-to-r from-blue-500 via-green-400 via-yellow-400 to-red-500" />
          <span>High</span>
        </div>
      </div>
    </div>
  );
};
