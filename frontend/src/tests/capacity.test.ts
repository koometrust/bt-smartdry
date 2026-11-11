import { describe, it, expect } from 'vitest';

describe('Hub Dryer Capacity (ADR-0002)', () => {
  const MAX_CAPACITY = 200;

  function calculateAvailableCapacity(loadedKg: number, maxKg: number = MAX_CAPACITY): number {
    return Math.max(0, maxKg - loadedKg);
  }

  function validateNewBatchWeight(newWeightKg: number, loadedKg: number, maxKg: number = MAX_CAPACITY): boolean {
    if (newWeightKg <= 0) return false;
    const available = calculateAvailableCapacity(loadedKg, maxKg);
    return newWeightKg <= available;
  }

  it('correctly calculates available capacity under 200 kg limit', () => {
    expect(calculateAvailableCapacity(0)).toBe(200);
    expect(calculateAvailableCapacity(45)).toBe(155);
    expect(calculateAvailableCapacity(180)).toBe(20);
    expect(calculateAvailableCapacity(200)).toBe(0);
    expect(calculateAvailableCapacity(220)).toBe(0);
  });

  it('rejects batch weights that exceed available capacity', () => {
    // 150 kg currently loaded, 50 kg available
    expect(validateNewBatchWeight(40, 150)).toBe(true);
    expect(validateNewBatchWeight(50, 150)).toBe(true);
    expect(validateNewBatchWeight(51, 150)).toBe(false);
    expect(validateNewBatchWeight(0, 150)).toBe(false);
    expect(validateNewBatchWeight(-5, 150)).toBe(false);
  });
});

