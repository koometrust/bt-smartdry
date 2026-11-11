import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { api } from '../api/client';
import {
  BarChart3,
  Award,
  Scale,
  Layers,
  PieChart,
  Building2,
} from 'lucide-react';

export const AnalyticsPage: React.FC = () => {
  const { t } = useTranslation();

  // Load all batches (completed and active)
  const { data: allBatches = [], isLoading } = useQuery({
    queryKey: ['batches', 'all'],
    queryFn: () => api.getBatches(),
  });



  // Calculate Metrics
  const totalBatches = allBatches.length;
  const completedBatches = allBatches.filter((b) => b.status === 'completed');
  const totalWeightKg = allBatches.reduce((acc, b) => acc + (b.initial_weight_kg || 0), 0);

  // Quality grades breakdown
  let exportCount = 0;
  let standardCount = 0;
  let downgradedCount = 0;

  allBatches.forEach((b) => {
    const grade = (b.final_quality_grade || b.predicted_quality_grade || 'standard').toLowerCase();
    if (grade === 'export') exportCount++;
    else if (grade === 'downgraded') downgradedCount++;
    else standardCount++;
  });

  const exportRatePct = totalBatches > 0 ? Math.round((exportCount / totalBatches) * 100) : 0;

  // Crops breakdown
  const cropCounts: Record<string, { count: number; weight: number }> = {
    moringa: { count: 0, weight: 0 },
    hibiscus: { count: 0, weight: 0 },
    prunus: { count: 0, weight: 0 },
  };

  allBatches.forEach((b) => {
    const c = b.crop_type.toLowerCase();
    if (!cropCounts[c]) cropCounts[c] = { count: 0, weight: 0 };
    cropCounts[c].count++;
    cropCounts[c].weight += b.initial_weight_kg || 0;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight flex items-center">
          <BarChart3 className="w-6 h-6 mr-2.5 text-brand-600" />
          {t('analytics.title')}
        </h1>
        <p className="mt-1 text-sm text-gray-600">{t('analytics.subtitle')}</p>
      </div>

      {isLoading ? (
        <div className="h-64 bg-white rounded-2xl border border-gray-200 animate-pulse" />
      ) : (
        <>
          {/* Top KPI Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white rounded-2xl border border-gray-200 p-5 shadow-2xs">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">
                  Total Batches
                </span>
                <div className="w-8 h-8 rounded-lg bg-brand-50 text-brand-700 flex items-center justify-center">
                  <Layers className="w-4 h-4" />
                </div>
              </div>
              <p className="mt-3 text-3xl font-black text-gray-900">{totalBatches}</p>
              <p className="mt-1 text-xs text-gray-500">{completedBatches.length} completed cycles</p>
            </div>

            <div className="bg-white rounded-2xl border border-gray-200 p-5 shadow-2xs">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">
                  Total Weight
                </span>
                <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-700 flex items-center justify-center">
                  <Scale className="w-4 h-4" />
                </div>
              </div>
              <p className="mt-3 text-3xl font-black text-gray-900">{totalWeightKg.toLocaleString()} kg</p>
              <p className="mt-1 text-xs text-gray-500">Across 3 regional hubs</p>
            </div>

            <div className="bg-white rounded-2xl border border-gray-200 p-5 shadow-2xs">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">
                  Export Quality Rate
                </span>
                <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-700 flex items-center justify-center">
                  <Award className="w-4 h-4" />
                </div>
              </div>
              <p className="mt-3 text-3xl font-black text-emerald-600">{exportRatePct}%</p>
              <p className="mt-1 text-xs text-emerald-700 font-medium">Optimal solar moisture range</p>
            </div>

            <div className="bg-white rounded-2xl border border-gray-200 p-5 shadow-2xs">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">
                  Dryer Capacity Limit
                </span>
                <div className="w-8 h-8 rounded-lg bg-purple-50 text-purple-700 flex items-center justify-center">
                  <Building2 className="w-4 h-4" />
                </div>
              </div>
              <p className="mt-3 text-3xl font-black text-gray-900">200 kg</p>
              <p className="mt-1 text-xs text-gray-500">Max per hub per ADR-0002</p>
            </div>
          </div>

          {/* Charts Row: Grade Breakdown & Crop Breakdown */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Grade Distribution */}
            <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-2xs">
              <h3 className="text-base font-bold text-gray-900 mb-4 flex items-center">
                <Award className="w-4 h-4 mr-2 text-brand-600" />
                {t('analytics.gradeDistribution')}
              </h3>

              <div className="space-y-4">
                {/* Export */}
                <div>
                  <div className="flex justify-between text-xs font-bold mb-1">
                    <span className="text-emerald-800">Export Grade (Highest Premium)</span>
                    <span className="text-emerald-900">
                      {exportCount} ({totalBatches > 0 ? Math.round((exportCount / totalBatches) * 100) : 0}%)
                    </span>
                  </div>
                  <div className="h-3 w-full bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-emerald-500 rounded-full"
                      style={{
                        width: `${totalBatches > 0 ? (exportCount / totalBatches) * 100 : 0}%`,
                      }}
                    />
                  </div>
                </div>

                {/* Standard */}
                <div>
                  <div className="flex justify-between text-xs font-bold mb-1">
                    <span className="text-blue-800">Standard Grade</span>
                    <span className="text-blue-900">
                      {standardCount} ({totalBatches > 0 ? Math.round((standardCount / totalBatches) * 100) : 0}%)
                    </span>
                  </div>
                  <div className="h-3 w-full bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-blue-500 rounded-full"
                      style={{
                        width: `${totalBatches > 0 ? (standardCount / totalBatches) * 100 : 0}%`,
                      }}
                    />
                  </div>
                </div>

                {/* Downgraded */}
                <div>
                  <div className="flex justify-between text-xs font-bold mb-1">
                    <span className="text-amber-800">Downgraded (Over/Under dried)</span>
                    <span className="text-amber-900">
                      {downgradedCount} ({totalBatches > 0 ? Math.round((downgradedCount / totalBatches) * 100) : 0}%)
                    </span>
                  </div>
                  <div className="h-3 w-full bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-amber-500 rounded-full"
                      style={{
                        width: `${totalBatches > 0 ? (downgradedCount / totalBatches) * 100 : 0}%`,
                      }}
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Crop Throughput */}
            <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-2xs">
              <h3 className="text-base font-bold text-gray-900 mb-4 flex items-center">
                <PieChart className="w-4 h-4 mr-2 text-brand-600" />
                {t('analytics.cropBreakdown')}
              </h3>

              <div className="space-y-4">
                {Object.entries(cropCounts).map(([crop, data]) => {
                  const pct = totalWeightKg > 0 ? Math.round((data.weight / totalWeightKg) * 100) : 0;
                  const label = t(`crops.${crop}`) || crop;

                  return (
                    <div key={crop}>
                      <div className="flex justify-between text-xs font-bold mb-1">
                        <span className="text-gray-800 capitalize">{label}</span>
                        <span className="text-gray-900">
                          {data.weight} kg ({pct}%)
                        </span>
                      </div>
                      <div className="h-3 w-full bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-brand-600 rounded-full"
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
