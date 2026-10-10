import { ChangeDetectionStrategy, Component, computed, inject, signal } from '@angular/core';
import { DecimalPipe } from '@angular/common';
import { markdownFileName, toMarkdown } from './markdown';
import { ProposalStreamService } from './proposal-stream.service';
import { Budget, PartialDraft, ProposalResponse, ReferenceProject } from './proposal.models';

// Keep in sync with MAX_BRIEF_CHARS on the backend.
const MAX_BRIEF_CHARS = 4000;

type Status = 'idle' | 'running' | 'done' | 'error' | 'cancelled';

interface Sample {
  label: string;
  client: string;
  brief: string;
}

const SAMPLES: Sample[] = [
  {
    label: 'Fleet tracking',
    client: 'NordTel',
    brief:
      'A telecom operator wants a web portal to track about 300 of its service vans in real time. Dispatchers need a live map, alerts when a van deviates from its route or sits idle, driver management and weekly KPI reports. Vehicle data comes from two telematics vendors.',
  },
  {
    label: 'Legal AI assistant',
    client: 'Baker & Lowe',
    brief:
      "A law firm wants a chat assistant that answers lawyers' questions using about 800 internal memos and precedents, shows which documents each answer came from, and only uses documents the asking lawyer is allowed to access. Web UI in Angular, SSO login.",
  },
  {
    label: 'Ticketing platform',
    client: 'Live Nation North',
    brief:
      'A concert promoter wants an event ticketing platform with interactive seat maps, a fair virtual queue for high-demand on-sales, payments, mobile tickets with QR codes and a venue entry scanning app.',
  },
];

@Component({
  selector: 'app-proposal-page',
  imports: [DecimalPipe],
  templateUrl: './proposal-page.html',
  styleUrl: './proposal-page.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProposalPage {
  private readonly api = inject(ProposalStreamService);
  private abort: AbortController | null = null;

  protected readonly samples = SAMPLES;
  protected readonly maxBriefChars = MAX_BRIEF_CHARS;
  protected readonly budgets: Budget[] = ['budget', 'standard', 'enterprise'];

  // form
  protected readonly clientName = signal('');
  protected readonly description = signal('');
  protected readonly budget = signal<Budget>('standard');
  protected readonly timelineWeeks = signal<number | null>(null);

  // stream state
  protected readonly status = signal<Status>('idle');
  protected readonly error = signal<string | null>(null);
  protected readonly fallbackModel = signal<string | null>(null);
  protected readonly references = signal<ReferenceProject[]>([]);
  protected readonly draft = signal<PartialDraft>({});
  protected readonly final = signal<ProposalResponse | null>(null);
  protected readonly exportNote = signal<string | null>(null);

  protected readonly running = computed(() => this.status() === 'running');
  protected readonly canSubmit = computed(
    () => !this.running() && this.clientName().trim().length > 0 && this.description().trim().length >= 20,
  );
  protected readonly started = computed(() => this.status() !== 'idle');
  protected readonly retrievedReferences = computed(() => this.references().length > 0);

  /** Server totals once complete, a running sum of the features received so far before that. */
  protected readonly totals = computed(() => {
    const final = this.final();
    if (final) return { min: final.total_hours_min, max: final.total_hours_max };
    const features = this.draft().features ?? [];
    return {
      min: features.reduce((sum, f) => sum + (f.hours_min ?? 0), 0),
      max: features.reduce((sum, f) => sum + (f.hours_max ?? 0), 0),
    };
  });

  protected useSample(sample: Sample): void {
    this.clientName.set(sample.client);
    this.description.set(sample.brief);
  }

  protected onTimeline(value: string): void {
    const weeks = Number.parseInt(value, 10);
    this.timelineWeeks.set(Number.isFinite(weeks) && weeks > 0 ? weeks : null);
  }

  protected async generate(): Promise<void> {
    if (!this.canSubmit()) return;

    this.references.set([]);
    this.draft.set({});
    this.final.set(null);
    this.error.set(null);
    this.fallbackModel.set(null);
    this.exportNote.set(null);
    this.status.set('running');

    const abort = new AbortController();
    this.abort = abort;

    try {
      const events = this.api.stream(
        {
          client_name: this.clientName().trim(),
          project_description: this.description().trim(),
          budget_level: this.budget(),
          target_timeline_weeks: this.timelineWeeks(),
        },
        abort.signal,
      );

      for await (const event of events) {
        switch (event.event) {
          case 'references':
            this.references.set(event.data);
            break;
          case 'notice':
            this.fallbackModel.set(event.data.fallback_model);
            break;
          case 'section':
            this.draft.update((draft) => ({ ...draft, [event.data.key]: event.data.value }));
            break;
          case 'complete':
            this.final.set(event.data);
            this.draft.set(event.data);
            this.status.set('done');
            break;
          case 'error':
            throw new Error(event.data.detail);
        }
      }
      if (this.status() === 'running') this.status.set('done');
    } catch (err) {
      if (abort.signal.aborted) {
        this.status.set('cancelled');
      } else {
        this.error.set(err instanceof Error ? err.message : 'Something went wrong.');
        this.status.set('error');
      }
    } finally {
      if (this.abort === abort) this.abort = null;
    }
  }

  /** Only a completed proposal can be exported: partial drafts have unvalidated, half-written fields. */
  private markdown(): string | null {
    const proposal = this.final();
    return proposal ? toMarkdown(proposal, new Date().toISOString().slice(0, 10)) : null;
  }

  protected async copyMarkdown(): Promise<void> {
    const text = this.markdown();
    if (!text) return;
    try {
      await navigator.clipboard.writeText(text);
      this.flashNote('Copied to clipboard');
    } catch {
      // Clipboard needs a secure context and a user gesture; downloading always works.
      this.flashNote('Copy is blocked by the browser, use Download instead');
    }
  }

  protected downloadMarkdown(): void {
    const text = this.markdown();
    const proposal = this.final();
    if (!text || !proposal) return;

    const url = URL.createObjectURL(new Blob([text], { type: 'text/markdown;charset=utf-8' }));
    const link = document.createElement('a');
    link.href = url;
    link.download = markdownFileName(proposal.project_title);
    link.click();
    URL.revokeObjectURL(url);
  }

  private flashNote(message: string): void {
    this.exportNote.set(message);
    setTimeout(() => this.exportNote.set(null), 2500);
  }

  protected cancel(): void {
    this.abort?.abort();
  }
}
