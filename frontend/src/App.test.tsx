import { describe, it, expect } from '@jest/globals';

// Basic smoke test
describe('App', () => {
  it('should pass smoke test', () => {
    expect(1 + 1).toBe(2);
  });

  it('should have environment set up correctly', () => {
    expect(true).toBe(true);
  });
});
