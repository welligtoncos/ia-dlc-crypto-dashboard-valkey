/**
 * Contrato de um item de GET /api/dashboard (H11: a API retorna DashboardItem[]).
 * Ver comentário em backend/main.py.
 */
export interface DashboardItem {
  moeda: string;
  preco: number | null;
  variacao_24h: number | null;
  media_movel: number | null;
  volatilidade: number | null;
  atualizado_em: string;
}

/** Alias usado pelo CardMoeda (mesmos campos de exibição). */
export type MoedaCard = Pick<
  DashboardItem,
  'moeda' | 'preco' | 'variacao_24h' | 'media_movel' | 'volatilidade'
>;
