import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { DashboardItem } from '../models/moeda-card.model';

@Injectable({ providedIn: 'root' })
export class DashboardService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = environment.apiBaseUrl;

  /** no-cache no browser: sempre consulta o BFF (que usa HIT do Valkey). */
  getDashboard(): Observable<DashboardItem[]> {
    return this.http.get<DashboardItem[]>(`${this.baseUrl}/api/dashboard`, {
      headers: new HttpHeaders({
        'Cache-Control': 'no-cache',
        Pragma: 'no-cache',
      }),
    });
  }
}
