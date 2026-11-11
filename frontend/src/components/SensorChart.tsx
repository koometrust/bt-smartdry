import React, { useState } from 'react';
import { Reading } from '../types';
import { useTranslation } from 'react-i18next';
import { TrendingDown, Thermometer, Droplets, Wind } from 'lucide-react';

interface SensorChartProps {
  readings: Reading[];
  targetMoisturePct: number;
}

export const SensorChart: React.FC<SensorChartProps> = ({
  readings,
  targetMoisturePct,
}) => {
  const { t } = useTranslation();
  const [activeMetric, setActiveMetric] = useState<'moisture' | 'temperature' | 'humidity' | 'vpd'>('moisture');

  if (!readings || readings.length === 0) {
    return (
      <div className="h-64 flex flex-col items-center justify-center bg-gray-50 rounded-xl border border-dashed border-gray-300 text-gray-500">
        <Wind className="w-8 h-8 mb-2 text-gray-400 animate-pulse" />
        <p className="text-sm font-medium">No sensor telemetry recorded yet for this batch.</p>
        <p className="text-xs text-gray-400 mt-1">Readings will appear automatically as sensors stream data.</p>
      </div>
    );
  }

  // Sort readings by timestamp ascending
  const sorted = [...readings].sort(
    (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
  );

  const pointsCount = sorted.length;
  const width = 600;
  const height = 220;
  const padding = { top: 20, right: 30, bottom: 30, left: 45 };

  const innerW = width - padding.left - padding.right;
  const innerH = height - padding.top - padding.bottom;

  // Extract series based on activeMetric
  let values: number[] = [];
  let unit = '';
  let color = '#16a34a'; // default brand green

  if (activeMetric === 'moisture') {
    values = sorted.map((r) => r.current_moisture);
    unit = '%';
    color = '#2563eb'; // blue
  } else if (activeMetric === 'temperature') {
    values = sorted.map((r) => r.temperature);
    unit = '°C';
    color = '#dc2626'; // red
  } else if (activeMetric === 'humidity') {
    values = sorted.map((r) => r.humidity);
    unit = '%';
    color = '#0891b2'; // cyan
  } else if (activeMetric === 'vpd') {
    values = sorted.map((r) => r.vpd);
    unit = ' kPa';
    color = '#7c3aed'; // purple
  }

  const minVal = Math.floor(Math.min(...values, activeMetric === 'moisture' ? targetMoisturePct : 0));
  const maxVal = Math.ceil(Math.max(...values, 10));
  const valRange = maxVal - minVal || 1;

  const getX = (index: number) => {
    if (pointsCount <= 1) return padding.left + innerW / 2;
    return padding.left + (index / (pointsCount - 1)) * innerW;
  };

  const getY = (val: number) => {
    return padding.top + innerH - ((val - minVal) / valRange) * innerH;
  };

  const pathD = sorted
    .map((_, i) => `${i === 0 ? 'M' : 'L'} ${getX(i).toFixed(1)} ${getY(values[i]).toFixed(1)}`)
    .join(' ');

  const areaD = `${pathD} L ${getX(pointsCount - 1)} ${padding.top + innerH} L ${getX(0)} ${padding.top + innerH} Z`;

  // Target moisture line for moisture view
  const targetY = activeMetric === 'moisture' ? getY(targetMoisturePct) : null;

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4 sm:p-5 shadow-sm">
      {/* Metric Toggle Tabs */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-gray-100 pb-3 mb-3">
        <h3 className="text-sm font-bold text-gray-900">{t('detail.telemetryChart')}</h3>
        <div className="flex items-center space-x-1 bg-gray-100 p-1 rounded-lg text-xs font-semibold">
          <button
            onClick={() => setActiveMetric('moisture')}
            className={`flex items-center px-2.5 py-1 rounded-md transition-colors ${
              activeMetric === 'moisture'
                ? 'bg-white text-blue-700 shadow-xs'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <TrendingDown className="w-3.5 h-3.5 mr-1" />
            Moisture
          </button>
          <button
            onClick={() => setActiveMetric('temperature')}
            className={`flex items-center px-2.5 py-1 rounded-md transition-colors ${
              activeMetric === 'temperature'
                ? 'bg-white text-red-700 shadow-xs'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Thermometer className="w-3.5 h-3.5 mr-1" />
            Temp
          </button>
          <button
            onClick={() => setActiveMetric('humidity')}
            className={`flex items-center px-2.5 py-1 rounded-md transition-colors ${
              activeMetric === 'humidity'
                ? 'bg-white text-cyan-700 shadow-xs'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Droplets className="w-3.5 h-3.5 mr-1" />
            Humidity
          </button>
          <button
            onClick={() => setActiveMetric('vpd')}
            className={`flex items-center px-2.5 py-1 rounded-md transition-colors ${
              activeMetric === 'vpd'
                ? 'bg-white text-purple-700 shadow-xs'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Wind className="w-3.5 h-3.5 mr-1" />
            VPD
          </button>
        </div>
      </div>

      {/* SVG Canvas */}
      <div className="w-full overflow-x-auto">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-56 sm:h-64 overflow-visible">
          <defs>
            <linearGradient id={`grad-${activeMetric}`} x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor={color} stopOpacity="0.25" />
              <stop offset="100%" stopColor={color} stopOpacity="0.0" />
            </linearGradient>
          </defs>

          {/* Grid lines */}
          {[0, 0.25, 0.5, 0.75, 1].map((pct) => {
            const y = padding.top + innerH * (1 - pct);
            const val = (minVal + pct * valRange).toFixed(1);
            return (
              <g key={pct}>
                <line
                  x1={padding.left}
                  y1={y}
                  x2={padding.left + innerW}
                  y2={y}
                  stroke="#f1f5f9"
                  strokeWidth="1"
                />
                <text
                  x={padding.left - 6}
                  y={y + 3}
                  textAnchor="end"
                  className="text-[10px] fill-gray-400 font-mono"
                >
                  {val}{unit}
                </text>
              </g>
            );
          })}

          {/* Target moisture dashed line */}
          {targetY !== null && (
            <g>
              <line
                x1={padding.left}
                y1={targetY}
                x2={padding.left + innerW}
                y2={targetY}
                stroke="#10b981"
                strokeWidth="1.5"
                strokeDasharray="4 3"
              />
              <text
                x={padding.left + innerW - 4}
                y={targetY - 4}
                textAnchor="end"
                className="text-[10px] fill-emerald-600 font-semibold"
              >
                Target {targetMoisturePct}%
              </text>
            </g>
          )}

          {/* Area fill and stroke line */}
          <path d={areaD} fill={`url(#grad-${activeMetric})`} />
          <path d={pathD} fill="none" stroke={color} strokeWidth="2.5" strokeLinecap="round" />

          {/* Data point dots */}
          {sorted.map((_, i) => (
            <circle
              key={i}
              cx={getX(i)}
              cy={getY(values[i])}
              r={pointsCount > 40 ? 2 : 3.5}
              fill="#ffffff"
              stroke={color}
              strokeWidth="2"
            />
          ))}
        </svg>
      </div>

      <div className="flex items-center justify-between text-xs text-gray-500 pt-2 border-t border-gray-100">
        <span>Start ({new Date(sorted[0].timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })})</span>
        <span className="font-semibold text-gray-700">Latest: {values[values.length - 1]}{unit}</span>
        <span>Now ({new Date(sorted[sorted.length - 1].timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })})</span>
      </div>
    </div>
  );
};

