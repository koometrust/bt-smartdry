import React from 'react';
import { useTranslation } from 'react-i18next';
import { Progress } from '@/components/ui/progress';
import { Scale } from 'lucide-react';

interface CapacityMeterProps {
  currentWeightKg: number;
  maxCapacityKg?: number;
  showLabels?: boolean;
}

export const CapacityMeter: React.FC<CapacityMeterProps> = ({
  currentWeightKg,
  maxCapacityKg = 200,
  showLabels = true,
}) => {
  const { t } = useTranslation();
  const pct = Math.min(100, Math.round((currentWeightKg / maxCapacityKg) * 100));
  const available = Math.max(0, maxCapacityKg - currentWeightKg);

  let indicatorColor = 'bg-brand-600';
  if (pct > 90) {
    indicatorColor = 'bg-red-500';
  } else if (pct > 75) {
    indicatorColor = 'bg-amber-500';
  }

  return (
    <div className="w-full">
      {showLabels && (
        <div className="flex justify-between items-center text-xs mb-1.5">
          <span className="flex items-center font-medium text-gray-700">
            <Scale className="w-3.5 h-3.5 mr-1 text-gray-500" />
            {t('hubs.kgLoaded', { loaded: currentWeightKg })}
          </span>
          <span className="font-semibold text-gray-900">{pct}% ({available} kg free)</span>
        </div>
      )}
      <Progress value={pct} indicatorClassName={indicatorColor} className="h-2.5" />
    </div>
  );
};
