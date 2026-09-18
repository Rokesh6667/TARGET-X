import React from 'react';
import type { TeamData } from '../types';
import { Shield, CheckCircle2, AlertTriangle, HelpCircle } from 'lucide-react';

interface Props {
  team1: TeamData;
  team2: TeamData;
}

export const TeamIntelligenceCard: React.FC<Props> = ({ team1, team2 }) => {
  const renderTeam = (team: TeamData, label: string) => {
    const intel = team.intelligence;

    return (
      <div className="flex-1 p-4 rounded-xl bg-pitch-card border border-pitch-border flex flex-col gap-3 relative overflow-hidden">
        {/* Color accent strip */}
        <div
          className="absolute top-0 left-0 right-0 h-1.5"
          style={{ backgroundColor: team.color }}
        />

        {/* Team Header */}
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2">
              <span
                className="w-3.5 h-3.5 rounded-full border border-white/40 shadow-sm"
                style={{ backgroundColor: team.color }}
              />
              <h3 className="font-extrabold text-base text-white uppercase tracking-wide">
                {team.name && team.name !== 'Team 1' && team.name !== 'Team 2' ? team.name : intel.identity || label}
              </h3>
              <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400 font-mono">
                {team.color}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">{intel.display_name || team.name}</p>
          </div>

          {/* Flag / Badge */}
          <div className="flex items-center gap-2">
            {intel.flag_file ? (
              <img
                src={`/static/data/flags/${intel.flag_file}`}
                alt={intel.country}
                className="w-8 h-5 object-cover rounded shadow-md border border-white/10"
                onError={(e: any) => {
                  e.target.src = '/static/data/flags/unknown.svg';
                }}
              />
            ) : (
              <div className="w-8 h-5 rounded bg-slate-800 border border-white/10 flex items-center justify-center text-[10px] text-slate-400">
                ?
              </div>
            )}
          </div>
        </div>

        {/* Identity Intelligence Gauge */}
        <div className="p-2.5 rounded-lg bg-pitch-dark/80 border border-slate-800/80 flex flex-col gap-1.5">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-400 flex items-center gap-1">
              <Shield className="w-3.5 h-3.5 text-cyan-400" />
              Verified Team Identity
            </span>
            <span className={`font-semibold flex items-center gap-1 ${
              intel.status === 'HIGH' ? 'text-emerald-400' :
              intel.status === 'MEDIUM' ? 'text-cyan-400' :
              intel.status === 'LOW' ? 'text-yellow-400' : 'text-slate-400'
            }`}>
              {intel.status === 'HIGH' && <CheckCircle2 className="w-3 h-3" />}
              {intel.status === 'LOW' && <AlertTriangle className="w-3 h-3" />}
              {intel.status === 'UNKNOWN' && <HelpCircle className="w-3 h-3" />}
              {intel.country || team.name} ({Math.round(intel.confidence * 100)}%)
            </span>
          </div>

          <div className="text-[11px] text-slate-400 italic">
            Evidence: {intel.evidence}
          </div>
        </div>

        {/* Goalkeeper & Roster Association */}
        <div className="text-xs space-y-1 pt-1 border-t border-slate-800/60 font-mono">
          <div className="flex justify-between">
            <span className="text-slate-400">Assigned Goalkeeper:</span>
            <span className="text-cyan-300 font-bold">{team.roster.goalkeeper}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Outfield Players:</span>
            <span className="text-slate-200">{team.roster.outfield_players.length} tracked</span>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="flex flex-col sm:flex-row gap-4 w-full">
      {renderTeam(team1, team1.name || 'PORTUGAL')}
      {renderTeam(team2, team2.name || 'SPAIN')}
    </div>
  );
};
