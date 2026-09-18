import React, { useRef, useEffect, useState, useCallback } from 'react';
import type { FrameSnapshot, BallItem } from '../types';
import {
  Play,
  Pause,
  RotateCcw,
  SkipBack,
  SkipForward,
  Video as VideoIcon,
  Crosshair,
  ShieldCheck,
  CheckCircle2,
} from 'lucide-react';

interface Props {
  videoUrl?: string;
  videoFilename?: string;
  frames: FrameSnapshot[];
  currentFrameIdx: number;
  onFrameChange: React.Dispatch<React.SetStateAction<number>>;
  team1Color: string;
  team2Color: string;
}

export const VideoPlayer: React.FC<Props> = ({
  videoUrl,
  videoFilename = 'Uploaded Match Video',
  frames,
  currentFrameIdx,
  onFrameChange,
  team1Color,
  team2Color,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const originalVideoRef = useRef<HTMLVideoElement | null>(null);
  const detectionVideoRef = useRef<HTMLVideoElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1);

  const totalFrames = frames.length;
  const currentSnapshot = frames[currentFrameIdx] || null;

  // Sync video element time with current frame snapshot
  const syncVideosToTimestamp = useCallback((targetTime: number) => {
    if (originalVideoRef.current) {
      if (Math.abs(originalVideoRef.current.currentTime - targetTime) > 0.05) {
        originalVideoRef.current.currentTime = targetTime;
      }
    }
    if (detectionVideoRef.current) {
      if (Math.abs(detectionVideoRef.current.currentTime - targetTime) > 0.05) {
        detectionVideoRef.current.currentTime = targetTime;
      }
    }
  }, []);

  // Sync when currentFrameIdx changes
  useEffect(() => {
    if (currentSnapshot) {
      syncVideosToTimestamp(currentSnapshot.timestamp);
    }
  }, [currentFrameIdx, currentSnapshot, syncVideosToTimestamp]);

  // Playback timer loop
  useEffect(() => {
    let interval: any = null;
    if (isPlaying && totalFrames > 0) {
      const frameDuration = Math.round(40 / playbackSpeed); // ~25 FPS adjusted by speed
      interval = setInterval(() => {
        onFrameChange((prev: number) => {
          if (prev >= totalFrames - 1) {
            setIsPlaying(false);
            return 0;
          }
          return prev + 1;
        });
      }, frameDuration);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isPlaying, totalFrames, playbackSpeed, onFrameChange]);

  // Render detection overlay onto right-side canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (!currentSnapshot) return;

    const w = canvas.width;
    const h = canvas.height;

    // 1. Draw Player & Referee Bounding Boxes (filtered strictly within Match-Area ROI)
    currentSnapshot.tracks.forEach((track) => {
      const [x1_n, y1_n, x2_n, y2_n] = track.box_normalized;
      const bx1 = x1_n * w;
      const by1 = y1_n * h;
      const bw = (x2_n - x1_n) * w;
      const bh = (y2_n - y1_n) * h;

      const isRef = track.class_id === 1;
      const boxColor = isRef ? '#FFD700' : (track.team === 'Team 1' ? team1Color : team2Color);

      // Subtle translucent box fill
      ctx.fillStyle = isRef ? 'rgba(255, 215, 0, 0.12)' : (track.team === 'Team 1' ? 'rgba(211, 47, 47, 0.15)' : 'rgba(59, 130, 246, 0.15)');
      ctx.fillRect(bx1, by1, bw, bh);

      // Box outline
      ctx.strokeStyle = boxColor;
      ctx.lineWidth = 2.4;
      ctx.strokeRect(bx1, by1, bw, bh);

      // Tactical corner accents
      const cornerLen = Math.min(10, bw * 0.25, bh * 0.25);
      ctx.strokeStyle = '#ffffff';
      ctx.lineWidth = 2.8;

      // Top-left corner
      ctx.beginPath();
      ctx.moveTo(bx1, by1 + cornerLen);
      ctx.lineTo(bx1, by1);
      ctx.lineTo(bx1 + cornerLen, by1);
      ctx.stroke();

      // Bottom-right corner
      ctx.beginPath();
      ctx.moveTo(bx1 + bw, by1 + bh - cornerLen);
      ctx.lineTo(bx1 + bw, by1 + bh);
      ctx.lineTo(bx1 + bw - cornerLen, by1 + bh);
      ctx.stroke();

      // Top label badge
      const roleSuffix = track.role === 'goalkeeper' ? ' [GK]' : '';
      const label = `${track.display_id}${roleSuffix}`;
      ctx.font = 'bold 11px Outfit, sans-serif';
      const textWidth = ctx.measureText(label).width;

      ctx.fillStyle = boxColor;
      ctx.fillRect(bx1, Math.max(0, by1 - 20), textWidth + 12, 20);

      ctx.fillStyle = isRef || boxColor === '#F5F5F5' || boxColor === '#FFFFFF' ? '#000000' : '#ffffff';
      ctx.fillText(label, bx1 + 6, Math.max(14, by1 - 5));

      // Trajectory trail
      if (track.trajectory && track.trajectory.length > 1) {
        ctx.beginPath();
        ctx.strokeStyle = boxColor;
        ctx.lineWidth = 1.4;
        ctx.setLineDash([3, 3]);

        const scaleX = w / 1280;
        const scaleY = h / 720;

        track.trajectory.forEach((pt, i) => {
          const px = pt[0] * scaleX;
          const py = pt[1] * scaleY;
          if (i === 0) ctx.moveTo(px, py);
          else ctx.lineTo(px, py);
        });
        ctx.stroke();
        ctx.setLineDash([]);
      }
    });

    // 2. Draw Ball Tracking Reticle
    const ball: BallItem = currentSnapshot.ball;
    if (ball && ball.detected && ball.current_pos) {
      const bx = ball.current_pos.x_norm * w;
      const by = ball.current_pos.y_norm * h;

      // Outer targeting reticle
      ctx.strokeStyle = '#38bdf8';
      ctx.lineWidth = 2.2;
      ctx.beginPath();
      ctx.arc(bx, by, 11, 0, Math.PI * 2);
      ctx.stroke();

      // Inner glowing core
      ctx.fillStyle = '#ffffff';
      ctx.beginPath();
      ctx.arc(bx, by, 4.5, 0, Math.PI * 2);
      ctx.fill();

      // Reticle crosshairs
      ctx.beginPath();
      ctx.moveTo(bx - 16, by);
      ctx.lineTo(bx - 11, by);
      ctx.moveTo(bx + 11, by);
      ctx.lineTo(bx + 16, by);
      ctx.moveTo(bx, by - 16);
      ctx.lineTo(bx, by - 11);
      ctx.moveTo(bx, by + 11);
      ctx.lineTo(bx, by + 16);
      ctx.strokeStyle = '#38bdf8';
      ctx.lineWidth = 2;
      ctx.stroke();

      // Ball badge
      ctx.fillStyle = '#38bdf8';
      ctx.fillRect(bx + 14, by - 8, 38, 16);
      ctx.fillStyle = '#000000';
      ctx.font = 'bold 9px Outfit, sans-serif';
      ctx.fillText('BALL', bx + 19, by + 4);
    }
  }, [currentSnapshot, team1Color, team2Color]);

  const handleSeek = (newFrame: number) => {
    setIsPlaying(false);
    onFrameChange(newFrame);
  };

  const handleStep = (step: number) => {
    setIsPlaying(false);
    onFrameChange((prev) => Math.max(0, Math.min(totalFrames - 1, prev + step)));
  };

  return (
    <div className="flex flex-col w-full bg-pitch-card rounded-2xl border border-pitch-border overflow-hidden shadow-2xl">
      {/* Side-by-Side Video Layout */}
      <div className="grid grid-cols-1 md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-pitch-border bg-black/40">
        {/* =========================================================================
            LEFT COLUMN: ORIGINAL VIDEO (Inserted / Uploaded Video)
            ========================================================================= */}
        <div className="flex flex-col">
          {/* Header Bar */}
          <div className="px-4 py-2.5 bg-pitch-dark/95 border-b border-pitch-border flex items-center justify-between text-xs">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
              <span className="font-bold tracking-wider text-slate-100 uppercase">ORIGINAL VIDEO</span>
              <span className="px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700 text-[10px] font-mono">
                Source Media
              </span>
            </div>
            <div className="flex items-center gap-1 text-[11px] font-mono text-slate-400 truncate max-w-[180px]">
              <VideoIcon className="w-3 h-3 text-slate-500 shrink-0" />
              <span className="truncate">{videoFilename}</span>
            </div>
          </div>

          {/* Video Viewport */}
          <div className="relative w-full aspect-video bg-black flex items-center justify-center overflow-hidden">
            {videoUrl ? (
              <video
                ref={originalVideoRef}
                src={videoUrl}
                className="w-full h-full object-cover"
                playsInline
                muted
                preload="auto"
              />
            ) : (
              <div className="absolute inset-0 bg-[#080d14] flex flex-col items-center justify-center text-slate-400 text-xs gap-2 p-6 text-center">
                <VideoIcon className="w-8 h-8 text-slate-600" />
                <span className="font-semibold text-slate-300">No original video source loaded</span>
                <span className="text-[11px] text-slate-500">Upload a match video to begin analysis</span>
              </div>
            )}

            {/* Bottom-left timestamp badge */}
            <div className="absolute bottom-2.5 left-3 px-2 py-1 rounded bg-black/70 backdrop-blur-sm border border-white/10 text-[10px] font-mono text-slate-300">
              RAW BROADCAST PIXELS
            </div>
          </div>
        </div>

        {/* =========================================================================
            RIGHT COLUMN: DETECTION VIDEO (Match-Area Detections + Persistent IDs)
            ========================================================================= */}
        <div className="flex flex-col">
          {/* Header Bar */}
          <div className="px-4 py-2.5 bg-pitch-dark/95 border-b border-pitch-border flex items-center justify-between text-xs">
            <div className="flex items-center gap-2">
              <Crosshair className="w-3.5 h-3.5 text-emerald-400" />
              <span className="font-bold tracking-wider text-white uppercase">DETECTION VIDEO</span>
              <span className="px-2 py-0.5 rounded-full bg-emerald-950/90 text-emerald-300 border border-emerald-800/60 font-mono text-[10px] flex items-center gap-1">
                <ShieldCheck className="w-2.5 h-2.5" />
                ROI FILTERED
              </span>
            </div>
            <div className="text-[11px] font-mono text-slate-400">
              <span className="text-emerald-400 font-bold">
                {currentSnapshot ? currentSnapshot.players_count : 0}
              </span>{' '}
              Players On-Pitch
            </div>
          </div>

          {/* Detection Viewport (Video + Real-time Canvas Vector Overlay) */}
          <div className="relative w-full aspect-video bg-black flex items-center justify-center overflow-hidden">
            {videoUrl ? (
              <video
                ref={detectionVideoRef}
                src={videoUrl}
                className="w-full h-full object-cover"
                playsInline
                muted
                preload="auto"
              />
            ) : (
              <div className="absolute inset-0 bg-[#080d14] flex flex-col items-center justify-center text-slate-400 text-xs gap-2 p-6 text-center">
                <Crosshair className="w-8 h-8 text-emerald-500/50 animate-pulse" />
                <span className="font-semibold text-slate-300">Awaiting detection results</span>
                <span className="text-[11px] text-slate-500">Run analysis to generate bounding boxes & track IDs</span>
              </div>
            )}

            {/* Tactical Vector Canvas Overlay */}
            <canvas
              ref={canvasRef}
              width={1280}
              height={720}
              className="absolute inset-0 w-full h-full pointer-events-none"
            />

            {/* Live Filter Indicator Badge */}
            <div className="absolute top-2.5 right-3 px-2 py-0.5 rounded bg-black/80 backdrop-blur-sm border border-emerald-500/40 text-[9px] font-mono text-emerald-300 flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3 text-emerald-400" />
              <span>CROWD/AUDIENCE REJECTED</span>
            </div>

            {/* Bottom-right info badge */}
            <div className="absolute bottom-2.5 right-3 px-2 py-1 rounded bg-black/70 backdrop-blur-sm border border-white/10 text-[10px] font-mono text-slate-300 flex items-center gap-2">
              <span>Referees: <strong className="text-yellow-400">{currentSnapshot ? currentSnapshot.referees_count : 0}</strong></span>
              <span>•</span>
              <span>Ball: <strong className={currentSnapshot?.ball?.detected ? 'text-emerald-400' : 'text-slate-500'}>
                {currentSnapshot?.ball?.detected ? 'Tracked' : 'Searching'}
              </strong></span>
            </div>
          </div>
        </div>
      </div>

      {/* =========================================================================
          UNIFIED CONTROLS BAR: Synchronizes both Original & Detection Viewports
          ========================================================================= */}
      <div className="p-3.5 bg-pitch-dark/95 border-t border-pitch-border flex flex-wrap items-center gap-3">
        {/* Play / Pause Toggle */}
        <button
          onClick={() => setIsPlaying(!isPlaying)}
          disabled={totalFrames === 0}
          className="p-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-emerald-500 hover:from-cyan-400 hover:to-emerald-400 text-slate-950 font-bold transition disabled:opacity-40 disabled:cursor-not-allowed shadow-lg shadow-cyan-500/20"
          title={isPlaying ? 'Pause' : 'Play Synchronized'}
        >
          {isPlaying ? <Pause className="w-4 h-4 fill-current" /> : <Play className="w-4 h-4 fill-current" />}
        </button>

        {/* Step Back 1 Frame */}
        <button
          onClick={() => handleStep(-1)}
          disabled={totalFrames === 0 || currentFrameIdx <= 0}
          className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition disabled:opacity-30 disabled:cursor-not-allowed border border-slate-700/60"
          title="Step Back 1 Frame"
        >
          <SkipBack className="w-4 h-4" />
        </button>

        {/* Step Forward 1 Frame */}
        <button
          onClick={() => handleStep(1)}
          disabled={totalFrames === 0 || currentFrameIdx >= totalFrames - 1}
          className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition disabled:opacity-30 disabled:cursor-not-allowed border border-slate-700/60"
          title="Step Forward 1 Frame"
        >
          <SkipForward className="w-4 h-4" />
        </button>

        {/* Restart to Frame 0 */}
        <button
          onClick={() => handleSeek(0)}
          disabled={totalFrames === 0}
          className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition disabled:opacity-30 disabled:cursor-not-allowed border border-slate-700/60"
          title="Restart"
        >
          <RotateCcw className="w-4 h-4" />
        </button>

        {/* Scrubber Range Slider */}
        <div className="flex-1 flex items-center gap-3 min-w-[180px]">
          <input
            type="range"
            min={0}
            max={Math.max(0, totalFrames - 1)}
            value={currentFrameIdx}
            onChange={(e) => handleSeek(Number(e.target.value))}
            disabled={totalFrames === 0}
            className="flex-1 h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400 disabled:cursor-not-allowed"
          />
        </div>

        {/* Frame & Time Index Display */}
        <div className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 font-mono text-xs text-slate-300 flex items-center gap-2">
          <span>
            Frame <strong className="text-white">{currentFrameIdx + 1}</strong> / {Math.max(1, totalFrames)}
          </span>
          <span className="text-slate-600">|</span>
          <span className="text-cyan-400 font-bold">
            {currentSnapshot ? `${currentSnapshot.timestamp.toFixed(2)}s` : '0.00s'}
          </span>
        </div>

        {/* Playback Speed Selector */}
        <div className="flex items-center gap-1 bg-slate-900 border border-slate-800 rounded-lg p-0.5 text-[11px] font-mono">
          {[0.5, 1.0, 2.0].map((speed) => (
            <button
              key={speed}
              onClick={() => setPlaybackSpeed(speed)}
              className={`px-2 py-1 rounded transition ${
                playbackSpeed === speed
                  ? 'bg-cyan-500 text-slate-950 font-bold'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {speed}x
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
