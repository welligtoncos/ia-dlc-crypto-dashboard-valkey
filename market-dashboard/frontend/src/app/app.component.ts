import { Component, OnInit, inject } from '@angular/core';
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
        this.carregando = false;
      },
      error: () => {
        this.erro = 'Não foi possível carregar o dashboard. Verifique se o BFF está em http://localhost:8000.';
        this.carregando = false;
      },
    });
  }
}
