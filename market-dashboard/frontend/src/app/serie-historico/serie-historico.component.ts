import { DatePipe, DecimalPipe } from '@angular/common';
import { Component, Input, OnChanges } from '@angular/core';
import { SerieHistorico, SeriePonto } from '../models/serie-historico.model';

@Component({
  selector: 'app-serie-historico',
  standalone: true,
  imports: [DatePipe, DecimalPipe],
  templateUrl: './serie-historico.component.html',
  styleUrl: './serie-historico.component.css',
})
export class SerieHistoricoComponent implements OnChanges {
  @Input({ required: true }) serie!: SerieHistorico | null;

  polylinePreco = '';
  polylineMm = '';
  /** Ultimos pontos na tabela (mais recente primeiro) */
  tabela: SeriePonto[] = [];

  ngOnChanges(): void {
    const pontos = this.serie?.pontos ?? [];
    this.tabela = [...pontos].reverse().slice(0, 12);
    this.polylinePreco = this.montarPolyline(pontos.map((p) => p.preco));
    const mmVals = pontos.map((p) => p.media_movel);
    this.polylineMm = this.montarPolylineMm(pontos.map((p) => p.preco), mmVals);
  }

  private montarPolyline(valores: number[]): string {
    if (valores.length < 2) {
      return '';
    }
    const min = Math.min(...valores);
    const max = Math.max(...valores);
    const span = max - min || 1;
    const w = 200;
    const h = 56;
    const pad = 4;
    return valores
      .map((v, i) => {
        const x = pad + (i / (valores.length - 1)) * (w - pad * 2);
        const y = pad + (1 - (v - min) / span) * (h - pad * 2);
        return `${x.toFixed(1)},${y.toFixed(1)}`;
      })
      .join(' ');
  }

  /** MM no mesmo eixo do preco (so pontos com media_movel). */
  private montarPolylineMm(precos: number[], mms: (number | null)[]): string {
    if (precos.length < 2) {
      return '';
    }
    const min = Math.min(...precos);
    const max = Math.max(...precos);
    const span = max - min || 1;
    const w = 200;
    const h = 56;
    const pad = 4;
    const parts: string[] = [];
    mms.forEach((mm, i) => {
      if (mm === null || mm === undefined) {
        return;
      }
      const x = pad + (i / (precos.length - 1)) * (w - pad * 2);
      const y = pad + (1 - (mm - min) / span) * (h - pad * 2);
      parts.push(`${x.toFixed(1)},${y.toFixed(1)}`);
    });
    return parts.length >= 2 ? parts.join(' ') : '';
  }
}
