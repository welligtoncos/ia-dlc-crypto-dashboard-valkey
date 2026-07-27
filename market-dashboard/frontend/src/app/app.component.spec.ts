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

  it('deve renderizar dados reais do dashboard', () => {
    const fixture = TestBed.createComponent(AppComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();

    const req = http.expectOne(`${environment.apiBaseUrl}/api/dashboard`);
    req.flush({
      moeda: 'bitcoin',
      preco: 65151,
      variacao_24h: 1.14,
      media_movel: null,
      volatilidade: null,
      atualizado_em: '2026-07-27T00:00:00+00:00',
    });
    fixture.detectChanges();

    const el: HTMLElement = fixture.nativeElement;
    expect(el.textContent).toContain('bitcoin');
    expect(el.textContent).toContain('65151');
    http.verify();
  });

  it('deve exibir estado de erro em 502 sem quebrar', () => {
    const fixture = TestBed.createComponent(AppComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();

    const req = http.expectOne(`${environment.apiBaseUrl}/api/dashboard`);
    req.flush(
      { detail: 'Não foi possível obter dados da fonte externa (CoinGecko). timeout' },
      { status: 502, statusText: 'Bad Gateway' },
    );
    fixture.detectChanges();

    const el: HTMLElement = fixture.nativeElement;
    expect(el.textContent).toContain('CoinGecko');
    expect(el.querySelector('app-card-moeda')).toBeNull();
    http.verify();
  });
});
