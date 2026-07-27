/**
 * Produção (H19) — build com fileReplacements.
 *
 * apiBaseUrl usa a URL pública HTTPS do CloudFront (mesma origem do Angular).
 * O CloudFront encaminha /api/* e /health ao ALB (HTTP interno) — evita mixed content
 * HTTPS→HTTP. O DNS do ALB continua em terraform output alb_dns_name / alb_url.
 */
export const environment = {
  production: true,
  apiBaseUrl: 'https://d1tc2mou5q4ezo.cloudfront.net',
};
