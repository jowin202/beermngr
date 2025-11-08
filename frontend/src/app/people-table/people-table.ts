import { Component, OnInit, inject, signal } from '@angular/core';
import { FinanceService, Person } from '../api';
import { MatTableModule } from '@angular/material/table';
import { CurrencyPipe } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-people-table',
  standalone: true,
  imports: [MatTableModule, CurrencyPipe, MatIconModule],
  templateUrl: './people-table.html',
  styleUrl: './people-table.scss',
})
export class PeopleTable implements OnInit {
  private financeService = inject(FinanceService);

  people = signal<Person[]>([]);
  displayedColumns = ['id', 'name', 'email', 'balance', 'actions'];

  ngOnInit() {
    this.refreshPeople();
  }

  refreshPeople() {
    this.financeService.listPeople().subscribe(data => this.people.set(data));
  }

  deposit(person: Person) {
    const amount = Number(prompt(`Einzahlung für ${person.name} (Euro):`, '0'));
    if (!isNaN(amount) && amount > 0) {
      this.financeService
        .addTransaction({ person_id: person.id, amount, description: 'Einzahlung' })
        .subscribe(() => this.refreshPeople());
    }
  }

  withdraw(person: Person) {
    const amount = Number(prompt(`Auszahlung für ${person.name} (Euro):`, '0'));
    if (!isNaN(amount) && amount > 0) {
      this.financeService
        .addTransaction({ person_id: person.id, amount: -amount, description: 'Auszahlung' })
        .subscribe(() => this.refreshPeople());
    }
  }

  downloadReport(person: Person) {
    this.financeService.generatePersonReport(person.id).subscribe(blob => {
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = `${person.name}_report.pdf`;
      link.click();
    });
  }
}
