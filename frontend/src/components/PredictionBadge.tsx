import React from 'react';
import { useTranslation } from 'react-i18next';
import { QualityGrade } from '../types';
import { Award, CheckCircle, AlertTriangle } from 'lucide-react';

interface PredictionBadgeProps {
  grade?: QualityGrade | string;
  size?: 'sm' | 'md' | 'lg';
}

export const PredictionBadge: React.FC<PredictionBadgeProps> = ({ grade, size = 'md' }) => {
  const { t } = useTranslation();

  if (!grade) {
    return (
      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-600">
        Pending reading
      </span>
    );
  }

  const normalized = grade.toLowerCase();

  let colorClasses = 'bg-gray-100 text-gray-800 border-gray-200';
  let Icon = CheckCircle;
  let labelKey = 'grades.standard';

  if (normalized === 'export') {
    colorClasses = 'bg-emerald-50 text-emerald-800 border-emerald-300 ring-1 ring-emerald-500/20';
    Icon = Award;
    labelKey = 'grades.export';
  } else if (normalized === 'standard') {
    colorClasses = 'bg-blue-50 text-blue-800 border-blue-300 ring-1 ring-blue-500/20';
    Icon = CheckCircle;
    labelKey = 'grades.standard';
  } else if (normalized === 'downgraded') {
    colorClasses = 'bg-amber-50 text-amber-800 border-amber-300 ring-1 ring-amber-500/20';
    Icon = AlertTriangle;
    labelKey = 'grades.downgraded';
  }

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-xs sm:text-sm px-2.5 py-1',
    lg: 'text-sm sm:text-base px-3 py-1.5 font-bold',
  }[size];

  return (
    <span
      className={`inline-flex items-center font-semibold rounded-full border shadow-sm ${colorClasses} ${sizeClasses}`}
    >
      <Icon className="w-3.5 h-3.5 mr-1.5 flex-shrink-0" />
      {t(labelKey)}
    </span>
  );
};

