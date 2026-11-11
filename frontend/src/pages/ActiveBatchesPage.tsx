import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import { api } from '../api/client';
import { PredictionBadge } from '../components/PredictionBadge';
import { CapacityMeter } from '../components/CapacityMeter';
import { CreateBatchModal } from '../components/CreateBatchModal';
import {
  Layers,
  Plus,
  Clock,
  Droplets,
  ArrowRight,
  CheckCircle,
  Building2,
  RefreshCw,
} from 'lucide-react';

export const ActiveBatchesPage: React.FC = () => {
  const { user, isAdmin } = useAuth();
  const { t } = useTranslation();
  const queryClient = useQueryClient();

  const [selectedHubId, setSelectedHubId] = useState<string>('');
  const [modalOpen, setModalOpen] = useState(false);

  // Load hubs
  const { data: hubs = [] } = useQuery({
    queryKey: ['hubs'],
    queryFn: () => api.getHubs(),
  });

  // Effective hub id for operator vs admin
  const effectiveHubId = isAdmin
    ? selectedHubId || undefined
    : user?.hub_id || undefined;

  // Load active batches with 30s polling
  const {
    data: batches = [],
    isLoading,
    isRefetching,
    refetch,
  } = useQuery({
    queryKey: ['batches', 'active', effectiveHubId],
    queryFn: () => api.getBatches('active', effectiveHubId),
    refetchInterval: 30000,
  });

  // Create Batch Mutation
  const createMutation = useMutation({
    mutationFn: (data: {
      hub_id: string;
      crop_type: string;
      initial_weight_kg: number;
      target_moisture_pct?: number;
    }) => api.createBatch(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['batches'] });
    },
  });

  // Complete Batch Mutation
  const completeMutation = useMutation({
    mutationFn: (id: string) => api.updateBatch(id, { status: 'completed' }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['batches'] });
    },
  });

  // Calculate current loaded weight in the selected hub for capacity check
  const currentLoadedWeight = batches.reduce(
    (acc, b) => acc + (b.initial_weight_kg || 0),
    0
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="sm:flex sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight flex items-center">
            <Layers className="w-6 h-6 mr-2.5 text-brand-600" />
            {t('batches.title')}
          </h1>
          <p className="mt-1 text-sm text-gray-600">{t('batches.subtitle')}</p>
        </div>
        <div className="mt-4 sm:mt-0 flex items-center space-x-2.5">
          <button
            onClick={() => refetch()}
            className="p-2 text-gray-500 hover:text-gray-700 bg-white border border-gray-300 rounded-lg shadow-2xs hover:bg-gray-50 transition-colors"
            title="Refresh now"
          >
            <RefreshCw className={`w-4 h-4 ${isRefetching ? 'animate-spin text-brand-600' : ''}`} />
          </button>
          <button
            onClick={() => setModalOpen(true)}
            className="inline-flex items-center px-4 py-2 text-sm font-semibold text-white bg-brand-600 hover:bg-brand-700 rounded-lg shadow-xs transition-colors"
          >
            <Plus className="w-4 h-4 mr-1.5" />
            {t('batches.createNew')}
          </button>
        </div>
      </div>

      {/* Admin Hub Filter Tabs */}
      {isAdmin && hubs.length > 0 && (
        <div className="flex items-center space-x-1.5 overflow-x-auto pb-1 border-b border-gray-200">
          <button
            onClick={() => setSelectedHubId('')}
            className={`px-3 py-1.5 text-xs font-bold rounded-lg transition-colors whitespace-nowrap ${
              selectedHubId === ''
                ? 'bg-brand-600 text-white shadow-xs'
                : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'
            }`}
          >
            {t('batches.allHubs')}
          </button>
          {hubs.map((hub) => (
            <button
              key={hub.id}
              onClick={() => setSelectedHubId(hub.id)}
              className={`flex items-center px-3 py-1.5 text-xs font-bold rounded-lg transition-colors whitespace-nowrap ${
                selectedHubId === hub.id
                  ? 'bg-brand-600 text-white shadow-xs'
                  : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'
              }`}
            >
              <Building2 className="w-3.5 h-3.5 mr-1" />
              {hub.name}
            </button>
          ))}
        </div>
      )}

      {/* Hub Dryer Capacity Meter banner (per ADR-0002) */}
      <div className="bg-white rounded-xl border border-gray-200 p-4 shadow-2xs">
        <div className="sm:flex sm:items-center sm:justify-between mb-2">
          <div className="text-xs font-bold text-gray-700 uppercase tracking-wider">
            Dryer Capacity Utilization (200 kg Max)
          </div>
          <div className="text-xs text-gray-500">
            {batches.length} active batch{batches.length !== 1 ? 'es' : ''} currently drying
          </div>
        </div>
        <CapacityMeter currentWeightKg={currentLoadedWeight} maxCapacityKg={200} />
      </div>

      {/* Batches Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white rounded-2xl border border-gray-200 p-6 h-64 animate-pulse" />
          ))}
        </div>
      ) : batches.length === 0 ? (
        <div className="bg-white rounded-2xl border border-dashed border-gray-300 p-12 text-center">
          <Layers className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <h3 className="text-base font-bold text-gray-900">{t('batches.noActive')}</h3>
          <p className="mt-1 text-sm text-gray-500">
            Click &quot;New Batch&quot; or start the simulator to feed real-time drying data.
          </p>
          <button
            onClick={() => setModalOpen(true)}
            className="mt-4 inline-flex items-center px-4 py-2 text-sm font-semibold text-white bg-brand-600 rounded-lg hover:bg-brand-700 shadow-xs"
          >
            <Plus className="w-4 h-4 mr-1.5" />
            {t('batches.createNew')}
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {batches.map((batch) => {
            const cropName =
              t(`crops.${batch.crop_type.toLowerCase()}`) || batch.crop_type;
            const hub = hubs.find((h) => h.id === batch.hub_id);

            // Remaining hours formatting
            const remHours = batch.predicted_remaining_hours ?? 0;
            const h = Math.floor(remHours);
            const m = Math.round((remHours - h) * 60);

            // Moisture progress estimate
            const currM = batch.current_moisture_pct ?? 75;
            const targetM = batch.target_moisture_pct;
            const moistureProgress = Math.min(
              100,
              Math.max(0, Math.round(((75 - currM) / (75 - targetM)) * 100))
            );

            return (
              <div
                key={batch.id}
                className="bg-white rounded-2xl border border-gray-200 p-5 shadow-2xs hover:shadow-md transition-shadow flex flex-col justify-between"
              >
                <div>
                  {/* Top: Hub & Crop */}
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <span className="text-[11px] font-bold uppercase tracking-wider text-brand-700 bg-brand-50 px-2 py-0.5 rounded">
                        {hub?.name || 'Solar Dryer'}
                      </span>
                      <h3 className="text-lg font-bold text-gray-900 mt-1">{cropName}</h3>
                    </div>
                    <PredictionBadge grade={batch.predicted_quality_grade} size="sm" />
                  </div>

                  {/* Weight and moisture metric row */}
                  <div className="grid grid-cols-2 gap-2 my-3 p-3 bg-gray-50 rounded-xl text-center">
                    <div>
                      <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider block">
                        {t('batches.initialWeight')}
                      </span>
                      <span className="text-base font-extrabold text-gray-900">
                        {batch.initial_weight_kg} kg
                      </span>
                    </div>
                    <div>
                      <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider block">
                        {t('batches.currentMoisture')}
                      </span>
                      <span className="text-base font-extrabold text-blue-600 flex items-center justify-center">
                        <Droplets className="w-4 h-4 mr-0.5 text-blue-500" />
                        {batch.current_moisture_pct !== undefined
                          ? `${batch.current_moisture_pct}%`
                          : 'Pending'}
                      </span>
                    </div>
                  </div>

                  {/* Moisture Progress Bar */}
                  <div className="mb-4">
                    <div className="flex justify-between text-xs text-gray-500 mb-1 font-medium">
                      <span>Drying Progress</span>
                      <span>Target: {targetM}%</span>
                    </div>
                    <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
                      <div
                        className="bg-brand-600 h-full rounded-full transition-all duration-300"
                        style={{ width: `${moistureProgress}%` }}
                      />
                    </div>
                  </div>

                  {/* Estimated remaining drying time countdown */}
                  <div className="flex items-center justify-between text-xs text-gray-700 py-2 border-t border-gray-100">
                    <span className="flex items-center text-gray-600">
                      <Clock className="w-3.5 h-3.5 mr-1 text-gray-400" />
                      {t('batches.remainingTime')}:
                    </span>
                    <span className="font-extrabold text-gray-900">
                      {remHours > 0 ? `${h}h ${m}m` : 'Target reached'}
                    </span>
                  </div>
                </div>

                {/* Bottom action buttons */}
                <div className="mt-4 pt-3 border-t border-gray-100 flex items-center space-x-2">
                  <Link
                    to={`/batches/${batch.id}`}
                    className="flex-1 inline-flex items-center justify-center px-3 py-2 text-xs font-bold text-brand-700 bg-brand-50 hover:bg-brand-100 rounded-lg transition-colors"
                  >
                    {t('batches.viewDetails')}
                    <ArrowRight className="w-3.5 h-3.5 ml-1" />
                  </Link>
                  <button
                    onClick={() => {
                      if (window.confirm(t('batches.confirmComplete'))) {
                        completeMutation.mutate(batch.id);
                      }
                    }}
                    className="p-2 text-gray-400 hover:text-emerald-600 hover:bg-emerald-50 rounded-lg transition-colors"
                    title={t('batches.completeBatch')}
                  >
                    <CheckCircle className="w-5 h-5" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Modal for creating batch */}
      <CreateBatchModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onSubmit={async (data) => {
          await createMutation.mutateAsync(data);
        }}
        hubs={hubs}
        defaultHubId={effectiveHubId}
        currentLoadedWeight={currentLoadedWeight}
      />
    </div>
  );
};

