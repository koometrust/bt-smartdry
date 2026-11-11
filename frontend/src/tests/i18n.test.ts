import { describe, it, expect } from 'vitest';
import en from '../i18n/locales/en.json';
import sw from '../i18n/locales/sw.json';

describe('Bilingual Internationalization (i18n)', () => {
  it('should have complete parity between English and Kiswahili translations', () => {
    function getKeys(obj: any, prefix = ''): string[] {
      return Object.keys(obj).reduce((res: string[], el: string) => {
        if (Array.isArray(obj[el])) {
          return res;
        } else if (typeof obj[el] === 'object' && obj[el] !== null) {
          return [...res, ...getKeys(obj[el], prefix + el + '.')];
        }
        return [...res, prefix + el];
      }, []);
    }

    const enKeys = getKeys(en).sort();
    const swKeys = getKeys(sw).sort();

    expect(enKeys).toEqual(swKeys);
  });

  it('should include translations for all three quality grades in both languages', () => {
    expect(en.grades.export).toBeDefined();
    expect(en.grades.standard).toBeDefined();
    expect(en.grades.downgraded).toBeDefined();

    expect(sw.grades.export).toBeDefined();
    expect(sw.grades.standard).toBeDefined();
    expect(sw.grades.downgraded).toBeDefined();
  });

  it('should include translations for all three crops', () => {
    expect(en.crops.moringa).toBeDefined();
    expect(en.crops.hibiscus).toBeDefined();
    expect(en.crops.prunus).toBeDefined();

    expect(sw.crops.moringa).toBeDefined();
    expect(sw.crops.hibiscus).toBeDefined();
    expect(sw.crops.prunus).toBeDefined();
  });
});

