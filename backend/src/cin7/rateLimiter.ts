import { RateLimitState, Cin7Config } from './types';

export class RateLimiter {
  private state: RateLimitState = {
    secondRequests: [],
    minuteRequests: [],
    dayRequests: []
  };

  constructor(private config: Cin7Config) {}

  async waitForAvailability(): Promise<void> {
    const now = Date.now();

    // Clean old requests
    this.cleanOldRequests(now);

    // Check if we need to wait
    const waitTime = this.getWaitTime(now);
    if (waitTime > 0) {
      console.log(`Rate limit: waiting ${waitTime}ms`);
      await this.sleep(waitTime);
      return this.waitForAvailability();
    }

    // Record this request
    this.recordRequest(now);
  }

  private cleanOldRequests(now: number): void {
    const oneSecondAgo = now - 1000;
    const oneMinuteAgo = now - 60000;
    const oneDayAgo = now - 86400000;

    this.state.secondRequests = this.state.secondRequests.filter(t => t > oneSecondAgo);
    this.state.minuteRequests = this.state.minuteRequests.filter(t => t > oneMinuteAgo);
    this.state.dayRequests = this.state.dayRequests.filter(t => t > oneDayAgo);
  }

  private getWaitTime(now: number): number {
    const { perSecond, perMinute, perDay } = this.config.rateLimits;

    if (this.state.secondRequests.length >= perSecond) {
      const oldestSecond = Math.min(...this.state.secondRequests);
      return Math.max(0, 1000 - (now - oldestSecond));
    }

    if (this.state.minuteRequests.length >= perMinute) {
      const oldestMinute = Math.min(...this.state.minuteRequests);
      return Math.max(0, 60000 - (now - oldestMinute));
    }

    if (this.state.dayRequests.length >= perDay) {
      const oldestDay = Math.min(...this.state.dayRequests);
      return Math.max(0, 86400000 - (now - oldestDay));
    }

    return 0;
  }

  private recordRequest(now: number): void {
    this.state.secondRequests.push(now);
    this.state.minuteRequests.push(now);
    this.state.dayRequests.push(now);
  }

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  public reset(): void {
    this.state = {
      secondRequests: [],
      minuteRequests: [],
      dayRequests: []
    };
  }
}
