import express from 'express';
import bodyParser from 'body-parser';
import fs from 'fs';
import crypto from 'crypto';
import swaggerUi from 'swagger-ui-express';
import YAML from 'yamljs';
import cors from 'cors';

const app = express();
app.use(cors());
app.use(bodyParser.json());

// Load OpenAPI spec (served at /openapi.yaml and used by swagger ui)
const openapi = YAML.load('./openapi.yaml');

// Helper: createEcdsaSignature(payloadString) -> base64 signature
function signPayload(payloadString) {
  const privKeyPem = process.env.SIGNER_PRIVATE_KEY_PEM;
  if (!privKeyPem) {
    // fallback: ephemeral demo key (NOT secure) for demo seals when no secret set
    const { privateKey } = crypto.generateKeyPairSync('ec', { namedCurve: 'secp256k1' });
    const sign = crypto.createSign('SHA256');
    sign.update(payloadString);
    sign.end();
    return {
      signature: sign.sign(privateKey, 'base64'),
      pubkey: privateKey.export({ type: 'spki', format: 'pem' }) // not ideal, but demo only
    };
  }
  const sign = crypto.createSign('SHA256');
  sign.update(payloadString);
  sign.end();
  const signature = sign.sign(privKeyPem, 'base64');
  const pubkey = process.env.SIGNER_PUBKEY || null;
  return { signature, pubkey };
}

// Root: metadata
app.get('/', (req, res) => {
  res.json({
    service: "Time Authority",
    endpoints: {
      timestamp: "/timestamp (POST) - issue seal (demo or paid)",
      demo: "/timestamp/demo (POST) - free demo seal",
      openapi: "/openapi.yaml",
      docs: "/docs"
    },
    note: "See /docs for interactive API docs. Add SIGNER_PRIVATE_KEY_PEM & SIGNER_PUBKEY as Fly secrets for real signatures."
  });
});

// Serve openapi.yaml
app.get('/openapi.yaml', (req, res) => {
  res.type('yaml').send(fs.readFileSync('./openapi.yaml', 'utf8'));
});

// Swagger UI at /docs
app.use('/docs', swaggerUi.serve, swaggerUi.setup(openapi));

// Demo seal route (no payment required) - quick test so devs don't need to pay
app.post('/timestamp/demo', (req, res) => {
  const dataHash = req.body.data_hash || req.body.hash || "sha256:demo";
  const issuedAt = new Date().toISOString();
  const payload = JSON.stringify({ data_hash: dataHash, issued_at: issuedAt });
  const { signature, pubkey } = signPayload(payload);
  const seal = {
    seal_id: 'demo_' + crypto.randomBytes(6).toString('hex'),
    issued_at: issuedAt,
    payload: { data_hash: dataHash },
    signer_pubkey: pubkey || process.env.SIGNER_PUBKEY || "demo_pubkey",
    signature
  };
  // optional: store to file/db for audit (demo app - append to a log)
  try {
    fs.appendFileSync('./issued_seals.log', JSON.stringify(seal) + '\n');
  } catch (e) {}
  res.json(seal);
});

// Paid route placeholder: verify payment and issue seal
// For now this is same as demo but you should implement payment verification (Coinbase/x402) before issuing
app.post('/timestamp', async (req, res) => {
  const { data_hash } = req.body || {};
  if (!data_hash) return res.status(400).json({ error: "missing data_hash" });

  // TODO: wire actual payment verification here (webhook / invoice settlement)
  // For now: respond like demo but include placeholder payment_tx
  const issuedAt = new Date().toISOString();
  const payload = JSON.stringify({ data_hash, issued_at: issuedAt });
  const { signature, pubkey } = signPayload(payload);
  const seal = {
    seal_id: 'seal_' + crypto.randomBytes(6).toString('hex'),
    issued_at: issuedAt,
    payload: { data_hash },
    signer_pubkey: pubkey || process.env.SIGNER_PUBKEY || "demo_pubkey",
    signature,
    payment_tx: null // fill once you verify settlement
  };
  try {
    fs.appendFileSync('./issued_seals.log', JSON.stringify(seal) + '\n');
  } catch (e) {}
  res.json(seal);
  
// use env PORT if present (Fly sets it), otherwise default to 8000
const port = process.env.PORT || 8000;
app.listen(port, () => {
console.log(`time-authority running on :${port}`);
});

