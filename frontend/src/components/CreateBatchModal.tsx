import React, { useState, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Batch, CreateBatchDTO, Hub } from '../types';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Scale, AlertCircle, Plus } from 'lucide-react';

interface CreateBatchModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CreateBatchDTO) => Promise<void>;
  hubs: Hub[];
  defaultHubId?: string;
  activeBatches: Batch[];
}

export const CreateBatchModal: React.FC<CreateBatchModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  hubs,
  defaultHubId,
  activeBatches,
}) => {
  const { t } = useTranslation();
  const [hubId, setHubId] = useState(defaultHubId || (hubs[0]?.id ?? ''));
  const [cropType, setCropType] = useState('moringa');
  const [weightKg, setWeightKg] = useState<number | ''>(40);
  const [targetMoisture, setTargetMoisture] = useState<number | ''>('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Keep hubId synced if defaultHubId changes and no manual selection made
  React.useEffect(() => {
    if (defaultHubId) {
      setHubId(defaultHubId);
    } else if (hubs.length > 0 && !hubId) {
      setHubId(hubs[0].id);
    }
  }, [defaultHubId, hubs]);

  // Per ADR-0002: 200 kg capacity per regional solar dryer
  const maxCapacity = 200;
  const currentHubLoadedWeight = useMemo(() => {
    return activeBatches
      .filter((b) => b.hub_id === hubId && b.status === 'active')
      .reduce((acc, b) => acc + (b.initial_weight_kg || 0), 0);
  }, [activeBatches, hubId]);

  const availableWeight = Math.max(0, maxCapacity - currentHubLoadedWeight);
  const selectedHub = hubs.find((h) => h.id === hubId);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const weight = Number(weightKg);
    if (!weight || weight <= 0) {
      setError(t('modal.enterValidWeight'));
      return;
    }

    if (weight > availableWeight) {
      setError(
        t('modal.exceedsCapacity', {
          weight,
          available: availableWeight,
        })
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
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-md p-6">
        <DialogHeader className="mb-2">
          <div className="flex items-center space-x-2.5">
            <div className="w-9 h-9 rounded-lg bg-brand-100 text-brand-700 flex items-center justify-center">
              <Plus className="w-5 h-5" />
            </div>
            <div>
              <DialogTitle className="text-lg font-bold text-gray-900">
                {t('modal.createTitle')}
              </DialogTitle>
              <p className="text-xs text-muted-foreground">Register harvest for smart solar drying</p>
            </div>
          </div>
        </DialogHeader>

        {error && (
          <div className="rounded-lg bg-destructive/10 p-3 border border-destructive/20 flex items-start space-x-2 text-xs text-destructive font-medium">
            <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
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
                className="w-full text-sm border border-input rounded-lg p-2.5 bg-background focus:ring-2 focus:ring-brand-500"
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
              className="w-full text-sm border border-input rounded-lg p-2.5 bg-background focus:ring-2 focus:ring-brand-500"
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
              className="w-full text-sm border border-input rounded-lg p-2.5 focus:ring-2 focus:ring-brand-500"
              placeholder="e.g. 45"
            />
            <p className="mt-1 text-[11px] text-muted-foreground">
              {t('modal.capacityNotice', {
                hubName: selectedHub?.name || 'this dryer',
                available: availableWeight,
              })}
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
              className="w-full text-sm border border-input rounded-lg p-2.5 focus:ring-2 focus:ring-brand-500"
              placeholder="Leave empty for crop default (10% Moringa/Hibiscus, 12% Prunus)"
            />
          </div>

          {/* Actions */}
          <div className="flex space-x-3 pt-3 border-t border-border">
            <Button
              type="button"
              variant="secondary"
              onClick={onClose}
              className="w-1/2"
            >
              {t('modal.cancel')}
            </Button>
            <Button
              type="submit"
              variant="brand"
              disabled={submitting || availableWeight <= 0}
              className="w-1/2"
            >
              {submitting ? t('modal.submitting') : t('modal.submit')}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
};
