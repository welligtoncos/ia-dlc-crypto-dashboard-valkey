export interface SeriePonto {
  ts: string;
  preco: number;
  media_movel: number | null;
}

export interface SerieHistorico {
  moeda: string;
  chave: string;
  janela_sma: number;
  total: number;
  pontos: SeriePonto[];
}
