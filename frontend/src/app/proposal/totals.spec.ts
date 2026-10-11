import { runningTotals } from './totals';

describe('runningTotals', () => {
  it('sums complete features', () => {
    expect(runningTotals([{ hours_min: 100, hours_max: 150 }, { hours_min: 40, hours_max: 60 }])).toEqual({ min: 140, max: 210 });
  });

  it('ignores a half-written feature so the minimum never exceeds the maximum', () => {
    const totals = runningTotals([{ hours_min: 100, hours_max: 150 }, { hours_min: 500 }]);

    expect(totals).toEqual({ min: 100, max: 150 });
    expect(totals.min).toBeLessThanOrEqual(totals.max);
  });

  it('handles no features yet', () => {
    expect(runningTotals(undefined)).toEqual({ min: 0, max: 0 });
    expect(runningTotals([])).toEqual({ min: 0, max: 0 });
  });

  it('counts a feature with zero hours as complete', () => {
    expect(runningTotals([{ hours_min: 0, hours_max: 0 }])).toEqual({ min: 0, max: 0 });
  });
});
