/** Dados exibidos pelo CardMoeda (contrato visual da H01; API real vem depois). */
export interface MoedaCard {
  moeda: string;
  preco: number | null;
  variacao_24h: number | null;
  media_movel: number | null;
  volatilidade: number | null;
}
