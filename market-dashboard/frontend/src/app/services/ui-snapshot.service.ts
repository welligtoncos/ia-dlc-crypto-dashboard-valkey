import { Injectable } from '@angular/core';
import { MoedaCard } from '../models/moeda-card.model';
import { ObservabilityEvent } from '../models/observability-event.model';
import { SerieHistorico } from '../models/serie-historico.model';

const SNAP_KEY = 'market-dashboard-ui-v1';
const MAX_AGE_MS = 15 * 60 * 1000;

export interface UiSnapshot {
  itens: MoedaCard[];
  seriesPorMoeda: Record<string, SerieHistorico | null>;
  eventos: ObservabilityEvent[];
  ultimaSyncEm: string | null;
  cicloReplayId: string;
  ultimoEventoDashboard: string;
  savedAt: number;
}

/**
 * Mantém o ultimo estado da UI no sessionStorage para F5 nao "zerar" o painel.
 * O cache real continua no Valkey (BFF); isto so evita flash/bug no browser.
 */
@Injectable({ providedIn: 'root' })
export class UiSnapshotService {
  ler(): UiSnapshot | null {
    try {
      const raw = sessionStorage.getItem(SNAP_KEY);
      if (!raw) {
        return null;
      }
      const snap = JSON.parse(raw) as UiSnapshot;
      if (!snap?.savedAt || Date.now() - snap.savedAt > MAX_AGE_MS) {
        return null;
      }
      if (!Array.isArray(snap.itens) || snap.itens.length === 0) {
        return null;
      }
      return snap;
    } catch {
      return null;
    }
  }

  salvar(parcial: Omit<UiSnapshot, 'savedAt'>): void {
    try {
      const snap: UiSnapshot = { ...parcial, savedAt: Date.now() };
      sessionStorage.setItem(SNAP_KEY, JSON.stringify(snap));
    } catch {
      // quota / private mode — ignore
    }
  }
}
