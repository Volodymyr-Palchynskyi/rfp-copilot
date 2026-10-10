import { markdownFileName, toMarkdown } from './markdown';
import { ProposalResponse } from './proposal.models';

function proposal(overrides: Partial<ProposalResponse> = {}): ProposalResponse {
  return {
    project_title: 'Fleet Portal',
    executive_summary: 'Track vans.',
    architecture_overview: 'Modular monolith.',
    tech_stack: [{ category: 'Backend', name: 'FastAPI', reason: 'Async and typed' }],
    features: [
      { module: 'Map', title: 'Live map', description: 'Vans on a map', complexity: 'high', hours_min: 400, hours_max: 500 },
      { module: 'QA', title: 'Testing', description: 'UAT', complexity: 'medium', hours_min: 1200, hours_max: 1500 },
    ],
    risks: [{ risk: 'Vendor API changes', impact: 'high', mitigation: 'Adapter layer' }],
    estimated_duration_weeks: 18,
    estimation_basis: 'Based on project 001.',
    total_hours_min: 1600,
    total_hours_max: 2000,
    references: [
      {
        project_id: '001',
        title: 'Fleet Tracking Portal',
        industry: 'logistics',
        stack: 'Angular',
        total_hours: 3000,
        duration_weeks: 20,
        relevance_score: 0.73,
        matched_sections: ['Overview'],
        reason: 'Same live map module.',
      },
    ],
    usage: null,
    ...overrides,
  };
}

describe('toMarkdown', () => {
  it('renders all sections with totals and references', () => {
    const md = toMarkdown(proposal(), '2026-10-10');

    expect(md).toContain('# Fleet Portal');
    expect(md).toContain('**Effort:** 1,600 - 2,000 h · **Duration:** 18 weeks · **Generated:** 2026-10-10');
    expect(md).toContain('## Tech stack');
    expect(md).toContain('| Backend | FastAPI | Async and typed |');
    expect(md).toContain('| Map | **Live map**: Vans on a map | high | 400 - 500 |');
    expect(md).toContain('|  | **Total** |  | **1,600 - 2,000** |'); // empty cells keep the column count
    expect(md).toContain('| high | Vendor API changes | Adapter layer |');
    expect(md).toContain('- **Fleet Tracking Portal** (3,000 h, 20 weeks). Same live map module.');
    expect(md.endsWith('\n')).toBe(true);
  });

  it('keeps tables intact when text contains pipes and line breaks', () => {
    const md = toMarkdown(
      proposal({ risks: [{ risk: 'A | B', impact: 'low', mitigation: 'first\nsecond' }] }),
    );

    expect(md).toContain('| low | A \\| B | first second |');
  });

  it('omits empty sections instead of rendering empty tables', () => {
    const md = toMarkdown(proposal({ references: [], risks: [], tech_stack: [], estimation_basis: '' }));

    expect(md).not.toContain('## Risks');
    expect(md).not.toContain('## Tech stack');
    expect(md).not.toContain('## Based on past projects');
    expect(md).not.toContain('## How the estimate was derived');
    expect(md).toContain('## Scope and estimates');
  });

  it('omits the generated date when none is given', () => {
    expect(toMarkdown(proposal())).not.toContain('Generated');
  });

  it('renders a reference without a reason', () => {
    const base = proposal();
    const md = toMarkdown(proposal({ references: [{ ...base.references[0], reason: null }] }));

    expect(md).toContain('- **Fleet Tracking Portal** (3,000 h, 20 weeks).\n');
  });
});

describe('markdownFileName', () => {
  it('slugifies the title', () => {
    expect(markdownFileName('NordTel FleetPulse: Real-Time Van Telematics')).toBe(
      'nordtel-fleetpulse-real-time-van-telematics.md',
    );
  });

  it('keeps non-latin letters and falls back when nothing is left', () => {
    expect(markdownFileName('Платформа для логістики')).toBe('платформа-для-логістики.md');
    expect(markdownFileName('Єдиний їдальний майданчик')).toBe('єдиний-їдальний-майданчик.md'); // й, ї must not split words
    expect(markdownFileName('???')).toBe('proposal.md');
  });

  it('limits the length', () => {
    expect(markdownFileName('a'.repeat(200)).length).toBeLessThanOrEqual(63);
  });
});
