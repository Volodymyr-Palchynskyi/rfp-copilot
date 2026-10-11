import { FeatureEstimate } from './proposal.models';

/**
 * Running effort total while the proposal is still streaming.
 *
 * A feature that is half written can already have `hours_min` but not yet `hours_max`. Counting it
 * would make the minimum exceed the maximum on screen, so only features with both numbers count.
 */
export function runningTotals(features: Partial<FeatureEstimate>[] | undefined): { min: number; max: number } {
  let min = 0;
  let max = 0;
  for (const feature of features ?? []) {
    if (typeof feature.hours_min === 'number' && typeof feature.hours_max === 'number') {
      min += feature.hours_min;
      max += feature.hours_max;
    }
  }
  return { min, max };
}
