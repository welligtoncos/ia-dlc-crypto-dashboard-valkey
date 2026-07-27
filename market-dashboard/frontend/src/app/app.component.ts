import { Component } from '@angular/core';
import { CardMoedaComponent } from './card-moeda/card-moeda.component';
import { MoedaCard } from './models/moeda-card.model';
import { environment } from '../environments/environment';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CardMoedaComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent {
  /** Objeto de exemplo — H01 sem HTTP; API base só em environment. */
  readonly exemploBitcoin: MoedaCard = {
    moeda: 'bitcoin',
    preco: null,
    variacao_24h: null,
    media_movel: null,
    volatilidade: null,
  };

  /** Referência à config (garante uso do environment; sem hardcode de URL no template). */
  readonly apiBaseUrl = environment.apiBaseUrl;
}
