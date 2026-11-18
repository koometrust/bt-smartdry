/**
 * Shared formatting and calculation utilities for BT-SmartDry frontend.
 */

export const CROP_INITIAL_MOISTURE: Record<string, number> = {
  moringa: 78.0,
  hibiscus: 82.0,
  prunus: 70.0,
};

export const CROP_DEFAULT_TARGET_MOISTURE: Record<string, number> = {
  moringa: 10.0,
  hibiscus: 11.0,
  prunus: 12.0,
};

/**
 * Returns expected initial harvest moisture for a given crop type.
 */
export function getInitialMoistureForCrop(cropType: string): number {
  return CROP_INITIAL_MOISTURE[cropType.toLowerCase()] ?? 75.0;
}

/**
 * Calculate moisture progress percentage towards target based on crop initial moisture.
 */
export function calculateMoistureProgress(
  cropType: string,
  currentMoisture: number,
  targetMoisture: number
): number {
  const initM = getInitialMoistureForCrop(cropType);
  if (initM <= targetMoisture) return 100;
  const progress = ((initM - currentMoisture) / (initM - targetMoisture)) * 100;
  return Math.min(100, Math.max(0, Math.round(progress)));
}

/**
 * Format remaining decimal hours into clean hours and minutes.
 */
export function formatRemainingHours(remainingHours?: number | null): {
  hours: number;
  minutes: number;
  formatted: string;
} {
  const total = Math.max(0, remainingHours ?? 0);
  const hours = Math.floor(total);
  const minutes = Math.round((total - hours) * 60);

  let formatted = '';
  if (hours > 0) {
    formatted = `${hours}h ${minutes}m`;
  } else if (minutes > 0) {
    formatted = `${minutes}m`;
  } else {
    formatted = '< 1m';
  }

  return { hours, minutes, formatted };
}

/**
 * Calculate duration between start and end timestamps in hours and minutes.
 */
export function formatBatchDuration(startTime: string, endTime?: string | null): string {
  const start = new Date(startTime).getTime();
  const end = endTime ? new Date(endTime).getTime() : Date.now();
  const diffHours = (end - start) / (1000 * 60 * 60);

  if (diffHours < 0.1) return '< 10 mins';
  const h = Math.floor(diffHours);
  const m = Math.round((diffHours - h) * 60);
  return h > 0 ? `${h}h ${m}m` : `${m}m`;
}
