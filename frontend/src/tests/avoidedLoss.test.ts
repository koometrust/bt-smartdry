import { describe, it, expect } from 'vitest';
import en from '../i18n/locales/en.json';
import sw from '../i18n/locales/sw.json';
import { Batch } from '../types';

describe('Avoided Post-Harvest Loss UI & Translations', () => {
  it('should have complete bilingual translations for avoided loss metrics and disclaimers', () => {
    expect(en.loss.title).toBe('Avoided Post-Harvest Loss');
    expect(sw.loss.title).toBe('Kupunguza Upotevu Baada ya Mavuno');

    expect(en.loss.biomassPreserved).toBeDefined();
    expect(sw.loss.biomassPreserved).toBeDefined();

    expect(en.loss.economicValue).toBeDefined();
    expect(sw.loss.economicValue).toBeDefined();

    expect(en.loss.indicativeDisclaimer).toContain('Indicative post-harvest metric');
    expect(sw.loss.indicativeDisclaimer).toContain('Kipimo cha makisio');

    expect(en.history.avoidedLoss).toBeDefined();
    expect(sw.history.avoidedLoss).toBeDefined();
  });

  it('should handle completed batch avoided loss presentation', () => {
    const completedBatch: Batch = {
      id: 'batch-12345678',
      hub_id: 'hub-meru',
      crop_type: 'moringa',
      initial_weight_kg: 100.0,
      target_moisture_pct: 10.0,
      status: 'completed',
      avoided_loss_kg: 30.0,
      avoided_loss_kes: 9000.0,
      start_time: '2026-11-20T10:00:00Z',
      end_time: '2026-11-20T18:00:00Z',
    };

    expect(completedBatch.avoided_loss_kg).toBe(30.0);
    expect(completedBatch.avoided_loss_kes).toBe(9000.0);
    expect(completedBatch.status).toBe('completed');
  });

  it('should handle active batch without avoided loss', () => {
    const activeBatch: Batch = {
      id: 'batch-active-1',
      hub_id: 'hub-meru',
      crop_type: 'prunus',
      initial_weight_kg: 50.0,
      target_moisture_pct: 12.0,
      status: 'active',
      start_time: '2026-11-20T10:00:00Z',
    };

    expect(activeBatch.avoided_loss_kg).toBeUndefined();
    expect(activeBatch.avoided_loss_kes).toBeUndefined();
  });
});

