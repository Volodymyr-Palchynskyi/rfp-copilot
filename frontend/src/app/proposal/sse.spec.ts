import { parseSse, RawSseMessage } from './sse';

function streamOf(...chunks: Uint8Array[]): ReadableStream<Uint8Array> {
  return new ReadableStream({
    start(controller) {
      chunks.forEach((chunk) => controller.enqueue(chunk));
      controller.close();
    },
  });
}

async function collect(body: ReadableStream<Uint8Array>): Promise<RawSseMessage[]> {
  const messages: RawSseMessage[] = [];
  for await (const message of parseSse(body)) messages.push(message);
  return messages;
}

const encode = (text: string) => new TextEncoder().encode(text);

describe('parseSse', () => {
  it('parses several events from one chunk', async () => {
    const body = streamOf(encode('event: references\ndata: []\n\nevent: complete\ndata: {"a":1}\n\n'));
    expect(await collect(body)).toEqual([
      { event: 'references', data: '[]' },
      { event: 'complete', data: '{"a":1}' },
    ]);
  });

  it('reassembles an event split across chunks', async () => {
    const body = streamOf(encode('event: sec'), encode('tion\ndata: {"key":"x"'), encode('}\n\n'));
    expect(await collect(body)).toEqual([{ event: 'section', data: '{"key":"x"}' }]);
  });

  it('does not corrupt multi-byte characters split between chunks', async () => {
    const bytes = encode('event: section\ndata: "Київ"\n\n');
    const cut = bytes.indexOf(0xd0) + 1; // between the two bytes of the first Cyrillic letter
    const body = streamOf(bytes.slice(0, cut), bytes.slice(cut));
    expect(await collect(body)).toEqual([{ event: 'section', data: '"Київ"' }]);
  });

  it('ignores an incomplete trailing event', async () => {
    const body = streamOf(encode('event: complete\ndata: {}\n\nevent: section\ndata: {"ke'));
    expect(await collect(body)).toEqual([{ event: 'complete', data: '{}' }]);
  });
});
