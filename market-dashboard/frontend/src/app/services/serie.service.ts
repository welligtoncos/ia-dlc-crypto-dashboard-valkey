import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { SerieHistorico } from '../models/serie-historico.model';

@Injectable({ providedIn: 'root' })
export class SerieService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = environment.apiBaseUrl;

  getSerie(moeda: string, limit = 40): Observable<SerieHistorico> {
    return this.http.get<SerieHistorico>(`${this.baseUrl}/api/series/${moeda}`, {
      params: { limit: String(limit) },
    });
  }
}
