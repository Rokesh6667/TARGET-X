export interface TrackItem {
  id: number;
  display_id: string;
  class_id: number;
  class_name: string;
  team: string;
  role: string;
  color: string;
  box_normalized: [number, number, number, number];
  box_pixels: [number, number, number, number];
  center_pixels: [number, number];
  confidence: number;
  trajectory: [number, number][];
}

export interface BallPoint {
  x: number;
  y: number;
  x_norm: number;
  y_norm: number;
  confidence: number;
  frame: number;
  timestamp: number;
  detected: boolean;
}

export interface BallItem {
  detected: boolean;
  current_pos: BallPoint | null;
  trail: BallPoint[];
  status: string;
}

export interface TacticalPitchPlayer {
  id: number;
  display_id: string;
  class_name: string;
  team: string;
  role: string;
  color: string;
  pitch_x: number;
  pitch_y: number;
}

export interface TacticalPitchSnapshot {
  mode: string;
  pitch_dimensions: { width: number; height: number };
  players: TacticalPitchPlayer[];
  ball: { pitch_x: number; pitch_y: number; confidence: number } | null;
  tactical_metrics: {
    team1_centroid: [number, number] | null;
    team1_spatial_spread: number | null;
    team2_centroid: [number, number] | null;
    team2_spatial_spread: number | null;
  } | null;
}

export interface FrameSnapshot {
  frame: number;
  timestamp: number;
  players_count: number;
  referees_count: number;
  tracks: TrackItem[];
  ball: BallItem;
  tactical_pitch: TacticalPitchSnapshot;
}

export interface TeamIntelligence {
  identity: string;
  display_name: string;
  country: string;
  iso_code: string;
  status: "HIGH" | "MEDIUM" | "LOW" | "UNKNOWN";
  confidence: number;
  evidence: string;
  flag_file: string;
  type: string;
}

export interface TeamData {
  name: string;
  color: string;
  intelligence: TeamIntelligence;
  roster: {
    name: string;
    color: string;
    outfield_players: string[];
    goalkeeper: string;
  };
}

export interface MatchResults {
  video_url?: string;
  output_video_url?: string;
  metadata: {
    video_path: string;
    output_video_path: string | null;
    processed_frames: number;
    fps: number;
    resolution: [number, number];
    processing_time_seconds: number;
  };
  summary: {
    total_unique_players: number;
    total_unique_referees: number;
    ball_detection_rate: number;
    player_roster: string[];
    referee_roster: string[];
  };
  teams: {
    team1: TeamData;
    team2: TeamData;
  };
  heatmaps: {
    grid_dimensions: { width: number; height: number };
    team1_heatmap: number[][];
    team2_heatmap: number[][];
    player_heatmaps: Record<string, number[][]>;
  };
  frames: FrameSnapshot[];
}

export interface ModelMetrics {
  model_name: string;
  architecture: string;
  trainable_parameters: number;
  overall_precision: number;
  overall_recall: number;
  mAP50: number;
  class_metrics: Record<string, {
    precision: number;
    recall: number;
    f1_score: number;
    tp: number;
    fp: number;
    fn: number;
  }>;
  training_history?: {
    train_loss: number[];
    val_loss: number[];
    loss_obj: number[];
    loss_cls: number[];
    loss_box: number[];
  };
  evaluation_samples?: number;
}
