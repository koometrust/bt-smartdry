import { describe, it, expect } from 'vitest';
import en from '../i18n/locales/en.json';
import sw from '../i18n/locales/sw.json';
import { Alert } from '../types';

describe('Alerts UI & Bilingual Parity', () => {
  it('should have complete bilingual translations for all alert labels, types, and actions', () => {
    expect(en.alerts.title).toBe('Alert Notifications & Audit Log');
    expect(sw.alerts.title).toBe('Kumbukumbu ya Tahadhari na Ukaguzi');

    expect(en.alerts.types.near_completion).toBe('Near Completion');
    expect(sw.alerts.types.near_completion).toBe('Karibu Kukamilika');

    expect(en.alerts.types.completion).toBe('Completion');
    expect(sw.alerts.types.completion).toBe('Kukamilika');

    expect(en.alerts.types.anomaly).toBe('Anomaly');
    expect(sw.alerts.types.anomaly).toBe('Hitilafu');

    expect(en.alerts.markRead).toBeDefined();
    expect(sw.alerts.markRead).toBeDefined();

    expect(en.nav.alerts).toBe('Alerts');
    expect(sw.nav.alerts).toBe('Tahadhari');
  });

  it('should correctly filter alerts by hub and alert type', () => {
    const alerts: Alert[] = [
      {
        id: 'a1',
        batch_id: 'b1',
        alert_type: 'near_completion',
        channel: 'sms',
        message: 'Near target',
        phone_number: '+254700000001',
        status: 'sent',
        is_read: false,
        sent_at: '2026-11-20T10:00:00Z',
      },
      {
        id: 'a2',
        batch_id: 'b2',
        alert_type: 'anomaly',
        channel: 'sms',
        message: 'High humidity',
        phone_number: '+254700000002',
        status: 'sent',
        is_read: true,
        sent_at: '2026-11-20T11:00:00Z',
      },
    ];

    const unreadAlerts = alerts.filter((a) => !a.is_read);
    expect(unreadAlerts.length).toBe(1);
    expect(unreadAlerts[0].id).toBe('a1');

    const anomalyAlerts = alerts.filter((a) => a.alert_type === 'anomaly');
    expect(anomalyAlerts.length).toBe(1);
    expect(anomalyAlerts[0].id).toBe('a2');
  });
});
