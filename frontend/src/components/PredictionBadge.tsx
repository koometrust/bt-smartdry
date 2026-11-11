import React from 'react';
import { useTranslation } from 'react-i18next';
import { QualityGrade } from '../types';
import { Badge } from '@/components/ui/badge';
import { Award, CheckCircle, AlertTriangle } from 'lucide-react';

interface PredictionBadgeProps {
  grade?: QualityGrade | string;
  size?: 'sm' | 'md' | 'lg';
}

export const PredictionBadge: React.FC<PredictionBadgeProps> = ({ grade, size = 'md' }) => {
  const { t } = useTranslation();

  if (!grade) {
    return (
      <Badge variant="outline" className="text-gray-500 font-normal">
        Pending reading
      </Badge>
    );
  }

  const normalized = grade.toLowerCase();
  let variant: 'export' | 'standard' | 'downgraded' = 'standard';
  let Icon = CheckCircle;
  let labelKey = 'grades.standard';

  if (normalized === 'export') {
    variant = 'export';
    Icon = Award;
    labelKey = 'grades.export';
  } else if (normalized === 'standard') {
    variant = 'standard';
    Icon = CheckCircle;
    labelKey = 'grades.standard';
  } else if (normalized === 'downgraded') {
    variant = 'downgraded';
    Icon = AlertTriangle;
    labelKey = 'grades.downgraded';
  }

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-xs px-2.5 py-1',
    lg: 'text-sm px-3 py-1.5 font-bold',
  }[size];

  return (
    <Badge variant={variant} className={`font-semibold shadow-2xs ${sizeClasses}`}>
      <Icon className="w-3.5 h-3.5 mr-1.5 flex-shrink-0" />
      {t(labelKey)}
    </Badge>
  );
};
