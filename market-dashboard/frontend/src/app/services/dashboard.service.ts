import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { DashboardItem } from '../models/moeda-card.model';

@Injectable({ providedIn: 'root' })
export class DashboardService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = environment.apiBaseUrl;

  getDashboard(): Observable<DashboardItem> {
    return this.http.get<DashboardItem>(`${this.baseUrl}/api/dashboard`);
  }
}
