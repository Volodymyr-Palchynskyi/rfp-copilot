export interface RawSseMessage {
  event: string;
  data: string;
}

/**
 * Incrementally parses a text/event-stream body.
 * EventSource cannot be used because it only supports GET and we need to POST the brief.
 */
export async function* parseSse(body: ReadableStream<Uint8Array>): AsyncGenerator<RawSseMessage> {
  const reader = body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';
  try {
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      let boundary = buffer.indexOf('\n\n');
      while (boundary >= 0) {
        const message = toMessage(buffer.slice(0, boundary));
        buffer = buffer.slice(boundary + 2);
        if (message) yield message;
        boundary = buffer.indexOf('\n\n');
      }
    }
  } finally {
    // Runs when the consumer stops early (cancel button) as well as on normal completion.
    await reader.cancel().catch(() => undefined);
  }
}

function toMessage(block: string): RawSseMessage | null {
  let event = 'message';
  const data: string[] = [];
  for (const line of block.split('\n')) {
    if (line.startsWith('event:')) event = line.slice(6).trim();
    else if (line.startsWith('data:')) data.push(line.slice(5).trimStart());
  }
  return data.length ? { event, data: data.join('\n') } : null;
}
