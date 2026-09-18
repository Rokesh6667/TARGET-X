import React, { useState, useRef, useEffect } from 'react';
import { Upload, Film, PlayCircle, X, AlertCircle, Loader2, CheckCircle2, Zap } from 'lucide-react';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onStartDemo: () => void;
  onUploadSuccess: (matchId: string) => void;
  isProcessing: boolean;
  progress: number;
  statusMessage: string;
}

interface ServerVideo {
  filename: string;
  display_name: string;
  size_mb: number;
  video_url: string;
}

export const UploadModal: React.FC<Props> = ({
  isOpen,
  onClose,
  onStartDemo,
  onUploadSuccess,
  isProcessing,
  progress,
  statusMessage,
}) => {
  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [serverVideos, setServerVideos] = useState<ServerVideo[]>([]);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  // Load existing uploaded videos from server when modal opens
  useEffect(() => {
    if (isOpen) {
      fetch('/api/uploads')
        .then((r) => (r.ok ? r.json() : []))
        .then((data) => {
          setServerVideos(data || []);
        })
        .catch(() => {});
    }
  }, [isOpen]);


  if (!isOpen) return null;

  const handleFileSelect = (file: File) => {
    const validExts = ['.mp4', '.mov', '.m4v', '.avi'];
    const ext = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!validExts.includes(ext)) {
      setErrorMsg(`Invalid file type. Allowed: ${validExts.join(', ')}`);
      return;
    }
    if (file.size > 200 * 1024 * 1024) {
      setErrorMsg('File exceeds 200MB limit.');
      return;
    }
    setErrorMsg(null);
    setSelectedFile(file);
  };

  const handleSelectExisting = async (filename: string) => {
    setUploading(true);
    setErrorMsg(null);
    try {
      const res = await fetch('/api/upload/select-existing', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Failed to select match video' }));
        throw new Error(err.detail || 'Selection failed');
      }
      const data = await res.json();
      setUploading(false);
      onUploadSuccess(data.match_id);
    } catch (err: any) {
      setUploading(false);
      setErrorMsg(err.message || 'Error selecting match video');
    }
  };

  const handleUploadAndProcess = () => {
    if (!selectedFile) return;
    setUploading(true);
    setUploadProgress(0);
    setErrorMsg(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/api/upload');

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable) {
        const pct = Math.round((e.loaded / e.total) * 100);
        setUploadProgress(pct);
      }
    };

    xhr.onload = () => {
      setUploading(false);
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const data = JSON.parse(xhr.responseText);
          onUploadSuccess(data.match_id);
        } catch {
          setErrorMsg('Invalid response from server. Please retry.');
        }
      } else {
        try {
          const err = JSON.parse(xhr.responseText);
          setErrorMsg(err.detail || 'Upload failed');
        } catch {
          setErrorMsg(`Upload failed (HTTP ${xhr.status}). Ensure backend is active.`);
        }
      }
    };

    xhr.onerror = () => {
      setUploading(false);
      setErrorMsg('Network error: Unable to reach TARGET-X backend server (port 8000).');
    };

    xhr.send(formData);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
      <div className="relative w-full max-w-lg p-6 rounded-2xl bg-[#0f1420] border border-pitch-border shadow-2xl flex flex-col gap-5 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Film className="w-5 h-5 text-cyan-400" />
            <h3 className="text-base font-bold text-white">Video Input & Match Selection</h3>
          </div>
          {!isProcessing && (
            <button
              onClick={onClose}
              className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* Processing State */}
        {isProcessing ? (
          <div className="py-8 flex flex-col items-center justify-center gap-4">
            <Loader2 className="w-10 h-10 text-cyan-400 animate-spin" />
            <div className="text-center">
              <h4 className="font-bold text-white text-sm">Running TARGET-X Pipeline</h4>
              <p className="text-xs text-slate-400 mt-1 max-w-sm">{statusMessage}</p>
            </div>
            {/* Progress Bar */}
            <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden mt-2">
              <div
                className="bg-gradient-to-r from-cyan-500 to-emerald-400 h-2 transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
            <span className="font-mono text-xs text-cyan-300 font-bold">{progress}%</span>
          </div>
        ) : (
          <>
            {/* Quick Demo Mode Trigger */}
            <div className="p-4 rounded-xl bg-cyan-950/40 border border-cyan-800/40 flex items-center justify-between gap-4">
              <div>
                <h4 className="font-bold text-white text-xs uppercase tracking-wider text-cyan-300">
                  Quick Benchmark
                </h4>
                <p className="text-xs text-slate-300 mt-0.5">
                  Analyze sample broadcast match (<code className="text-cyan-200">football_demo.mp4</code>)
                </p>
              </div>
              <button
                onClick={onStartDemo}
                className="px-4 py-2 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs flex items-center gap-1.5 shrink-0 shadow-lg transition"
              >
                <PlayCircle className="w-4 h-4" />
                Run Demo
              </button>
            </div>

            {/* Instant Server Videos (Zero Upload Time) */}
            {serverVideos.length > 0 && (
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                    <Zap className="w-3.5 h-3.5" />
                    Available On Server (Instant Analysis)
                  </span>
                  <span className="text-[10px] text-slate-400 font-mono">No upload delay</span>
                </div>
                <div className="space-y-1.5 max-h-36 overflow-y-auto pr-1">
                  {serverVideos.slice(0, 3).map((vid) => (
                    <div
                      key={vid.filename}
                      className="p-2.5 rounded-lg bg-emerald-950/20 border border-emerald-800/40 flex items-center justify-between gap-3 text-xs"
                    >
                      <div className="truncate min-w-0">
                        <div className="font-semibold text-white truncate">{vid.display_name}</div>
                        <div className="text-[10px] text-slate-400 font-mono truncate">
                          {vid.filename} &bull; {vid.size_mb} MB
                        </div>
                      </div>
                      <button
                        onClick={() => handleSelectExisting(vid.filename)}
                        disabled={uploading}
                        className="px-3 py-1 rounded-md bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs flex items-center gap-1 shrink-0 transition"
                      >
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        Analyze
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="relative flex py-1 items-center">
              <div className="flex-grow border-t border-slate-800"></div>
              <span className="flex-shrink mx-4 text-[11px] font-mono text-slate-500 uppercase">
                Or Upload New Match Video
              </span>
              <div className="flex-grow border-t border-slate-800"></div>
            </div>

            {/* Drop Zone */}
            <div
              onDragOver={(e) => {
                e.preventDefault();
                setDragOver(true);
              }}
              onDragLeave={() => setDragOver(false)}
              onDrop={(e) => {
                e.preventDefault();
                setDragOver(false);
                if (e.dataTransfer.files?.[0]) {
                  handleFileSelect(e.dataTransfer.files[0]);
                }
              }}
              onClick={() => fileInputRef.current?.click()}
              className={`p-6 rounded-xl border-2 border-dashed cursor-pointer transition flex flex-col items-center justify-center gap-2 text-center ${
                dragOver
                  ? 'border-cyan-400 bg-cyan-950/20'
                  : 'border-slate-700 hover:border-slate-500 bg-slate-900/40'
              }`}
            >
              <Upload className="w-8 h-8 text-slate-400" />
              <div className="text-xs text-slate-300">
                <span className="font-semibold text-cyan-400">Click to browse</span> or drag and drop
              </div>
              <div className="text-[10px] text-slate-500 font-mono">
                MP4, MOV, M4V, AVI up to 200MB
              </div>
              <input
                ref={fileInputRef}
                type="file"
                accept=".mp4,.mov,.m4v,.avi"
                className="hidden"
                onChange={(e) => {
                  if (e.target.files?.[0]) handleFileSelect(e.target.files[0]);
                }}
              />
            </div>

            {/* Selected File Display & Progress */}
            {selectedFile && (
              <div className="space-y-2">
                <div className="p-3 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2 truncate min-w-0">
                    <Film className="w-4 h-4 text-cyan-400 shrink-0" />
                    <span className="text-white truncate font-mono">{selectedFile.name}</span>
                    <span className="text-slate-500 text-[10px] shrink-0">
                      ({(selectedFile.size / (1024 * 1024)).toFixed(1)} MB)
                    </span>
                  </div>
                  <button
                    onClick={handleUploadAndProcess}
                    disabled={uploading}
                    className="px-3 py-1.5 rounded bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs transition disabled:opacity-50 shrink-0"
                  >
                    {uploading ? `Uploading ${uploadProgress}%...` : 'Process Video'}
                  </button>
                </div>
                {uploading && (
                  <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                    <div
                      className="bg-emerald-400 h-1.5 transition-all duration-150"
                      style={{ width: `${uploadProgress}%` }}
                    />
                  </div>
                )}
              </div>
            )}

            {/* Error Message */}
            {errorMsg && (
              <div className="p-3 rounded-lg bg-red-950/40 border border-red-800/60 text-xs text-red-300 flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};


