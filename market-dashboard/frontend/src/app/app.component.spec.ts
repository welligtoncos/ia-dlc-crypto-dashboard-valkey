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

  it('deve renderizar o card com dados do endpoint mock', () => {
    const fixture = TestBed.createComponent(AppComponent);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();

    const req = http.expectOne(`${environment.apiBaseUrl}/api/dashboard`);
    req.flush({
      moeda: 'bitcoin',
      preco: 100000,
      variacao_24h: 2.5,
      media_movel: null,
      volatilidade: null,
      atualizado_em: '2026-07-27T00:00:00+00:00',
    });
    fixture.detectChanges();

    const el: HTMLElement = fixture.nativeElement;
    expect(el.textContent).toContain('bitcoin');
    expect(el.textContent).toContain('100000');
    http.verify();
  });
});
