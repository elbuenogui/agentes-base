// consumo — Operação 2 do contrato do núcleo (`GET /consumo`) como Edge Function do Supabase.
//
// Mesma forma de `GET /consumo` de `transcritor/backend/main.py` (`sessao`, `por_dia`, `requisicoes`),
// lida de `assistente.consumo` e `assistente.transcricoes` **como o usuário** — o RLS só devolve as
// linhas dele. Mesmo padrão de cliente e de conferência de usuário da função `transcrever`; nenhuma
// chave `service_role`. As divergências em relação ao núcleo local estão declaradas no PROGRESSO da
// Etapa 4 e marcadas abaixo com "Divergência:".
//
// Implantada com `verify_jwt: true`. Nunca loga texto de transcrição, token nem chave.

import { createClient } from "npm:@supabase/supabase-js@2";

const VERSAO_CONTRATO_NUCLEO = "2";
const CABECALHO_CONTRATO = { "X-Nucleo-Contrato": VERSAO_CONTRATO_NUCLEO };
// Sem CORS de propósito: nenhum Access-Control-Allow-Origin (o cliente é o app de desktop; B-08).

// A API de dados devolve no máximo 1000 linhas por chamada: lê em páginas até o fim.
const TAMANHO_PAGINA = 1000;
// Divergência: `sessao` e `por_dia` usam o dia do calendário de São Paulo (o local usava o processo e
// a data UTC do timestamp).
const FUSO = "America/Sao_Paulo";
const formatoData = new Intl.DateTimeFormat("en-CA", {
  timeZone: FUSO,
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
});

class ErroNucleo extends Error {
  constructor(public status: number, public codigo: string, public detail: string) {
    super(detail);
  }
}

function json(corpo: unknown, status = 200): Response {
  return new Response(JSON.stringify(corpo), {
    status,
    headers: { "Content-Type": "application/json", ...CABECALHO_CONTRATO },
  });
}

function dataEmSaoPaulo(timestamp: string | null): string {
  if (!timestamp) return "";
  const instante = new Date(timestamp);
  return Number.isNaN(instante.getTime()) ? "" : formatoData.format(instante); // AAAA-MM-DD
}

type LinhaConsumo = {
  id: string;
  timestamp: string | null;
  modelo: string | null;
  custo_usd: number | string | null;
  total_tokens: number | null;
};
type LinhaTranscricao = { id_consumo: string | null; texto: string | null };

// Lê uma tabela inteira em páginas, ordenada por uma chave única (estável entre páginas).
// deno-lint-ignore no-explicit-any
async function lerTudo<T>(banco: any, tabela: string, colunas: string): Promise<T[]> {
  const linhas: T[] = [];
  for (let inicio = 0; ; inicio += TAMANHO_PAGINA) {
    const { data, error } = await banco
      .from(tabela)
      .select(colunas)
      .order("id", { ascending: true })
      .range(inicio, inicio + TAMANHO_PAGINA - 1);
    if (error) {
      console.error(`[consumo] falha ao ler ${tabela}: ${error.code} ${error.message}`);
      throw new ErroNucleo(
        502,
        "FALHA_BANCO",
        "Não foi possível ler o consumo no banco do Supabase — tente novamente",
      );
    }
    linhas.push(...(data as T[]));
    if (!data || data.length < TAMANHO_PAGINA) return linhas;
  }
}

async function consumo(req: Request): Promise<Response> {
  if (req.method !== "GET") {
    return json({ detail: "Método não permitido — use GET", codigo: "METODO_NAO_PERMITIDO" }, 405);
  }

  // O gateway já recusou quem não tem JWT válido (verify_jwt). Aqui confirma que é um usuário do Auth:
  // a chave anônima também é um JWT válido.
  const autorizacao = req.headers.get("Authorization") ?? "";
  const token = autorizacao.replace(/^Bearer\s+/i, "");
  const banco = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_ANON_KEY")!, {
    global: { headers: { Authorization: autorizacao } },
    db: { schema: "assistente" },
    auth: { persistSession: false, autoRefreshToken: false },
  });
  if (!token) {
    throw new ErroNucleo(401, "NAO_AUTENTICADO", "Sessão ausente — faça login de novo");
  }
  const { data: sessaoAuth, error: erroSessao } = await banco.auth.getUser(token);
  if (erroSessao || !sessaoAuth?.user) {
    throw new ErroNucleo(401, "NAO_AUTENTICADO", "Sessão inválida ou expirada — faça login de novo");
  }

  const [linhasConsumo, linhasTranscricoes] = await Promise.all([
    lerTudo<LinhaConsumo>(banco, "consumo", "id,timestamp,modelo,custo_usd,total_tokens"),
    lerTudo<LinhaTranscricao>(banco, "transcricoes", "id,id_consumo,texto"),
  ]);

  // Texto por id_consumo, como o local faz com transcricoes.jsonl (só texto não vazio).
  const textosPorId = new Map<string, string>();
  for (const t of linhasTranscricoes) {
    if (t.id_consumo && t.texto) textosPorId.set(t.id_consumo, t.texto);
  }

  const hoje = formatoData.format(new Date());
  const sessao = { requisicoes: 0, tokens: 0, custo_usd: 0 };
  const porDia = new Map<string, { data: string; requisicoes: number; tokens: number; custo_usd: number }>();
  const requisicoes: {
    id: string;
    timestamp: string | null;
    modelo: string | null;
    custo_usd: number;
    texto: string | null;
  }[] = [];

  for (const linha of linhasConsumo) {
    const custo = Number(linha.custo_usd ?? 0) || 0;
    const tokens = linha.total_tokens ?? 0;
    const data = dataEmSaoPaulo(linha.timestamp);
    const agregado = porDia.get(data) ?? { data, requisicoes: 0, tokens: 0, custo_usd: 0 };
    agregado.requisicoes += 1;
    agregado.tokens += tokens;
    agregado.custo_usd += custo;
    porDia.set(data, agregado);
    if (data === hoje) {
      // Divergência: `sessao` = acumulado do dia corrente em São Paulo (não há "processo" remoto).
      sessao.requisicoes += 1;
      sessao.tokens += tokens;
      sessao.custo_usd += custo;
    }
    requisicoes.push({
      id: linha.id,
      timestamp: linha.timestamp,
      modelo: linha.modelo,
      custo_usd: custo,
      texto: textosPorId.get(linha.id) ?? null,
    });
  }

  const instante = (t: string | null) => (t ? new Date(t).getTime() : 0) || 0;
  return json({
    sessao,
    por_dia: [...porDia.values()].sort((a, b) => (a.data < b.data ? -1 : a.data > b.data ? 1 : 0)),
    requisicoes: requisicoes.sort((a, b) => instante(a.timestamp) - instante(b.timestamp)),
  });
}

Deno.serve(async (req: Request) => {
  try {
    return await consumo(req);
  } catch (e) {
    if (e instanceof ErroNucleo) return json({ detail: e.detail, codigo: e.codigo }, e.status);
    console.error(`[consumo] erro inesperado: ${(e as Error)?.name}: ${(e as Error)?.message}`);
    return json({ detail: "Erro interno do núcleo remoto", codigo: "ERRO_INTERNO" }, 500);
  }
});
