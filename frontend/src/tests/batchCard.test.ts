import { describe, it, expect } from 'vitest';
import {
  getInitialMoistureForCrop,
  calculateMoistureProgress,
  formatRemainingHours,
  formatBatchDuration,
} from '../utils/formatters';

describe('Batch Card Calculations & Formatters', () => {
  it('correctly retrieves crop-specific initial moisture baselines', () => {
    expect(getInitialMoistureForCrop('moringa')).toBe(78.0);
    expect(getInitialMoistureForCrop('hibiscus')).toBe(82.0);
    expect(getInitialMoistureForCrop('prunus')).toBe(70.0);
    // Case-insensitivity
    expect(getInitialMoistureForCrop('MORINGA')).toBe(78.0);
    expect(getInitialMoistureForCrop('UnknownCrop')).toBe(75.0);
  });

  it('calculates moisture decay progress percentage accurately', () => {
    // Moringa: 78% initial, target 10%
    // At 78%: 0% progress
    expect(calculateMoistureProgress('moringa', 78.0, 10.0)).toBe(0);
    // At 44% (halfway): 50% progress
    expect(calculateMoistureProgress('moringa', 44.0, 10.0)).toBe(50);
    // At 10%: 100% progress
    expect(calculateMoistureProgress('moringa', 10.0, 10.0)).toBe(100);
    // Over-dried at 8%: capped at 100%
    expect(calculateMoistureProgress('moringa', 8.0, 10.0)).toBe(100);

    // Prunus: 70% initial, target 12%
    // At 41%: (70-41)/(70-12) = 29/58 = 50%
    expect(calculateMoistureProgress('prunus', 41.0, 12.0)).toBe(50);
  });

  it('formats predicted remaining hours into clean human-readable countdowns', () => {
    expect(formatRemainingHours(4.5).formatted).toBe('4h 30m');
    expect(formatRemainingHours(1.0).formatted).toBe('1h 0m');
    expect(formatRemainingHours(0.75).formatted).toBe('45m');
    expect(formatRemainingHours(0.0).formatted).toBe('< 1m');
    expect(formatRemainingHours(-0.5).formatted).toBe('< 1m');
    expect(formatRemainingHours(null).formatted).toBe('< 1m');
  });

  it('formats batch drying duration between timestamps', () => {
    const startTime = new Date(Date.now() - 3.5 * 3600 * 1000).toISOString();
    const endTime = new Date(Date.now()).toISOString();
    expect(formatBatchDuration(startTime, endTime)).toBe('3h 30m');
  });
});
