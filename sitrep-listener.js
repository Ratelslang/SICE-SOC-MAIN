#!/usr/bin/env node
/**
 * SICE SOC — WhatsApp SITREP Listener
 * ------------------------------------
 * Polls the local whatsapp-mcp bridge for incoming messages containing
 * "SITREP" (case-insensitive) and replies in-thread with a full SOC MAIN
 * status brief pulled from sice-server.
 *
 * Deploy as a systemd user service alongside whatsapp-mcp.service and
 * sice-server.service (see sitrep-listener.service in this folder).
 *
 * >>> BEFORE RUNNING: fill in the CONFIG block below. <<<
 */

const { Client } = require("@modelcontextprotocol/sdk/client/index.js");
const { StreamableHTTPClientTransport } = require("@modelcontextprotocol/sdk/client/streamableHttp.js");

// ============================================================
// CONFIG — Boss1 must confirm/fill these in
// ============================================================
const CONFIG = {
  // CONFIRMED from claude_desktop_config.json (11-Jul-2026):
  // whatsapp-mcp bridge listens on http://127.0.0.1:8765/mcp (Streamable HTTP)
  WHATSAPP_MCP_URL: process.env.WHATSAPP_MCP_URL || "http://127.0.0.1:8765/mcp",


  // Your own number — listen for SITREP sent to/from yourself.
  // Also works if sent from your phone into a group; add group JIDs here too.
  WATCH_CHATS: [
    "27683605393@s.whatsapp.net", // Philip's own number (notes-to-self)
    // "1234567890-1234567890@g.us", // add SOC ops group JID if needed
  ],

  // Trigger word (case-insensitive substring match)
  TRIGGER: "sitrep",

  // How often to poll for new messages (ms). WhatsApp has no push webhook
  // in this bridge, so this is poll-based.
  POLL_INTERVAL_MS: 15000,

  // sice-server SOC MAIN status endpoint.
  // >>> CONFIRM THIS PATH — I don't have your actual API route names. <<<
  // Expected to return JSON: { threats: [], movements: [], comms: {}, incidents: [] }
  SOC_MAIN_STATUS_URL: process.env.SOC_MAIN_STATUS_URL || "http://localhost:8743/api/soc-main/status",
};

// ============================================================
// STATE — tracks last-seen message timestamp to avoid re-triggering
// ============================================================
let lastCheckedISO = new Date().toISOString();

// ============================================================
// Format the Mode A tactical brief from SOC MAIN status JSON
// ============================================================
function formatBrief(status) {
  const now = new Date();
  const sast = new Date(now.getTime() + 2 * 60 * 60 * 1000); // UTC+2 approx (no DST in SA)
  const dateStr = sast.toISOString().slice(0, 10).split("-").reverse().join("-");
  const timeStr = sast.toISOString().slice(11, 16);

  // NOTE: SOC MAIN's real data model only tracks incidents (from
  // localStorage 'sice_so_incidents', shared with OPS/Intel Hub).
  // Threats/movements/comms have no dedicated source yet — omitted
  // rather than faked. Add sections back once those feeds exist.
  const incidents = (status.incidents && status.incidents.length)
    ? status.incidents.map(i =>
        `- ${i.type || "Incident"} | ${i.severity || "Unconfirmed"} | ${i.status || "—"} | ${i.location || "—"} (Ref: ${i.ref || "—"} | ${i.date || "—"} ${i.time || "—"})`
      ).join("\n")
    : "Negative. No incidents logged for AO in last 24hrs.";

  const staleness = status.updated_at
    ? `Last sync: ${status.updated_at}`
    : "Status: Unconfirmed — no sync received yet from SOC MAIN.";

  return (
`*SICE SOC OPS SECURITY BRIEF*
📍 Sinoville • Montana • Pretoria North
📅 ${dateStr} • ${timeStr} SAST

*SITREP* — auto-pulled on request

*INTEL (LAST 24H)*
${incidents}

${staleness}

☎ SAPS Sinoville 012 543 8831 · CPF Sector 1 071 509 6830 · CPF Sector 2 079 025 5001 · SAPS 10111 · Crime Stop 08600 10111

Delta-6, out.`
  );
}

// ============================================================
// Pull live status from sice-server
// ============================================================
async function getSocMainStatus() {
  try {
    const res = await fetch(CONFIG.SOC_MAIN_STATUS_URL, { signal: AbortSignal.timeout(5000) });
    if (!res.ok) throw new Error(`sice-server returned ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error(`[sitrep-listener] Failed to reach sice-server: ${err.message}`);
    // Degrade gracefully — still reply, but flag the outage per TRUTH OR SILENCE rule
    return {
      threats: [],
      movements: [],
      comms: { status: "UNCONFIRMED — sice-server unreachable" },
      incidents: [],
    };
  }
}

// ============================================================
// Main poll loop
// ============================================================
async function pollLoop(mcpClient) {
  try {
    for (const chatJid of CONFIG.WATCH_CHATS) {
      const result = await mcpClient.callTool({
        name: "list_messages",
        arguments: {
          chat_jid: chatJid,
          query: CONFIG.TRIGGER,
          after: lastCheckedISO,
          limit: 20,
          include_context: false,
        },
      });

      const text = extractText(result);
      const matches = parseMatches(text);

      for (const msg of matches) {
        console.log(`[sitrep-listener] Trigger matched in ${chatJid}: "${msg.body}" @ ${msg.timestamp}`);

        const status = await getSocMainStatus();
        const brief = formatBrief(status);

        await mcpClient.callTool({
          name: "send_reply",
          arguments: {
            chat_jid: chatJid,
            body: brief,
            target_message_id: msg.message_id,
          },
        });

        console.log(`[sitrep-listener] Replied to ${chatJid}`);
      }
    }
    lastCheckedISO = new Date().toISOString();
  } catch (err) {
    console.error(`[sitrep-listener] Poll error: ${err.message}`);
  }
}

// Helper: list_messages returns human-readable text, not structured JSON.
// This is a best-effort parser — adjust regex if your bridge's format differs.
function extractText(result) {
  if (!result || !result.content) return "";
  return result.content.map(c => c.text || "").join("\n");
}

function parseMatches(text) {
  // Expects lines roughly like: [2026-07-11T13:00:00Z] id=ABC123 from=27... : SITREP
  // >>> ADJUST THIS PARSER once you see real list_messages output format. <<<
  const lines = text.split("\n").filter(l => l.toLowerCase().includes(CONFIG.TRIGGER));
  return lines.map(line => {
    const idMatch = line.match(/id=(\S+)/);
    const tsMatch = line.match(/\[([^\]]+)\]/);
    return {
      message_id: idMatch ? idMatch[1] : null,
      timestamp: tsMatch ? tsMatch[1] : null,
      body: line.trim(),
    };
  }).filter(m => m.message_id);
}

// ============================================================
// Bootstrap
// ============================================================
async function main() {
  console.log("[sitrep-listener] Starting — SICE SOC WhatsApp SITREP listener");
  console.log(`[sitrep-listener] Watching: ${CONFIG.WATCH_CHATS.join(", ")}`);
  console.log(`[sitrep-listener] Poll interval: ${CONFIG.POLL_INTERVAL_MS}ms`);

  const transport = new StreamableHTTPClientTransport(new URL(CONFIG.WHATSAPP_MCP_URL));
  const client = new Client({ name: "sitrep-listener", version: "1.0.0" }, { capabilities: {} });
  await client.connect(transport);
  console.log("[sitrep-listener] Connected to whatsapp-mcp bridge");

  setInterval(() => pollLoop(client), CONFIG.POLL_INTERVAL_MS);
  pollLoop(client); // run immediately on start
}

main().catch(err => {
  console.error("[sitrep-listener] Fatal:", err);
  process.exit(1);
});
