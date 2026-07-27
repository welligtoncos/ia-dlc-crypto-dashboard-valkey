import { Component, OnInit, inject } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { CardMoedaComponent } from './card-moeda/card-moeda.component';
import { MoedaCard } from './models/moeda-card.model';
import { DashboardService } from './services/dashboard.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CardMoedaComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent implements OnInit {
  private readonly dashboardService = inject(DashboardService);

  dados: MoedaCard | null = null;
  erro: string | null = null;
  carregando = true;

  ngOnInit(): void {
    this.dashboardService.getDashboard().subscribe({
      next: (item) => {
        this.dados = {
          moeda: item.moeda,
          preco: item.preco,
          variacao_24h: item.variacao_24h,
          media_movel: item.media_movel,
          volatilidade: item.volatilidade,
        };
        this.erro = null;
        this.carregando = false;
      },
      error: (err: HttpErrorResponse) => {
        this.dados = null;
        this.erro = this.mensagemErro(err);
        this.carregando = false;
      },
    });
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
