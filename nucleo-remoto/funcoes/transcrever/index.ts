// transcrever — Operação 1 do contrato do núcleo (`POST /transcrever`) como Edge Function do Supabase.
//
// Reproduz o caminho de `/transcrever` de `transcritor/backend/main.py` (validação, chamada à OpenAI,
// streaming NDJSON, cálculo de custo, registro) e o contrato de `spec/contrato/NUCLEO.md`. As
// divergências em relação ao núcleo local estão declaradas no PROGRESSO da Etapa 3 e marcadas abaixo
// com "Divergência:".
//
// Implantada com `verify_jwt: true`: o gateway do Supabase só deixa passar requisição com JWT válido.
// A função ainda confirma que o JWT é de um **usuário** (e não a chave anônima, que também é um JWT
// válido) antes de gastar uma chamada paga.
//
// O registro no banco (schema `assistente`) é feito **com o JWT do próprio usuário** — o RLS decide o
// que ele pode gravar. Nenhuma chave `service_role` aqui. Segredo necessário: `OPENAI_API_KEY`.
//
// Nunca loga texto transcrito, token nem chave.

import { createClient } from "npm:@supabase/supabase-js@2";

const VERSAO_CONTRATO_NUCLEO = "2";
const MODELO_PADRAO = "gpt-4o-transcribe";
// Divergência: `gpt-4o-transcribe-diarize` fica fora (estoura os 150 s de uma Edge Function).
const MODELOS_PERMITIDOS = ["gpt-4o-transcribe", "gpt-4o-mini-transcribe"];
const TAMANHO_MAXIMO_AUDIO_BYTES = 25 * 1024 * 1024; // "Files can be up to 25 MB." (OpenAI)
// Divergência: prazo único de 120 s para a chamada inteira, sem novas tentativas. O núcleo local usa
// 120 s de leitura por tentativa com 2 tentativas automáticas do SDK (até ~6 min).
const PRAZO_OPENAI_MS = 120_000;
const ORIGEM = "nucleo-remoto";

// Mesmos preços de `main.py` (PRECOS_POR_TOKEN_USD e PRECO_POR_MINUTO_USD), em dólares.
const PRECOS_POR_TOKEN_USD: Record<string, { entrada: number; saida: number }> = {
  "gpt-4o-transcribe": { entrada: 2.50 / 1_000_000, saida: 10.00 / 1_000_000 },
  "gpt-4o-mini-transcribe": { entrada: 1.25 / 1_000_000, saida: 5.00 / 1_000_000 },
};
const PRECO_POR_MINUTO_USD: Record<string, number> = {
  "gpt-4o-transcribe": 0.006,
  "gpt-4o-mini-transcribe": 0.003,
};

const CABECALHO_CONTRATO = { "X-Nucleo-Contrato": VERSAO_CONTRATO_NUCLEO };
// Sem CORS de propósito: nenhum Access-Control-Allow-Origin (o cliente é o app de desktop; B-08).

type Usage = {
  type?: string;
  input_tokens?: number;
  output_tokens?: number;
  total_tokens?: number;
  seconds?: number;
} | null | undefined;

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

function respostaDeErro(e: ErroNucleo): Response {
  return json({ detail: e.detail, codigo: e.codigo }, e.status);
}

// Tradução de falha da chamada à OpenAI em (codigo, detail, status) — mesma tabela de
// `_erro_api_para_codigo`, com o texto adaptado onde citava `transcritor/.env`.
function erroDaOpenAI(falha: unknown, statusHttp?: number): ErroNucleo {
  if (statusHttp === 401) {
    return new ErroNucleo(
      502,
      "FALHA_AUTENTICACAO",
      "Falha de autenticação na API da OpenAI — verifique o segredo OPENAI_API_KEY nas Edge Functions do Supabase",
    );
  }
  if (statusHttp !== undefined) {
    return new ErroNucleo(
      502,
      "API_RECUSOU",
      `A API da OpenAI recusou a requisição (HTTP ${statusHttp}) — verifique o formato do arquivo de áudio`,
    );
  }
  const nome = (falha as { name?: string })?.name;
  if (nome === "TimeoutError" || nome === "AbortError") {
    return new ErroNucleo(504, "TEMPO_ESGOTADO", "A API da OpenAI não respondeu a tempo — tente novamente");
  }
  return new ErroNucleo(502, "SEM_CONEXAO", "Não foi possível conectar à API da OpenAI — verifique a rede");
}

// Mesmo cálculo de `_calcular_custo_usd` (ramo de transcrição).
function calcularCusto(modelo: string, usage: Usage) {
  if (usage?.type === "tokens") {
    const precos = PRECOS_POR_TOKEN_USD[modelo] ?? { entrada: 0, saida: 0 };
    const entrada = usage.input_tokens ?? 0;
    const saida = usage.output_tokens ?? 0;
    return {
      custo_usd: entrada * precos.entrada + saida * precos.saida,
      tipo_usage: "tokens",
      input_tokens: usage.input_tokens ?? null,
      output_tokens: usage.output_tokens ?? null,
      total_tokens: usage.total_tokens ?? null,
      segundos: null,
    };
  }
  // usage.type == "duration", ou usage ausente/formato inesperado: preço por minuto.
  const segundos = usage?.seconds ?? null;
  return {
    custo_usd: segundos !== null ? (segundos / 60) * (PRECO_POR_MINUTO_USD[modelo] ?? 0) : 0,
    tipo_usage: usage?.type || "ausente",
    input_tokens: null,
    output_tokens: null,
    total_tokens: null,
    segundos,
  };
}

// Registro: consumo primeiro, transcrição depois (chave estrangeira). Acessório — falha aqui nunca
// quebra a resposta ao usuário; vai só para o log da função, com código e mensagem do banco, sem texto.
// deno-lint-ignore no-explicit-any
async function registrar(banco: any, modelo: string, usage: Usage, texto: string): Promise<void> {
  const idConsumo = crypto.randomUUID();
  try {
    const { error } = await banco.from("consumo").insert({
      id: idConsumo,
      timestamp: new Date().toISOString(),
      modelo,
      ...calcularCusto(modelo, usage),
      origem: ORIGEM,
    });
    if (error) {
      console.error(`[consumo] falha ao registrar (resposta segue normalmente): ${error.code} ${error.message}`);
      return;
    }
  } catch (e) {
    console.error(`[consumo] falha ao registrar (resposta segue normalmente): ${(e as Error)?.name}`);
    return;
  }
  if (!texto || !texto.trim()) return; // como no núcleo local: transcrição vazia não é registrada
  try {
    const { error } = await banco.from("transcricoes").insert({
      id_consumo: idConsumo,
      timestamp: new Date().toISOString(),
      modelo,
      texto,
    });
    if (error) {
      console.error(`[transcricao] falha ao registrar (resposta segue normalmente): ${error.code} ${error.message}`);
    }
  } catch (e) {
    console.error(`[transcricao] falha ao registrar (resposta segue normalmente): ${(e as Error)?.name}`);
  }
}

function ehVerdadeiro(valor: FormDataEntryValue | null): boolean {
  return typeof valor === "string" && ["true", "1", "yes", "on"].includes(valor.trim().toLowerCase());
}

async function chamarOpenAI(chave: string, modelo: string, audio: File, stream: boolean): Promise<Response> {
  const form = new FormData();
  form.append("model", modelo);
  form.append("file", audio, audio.name || "audio");
  if (stream) form.append("stream", "true");
  const base = (Deno.env.get("OPENAI_BASE_URL") ?? "https://api.openai.com/v1").replace(/\/+$/, "");
  return await fetch(`${base}/audio/transcriptions`, {
    method: "POST",
    headers: { Authorization: `Bearer ${chave}` },
    body: form,
    signal: AbortSignal.timeout(PRAZO_OPENAI_MS),
  });
}

// Lê o SSE da OpenAI e devolve NDJSON no formato do contrato: `delta`, `final` ou `erro`.
function respostaStreaming(
  chave: string,
  modelo: string,
  audio: File,
  // deno-lint-ignore no-explicit-any
  banco: any,
): Response {
  const codificador = new TextEncoder();
  const corpo = new ReadableStream<Uint8Array>({
    async start(controle) {
      const enviar = (evento: unknown) => {
        try {
          controle.enqueue(codificador.encode(JSON.stringify(evento) + "\n"));
        } catch {
          // cliente desconectou; nada a fazer
        }
      };
      try {
        const resp = await chamarOpenAI(chave, modelo, audio, true);
        if (!resp.ok || !resp.body) {
          await resp.body?.cancel();
          const e = erroDaOpenAI(null, resp.status);
          enviar({ tipo: "erro", detail: e.detail, codigo: e.codigo });
          return;
        }
        const leitor = resp.body.pipeThrough(new TextDecoderStream()).getReader();
        let resto = "";
        while (true) {
          const { value, done } = await leitor.read();
          if (done) break;
          resto += value;
          const linhas = resto.split("\n");
          resto = linhas.pop() ?? "";
          for (const linha of linhas) {
            const l = linha.trim();
            if (!l.startsWith("data:")) continue;
            let evento: { type?: string; delta?: string; text?: string; usage?: Usage };
            try {
              evento = JSON.parse(l.slice(5).trim());
            } catch {
              continue; // ex.: "[DONE]"
            }
            if (evento.type === "transcript.text.delta") {
              enviar({ tipo: "delta", texto: evento.delta ?? "" });
            } else if (evento.type === "transcript.text.done") {
              const texto = evento.text ?? "";
              if (evento.usage) {
                await registrar(banco, modelo, evento.usage, texto);
              } else {
                console.error(`[consumo] evento final do streaming sem 'usage' (modelo ${modelo}) — consumo não registrado`);
              }
              enviar({ tipo: "final", texto });
            }
          }
        }
      } catch (falha) {
        const e = erroDaOpenAI(falha);
        enviar({ tipo: "erro", detail: e.detail, codigo: e.codigo });
      } finally {
        try {
          controle.close();
        } catch {
          // já fechado
        }
      }
    },
  });
  return new Response(corpo, {
    status: 200,
    headers: { "Content-Type": "application/x-ndjson", ...CABECALHO_CONTRATO },
  });
}

async function transcrever(req: Request): Promise<Response> {
  if (req.method !== "POST") {
    return json({ detail: "Método não permitido — use POST", codigo: "METODO_NAO_PERMITIDO" }, 405);
  }

  // O gateway já recusou quem não tem JWT válido (verify_jwt). Aqui confirma que é um usuário do Auth:
  // a chave anônima também é um JWT válido e não pode gastar chamada paga.
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
  const { data: sessao, error: erroSessao } = await banco.auth.getUser(token);
  if (erroSessao || !sessao?.user) {
    throw new ErroNucleo(401, "NAO_AUTENTICADO", "Sessão inválida ou expirada — faça login de novo");
  }

  let form: FormData;
  try {
    form = await req.formData();
  } catch {
    throw new ErroNucleo(422, "REQUISICAO_INVALIDA", "O corpo precisa ser multipart/form-data com o campo 'audio'");
  }

  const modeloCampo = form.get("modelo");
  const modelo = typeof modeloCampo === "string" && modeloCampo !== "" ? modeloCampo : MODELO_PADRAO;
  const stream = ehVerdadeiro(form.get("stream"));

  // Mesma ordem de validação de main.py: modelo, chave, vazio, tamanho — tudo antes de abrir o stream.
  if (!MODELOS_PERMITIDOS.includes(modelo)) {
    throw new ErroNucleo(
      422,
      "MODELO_INVALIDO",
      `Modelo inválido: '${modelo}'. Valores aceitos: ${MODELOS_PERMITIDOS.join(", ")}`,
    );
  }

  const chave = Deno.env.get("OPENAI_API_KEY");
  if (!chave) {
    throw new ErroNucleo(
      503,
      "SEM_CHAVE",
      "OPENAI_API_KEY não configurada — crie o segredo nas Edge Functions do Supabase",
    );
  }

  const audio = form.get("audio");
  if (!(audio instanceof File)) {
    throw new ErroNucleo(422, "REQUISICAO_INVALIDA", "Campo 'audio' ausente no formulário");
  }
  if (audio.size === 0) {
    throw new ErroNucleo(400, "AUDIO_VAZIO", "Arquivo de áudio vazio");
  }
  if (audio.size > TAMANHO_MAXIMO_AUDIO_BYTES) {
    const tamanhoMb = (audio.size / (1024 * 1024)).toFixed(1).replace(".", ",");
    const limiteMb = TAMANHO_MAXIMO_AUDIO_BYTES / (1024 * 1024);
    throw new ErroNucleo(413, "ARQUIVO_MUITO_GRANDE", `Arquivo de ${tamanhoMb} MB; o limite é ${limiteMb} MB`);
  }

  if (stream) {
    return respostaStreaming(chave, modelo, audio, banco);
  }

  let resp: Response;
  try {
    resp = await chamarOpenAI(chave, modelo, audio, false);
  } catch (falha) {
    throw erroDaOpenAI(falha);
  }
  if (!resp.ok) {
    await resp.body?.cancel();
    throw erroDaOpenAI(null, resp.status);
  }
  let resultado: { text?: string; usage?: Usage };
  try {
    resultado = await resp.json();
  } catch (falha) {
    throw erroDaOpenAI(falha);
  }
  const texto = resultado.text ?? "";
  await registrar(banco, modelo, resultado.usage, texto);
  return json({ transcricao: texto });
}

Deno.serve(async (req: Request) => {
  try {
    return await transcrever(req);
  } catch (e) {
    if (e instanceof ErroNucleo) return respostaDeErro(e);
    console.error(`[transcrever] erro inesperado: ${(e as Error)?.name}: ${(e as Error)?.message}`);
    return json({ detail: "Erro interno do núcleo remoto", codigo: "ERRO_INTERNO" }, 500);
  }
});
