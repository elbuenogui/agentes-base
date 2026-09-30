// transcrever-servico — serviço de transcrição para projetos clientes (D-37), começando pela Mari.
//
// Chamada só de servidor: `POST` `multipart/form-data` com o campo `audio` e o cabeçalho
// `x-servico-chave`. O projeto cliente sai da chave que casou (tabela PROJETOS abaixo) — nenhum campo
// do corpo escolhe projeto, modelo ou streaming; campos além de `audio` são ignorados.
//
// Implantada com `verify_jwt: false`: a autenticação é a chave do projeto, comparada em tempo
// constante. Sem CORS de propósito (nenhum Access-Control-Allow-Origin): o cliente é servidor, e o
// navegador que tentar chamar direto deve falhar.
//
// Registro: uma linha em `servicos.transcricao_uso` para toda requisição que passou da autenticação
// (schema em `nucleo-remoto/banco/servicos_base.sql`) — só consumo, **nunca o texto**. Teto de gasto
// por dia e por projeto, lido de `servicos.gasto_do_dia`; se a consulta falhar, a função recusa
// (falha fechada: o serviço é público e pago).
//
// Banco pelo `SUPABASE_DB_URL` com `npm:postgres`: um cliente por requisição com uma conexão só
// (`max: 1`), fechado no fim. Manter conexão aberta entre requisições esgotou o Postgres em 29/09.
// Cada acesso numa transação com `set local role service_role`.
//
// Segredos: SERVICO_CHAVE_<PROJETO> e OPENAI_API_KEY_<PROJETO> (ver PROJETOS); SERVICO_TETO_DIARIO_USD
// é opcional (padrão US$ 1,00).
//
// Trechos copiados da função `transcrever` (tradução de erros da OpenAI, custo por tokens, prazo de
// 120 s em uma tentativa); nada é importado dela.
//
// Nunca loga texto transcrito, chave nem áudio.

import postgres from "npm:postgres@3.4.5";

const VERSAO_CONTRATO_SERVICO = "1";
const MODELO = "gpt-4o-transcribe";
const TAMANHO_MAXIMO_AUDIO_BYTES = 4 * 1024 * 1024;
// Prazo único de 120 s para a chamada inteira, sem novas tentativas (como na `transcrever`).
const PRAZO_OPENAI_MS = 120_000;
const TETO_DIARIO_PADRAO_USD = 1.0;
const TAMANHO_MINIMO_CHAVE = 32;

// Projetos clientes: nome -> nomes dos segredos. Segredo de chave ausente ou curto = projeto desligado.
const PROJETOS: Record<string, { chave: string; openai: string }> = {
  mari: { chave: "SERVICO_CHAVE_MARI", openai: "OPENAI_API_KEY_MARI" },
};

// Mesmos preços da `transcrever` (e de `main.py`) para gpt-4o-transcribe, em dólares.
const PRECO_ENTRADA_POR_TOKEN_USD = 2.50 / 1_000_000;
const PRECO_SAIDA_POR_TOKEN_USD = 10.00 / 1_000_000;
const PRECO_POR_MINUTO_USD = 0.006;

const CABECALHOS = { "Content-Type": "application/json", "X-Servico-Contrato": VERSAO_CONTRATO_SERVICO };

type Usage = {
  type?: string;
  input_tokens?: number;
  output_tokens?: number;
  total_tokens?: number;
  seconds?: number;
} | null | undefined;

// Uma linha de `servicos.transcricao_uso` (menos projeto e timestamp). Nunca guarda texto.
type Uso = {
  modelo: string | null;
  custo_usd: number;
  input_tokens: number | null;
  output_tokens: number | null;
  total_tokens: number | null;
  bytes_audio: number | null;
  latencia_ms: number | null;
  codigo: string | null;
};

type Sql = ReturnType<typeof postgres>;

class ErroServico extends Error {
  constructor(public status: number, public codigo: string, public detail: string) {
    super(detail);
  }
}

function json(corpo: unknown, status = 200): Response {
  return new Response(JSON.stringify(corpo), { status, headers: CABECALHOS });
}

function respostaDeErro(e: ErroServico): Response {
  return json({ detail: e.detail, codigo: e.codigo }, e.status);
}

// Só o nome e o código do erro vão para o log — nunca a mensagem inteira, que poderia carregar dado.
function descreverFalha(e: unknown): string {
  const nome = (e as { name?: string })?.name ?? "desconhecido";
  const codigo = (e as { code?: string })?.code;
  return codigo ? `${nome} (${codigo})` : nome;
}

// ---------- autenticação ----------

async function resumoSha256(valor: string): Promise<Uint8Array> {
  return new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(valor)));
}

// Compara a chave recebida com a de cada projeto em tempo constante: os dois lados viram SHA-256
// (mesmo tamanho) e a comparação percorre os 32 bytes sem sair antes; todos os projetos são
// comparados, mesmo depois de um casar.
async function projetoDaChave(recebida: string): Promise<string | null> {
  const r = await resumoSha256(recebida);
  let achado: string | null = null;
  for (const [nome, segredos] of Object.entries(PROJETOS)) {
    const esperada = Deno.env.get(segredos.chave) ?? "";
    const ligado = esperada.length >= TAMANHO_MINIMO_CHAVE;
    const e = await resumoSha256(ligado ? esperada : "");
    let diferenca = 0;
    for (let i = 0; i < r.length; i++) diferenca |= r[i] ^ e[i];
    if (ligado && diferenca === 0 && achado === null) achado = nome;
  }
  return achado;
}

// ---------- banco ----------

function abrirBanco(): Sql {
  const url = Deno.env.get("SUPABASE_DB_URL");
  if (!url) throw new Error("SUPABASE_DB_URL ausente");
  return postgres(url, { max: 1, prepare: false, idle_timeout: 5, connect_timeout: 10 });
}

// deno-lint-ignore no-explicit-any
async function comoServiceRole<T>(sql: Sql, fn: (tx: any) => Promise<T>): Promise<T> {
  // deno-lint-ignore no-explicit-any
  return await sql.begin(async (tx: any) => {
    await tx`set local role service_role`;
    return await fn(tx);
  }) as T;
}

async function gastoDoDia(sql: Sql, projeto: string): Promise<number> {
  const linhas = await comoServiceRole(sql, (tx) => tx`select servicos.gasto_do_dia(${projeto}) as gasto`);
  // deno-lint-ignore no-explicit-any
  const gasto = Number((linhas as any)[0]?.gasto);
  if (!Number.isFinite(gasto)) throw new Error("gasto_do_dia devolveu valor não numérico");
  return gasto;
}

async function registrarUso(sql: Sql, projeto: string, uso: Uso): Promise<void> {
  await comoServiceRole(sql, (tx) => tx`
    insert into servicos.transcricao_uso
      (projeto, modelo, custo_usd, input_tokens, output_tokens, total_tokens, bytes_audio, latencia_ms, codigo)
    values
      (${projeto}, ${uso.modelo}, ${uso.custo_usd}, ${uso.input_tokens}, ${uso.output_tokens},
       ${uso.total_tokens}, ${uso.bytes_audio}, ${uso.latencia_ms}, ${uso.codigo})`);
}

// Teto do dia: segredo opcional; ausente ou inválido = padrão. Zero é válido (bloqueia tudo).
function tetoDiarioUsd(): number {
  const bruto = Deno.env.get("SERVICO_TETO_DIARIO_USD");
  if (bruto === undefined || bruto.trim() === "") return TETO_DIARIO_PADRAO_USD;
  const valor = Number(bruto.trim());
  return Number.isFinite(valor) && valor >= 0 ? valor : TETO_DIARIO_PADRAO_USD;
}

// ---------- OpenAI ----------

// Mesma tabela da `transcrever`, com o `detail` citando o segredo do projeto.
function erroDaOpenAI(segredo: string, falha: unknown, statusHttp?: number): ErroServico {
  if (statusHttp === 401) {
    return new ErroServico(
      502,
      "FALHA_AUTENTICACAO",
      `Falha de autenticação na API da OpenAI — verifique o segredo ${segredo} nas Edge Functions do Supabase`,
    );
  }
  if (statusHttp !== undefined) {
    return new ErroServico(
      502,
      "API_RECUSOU",
      `A API da OpenAI recusou a requisição (HTTP ${statusHttp}) — verifique o formato do arquivo de áudio`,
    );
  }
  const nome = (falha as { name?: string })?.name;
  if (nome === "TimeoutError" || nome === "AbortError") {
    return new ErroServico(504, "TEMPO_ESGOTADO", "A API da OpenAI não respondeu a tempo — tente novamente");
  }
  return new ErroServico(502, "SEM_CONEXAO", "Não foi possível conectar à API da OpenAI — verifique a rede");
}

// Mesmo cálculo da `transcrever` (tokens; senão preço por minuto; senão 0).
function calcularCusto(usage: Usage) {
  if (usage?.type === "tokens") {
    const entrada = usage.input_tokens ?? 0;
    const saida = usage.output_tokens ?? 0;
    return {
      custo_usd: entrada * PRECO_ENTRADA_POR_TOKEN_USD + saida * PRECO_SAIDA_POR_TOKEN_USD,
      input_tokens: usage.input_tokens ?? null,
      output_tokens: usage.output_tokens ?? null,
      total_tokens: usage.total_tokens ?? null,
    };
  }
  const segundos = usage?.seconds ?? null;
  return {
    custo_usd: segundos !== null ? (segundos / 60) * PRECO_POR_MINUTO_USD : 0,
    input_tokens: null,
    output_tokens: null,
    total_tokens: null,
  };
}

// Uma tentativa, sem streaming. Toda falha sai como ErroServico.
async function chamarOpenAI(
  chave: string,
  segredo: string,
  audio: File,
): Promise<{ text?: string; usage?: Usage }> {
  const form = new FormData();
  form.append("model", MODELO);
  form.append("file", audio, audio.name || "audio");
  const base = (Deno.env.get("OPENAI_BASE_URL") ?? "https://api.openai.com/v1").replace(/\/+$/, "");
  let resp: Response;
  try {
    resp = await fetch(`${base}/audio/transcriptions`, {
      method: "POST",
      headers: { Authorization: `Bearer ${chave}` },
      body: form,
      signal: AbortSignal.timeout(PRAZO_OPENAI_MS),
    });
  } catch (falha) {
    throw erroDaOpenAI(segredo, falha);
  }
  if (!resp.ok) {
    await resp.body?.cancel();
    throw erroDaOpenAI(segredo, null, resp.status);
  }
  try {
    return await resp.json();
  } catch (falha) {
    throw erroDaOpenAI(segredo, falha);
  }
}

// ---------- fluxo ----------

// Lê e descarta o corpo que não vai ser usado (405 e 401), pedaço a pedaço, sem acumular na memória.
// No Supabase, responder sem ler o corpo trava o envio do cliente nos intermediários, e a plataforma
// derruba a requisição pelo tempo (Correção 1 da Etapa 2). Falha ao ler é ignorada.
async function drenarCorpo(req: Request): Promise<void> {
  if (!req.body) return;
  try {
    const leitor = req.body.getReader();
    while (!(await leitor.read()).done) {
      // descarta o pedaço
    }
  } catch {
    // o cliente desistiu ou o corpo já foi lido; a resposta segue igual
  }
}

// Passos 3 a 8 (depois da autenticação). Preenche `uso` à medida que avança.
async function transcrever(req: Request, projeto: string, uso: Uso, banco: () => Sql): Promise<Response> {
  const segredos = PROJETOS[projeto];

  // 3. multipart com o campo `audio`
  const tipo = (req.headers.get("Content-Type") ?? "").toLowerCase();
  if (!tipo.startsWith("multipart/form-data")) {
    throw new ErroServico(422, "REQUISICAO_INVALIDA", "O corpo precisa ser multipart/form-data com o campo 'audio'");
  }
  let form: FormData;
  try {
    form = await req.formData();
  } catch {
    throw new ErroServico(422, "REQUISICAO_INVALIDA", "O corpo precisa ser multipart/form-data com o campo 'audio'");
  }
  const audio = form.get("audio");
  if (!(audio instanceof File)) {
    throw new ErroServico(422, "REQUISICAO_INVALIDA", "Campo 'audio' ausente no formulário");
  }
  uso.bytes_audio = audio.size;

  // 4. vazio
  if (audio.size === 0) {
    throw new ErroServico(400, "AUDIO_VAZIO", "Arquivo de áudio vazio");
  }
  // 5. tamanho
  if (audio.size > TAMANHO_MAXIMO_AUDIO_BYTES) {
    const tamanhoMb = (audio.size / (1024 * 1024)).toFixed(1).replace(".", ",");
    const limiteMb = TAMANHO_MAXIMO_AUDIO_BYTES / (1024 * 1024);
    throw new ErroServico(413, "ARQUIVO_MUITO_GRANDE", `Arquivo de ${tamanhoMb} MB; o limite é ${limiteMb} MB`);
  }

  // 6. teto do dia (falha fechada)
  let gasto: number;
  try {
    gasto = await gastoDoDia(banco(), projeto);
  } catch (falha) {
    console.error(`[transcrever-servico] falha ao consultar o gasto do dia (${projeto}): ${descreverFalha(falha)}`);
    throw new ErroServico(
      503,
      "LIMITE_INDISPONIVEL",
      "Não foi possível conferir o limite diário de gasto — tente novamente mais tarde",
    );
  }
  if (gasto >= tetoDiarioUsd()) {
    throw new ErroServico(429, "LIMITE_DIARIO", "Limite diário de gasto do projeto atingido — tente novamente amanhã");
  }

  // 7. chave da OpenAI do projeto
  const chaveOpenAI = Deno.env.get(segredos.openai);
  if (!chaveOpenAI) {
    throw new ErroServico(
      503,
      "SEM_CHAVE",
      `${segredos.openai} não configurada — crie o segredo nas Edge Functions do Supabase`,
    );
  }

  // 8. chamada paga
  uso.modelo = MODELO;
  const inicio = performance.now();
  let resultado: { text?: string; usage?: Usage };
  try {
    resultado = await chamarOpenAI(chaveOpenAI, segredos.openai, audio);
  } finally {
    uso.latencia_ms = Math.round(performance.now() - inicio);
  }
  Object.assign(uso, calcularCusto(resultado.usage));
  const texto = typeof resultado.text === "string" ? resultado.text : "";
  return json({ transcricao: texto });
}

async function atender(req: Request): Promise<Response> {
  // 1. método
  if (req.method !== "POST") {
    await drenarCorpo(req);
    return json({ detail: "Método não permitido — use POST", codigo: "METODO_NAO_PERMITIDO" }, 405);
  }

  // 2. chave
  const recebida = req.headers.get("x-servico-chave") ?? "";
  const projeto = recebida ? await projetoDaChave(recebida) : null;
  if (!projeto) {
    await drenarCorpo(req);
    return json({ detail: "Chave do serviço ausente ou inválida", codigo: "CHAVE_INVALIDA" }, 401);
  }

  // Daqui em diante toda requisição deixa uma linha de uso. Um cliente de banco por requisição,
  // aberto só se for preciso e fechado no fim.
  const conexao: { sql: Sql | null } = { sql: null };
  const banco = () => (conexao.sql ??= abrirBanco());
  const uso: Uso = {
    modelo: null,
    custo_usd: 0,
    input_tokens: null,
    output_tokens: null,
    total_tokens: null,
    bytes_audio: null,
    latencia_ms: null,
    codigo: null,
  };

  let resposta: Response;
  try {
    resposta = await transcrever(req, projeto, uso, banco);
  } catch (e) {
    if (e instanceof ErroServico) {
      uso.codigo = e.codigo;
      resposta = respostaDeErro(e);
    } else {
      console.error(`[transcrever-servico] erro inesperado: ${descreverFalha(e)}`);
      uso.codigo = "ERRO_INTERNO";
      resposta = json({ detail: "Erro interno do serviço de transcrição", codigo: "ERRO_INTERNO" }, 500);
    }
  }

  // Registro acessório: falha aqui não quebra a resposta; vai só para o log, sem texto, chave ou áudio.
  try {
    await registrarUso(banco(), projeto, uso);
  } catch (falha) {
    console.error(
      `[transcrever-servico] falha ao registrar o uso (${projeto}, ${uso.codigo ?? "sucesso"}): ${descreverFalha(falha)}`,
    );
  } finally {
    if (conexao.sql) {
      try {
        await conexao.sql.end({ timeout: 5 });
      } catch {
        // já fechado
      }
    }
  }
  return resposta;
}

Deno.serve(async (req: Request) => {
  try {
    return await atender(req);
  } catch (e) {
    console.error(`[transcrever-servico] erro inesperado: ${descreverFalha(e)}`);
    return json({ detail: "Erro interno do serviço de transcrição", codigo: "ERRO_INTERNO" }, 500);
  }
});
