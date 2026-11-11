import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { api } from '../api/client';
import { CapacityMeter } from '../components/CapacityMeter';
import {
  Building2,
  MapPin,
  ArrowRight,
  Sun,
  CheckCircle2,
} from 'lucide-react';

export const HubOverviewPage: React.FC = () => {
  const { t } = useTranslation();

  // Load hubs
  const { data: hubs = [], isLoading: hubsLoading } = useQuery({
    queryKey: ['hubs'],
    queryFn: () => api.getHubs(),
  });

  // Load all active batches to compute per-hub capacity utilization
  const { data: activeBatches = [], isLoading: batchesLoading } = useQuery({
    queryKey: ['batches', 'active'],
    queryFn: () => api.getBatches('active'),
  });

  const isLoading = hubsLoading || batchesLoading;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-extrabold text-gray-900 tracking-tight flex items-center">
          <Building2 className="w-6 h-6 mr-2.5 text-brand-600" />
          {t('hubs.title')}
        </h1>
        <p className="mt-1 text-sm text-gray-600">{t('hubs.subtitle')}</p>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-64 bg-white rounded-2xl border border-gray-200 animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {hubs.map((hub) => {
            // Find active batches for this hub
            const hubBatches = activeBatches.filter((b) => b.hub_id === hub.id);
            const loadedWeight = hubBatches.reduce(
              (acc, b) => acc + (b.initial_weight_kg || 0),
              0
            );
            const maxCap = hub.total_capacity_kg || 200;
            const availableKg = Math.max(0, maxCap - loadedWeight);
            const isFull = availableKg <= 0;

            let hubDesc = 'Highland agroforestry zone';
            if (hub.location.toLowerCase().includes('tharaka')) {
              hubDesc = 'Semi-arid warm solar basin';
            } else if (hub.location.toLowerCase().includes('eldoret')) {
              hubDesc = 'High-altitude Western highlands';
            }

            return (
              <div
                key={hub.id}
                className="bg-white rounded-2xl border border-gray-200 p-6 shadow-2xs hover:shadow-md transition-shadow flex flex-col justify-between"
              >
                <div>
                  {/* Top Location & Badge */}
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <span className="inline-flex items-center text-xs font-bold text-brand-700 bg-brand-50 px-2.5 py-0.5 rounded-full mb-1">
                        <MapPin className="w-3 h-3 mr-1" />
                        {hub.location.toUpperCase()}
                      </span>
                      <h3 className="text-xl font-bold text-gray-900">{hub.name}</h3>
                      <p className="text-xs text-gray-500 mt-0.5">{hubDesc}</p>
                    </div>
                    <div className="w-10 h-10 rounded-xl bg-solar-50 flex items-center justify-center text-solar-600">
                      <Sun className="w-6 h-6" />
                    </div>
                  </div>

                  {/* Capacity Bar */}
                  <div className="my-5 p-4 bg-gray-50 rounded-xl border border-gray-100">
                    <div className="flex justify-between items-center text-xs font-bold text-gray-700 mb-2">
                      <span>{t('hubs.capacityUsed')}</span>
                      <span className={isFull ? 'text-red-600' : 'text-emerald-700'}>
                        {isFull ? t('hubs.full') : t('hubs.normal')}
                      </span>
                    </div>
                    <CapacityMeter
                      currentWeightKg={loadedWeight}
                      maxCapacityKg={maxCap}
                      showLabels={true}
                    />
                  </div>

                  {/* Hub Stats */}
                  <div className="grid grid-cols-2 gap-3 mb-4 text-center">
                    <div className="p-3 bg-brand-50/60 rounded-lg">
                      <span className="text-[10px] font-bold text-brand-700 uppercase block">
                        Active Batches
                      </span>
                      <span className="text-xl font-black text-brand-900">
                        {hubBatches.length}
                      </span>
                    </div>
                    <div className="p-3 bg-blue-50/60 rounded-lg">
                      <span className="text-[10px] font-bold text-blue-700 uppercase block">
                        Available Cap.
                      </span>
                      <span className="text-xl font-black text-blue-900">
                        {availableKg} kg
                      </span>
                    </div>
                  </div>

                  {/* Operator Info */}
                  <div className="text-xs text-gray-500 space-y-1 pt-3 border-t border-gray-100">
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-gray-600">Standard Tray Capacity:</span>
                      <span className="font-bold text-gray-900">{maxCap} kg</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-gray-600">IoT Sensor Node:</span>
                      <span className="font-semibold text-emerald-600 flex items-center">
                        <CheckCircle2 className="w-3 h-3 mr-1" />
                        Online
                      </span>
                    </div>
                  </div>
                </div>

                <div className="mt-5 pt-4 border-t border-gray-100">
                  <Link
                    to="/"
                    className="w-full inline-flex items-center justify-center px-4 py-2 text-xs font-bold text-brand-700 bg-brand-50 hover:bg-brand-100 rounded-lg transition-colors"
                  >
                    View Hub Active Batches
                    <ArrowRight className="w-3.5 h-3.5 ml-1.5" />
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
