import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Person {
  id: number;
  name: string;
  email: string;
  saldo: number;
  last_change: string;
}

export interface TransactionInput {
  person_id: number;
  amount: number;
  description?: string;
}

@Injectable({ providedIn: 'root' })
export class FinanceService {
  private http = inject(HttpClient);
  private apiUrl = 'api';

  listPeople(): Observable<Person[]> {
    return this.http.get<Person[]>(`${this.apiUrl}/people`);
  }

  addTransaction(input: TransactionInput): Observable<any> {
    return this.http.post(`${this.apiUrl}/transaction`, input);
  }

  initializeDatabase(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post(`${this.apiUrl}/init`, formData);
  }

  generatePersonReport(personId: number): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/report/person?person_id=${personId}`, { responseType: 'blob' });
  }
}