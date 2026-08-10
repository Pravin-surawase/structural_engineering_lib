import { describe, expect, it } from 'vitest';
import { catalogueQuickEnabled } from '../config';

describe('catalogue quick-beam cutover', () => {
  it('defaults to the catalogue and keeps one explicit rollback value', () => {
    expect(catalogueQuickEnabled(undefined)).toBe(true);
    expect(catalogueQuickEnabled('true')).toBe(true);
    expect(catalogueQuickEnabled('false')).toBe(false);
  });
});
