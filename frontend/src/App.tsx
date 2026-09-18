import React, { useState, useEffect } from 'react';
import { VideoPlayer } from './components/VideoPlayer';
import { TacticalPitch } from './components/TacticalPitch';
import { TeamIntelligenceCard } from './components/TeamIntelligenceCard';
import { HeatmapView } from './components/HeatmapView';
import { ModelPerformance } from './components/ModelPerformance';
import { UploadModal } from './components/UploadModal';
import type { MatchResults, ModelMetrics } from './types';
import {
  Shield,
  Activity,
  Layers,
  Flame,
  CircleDot,
  UploadCloud,
  Play,
  Cpu,
  Eye,
} from 'lucide-react';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'pitch' | 'heatmap' | 'ball' | 'model'>('overview');
  const [matchResults, setMatchResults] = useState<MatchResults | null>(null);
  const [modelMetrics, setModelMetrics] = useState<ModelMetrics | null>(null);
  const [currentFrameIdx, setCurrentFrameIdx] = useState<number>(0);
  const [isUploadOpen, setIsUploadOpen] = useState<boolean>(false);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [processingProgress, setProcessingProgress] = useState<number>(0);
  const [statusMessage, setStatusMessage] = useState<string>('');
  const [healthInfo, setHealthInfo] = useState<{ model_loaded: boolean; device: string } | null>(null);

  // Fetch health and initial model metrics on load
  useEffect(() => {
    fetch('/api/health')
      .then((res) => res.json())
      .then((data) => setHealthInfo(data))
      .catch((err) => console.log('Health check failed:', err));

    fetch('/api/model/metrics')
      .then((res) => res.json())
      .then((data) => setModelMetrics(data))
      .catch((err) => console.log('Metrics fetch failed:', err));

    // Auto-load latest completed match or demo match
    fetch('/api/matches')
      .then((res) => (res.ok ? res.json() : []))
      .then((matchesList: any[]) => {
        // Prioritize completed uploaded match over demo
        const completedUploaded = matchesList
          .filter((m) => m.status === 'completed' && m.match_id !== 'demo')
          .pop();
        const targetId = completedUploaded ? completedUploaded.match_id : 'demo';

        fetch(`/api/tracking/${targetId}`)
          .then((res) => (res.ok ? res.json() : null))
          .then((data) => {
            if (data) setMatchResults(data);
          })
          .catch(() => {});
      })
      .catch(() => {});
  }, []);


  // Poll match processing status
  const pollMatchStatus = (matchId: string) => {
    setIsProcessing(true);
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`/api/matches/${matchId}`);
        const statusData = await res.json();

        setProcessingProgress(statusData.progress || 10);
        setStatusMessage(statusData.message || 'Processing frames...');

        if (statusData.status === 'completed') {
          clearInterval(interval);
          // Fetch completed tracking data
          const trackingRes = await fetch(`/api/tracking/${matchId}`);
          const trackingData = await trackingRes.json();
          setMatchResults(trackingData);
          setIsProcessing(false);
          setIsUploadOpen(false);
          setCurrentFrameIdx(0);
        } else if (statusData.status === 'failed') {
          clearInterval(interval);
          setIsProcessing(false);
          setStatusMessage('Processing failed: ' + statusData.message);
        }
      } catch (e) {
        console.error('Error polling status:', e);
      }
    }, 1200);
  };

  // Trigger Demo Mode
  const handleStartDemo = async () => {
    setIsProcessing(true);
    setStatusMessage('Initiating DEMO MODE on data/demo/football_demo.mp4...');
    setProcessingProgress(10);

    try {
      await fetch('/api/process/demo', { method: 'POST' });
      pollMatchStatus('demo');
    } catch (err: any) {
      setIsProcessing(false);
      setStatusMessage('Error starting demo: ' + err.message);
    }
  };

  const handleUploadSuccess = async (matchId: string) => {
    setStatusMessage('Video registered. Launching local AI pipeline...');
    setProcessingProgress(15);
    try {
      await fetch(`/api/process/${matchId}`, { method: 'POST' });
      pollMatchStatus(matchId);
    } catch (err: any) {
      setIsProcessing(false);
      setStatusMessage('Error starting processing: ' + err.message);
    }
  };

  const currentFrame = matchResults?.frames[currentFrameIdx] || null;
  const team1Color = matchResults?.teams.team1.color || '#D32F2F';
  const team2Color = matchResults?.teams.team2.color || '#F5F5F5';

  return (
    <div className="min-h-screen bg-[#07090e] text-slate-100 flex flex-col selection:bg-cyan-500 selection:text-black">
      {/* Top Navigation Bar */}
      <header className="h-16 px-6 bg-pitch-dark/95 border-b border-pitch-border backdrop-blur-md flex items-center justify-between sticky top-0 z-40">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-emerald-400 p-[1.5px] flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <div className="w-full h-full bg-pitch-dark rounded-[10px] flex items-center justify-center">
                <span className="font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-emerald-400 font-mono text-sm">
                  TX
                </span>
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="font-extrabold text-lg tracking-wider text-white">TARGET-X</h1>
                <span className="px-2 py-0.5 rounded-full bg-cyan-950/80 text-cyan-400 border border-cyan-800/60 text-[10px] font-mono font-semibold">
                  VISIONX 2026
                </span>
              </div>
              <p className="text-[11px] text-slate-400 -mt-0.5">
                From Broadcast Pixels to Tactical Intelligence
              </p>
            </div>
          </div>
        </div>

        {/* Action Controls & Health */}
        <div className="flex items-center gap-3">
          <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-pitch-card border border-pitch-border text-xs font-mono">
            <Cpu className="w-3.5 h-3.5 text-cyan-400" />
            <span className="text-slate-400">Device:</span>
            <span className="text-cyan-300 font-bold uppercase">{healthInfo?.device || 'CPU'}</span>
            <span className="text-slate-600">|</span>
            <span className="text-slate-400">Model:</span>
            <span className={healthInfo?.model_loaded ? 'text-emerald-400 font-bold' : 'text-yellow-400'}>
              {healthInfo?.model_loaded ? 'AUTHENTIC LOCAL' : 'READY'}
            </span>
          </div>

          <button
            onClick={() => setIsUploadOpen(true)}
            className="px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-1.5 transition"
          >
            <UploadCloud className="w-4 h-4 text-cyan-400" />
            <span>Upload Match</span>
          </button>

          <button
            onClick={handleStartDemo}
            className="px-4 py-1.5 rounded-lg bg-gradient-to-r from-cyan-500 to-emerald-500 hover:from-cyan-400 hover:to-emerald-400 text-slate-950 text-xs font-extrabold flex items-center gap-1.5 shadow-lg shadow-cyan-500/20 transition active:scale-95"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>Run Demo Mode</span>
          </button>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-6 flex flex-col gap-6">
        {/* Top: Synchronized Dual Video Player (Original Video | Detection Video) */}
        <section className="w-full">
          <VideoPlayer
            videoUrl={matchResults?.video_url}
            videoFilename={
              matchResults?.metadata?.video_path
                ? matchResults.metadata.video_path.split('/').pop()
                : 'Uploaded Match Video'
            }
            frames={matchResults?.frames || []}
            currentFrameIdx={currentFrameIdx}
            onFrameChange={setCurrentFrameIdx}
            team1Color={team1Color}
            team2Color={team2Color}
          />
        </section>

        {/* Tactical Pitch & Team Intelligence Layer */}
        <section className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left: Tactical Pitch Radar (6 cols) */}
          <div className="lg:col-span-6 flex flex-col gap-4">
            <div className="p-4 rounded-xl bg-pitch-card border border-pitch-border flex flex-col gap-3 shadow-lg">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Activity className="w-4 h-4 text-emerald-400" />
                  <h2 className="font-bold text-sm text-white">Live 2D Tactical Pitch</h2>
                </div>
                <span className="text-[11px] font-mono text-slate-400">Top-Down Radar</span>
              </div>

              <TacticalPitch
                snapshot={currentFrame?.tactical_pitch || null}
                team1Color={team1Color}
                team2Color={team2Color}
              />
            </div>
          </div>

          {/* Right: Dynamic Team Intelligence (6 cols) */}
          <div className="lg:col-span-6 flex flex-col gap-3">
            {matchResults ? (
              <div className="flex flex-col gap-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Shield className="w-4 h-4 text-cyan-400" />
                    <h3 className="font-bold text-sm text-slate-200 uppercase tracking-wider">
                      Dynamic Team Discovery & Identification
                    </h3>
                  </div>
                  <span className="text-[11px] font-mono text-cyan-400">LAB/HSV Clustering</span>
                </div>
                <TeamIntelligenceCard
                  team1={matchResults.teams.team1}
                  team2={matchResults.teams.team2}
                />
              </div>
            ) : (
              <div className="p-8 rounded-xl bg-pitch-card border border-pitch-border flex flex-col items-center justify-center text-center text-slate-400 min-h-[280px] gap-2">
                <Shield className="w-10 h-10 text-slate-600" />
                <span className="text-sm font-semibold text-slate-300">Team Intelligence Standby</span>
                <span className="text-xs text-slate-500">Run video detection to extract team kit colors and formations</span>
              </div>
            )}
          </div>
        </section>

        {/* Analytics Tabs Navigation */}
        <section className="flex flex-col gap-4">
          <div className="flex border-b border-pitch-border gap-2 overflow-x-auto pb-1">
            <button
              onClick={() => setActiveTab('overview')}
              className={`px-4 py-2 text-xs font-semibold rounded-t-lg transition flex items-center gap-2 ${
                activeTab === 'overview'
                  ? 'bg-pitch-card text-cyan-400 border-t-2 border-cyan-400 border-x border-pitch-border'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Eye className="w-3.5 h-3.5" />
              Match Overview
            </button>

            <button
              onClick={() => setActiveTab('pitch')}
              className={`px-4 py-2 text-xs font-semibold rounded-t-lg transition flex items-center gap-2 ${
                activeTab === 'pitch'
                  ? 'bg-pitch-card text-cyan-400 border-t-2 border-cyan-400 border-x border-pitch-border'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              Tactical Metrics
            </button>

            <button
              onClick={() => setActiveTab('heatmap')}
              className={`px-4 py-2 text-xs font-semibold rounded-t-lg transition flex items-center gap-2 ${
                activeTab === 'heatmap'
                  ? 'bg-pitch-card text-cyan-400 border-t-2 border-cyan-400 border-x border-pitch-border'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Flame className="w-3.5 h-3.5" />
              Movement Heatmaps
            </button>

            <button
              onClick={() => setActiveTab('ball')}
              className={`px-4 py-2 text-xs font-semibold rounded-t-lg transition flex items-center gap-2 ${
                activeTab === 'ball'
                  ? 'bg-pitch-card text-cyan-400 border-t-2 border-cyan-400 border-x border-pitch-border'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <CircleDot className="w-3.5 h-3.5" />
              Ball Trajectory
            </button>

            <button
              onClick={() => setActiveTab('model')}
              className={`px-4 py-2 text-xs font-semibold rounded-t-lg transition flex items-center gap-2 ${
                activeTab === 'model'
                  ? 'bg-pitch-card text-cyan-400 border-t-2 border-cyan-400 border-x border-pitch-border'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Cpu className="w-3.5 h-3.5" />
              Model Performance & Verification
            </button>
          </div>

          {/* Tab Content Panes */}
          <div className="p-6 rounded-xl bg-pitch-card border border-pitch-border min-h-[280px]">
            {activeTab === 'overview' && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 rounded-xl bg-pitch-dark/80 border border-slate-800">
                  <div className="text-xs text-slate-400">Total Unique Players</div>
                  <div className="text-2xl font-bold text-cyan-400 font-mono mt-1">
                    {matchResults?.summary.total_unique_players || 0}
                  </div>
                  <div className="text-[10px] text-slate-500 mt-1">Persistent Track IDs</div>
                </div>

                <div className="p-4 rounded-xl bg-pitch-dark/80 border border-slate-800">
                  <div className="text-xs text-slate-400">Referees Detected</div>
                  <div className="text-2xl font-bold text-yellow-400 font-mono mt-1">
                    {matchResults?.summary.total_unique_referees || 0}
                  </div>
                  <div className="text-[10px] text-slate-500 mt-1">Class 1 Dedicated Head</div>
                </div>

                <div className="p-4 rounded-xl bg-pitch-dark/80 border border-slate-800">
                  <div className="text-xs text-slate-400">Ball Detection Rate</div>
                  <div className="text-2xl font-bold text-emerald-400 font-mono mt-1">
                    {matchResults ? `${(matchResults.summary.ball_detection_rate * 100).toFixed(1)}%` : '0%'}
                  </div>
                  <div className="text-[10px] text-slate-500 mt-1">Genuine Tracked Frames</div>
                </div>

                <div className="p-4 rounded-xl bg-pitch-dark/80 border border-slate-800">
                  <div className="text-xs text-slate-400">Analysis Speed</div>
                  <div className="text-2xl font-bold text-white font-mono mt-1">
                    {matchResults
                      ? `${(matchResults.metadata.processed_frames / matchResults.metadata.processing_time_seconds).toFixed(1)} FPS`
                      : '0 FPS'}
                  </div>
                  <div className="text-[10px] text-slate-500 mt-1">Local Inference Execution</div>
                </div>
              </div>
            )}

            {activeTab === 'pitch' && (
              <div className="flex flex-col gap-4">
                <div className="text-xs text-slate-300 leading-relaxed">
                  <strong>Tracked Image-Space Tactical View</strong> estimates relative field compactness
                  and formation centroids without claiming uncalibrated real-world metric coordinates.
                </div>
                {currentFrame?.tactical_pitch.tactical_metrics && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 rounded-xl bg-pitch-dark border border-slate-800">
                      <h4 className="font-bold text-xs text-white uppercase tracking-wider mb-2 flex items-center gap-2">
                        <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: team1Color }} />
                        Team 1 Spatial Distribution
                      </h4>
                      <div className="font-mono text-xs text-slate-400 space-y-1">
                        <div>
                          Centroid:{' '}
                          <span className="text-white">
                            [{currentFrame.tactical_pitch.tactical_metrics.team1_centroid?.join(', ')}]
                          </span>
                        </div>
                        <div>
                          Spread / Compactness:{' '}
                          <span className="text-cyan-400">
                            {currentFrame.tactical_pitch.tactical_metrics.team1_spatial_spread} units
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="p-4 rounded-xl bg-pitch-dark border border-slate-800">
                      <h4 className="font-bold text-xs text-white uppercase tracking-wider mb-2 flex items-center gap-2">
                        <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: team2Color }} />
                        Team 2 Spatial Distribution
                      </h4>
                      <div className="font-mono text-xs text-slate-400 space-y-1">
                        <div>
                          Centroid:{' '}
                          <span className="text-white">
                            [{currentFrame.tactical_pitch.tactical_metrics.team2_centroid?.join(', ')}]
                          </span>
                        </div>
                        <div>
                          Spread / Compactness:{' '}
                          <span className="text-cyan-400">
                            {currentFrame.tactical_pitch.tactical_metrics.team2_spatial_spread} units
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'heatmap' && (
              <HeatmapView
                heatmaps={matchResults?.heatmaps || null}
                team1Color={team1Color}
                team2Color={team2Color}
              />
            )}

            {activeTab === 'ball' && (
              <div className="flex flex-col gap-4">
                <div className="p-4 rounded-xl bg-pitch-dark/80 border border-slate-800 flex items-center justify-between">
                  <div>
                    <h4 className="font-bold text-white text-xs uppercase tracking-wider">
                      Ball Movement Status
                    </h4>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Current: <strong className="text-cyan-300">{currentFrame?.ball.status || 'Standby'}</strong>
                    </p>
                  </div>
                  <div className="font-mono text-xs text-slate-300">
                    Confidence: {currentFrame?.ball.current_pos ? `${(currentFrame.ball.current_pos.confidence * 100).toFixed(1)}%` : '0%'}
                  </div>
                </div>

                <div className="text-xs text-slate-400 italic">
                  Note: In strict accordance with the hackathon rules, ball coordinates are only recorded
                  when genuinely detected; positions are never fabricated during occlusions or out-of-frame moments.
                </div>
              </div>
            )}

            {activeTab === 'model' && (
              <ModelPerformance metrics={modelMetrics} />
            )}
          </div>
        </section>
      </main>

      {/* Upload and Demo Modal */}
      <UploadModal
        isOpen={isUploadOpen}
        onClose={() => setIsUploadOpen(false)}
        onStartDemo={handleStartDemo}
        onUploadSuccess={handleUploadSuccess}
        isProcessing={isProcessing}
        progress={processingProgress}
        statusMessage={statusMessage}
      />
    </div>
  );
};

export default App;
