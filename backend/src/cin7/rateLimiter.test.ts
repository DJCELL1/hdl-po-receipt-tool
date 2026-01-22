import { RateLimiter } from './rateLimiter';
import { Cin7Config } from './types';

describe('RateLimiter', () => {
  let rateLimiter: RateLimiter;
  let config: Cin7Config;

  beforeEach(() => {
    config = {
      apiKey: 'test',
      apiSecret: 'test',
      baseUrl: 'https://test.com',
      maxRetries: 3,
      rateLimits: {
        perSecond: 3,
        perMinute: 60,
        perDay: 5000
      }
    };
    rateLimiter = new RateLimiter(config);
  });

  afterEach(() => {
    rateLimiter.reset();
  });

  it('should allow requests under rate limit', async () => {
    const start = Date.now();
    await rateLimiter.waitForAvailability();
    await rateLimiter.waitForAvailability();
    const duration = Date.now() - start;

    // Should complete quickly (under 100ms) as we're under limit
    expect(duration).toBeLessThan(100);
  });

  it('should throttle when hitting per-second limit', async () => {
    const start = Date.now();

    // Make 3 requests (at limit)
    await rateLimiter.waitForAvailability();
    await rateLimiter.waitForAvailability();
    await rateLimiter.waitForAvailability();

    // 4th request should wait
    await rateLimiter.waitForAvailability();

    const duration = Date.now() - start;

    // Should have waited at least 900ms (close to 1 second)
    expect(duration).toBeGreaterThan(900);
  }, 10000);

  it('should reset state correctly', async () => {
    await rateLimiter.waitForAvailability();
    await rateLimiter.waitForAvailability();

    rateLimiter.reset();

    const start = Date.now();
    await rateLimiter.waitForAvailability();
    const duration = Date.now() - start;

    // After reset, should not wait
    expect(duration).toBeLessThan(100);
  });
});
