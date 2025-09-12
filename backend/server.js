// backend/server.js

// 1) Variables d'env en dev
if (process.env.NODE_ENV !== 'production') {
  require('dotenv').config();
}

const express   = require('express');
const cors      = require('cors');
const multer    = require('multer');
const path      = require('path');
const fs        = require('fs');
const mongoose  = require('mongoose');
const morgan    = require('morgan');
const helmet    = require('helmet');
const rateLimit = require('express-rate-limit');
const xssClean  = require('xss-clean');
const hpp       = require('hpp');
const jwt       = require('jsonwebtoken');

// Mailer (Brevo)
const { buildTransport, sendMail } = require('./mailer');

// 2) Flags / stores
const sumupTokenStore = require('./sumupTokenStore');
const isSandbox = process.env.USE_SUMUP_SANDBOX === 'true';

// 3) Express
const app  = express();
const PORT = process.env.PORT || 3001;
app.set('trust proxy', 1);

// 4) Sécurité & logs
app.use(helmet());
app.use(rateLimit({ windowMs: 15 * 60 * 1000, max: 100 }));
app.use(xssClean());
app.use(hpp());
app.use(morgan('combined'));

// 5) CORS + parsers
app.use(cors({ origin: true, credentials: true }));
app.use(express.json({ limit: '1mb' }));
app.use(express.urlencoded({ extended: true }));

// 6) Static
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));
app.use(express.static(path.join(__dirname, 'dist')));

// 7) MongoDB
mongoose.connect(process.env.MONGODB_URI)
  .then(() => console.log('✅ MongoDB connectée !'))
  .catch(err => console.error('❌ Erreur MongoDB :', err));

// 8) Modèles Mongoose
const produitSchema = new mongoose.Schema({
  nom:         { type: String, required: true },
  description: { type: String, required: true },
  prix:        { type: Number, required: true },
  categorie:   { type: String, required: true },
  images:      [String]
}, { timestamps: true });
const Produit = mongoose.model('Produit', produitSchema);

// Order (si présent dans ./models/Order.js)
require('./models/Order'); // enregistre le modèle
const Order = mongoose.models.Order || mongoose.model('Order');

// 9) Routes importées
const authRouter     = require('./routes/authentification');
const checkoutRouter = require('./routes/checkout');
const webhookRouter  = require('./routes/webhooksumup');

// 10) Auth SumUp & statut
app.use('/auth', authRouter);
app.get('/auth/status', (_req, res) => {
  res.json({ connected: sumupTokenStore.isSet() });
});

// 11) Uploads (Multer)
const uploadDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadDir)) fs.mkdirSync(uploadDir);
const storage = multer.diskStorage({
  destination: (_req, _file, cb) => cb(null, uploadDir),
  filename:    (_req, file, cb) => cb(null, `${Date.now()}-${file.originalname}`)
});
const upload = multer({
  storage,
  limits: { fileSize: 5 * 1024 * 1024 },
  fileFilter(_req, file, cb) {
    if (/image\/(jpeg|png|gif)/.test(file.mimetype)) cb(null, true);
    else cb(new Error('Seules JPEG, PNG et GIF sont acceptées'));
  }
});
async function supprimerFichier(fp) {
  try { await fs.promises.unlink(fp); } catch (err) { console.error('Erreur suppression', fp, err); }
}

// 12) Middleware d’auth simple JWT (admin)
function authMiddleware(req, res, next) {
  const h = req.headers.authorization;
  if (!h) return res.status(401).json({ message: 'Authentification requise' });
  const token = h.split(' ')[1];
  try { req.user = jwt.verify(token, process.env.JWT_SECRET); next(); }
  catch { return res.status(401).json({ message: 'Token invalide' }); }
}

// 13) Login Admin
app.post('/api/login', (req, res) => {
  const { username, password } = req.body;
  if (username === process.env.ADMIN_USER && password === process.env.ADMIN_PASS) {
    const token = jwt.sign({ username }, process.env.JWT_SECRET, { expiresIn: '2h' });
    return res.json({ token });
  }
  res.status(401).json({ message: 'Identifiants invalides' });
});

// 14) Contact email (via Brevo)
app.post('/api/send-email', async (req, res) => {
  try {
    const { nom, name, email, message } = req.body || {};
    const senderName = (nom || name || 'Client').toString().trim();
    const replyEmail = (email || '').toString().trim();
    const body       = (message || '').toString();

    const MAIL_FROM = (process.env.MAIL_FROM || '').trim();
    const EMAIL_TO  = (process.env.EMAIL_TO  || '').trim();

    if (!MAIL_FROM || !EMAIL_TO) {
      return res.status(500).json({ success: false, message: 'Config email manquante (MAIL_FROM / EMAIL_TO)' });
    }
    if (!replyEmail || !body) {
      return res.status(400).json({ success: false, message: 'Email et message sont requis' });
    }

    const html = `
      <p><b>Nom :</b> ${senderName}</p>
      <p><b>Email :</b> ${replyEmail}</p>
      <p><b>Message :</b><br/>${body.replace(/\n/g, '<br/>')}</p>
    `;

    const info = await sendMail({
      from: MAIL_FROM,
      to: EMAIL_TO,
      replyTo: `"${senderName}" <${replyEmail}>`,
      subject: `📩 Nouveau message Arc En Ciel – ${senderName}`,
      html,
    });

    console.log('EMAIL SENT:', info && (info.messageId || info.response));
    res.json({ success: true, message: 'Message envoyé' });
  } catch (err) {
    console.error('EMAIL ERROR:', err);
    res.status(500).json({ success: false, message: 'Envoi impossible' });
  }
});

// 15) Produits (public)
app.get('/api/produits', (_req, res) => Produit.find().then(r => res.json(r)));
app.get('/api/produits/recherche', (req, res) => {
  const q = req.query.q || '';
  Produit.find({ nom: { $regex: q, $options: 'i' } }).then(r => res.json(r));
});
app.get('/api/produits/:id', (req, res) => {
  Produit.findById(req.params.id)
    .then(p => p ? res.json(p) : res.status(404).json({ message: 'Produit introuvable' }));
});

// 16) Produits (admin)
app.post('/api/produits', authMiddleware, upload.array('images'), async (req, res) => {
  const images = (req.files || []).map(f => `/uploads/${f.filename}`);
  const p = new Produit({ ...req.body, prix: parseFloat(req.body.prix), images });
  await p.save();
  res.status(201).json(p);
});
app.put('/api/produits/:id', authMiddleware, upload.array('images'), async (req, res) => {
  const prod = await Produit.findById(req.params.id);
  if (!prod) return res.status(404).json({ message: 'Produit introuvable' });
  if (req.files && req.files.length) {
    for (const img of prod.images) await supprimerFichier(path.join(__dirname, img));
    prod.images = req.files.map(f => `/uploads/${f.filename}`);
  }
  Object.assign(prod, {
    nom:         req.body.nom,
    description: req.body.description,
    prix:        parseFloat(req.body.prix),
    categorie:   req.body.categorie
  });
  await prod.save();
  res.json(prod);
});
app.delete('/api/produits/:id', authMiddleware, async (req, res) => {
  const prod = await Produit.findByIdAndDelete(req.params.id);
  if (!prod) return res.status(404).json({ message: 'Produit introuvable' });
  prod.images.forEach(img => supprimerFichier(path.join(__dirname, img)));
  res.json({ message: 'Produit supprimé' });
});

// 17) API Checkout + Webhook SumUp
app.use('/api/checkout', checkoutRouter); // crée le checkout (PENDING)
app.use('/webhooks', webhookRouter);      // webhook (si utilisé)

// 18) Endpoints de statut commande (utilisés par Merci.vue)
app.get('/api/orders/:ref/status', async (req, res) => {
  try {
    res.set('Cache-Control', 'no-store, no-cache, must-revalidate, proxy-revalidate');
    res.set('Pragma', 'no-cache');
    res.set('Expires', '0');

    const order = await Order.findOne({ ref: req.params.ref }).lean();
    if (!order) return res.status(404).json({ error: 'Order not found' });
    res.json({ status: order.status, amounts: order.amounts || null });
  } catch (e) {
    console.error('Erreur statut commande:', e.message);
    res.status(500).json({ error: 'Server error' });
  }
});

// (Optionnel) si SumUp POST sur /merci côté back
app.post('/merci', (req, res) => {
  console.log('SumUp return_url POST ping →', req.body);
  res.status(204).end();
});

// 19) Fallback SPA (toutes routes non-API → index.html)
app.get(/^(?!\/api|\/uploads|\/auth|\/webhooks).*/, (_req, res) => {
  res.sendFile(path.resolve(__dirname, 'dist', 'index.html'));
});

// --- DIAGNOSTIC SMTP (temporaire) ---
app.get('/api/_mail-diagnose', async (_req, res) => {
  try {
    const MAIL_FROM = (process.env.MAIL_FROM || '').trim();
    const EMAIL_TO  = (process.env.EMAIL_TO  || '').trim();
    const transport = buildTransport();

    await transport.verify(); // teste connexion + auth
    res.json({
      ok: true,
      provider: (process.env.MAIL_PROVIDER || 'brevo'),
      host: process.env.BREVO_SMTP_HOST || 'smtp-relay.brevo.com',
      port: Number(process.env.BREVO_SMTP_PORT || 587),
      user: process.env.BREVO_SMTP_USER || '',
      to: EMAIL_TO,
      from: MAIL_FROM,
      note: 'Connexion/auth SMTP OK',
    });
  } catch (e) {
    res.status(500).json({
      ok: false,
      code: e.code,
      responseCode: e.responseCode,
      msg: e.message,
      hint: 'Vérifie BREVO_SMTP_USER / BREVO_SMTP_KEY / host / port et supprime les anciennes variables Gmail.',
    });
  }
});

// 20) Start
app.listen(PORT, () => {
  console.log(`🚀 Serveur front+API sur port ${PORT} (Sandbox: ${isSandbox})`);
});
