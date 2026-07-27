import { DatePipe } from '@angular/common';
import { Component, OnDestroy, OnInit, inject } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { forkJoin, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { CardEstado, CardMoedaComponent } from './card-moeda/card-moeda.component';
import { MoedaCard } from './models/moeda-card.model';
import { ObservabilityEvent } from './models/observability-event.model';
import { SerieHistorico } from './models/serie-historico.model';
import { SerieHistoricoComponent } from './serie-historico/serie-historico.component';
import { DashboardService } from './services/dashboard.service';
import { ObservabilityService } from './services/observability.service';
import { SerieService } from './services/serie.service';
import { UiSnapshotService } from './services/ui-snapshot.service';

/** Log / desenho da fila — leve (so le LIST no Valkey) */
const LOG_POLL_MS = 1500;
/** Soft refresh dos cards — evita spam de MISS/CoinGecko */
const DASHBOARD_POLL_MS = 15_000;
/** Duracao total da reapresentacao visual (ciclo real e ~1s — desenhamos mais lento) */
const CICLO_REPLAY_MS = 18_000;
/** Enquanto o ultimo Beat estiver nesta janela, o desenho pode ser reapresentado */
const CICLO_VISIBLE_MS = 120_000;

const MOEDAS_PADRAO = ['bitcoin', 'ethereum', 'solana'];

function cardVazio(moeda: string): MoedaCard {
  return {
    moeda,
    preco: null,
    variacao_24h: null,
    media_movel: null,
    volatilidade: null,
    atualizado_em: '',
  };
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CardMoedaComponent, SerieHistoricoComponent, DatePipe],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent implements OnInit, OnDestroy {
  private readonly dashboardService = inject(DashboardService);
  private readonly observabilityService = inject(ObservabilityService);
  private readonly serieService = inject(SerieService);
  private readonly uiSnap = inject(UiSnapshotService);

  /** Sempre 3 cards — nunca esvazia a lista (merge por moeda) */
  itens: MoedaCard[] = MOEDAS_PADRAO.map(cardVazio);
  erro: string | null = null;
  carregando = true;
  sincronizando = false;
  ultimaSyncEm: string | null = null;
  avisoSuave: string | null = null;

  moedaDestaque: string | null = null;
  moedaProcessando: string | null = null;
  moedasNaFila: string[] = [];

  seriesPorMoeda: Record<string, SerieHistorico | null> = {};
  serieErro: string | null = null;

  eventos: ObservabilityEvent[] = [];
  logErro: string | null = null;
  private logTimer: ReturnType<typeof setInterval> | null = null;
  private dashTimer: ReturnType<typeof setInterval> | null = null;
  private destaqueTimer: ReturnType<typeof setTimeout> | null = null;
  private replayTimers: ReturnType<typeof setTimeout>[] = [];
  private ultimoEventoDashboard = '';
  private dashboardEmVoo = false;
  private cicloReplayId = '';
  private replayEmAndamento = false;
  /** Ultimo ciclo detectado (para botao "Reapresentar") */
  private ultimoCicloMoedas: string[] = [];
  private ultimoCicloAncora = 0;
  /** Eventos anteriores ao F5 nao disparam sync de dashboard */
  private paginaIniciadaEm = 0;

  beatAtivo = false;
  workerAtivo = false;
  pipelineAtivo = false;
  setaEnfileira = false;
  setaConsome = false;
  filaSlots: (string | null)[] = [null, null, null];
  filaCheia = false;
  filaStatus = 'Aguardando o Beat enfileirar (~90s) ou um ciclo recente no log…';

  ngOnInit(): void {
    this.paginaIniciadaEm = Date.now();
    this.restaurarSnapshot();
    this.carregarDashboard();
    this.atualizarLog();
    this.logTimer = setInterval(() => this.atualizarLog(), LOG_POLL_MS);
    this.dashTimer = setInterval(() => this.carregarDashboard(), DASHBOARD_POLL_MS);
  }

  ngOnDestroy(): void {
    if (this.logTimer) {
      clearInterval(this.logTimer);
    }
    if (this.dashTimer) {
      clearInterval(this.dashTimer);
    }
    if (this.destaqueTimer) {
      clearTimeout(this.destaqueTimer);
    }
    this.limparReplayTimers();
  }

  carregarDashboard(): void {
    if (this.dashboardEmVoo) {
      return;
    }
    this.dashboardEmVoo = true;
    // Nunca volta para "Carregando" se ja houver dados (F5 / soft refresh).
    this.sincronizando = this.itens.some((i) => i.preco !== null);
    if (!this.sincronizando) {
      this.carregando = true;
    }
    this.dashboardService.getDashboard().subscribe({
      next: (lista) => {
        this.aplicarLista(lista);
        this.erro = null;
        this.avisoSuave = null;
        this.carregando = false;
        this.sincronizando = false;
        this.dashboardEmVoo = false;
        this.ultimaSyncEm = new Date().toISOString();
        this.persistirSnapshot();
        this.carregarSeries();
      },
      error: (err: HttpErrorResponse) => {
        this.dashboardEmVoo = false;
        this.sincronizando = false;
        this.carregando = false;
        if (this.itens.every((i) => i.preco === null)) {
          this.erro = this.mensagemErro(err);
        } else {
          this.avisoSuave =
            'Sincronização temporária falhou — mantendo últimos valores (cache local da sessão + Valkey).';
        }
        this.persistirSnapshot();
      },
    });
  }

  private restaurarSnapshot(): void {
    const snap = this.uiSnap.ler();
    if (!snap) {
      return;
    }
    this.itens = snap.itens;
    this.seriesPorMoeda = snap.seriesPorMoeda ?? {};
    this.eventos = snap.eventos ?? [];
    this.ultimaSyncEm = snap.ultimaSyncEm;
    // Nao restaura cicloReplayId — assim o desenho da fila anima de novo apos F5.
    this.ultimoEventoDashboard = snap.ultimoEventoDashboard ?? '';
    this.carregando = false;
    this.filaStatus =
      'Sessão restaurada — preparando reapresentação da fila…';
  }

  private persistirSnapshot(): void {
    this.uiSnap.salvar({
      itens: this.itens,
      seriesPorMoeda: this.seriesPorMoeda,
      eventos: this.eventos.slice(0, 40),
      ultimaSyncEm: this.ultimaSyncEm,
      cicloReplayId: this.cicloReplayId,
      ultimoEventoDashboard: this.ultimoEventoDashboard,
    });
  }

  private carregarSeries(): void {
    const moedas = this.itens.map((i) => i.moeda);
    if (!moedas.length) {
      return;
    }
    const reqs = moedas.map((m) =>
      this.serieService.getSerie(m, 40).pipe(catchError(() => of(null))),
    );
    forkJoin(reqs).subscribe((listas) => {
      const mapa: Record<string, SerieHistorico | null> = { ...this.seriesPorMoeda };
      let ok = 0;
      listas.forEach((s, idx) => {
        if (s) {
          mapa[moedas[idx]] = s;
          ok += 1;
        }
        // Se falhar uma moeda, mantem o historico anterior dessa moeda (F5/rede).
      });
      this.seriesPorMoeda = mapa;
      this.serieErro =
        ok === 0 && !Object.values(mapa).some((v) => !!v)
          ? 'Não foi possível carregar o histórico das séries (BFF/Valkey).'
          : null;
      this.persistirSnapshot();
    });
  }

  estadoDoCard(moeda: string): CardEstado {
    if (this.moedaProcessando === moeda) {
      return 'processando';
    }
    if (this.moedasNaFila.includes(moeda)) {
      return 'na_fila';
    }
    if (this.moedaDestaque === moeda) {
      return 'atualizado';
    }
    const item = this.itens.find((i) => i.moeda === moeda);
    if (!item || item.preco === null) {
      return 'aguardando';
    }
    return 'ok';
  }

  get statusIndicadores(): string {
    const comDados = this.itens.filter((i) => i.preco !== null).length;
    const total = this.itens.length;
    if (this.carregando && comDados === 0) {
      return `Carregando indicadores de ${total} moedas…`;
    }
    if (this.moedaProcessando) {
      return `Worker atualizando ${this.moedaProcessando} — os demais cards permanecem visíveis.`;
    }
    if (this.moedasNaFila.length) {
      return `${this.moedasNaFila.length} moeda(s) na fila Valkey — cards estáveis até o Worker concluir.`;
    }
    if (this.sincronizando) {
      return `Sincronizando com o BFF (cache Valkey)… (${comDados}/${total} com dados)`;
    }
    return `${comDados}/${total} moedas com dados · F5 mantém a sessão`;
  }

  private aplicarLista(lista: MoedaCard[]): void {
    if (!lista?.length) {
      return;
    }

    const porMoeda = new Map(lista.map((i) => [i.moeda, i]));
    const ordem = [
      ...MOEDAS_PADRAO,
      ...lista.map((i) => i.moeda).filter((m) => !MOEDAS_PADRAO.includes(m)),
    ];
    const unicos = [...new Set(ordem)];

    const anteriores = new Map(this.itens.map((i) => [i.moeda, i]));
    this.itens = unicos.map((moeda) => {
      const novo = porMoeda.get(moeda);
      const ant = anteriores.get(moeda);
      if (novo) {
        return {
          moeda: novo.moeda,
          preco: novo.preco,
          variacao_24h: novo.variacao_24h,
          media_movel: novo.media_movel,
          volatilidade: novo.volatilidade,
          atualizado_em: novo.atualizado_em,
        };
      }
      return ant ?? cardVazio(moeda);
    });

    for (const moeda of unicos) {
      const ant = anteriores.get(moeda);
      const cur = this.itens.find((i) => i.moeda === moeda);
      if (
        ant &&
        cur &&
        ant.preco !== null &&
        (ant.preco !== cur.preco ||
          ant.media_movel !== cur.media_movel ||
          ant.volatilidade !== cur.volatilidade ||
          ant.atualizado_em !== cur.atualizado_em)
      ) {
        this.marcarDestaque(moeda);
        break;
      }
    }
  }

  atualizarLog(): void {
    this.observabilityService.getEvents(100).subscribe({
      next: (evs) => {
        this.eventos = evs;
        this.logErro = null;
        this.atualizarFilaViz(evs);
        this.sincronizarComFila(evs);
        this.persistirSnapshot();
      },
      error: (err: HttpErrorResponse) => {
        if (this.eventos.length === 0) {
          const code = err.status ? ` HTTP ${err.status}` : '';
          this.logErro =
            `Nao foi possivel ler o log (BFF/Valkey).${code} ` +
            'Se acabou de publicar, aguarde o deploy do BFF e atualize a pagina.';
        } else {
          this.logErro = null;
        }
      },
    });
  }

  classeFonte(source: string): string {
    return `log__src log__src--${source.replace(/_/g, '-')}`;
  }

  /**
   * So reage a conclusoes do Worker DEPOIS deste F5/carregamento.
   * Eventos antigos no Valkey nao disparam novo GET (evita bug/loop no refresh).
   */
  private sincronizarComFila(evs: ObservabilityEvent[]): void {
    const gatilho = evs.find((e) => {
      if (e.source !== 'worker' || !e.message.includes('concluida')) {
        return false;
      }
      const t = Date.parse(e.ts);
      return !Number.isNaN(t) && t >= this.paginaIniciadaEm;
    });
    if (!gatilho) {
      return;
    }
    const chave = `${gatilho.ts}|${gatilho.message}`;
    if (chave === this.ultimoEventoDashboard) {
      return;
    }
    this.ultimoEventoDashboard = chave;
    const moeda = this.moedaDoEvento(gatilho);
    if (moeda !== 'job') {
      this.marcarDestaque(moeda);
    }
    this.carregarDashboard();
  }

  private marcarDestaque(moeda: string): void {
    this.moedaDestaque = moeda;
    if (this.destaqueTimer) {
      clearTimeout(this.destaqueTimer);
    }
    this.destaqueTimer = setTimeout(() => {
      this.moedaDestaque = null;
    }, 2500);
  }

  /** Botao na UI — forca o desenho a andar de novo com o ultimo ciclo. */
  reapresentarCiclo(): void {
    if (this.replayEmAndamento) {
      return;
    }
    if (this.ultimoCicloMoedas.length && this.ultimoCicloAncora) {
      this.cicloReplayId = '';
      this.iniciarReplayCiclo(this.ultimoCicloMoedas, this.ultimoCicloAncora);
      return;
    }
    this.cicloReplayId = '';
    this.atualizarFilaViz(this.eventos);
  }

  private atualizarFilaViz(evs: ObservabilityEvent[]): void {
    if (this.replayEmAndamento) {
      return;
    }

    const enfileirou = evs.filter(
      (e) => e.source === 'beat' && e.message.includes('Enfileirou'),
    );
    if (enfileirou.length === 0) {
      this.mostrarFilaOciosa('Aguardando o primeiro ciclo do Beat (~90s)…');
      return;
    }

    const ancora = Date.parse(enfileirou[0].ts);
    if (Number.isNaN(ancora)) {
      this.mostrarFilaOciosa('Aguardando o Beat enfileirar (~90s)…');
      return;
    }

    const moedasCiclo = [
      ...new Set(
        enfileirou
          .filter((e) => Math.abs(Date.parse(e.ts) - ancora) < 5000)
          .map((e) => this.moedaDoEvento(e))
          .filter((m) => m !== 'job'),
      ),
    ];
    if (moedasCiclo.length === 0) {
      this.mostrarFilaOciosa('Aguardando o Beat enfileirar (~90s)…');
      return;
    }

    this.ultimoCicloMoedas = moedasCiclo;
    this.ultimoCicloAncora = ancora;

    const cicloId = `${ancora}|${moedasCiclo.join(',')}`;
    const idade = Date.now() - ancora;

    if (idade > CICLO_VISIBLE_MS) {
      this.mostrarFilaOciosa(
        `Ultimo ciclo ha ${Math.round(idade / 1000)}s (${moedasCiclo.join(', ')}). ` +
          'Proximo Beat ~90s — ou clique em “Reapresentar desenho”.',
      );
      return;
    }

    // Novo ciclo (ou primeiro load apos F5): SEMPRE anima o desenho.
    if (cicloId !== this.cicloReplayId) {
      this.cicloReplayId = cicloId;
      this.persistirSnapshot();
      this.iniciarReplayCiclo(moedasCiclo, ancora);
      return;
    }

    this.mostrarCicloConcluido(moedasCiclo, ancora);
  }

  private mostrarCicloConcluido(moedas: string[], ancoraMs: number): void {
    this.beatAtivo = false;
    this.workerAtivo = false;
    this.pipelineAtivo = false;
    this.setaEnfileira = false;
    this.setaConsome = false;
    this.filaSlots = [null, null, null];
    this.filaCheia = false;
    this.moedasNaFila = [];
    this.moedaProcessando = null;
    const hhmmss = new Date(ancoraMs).toLocaleTimeString();
    this.filaStatus =
      `Ultimo ciclo ${hhmmss}: Beat → Fila → Worker → pipeline concluiu (${moedas.join(', ')}). ` +
      'Clique em “Reapresentar desenho” para ver de novo, ou aguarde o proximo Beat (~90s).';
  }

  private iniciarReplayCiclo(moedas: string[], ancoraMs: number): void {
    this.limparReplayTimers();
    this.replayEmAndamento = true;
    this.cicloReplayId = `${ancoraMs}|${moedas.join(',')}`;
    const hhmmss = new Date(ancoraMs).toLocaleTimeString();

    // Passo 1 — Beat
    this.beatAtivo = true;
    this.setaEnfileira = true;
    this.setaConsome = false;
    this.workerAtivo = false;
    this.pipelineAtivo = false;
    this.filaSlots = [null, null, null];
    this.filaCheia = false;
    this.moedasNaFila = [];
    this.moedaProcessando = null;
    this.filaStatus = `▶ ${hhmmss} — Beat enfileirando ${moedas.join(', ')}…`;

    // Passo 2 — bolinhas na fila
    this.replayTimers.push(
      setTimeout(() => {
        const slots: (string | null)[] = [null, null, null];
        moedas.slice(0, 3).forEach((m, i) => {
          slots[i] = m;
        });
        this.filaSlots = [...slots];
        this.filaCheia = true;
        this.moedasNaFila = [...moedas];
        this.filaStatus = `▶ ${hhmmss} — ${moedas.length} mensagem(ns) na Fila Valkey (broker).`;
      }, 1500),
    );

    // Passo 3+ — Worker consome uma a uma (mais lento para dar tempo de observar)
    const passoMoedaMs = 2800;
    const inicioWorkerMs = 3200;
    moedas.forEach((moeda, idx) => {
      this.replayTimers.push(
        setTimeout(() => {
          this.beatAtivo = false;
          this.setaEnfileira = false;
          this.setaConsome = true;
          this.workerAtivo = true;
          this.pipelineAtivo = true;
          this.moedaProcessando = moeda;
          const restantes = moedas.slice(idx + 1);
          const slots: (string | null)[] = [null, null, null];
          restantes.slice(0, 3).forEach((m, i) => {
            slots[i] = m;
          });
          this.filaSlots = [...slots];
          this.filaCheia = restantes.length > 0;
          this.moedasNaFila = restantes;
          this.filaStatus = `▶ ${hhmmss} — Worker processando ${moeda} → pipeline (MM/vol)…`;
          this.marcarDestaque(moeda);
        }, inicioWorkerMs + idx * passoMoedaMs),
      );
    });

    const fimMs = inicioWorkerMs + moedas.length * passoMoedaMs + 1200;
    this.replayTimers.push(
      setTimeout(() => {
        this.mostrarCicloConcluido(moedas, ancoraMs);
        this.replayEmAndamento = false;
        this.persistirSnapshot();
      }, Math.min(fimMs, CICLO_REPLAY_MS)),
    );
  }

  private limparReplayTimers(): void {
    for (const t of this.replayTimers) {
      clearTimeout(t);
    }
    this.replayTimers = [];
    this.replayEmAndamento = false;
  }

  private mostrarFilaOciosa(msg: string): void {
    this.beatAtivo = false;
    this.workerAtivo = false;
    this.pipelineAtivo = false;
    this.setaEnfileira = false;
    this.setaConsome = false;
    this.filaSlots = [null, null, null];
    this.filaCheia = false;
    this.moedasNaFila = [];
    this.moedaProcessando = null;
    this.filaStatus = msg;
  }

  private moedaDoEvento(e: ObservabilityEvent): string {
    const d = e.detail?.['moeda'];
    if (typeof d === 'string' && d.trim()) {
      return d;
    }
    return 'job';
  }

  private mensagemErro(err: HttpErrorResponse): string {
    const detail = err.error?.detail;
    if (typeof detail === 'string' && detail.trim()) {
      return detail;
    }
    if (err.status === 502) {
      return 'Fonte externa indisponível. Tente novamente em instantes.';
    }
    if (err.status === 0) {
      return 'Não foi possível conectar ao BFF. Confira se está em http://localhost:8000.';
    }
    return `Erro ao carregar o dashboard (HTTP ${err.status}).`;
  }
}
