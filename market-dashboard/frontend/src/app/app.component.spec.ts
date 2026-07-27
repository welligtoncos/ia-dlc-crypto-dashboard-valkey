import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { AppComponent } from './app.component';
import { environment } from '../environments/environment';

describe('AppComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AppComponent],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    }).compileComponents();
  });

  it('mantem os tres cards visiveis com merge parcial da API', () => {
    const fixture = TestBed.createComponent(AppComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelectorAll('app-card-moeda').length).toBe(3);

    const reqDash = http.expectOne(`${environment.apiBaseUrl}/api/dashboard`);
    reqDash.flush([
      {
        moeda: 'bitcoin',
        preco: 65000,
        variacao_24h: 1,
        media_movel: 64000,
        volatilidade: 0.5,
        atualizado_em: '2026-07-27T00:00:00+00:00',
      },
      {
        moeda: 'ethereum',
        preco: 3500,
        variacao_24h: -2,
        media_movel: 3400,
        volatilidade: 1.2,
        atualizado_em: '2026-07-27T00:00:00+00:00',
      },
      {
        moeda: 'solana',
        preco: 100,
        variacao_24h: 0.5,
        media_movel: 99,
        volatilidade: 0.1,
        atualizado_em: '2026-07-27T00:00:00+00:00',
      },
    ]);

    const reqLog = http.expectOne(
      `${environment.apiBaseUrl}/api/observability/events?limit=100`,
    );
    reqLog.flush([]);

    // series carregadas apos dashboard
    for (const moeda of ['bitcoin', 'ethereum', 'solana']) {
      const req = http.expectOne(
        `${environment.apiBaseUrl}/api/series/${moeda}?limit=40`,
      );
      req.flush({
        moeda,
        chave: `serie:${moeda}:precos`,
        janela_sma: 20,
        total: 2,
        pontos: [
          { ts: '2026-07-27T00:00:00Z', preco: 1, media_movel: null },
          { ts: '2026-07-27T00:01:00Z', preco: 2, media_movel: null },
        ],
      });
    }

    fixture.detectChanges();

    const el: HTMLElement = fixture.nativeElement;
    expect(el.textContent).toContain('bitcoin');
    expect(el.textContent).toContain('Histórico da série');
    expect(el.querySelectorAll('app-card-moeda').length).toBe(3);
    http.verify();
  });
});
