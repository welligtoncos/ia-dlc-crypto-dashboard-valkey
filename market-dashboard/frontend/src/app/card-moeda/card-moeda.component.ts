import { Component, Input } from '@angular/core';
import { MoedaCard } from '../models/moeda-card.model';

@Component({
  selector: 'app-card-moeda',
  standalone: true,
  imports: [],
  templateUrl: './card-moeda.component.html',
  styleUrl: './card-moeda.component.css',
})
export class CardMoedaComponent {
  @Input({ required: true }) dados!: MoedaCard;

  formatar(valor: number | null): string {
    return valor === null || valor === undefined ? '—' : String(valor);
  }
}
