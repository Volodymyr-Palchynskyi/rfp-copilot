import { Injectable, isDevMode } from '@angular/core';
import { ProposalRequest, StreamEvent } from './proposal.models';
import { parseSse } from './sse';

/**
 * `ng serve` talks to the API directly (CORS is enabled for localhost:4200).
 * Production builds use the same origin: nginx proxies /api to the backend, so no CORS and no hardcoded host.
 */
const apiBase = () => (isDevMode() ? 'http://localhost:8000/api/v1' : '/api/v1');

@Injectable({ providedIn: 'root' })
export class ProposalStreamService {
  /** Streams events for one proposal. Aborting the signal closes the connection and ends the generator. */
  async *stream(request: ProposalRequest, signal: AbortSignal): AsyncGenerator<StreamEvent> {
    const response = await fetch(`${apiBase()}/proposals/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'text/event-stream' },
      body: JSON.stringify(request),
      signal,
    });

    if (!response.ok || !response.body) {
      throw new Error(await this.describeFailure(response));
    }

    for await (const message of parseSse(response.body)) {
      yield { event: message.event, data: JSON.parse(message.data) } as StreamEvent;
    }
  }

  private async describeFailure(response: Response): Promise<string> {
    if (response.status === 422) return 'The brief is not valid: use 20 to 4000 characters and a client name.';
    try {
      const body = await response.json();
      if (typeof body?.detail === 'string') return body.detail;
    } catch {
      // not JSON, fall through
    }
    return `Request failed with status ${response.status}.`;
  }
}
