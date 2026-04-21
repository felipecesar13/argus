import { Component } from '@angular/core';
import { CommonModule, TitleCasePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, FormsModule, TitleCasePipe],
  templateUrl: './home.component.html',
})
export class HomeComponent {
  diffInput = '';
  isReviewing = false;

  readonly mockComments = [
    {
      id: 1,
      severity: 'critical',
      category: 'Security',
      file: 'src/auth/login.service.ts',
      line: 42,
      message: 'SQL query built with string interpolation — vulnerable to SQL injection.',
      suggestion: 'Use parameterized queries or an ORM (e.g. TypeORM query builder).',
    },
    {
      id: 2,
      severity: 'warning',
      category: 'Performance',
      file: 'src/review/review.service.ts',
      line: 87,
      message: 'N+1 query detected: fetching comments inside a loop over reviews.',
      suggestion: 'Use a JOIN or batch-load comments with a single query before the loop.',
    },
    {
      id: 3,
      severity: 'info',
      category: 'Style',
      file: 'src/shared/utils.ts',
      line: 15,
      message: 'Function `processData` handles both parsing and validation — violates SRP.',
      suggestion: 'Split into `parseInput()` and `validateInput()` to keep concerns separate.',
    },
  ];

  readonly activeCategory = 'All';

  get filteredComments() {
    if (this.activeCategory === 'All') return this.mockComments;
    return this.mockComments.filter((c) => c.category === this.activeCategory);
  }

  severityClass(severity: string): string {
    const map: Record<string, string> = {
      critical: 'bg-red-100 text-red-700 border border-red-300',
      warning: 'bg-yellow-100 text-yellow-700 border border-yellow-300',
      info: 'bg-blue-100 text-blue-700 border border-blue-300',
    };
    return map[severity] ?? '';
  }

  severityDot(severity: string): string {
    const map: Record<string, string> = {
      critical: 'bg-red-500',
      warning: 'bg-yellow-500',
      info: 'bg-blue-500',
    };
    return map[severity] ?? 'bg-gray-400';
  }
}
