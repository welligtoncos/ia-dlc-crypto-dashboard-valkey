import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { ObservabilityEvent } from '../models/observability-event.model';

@Injectable({ providedIn: 'root' })
export class ObservabilityService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = environment.apiBaseUrl;

  getEvents(limit = 50): Observable<ObservabilityEvent[]> {
    return this.http.get<ObservabilityEvent[]>(
      `${this.baseUrl}/api/observability/events`,
      { params: { limit: String(limit) } },
    );
  }
}
