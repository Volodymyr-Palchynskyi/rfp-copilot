import { ProposalResponse } from './proposal.models';

/** Makes arbitrary text safe inside one Markdown table cell. */
function cell(text: string | number): string {
  return String(text).replace(/\|/g, '\\|').replace(/\s*\n\s*/g, ' ').trim();
}

function table(headers: string[], rows: (string | number)[][], alignRight: number[] = []): string {
  const separator = headers.map((_, i) => (alignRight.includes(i) ? '---:' : '---'));
  const lines = [
    `| ${headers.join(' | ')} |`,
    `| ${separator.join(' | ')} |`,
    ...rows.map((row) => `| ${row.map(cell).join(' | ')} |`),
  ];
  return lines.join('\n');
}

const number = (value: number) => value.toLocaleString('en-US');

/**
 * Renders a finished proposal as Markdown for pasting into a doc or an email.
 * Pure on purpose (no Date, no DOM): the caller passes the generation date, so output is testable.
 */
export function toMarkdown(proposal: ProposalResponse, generatedOn?: string): string {
  const parts: string[] = [`# ${proposal.project_title}`];

  const facts = [
    `**Effort:** ${number(proposal.total_hours_min)} - ${number(proposal.total_hours_max)} h`,
    `**Duration:** ${proposal.estimated_duration_weeks} weeks`,
  ];
  if (generatedOn) facts.push(`**Generated:** ${generatedOn}`);
  parts.push(facts.join(' · '));

  parts.push('## Executive summary', proposal.executive_summary);
  parts.push('## Architecture', proposal.architecture_overview);

  if (proposal.tech_stack.length) {
    parts.push(
      '## Tech stack',
      table(
        ['Category', 'Technology', 'Why'],
        proposal.tech_stack.map((t) => [t.category, t.name, t.reason]),
      ),
    );
  }

  if (proposal.features.length) {
    const rows: (string | number)[][] = proposal.features.map((f) => [
      f.module,
      `**${f.title}**: ${f.description}`,
      f.complexity,
      `${number(f.hours_min)} - ${number(f.hours_max)}`,
    ]);
    rows.push(['', '**Total**', '', `**${number(proposal.total_hours_min)} - ${number(proposal.total_hours_max)}**`]);
    parts.push('## Scope and estimates', table(['Module', 'Feature', 'Complexity', 'Hours'], rows, [3]));
  }

  if (proposal.risks.length) {
    parts.push(
      '## Risks',
      table(
        ['Impact', 'Risk', 'Mitigation'],
        proposal.risks.map((r) => [r.impact, r.risk, r.mitigation]),
      ),
    );
  }

  if (proposal.estimation_basis) {
    parts.push('## How the estimate was derived', proposal.estimation_basis);
  }

  if (proposal.references.length) {
    const items = proposal.references.map((r) => {
      const why = r.reason ? ` ${r.reason}` : '';
      return `- **${r.title}** (${number(r.total_hours)} h, ${r.duration_weeks} weeks).${why}`;
    });
    parts.push('## Based on past projects', items.join('\n'));
  }

  return parts.join('\n\n') + '\n';
}

/** File name for the download, e.g. "NordTel FleetPulse: Real-Time" -> "nordtel-fleetpulse-real-time.md". */
export function markdownFileName(title: string): string {
  const slug = title
    .toLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 60)
    .replace(/-+$/g, '');
  return `${slug || 'proposal'}.md`;
}
