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

  it('deve renderizar um card por moeda da lista', () => {
    const fixture = TestBed.createComponent(AppComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();

    const req = http.expectOne(`${environment.apiBaseUrl}/api/dashboard`);
    req.flush([
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
        variacao_24h: 2,
        media_movel: 3400,
        volatilidade: 1.2,
        atualizado_em: '2026-07-27T00:00:00+00:00',
      },
    ]);
    fixture.detectChanges();

    const el: HTMLElement = fixture.nativeElement;
    expect(el.textContent).toContain('bitcoin');
    expect(el.textContent).toContain('ethereum');
    expect(el.querySelectorAll('app-card-moeda').length).toBe(2);
    http.verify();
  });
});
