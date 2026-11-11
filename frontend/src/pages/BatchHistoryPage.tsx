import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { api } from '../api/client';
import { PredictionBadge } from '../components/PredictionBadge';
import { History, Filter, ArrowRight } from 'lucide-react';

export const BatchHistoryPage: React.FC = () => {
  const { t } = useTranslation();
  const [selectedCrop, setSelectedCrop] = useState<string>('all');
  const [selectedGrade, setSelectedGrade] = useState<string>('all');

  const { data: batches = [], isLoading } = useQuery({
    queryKey: ['batches', 'completed'],
    queryFn: () => api.getBatches('completed'),
  });

  const filtered = batches.filter((b) => {
    if (selectedCrop !== 'all' && b.crop_type.toLowerCase() !== selectedCrop) {
      return false;
    }
    const finalGrade = (b.final_quality_grade || b.predicted_quality_grade || '').toLowerCase();
    if (selectedGrade !== 'all' && finalGrade !== selectedGrade) {
      return false;
    }
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="sm:flex sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight flex items-center">
            <History className="w-6 h-6 mr-2.5 text-brand-600" />
            {t('history.title')}
          </h1>
          <p className="mt-1 text-sm text-gray-600">{t('history.subtitle')}</p>
        </div>
        <div className="mt-2 text-xs font-semibold text-gray-500">
          {t('history.totalCompleted', { count: batches.length })}
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-white rounded-xl border border-gray-200 p-3.5 shadow-2xs flex flex-wrap items-center gap-3">
        <div className="flex items-center text-xs font-bold text-gray-500 uppercase tracking-wider mr-1">
          <Filter className="w-3.5 h-3.5 mr-1" />
          Filter:
        </div>
        {/* Crop filter */}
        <select
          value={selectedCrop}
          onChange={(e) => setSelectedCrop(e.target.value)}
          className="text-xs border border-gray-300 rounded-lg py-1.5 px-2.5 bg-gray-50 font-medium text-gray-800"
        >
          <option value="all">All Crops</option>
          <option value="moringa">Moringa</option>
          <option value="hibiscus">Hibiscus</option>
          <option value="prunus">Prunus</option>
        </select>

        {/* Grade filter */}
        <select
          value={selectedGrade}
          onChange={(e) => setSelectedGrade(e.target.value)}
          className="text-xs border border-gray-300 rounded-lg py-1.5 px-2.5 bg-gray-50 font-medium text-gray-800"
        >
          <option value="all">{t('history.allGrades')}</option>
          <option value="export">Export Grade</option>
          <option value="standard">Standard Grade</option>
          <option value="downgraded">Downgraded</option>
        </select>
      </div>

      {/* Table / List View */}
      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 bg-white rounded-xl border border-gray-200 animate-pulse" />
          ))}
        </div>
      ) : filtered.length === 0 ? (
        <div className="bg-white rounded-2xl border border-dashed border-gray-300 p-12 text-center text-gray-500">
          <History className="w-10 h-10 text-gray-300 mx-auto mb-2" />
          <p className="font-semibold text-sm">{t('history.noHistory')}</p>
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-gray-200 shadow-2xs overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 text-left text-sm">
              <thead className="bg-gray-50 text-gray-500 text-xs font-bold uppercase tracking-wider">
                <tr>
                  <th className="py-3 px-4">Batch / Crop</th>
                  <th className="py-3 px-4">Harvest Weight</th>
                  <th className="py-3 px-4">Final Moisture</th>
                  <th className="py-3 px-4">Final Quality Grade</th>
                  <th className="py-3 px-4">Completed Date</th>
                  <th className="py-3 px-4 text-right">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100 bg-white">
                {filtered.map((batch) => {
                  const finalGrade = batch.final_quality_grade || batch.predicted_quality_grade || 'standard';
                  const endDate = batch.end_time ? new Date(batch.end_time).toLocaleDateString() : 'N/A';

                  return (
                    <tr key={batch.id} className="hover:bg-gray-50/80 transition-colors">
                      <td className="py-3.5 px-4">
                        <div className="font-bold text-gray-900">
                          {t(`crops.${batch.crop_type.toLowerCase()}`) || batch.crop_type}
                        </div>
                        <div className="text-[11px] font-mono text-gray-400">
                          #{batch.id.slice(0, 8)}
                        </div>
                      </td>
                      <td className="py-3.5 px-4 font-semibold text-gray-700">
                        {batch.initial_weight_kg} kg
                      </td>
                      <td className="py-3.5 px-4">
                        <span className="font-bold text-blue-600">
                          {batch.current_moisture_pct !== undefined ? `${batch.current_moisture_pct}%` : `${batch.target_moisture_pct}%`}
                        </span>
                        <span className="text-[11px] text-gray-400 block">
                          Target: {batch.target_moisture_pct}%
                        </span>
                      </td>
                      <td className="py-3.5 px-4">
                        <PredictionBadge grade={finalGrade} size="sm" />
                      </td>
                      <td className="py-3.5 px-4 text-xs text-gray-600 font-medium">
                        {endDate}
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <Link
                          to={`/batches/${batch.id}`}
                          className="inline-flex items-center text-xs font-bold text-brand-700 hover:text-brand-900 bg-brand-50 hover:bg-brand-100 py-1 px-2.5 rounded transition-colors"
                        >
                          View
                          <ArrowRight className="w-3 h-3 ml-1" />
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
