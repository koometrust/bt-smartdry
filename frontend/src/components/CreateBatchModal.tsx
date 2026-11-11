import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Hub } from '../types';
import { X, Scale, AlertCircle, Plus } from 'lucide-react';

interface CreateBatchModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: {
    hub_id: string;
    crop_type: string;
    initial_weight_kg: number;
    target_moisture_pct?: number;
  }) => Promise<void>;
  hubs: Hub[];
  defaultHubId?: string;
  currentLoadedWeight: number; // weight currently active in this hub
}

export const CreateBatchModal: React.FC<CreateBatchModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  hubs,
  defaultHubId,
  currentLoadedWeight,
}) => {
  const { t } = useTranslation();
  const [hubId, setHubId] = useState(defaultHubId || (hubs[0]?.id ?? ''));
  const [cropType, setCropType] = useState('moringa');
  const [weightKg, setWeightKg] = useState<number | ''>(40);
  const [targetMoisture, setTargetMoisture] = useState<number | ''>('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  if (!isOpen) return null;

  const maxCapacity = 200;
  const availableWeight = Math.max(0, maxCapacity - currentLoadedWeight);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const weight = Number(weightKg);
    if (!weight || weight <= 0) {
      setError('Please enter a valid harvest weight.');
      return;
    }

    if (weight > availableWeight) {
      setError(
        `Batch weight (${weight} kg) exceeds available capacity (${availableWeight} kg) of this 200 kg solar dryer!`
      );
      return;
    }

    setSubmitting(true);
    try {
      await onSubmit({
        hub_id: hubId,
        crop_type: cropType,
        initial_weight_kg: weight,
        target_moisture_pct: targetMoisture !== '' ? Number(targetMoisture) : undefined,
      });
      onClose();
    } catch (err: any) {
      setError(err?.message || 'Failed to register batch');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-gray-100 relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 p-1"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-2.5 mb-4">
          <div className="w-9 h-9 rounded-lg bg-brand-100 text-brand-700 flex items-center justify-center">
            <Plus className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-gray-900">{t('modal.createTitle')}</h3>
            <p className="text-xs text-gray-500">Register harvest for smart solar drying</p>
          </div>
        </div>

        {error && (
          <div className="mb-4 rounded-lg bg-red-50 p-3 border border-red-200 flex items-start space-x-2 text-xs text-red-800 font-medium">
            <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Hub selection */}
          {hubs.length > 1 && (
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-gray-700 mb-1">
                {t('modal.hub')}
              </label>
              <select
                value={hubId}
                onChange={(e) => setHubId(e.target.value)}
                className="w-full text-sm border border-gray-300 rounded-lg p-2.5 bg-white focus:ring-2 focus:ring-brand-500"
              >
                {hubs.map((h) => (
                  <option key={h.id} value={h.id}>
                    {h.name} ({h.location})
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Crop Type */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-gray-700 mb-1">
              {t('modal.cropType')}
            </label>
            <select
              value={cropType}
              onChange={(e) => setCropType(e.target.value)}
              className="w-full text-sm border border-gray-300 rounded-lg p-2.5 bg-white focus:ring-2 focus:ring-brand-500"
            >
              <option value="moringa">🌿 {t('crops.moringa')}</option>
              <option value="hibiscus">🌺 {t('crops.hibiscus')}</option>
              <option value="prunus">🌳 {t('crops.prunus')}</option>
            </select>
          </div>

          {/* Initial Weight */}
          <div>
            <div className="flex justify-between items-center mb-1">
              <label className="block text-xs font-bold uppercase tracking-wider text-gray-700">
                {t('modal.weightKg')}
              </label>
              <span className="text-xs font-semibold text-brand-700 flex items-center">
                <Scale className="w-3.5 h-3.5 mr-1" />
                {availableWeight} kg free
              </span>
            </div>
            <input
              type="number"
              min="1"
              max={availableWeight}
              step="0.5"
              required
              value={weightKg}
              onChange={(e) => setWeightKg(e.target.value === '' ? '' : parseFloat(e.target.value))}
              className="w-full text-sm border border-gray-300 rounded-lg p-2.5 focus:ring-2 focus:ring-brand-500"
              placeholder="e.g. 45"
            />
            <p className="mt-1 text-[11px] text-gray-500">
              {t('modal.capacityNotice', { available: availableWeight })}
            </p>
          </div>

          {/* Optional Target Moisture */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-gray-700 mb-1">
              {t('modal.targetMoisturePct')}
            </label>
            <input
              type="number"
              min="5"
              max="25"
              step="0.5"
              value={targetMoisture}
              onChange={(e) =>
                setTargetMoisture(e.target.value === '' ? '' : parseFloat(e.target.value))
              }
              className="w-full text-sm border border-gray-300 rounded-lg p-2.5 focus:ring-2 focus:ring-brand-500"
              placeholder="Leave empty for crop default (10% Moringa/Hibiscus, 12% Prunus)"
            />
          </div>

          {/* Actions */}
          <div className="flex space-x-3 pt-3 border-t border-gray-100">
            <button
              type="button"
              onClick={onClose}
              className="w-1/2 py-2.5 px-4 text-sm font-semibold text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            >
              {t('modal.cancel')}
            </button>
            <button
              type="submit"
              disabled={submitting || availableWeight <= 0}
              className="w-1/2 py-2.5 px-4 text-sm font-semibold text-white bg-brand-600 hover:bg-brand-700 rounded-lg transition-colors disabled:opacity-50"
            >
              {submitting ? t('modal.submitting') : t('modal.submit')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

