import { DatePipe, DecimalPipe } from '@angular/common';
import { Component, Input } from '@angular/core';
import { MoedaCard } from '../models/moeda-card.model';

export type CardEstado = 'aguardando' | 'na_fila' | 'processando' | 'atualizado' | 'ok';

@Component({
  selector: 'app-card-moeda',
  standalone: true,
  imports: [DatePipe, DecimalPipe],
  templateUrl: './card-moeda.component.html',
  styleUrl: './card-moeda.component.css',
})
export class CardMoedaComponent {
  @Input({ required: true }) dados!: MoedaCard;
  @Input() estado: CardEstado = 'ok';

  get temDados(): boolean {
    return this.dados.preco !== null && this.dados.preco !== undefined;
  }

  get rotuloEstado(): string {
    switch (this.estado) {
      case 'aguardando':
        return 'Aguardando dados';
      case 'na_fila':
        return 'Na fila';
      case 'processando':
        return 'Processando';
      case 'atualizado':
        return 'Recém atualizado';
      default:
        return 'Sincronizado';
    }
  }

  variacaoClass(): string {
    const v = this.dados.variacao_24h;
    if (v === null || v === undefined) {
      return '';
    }
    if (v > 0) {
      return 'card-moeda__var--up';
    }
    if (v < 0) {
      return 'card-moeda__var--down';
    }
    return '';
  }
}
