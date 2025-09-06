// backend/server.js

// ─── 1) Chargement des variables d'environnement en dev ───────────────────
if (process.env.NODE_ENV !== 'production') {
  require('dotenv').config();
}

const express    = require('express');
const cors       = require('cors');
const multer     = require('multer');
const path       = require('path');
const fs         = require('fs');
const mongoose   = require('mongoose');
const morgan     = require('morgan');
const helmet     = require('helmet');
const rateLimit  = require('express-rate-limit');
const xssClean   = require('xss-clean');
const hpp        = require('hpp');
const jwt        = require('jsonwebtoken');
const nodemailer = require('nodemailer');

// ─── Import des routeurs ──────────────────────────────────────────────────
const authRouter = require('./routes/authentification');

// ─── Store en mémoire pour le token SumUp ─────────────────────────────────
const sumupTokenStore = require('./sumupTokenStore');

// ─── 2) Endpoints SumUp (prod vs sandbox) ─────────────────────────────────
const isSandbox = process.env.USE_SUMUP_SANDBOX === 'true';

// ─── 4) Express setup ─────────────────────────────────────────────────────
const app  = express();
const PORT = process.env.PORT || 3001;
app.set('trust proxy', 1); // Render/Heroku derrière un proxy

// ─── 5) Sécurité & logs ──────────────────────────────────────────────────
app.use(helmet());
app.use(rateLimit({ windowMs: 15 * 60 * 1000, max: 100 }));
app.use(xssClean());
app.use(hpp());
app.use(morgan('combined'));

// ─── 6) CORS + JSON ───────────────────────────────────────────────────────
app.use(cors({ origin: true, credentials: true }));
app.use(express.json());

// ─── 7) Routes OAuth SumUp + statut connexion ─────────────────────────────
app.use('/auth', authRouter);

// Petit endpoint de diagnostic : indique si un token est présent côté serveur
app.get('/auth/status', (_req, res) => {
  res.json({ connected: sumupTokenStore.isSet() });
});

// ─── 8) Static + uploads ─────────────────────────────────────────────────
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));
app.use(express.static(path.join(__dirname, 'dist')));

// ─── 9) MongoDB ─────────────────────────────────────────────────────────
mongoose.connect(process.env.MONGODB_URI)
  .then(() => console.log('✅ MongoDB connectée !'))
  .catch(err => console.error('❌ Erreur MongoDB :', err));

// ─── 10) Modèle Produit ─────────────────────────────────────────────────
const produitSchema = new mongoose.Schema({
  nom:         { type: String, required: true },
  description: { type: String, required: true },
  prix:        { type: Number, required: true },
  categorie:   { type: String, required: true },
  images:      [String]
}, { timestamps: true });
const Produit = mongoose.model('Produit', produitSchema);

// --- Modèle Order (statut de paiement) ---
const orderSchema = new mongoose.Schema({
  ref:        { type: String, required: true, unique: true }, // checkout_reference
  checkoutId: { type: String },                                // id du checkout SumUp
  amount:     { type: Number, required: true },
  currency:   { type: String, default: 'EUR' },
  status:     { type: String, default: 'PENDING' },            // PENDING | PAID | FAILED | CANCELED
  raw:        { type: Object }                                 // payload SumUp (utile en test)
}, { timestamps: true });
const Order = mongoose.model('Order', orderSchema);

// ─── 10 bis) Route checkout chargée APRÈS les modèles ─────────────────────
const checkoutRouter = require('./routes/checkout');

// ─── 11) Multer & nettoyage ───────────────────────────────────────────────
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
  try { await fs.promises.unlink(fp); }
  catch (err) { console.error('Erreur suppression', fp, err); }
}

// ─── 12) Auth middleware ─────────────────────────────────────────────────
function authMiddleware(req, res, next) {
  const h = req.headers.authorization;
  if (!h) return res.status(401).json({ message: 'Authentification requise' });
  const token = h.split(' ')[1];
  try { req.user = jwt.verify(token, process.env.JWT_SECRET); next(); }
  catch { return res.status(401).json({ message: 'Token invalide' }); }
}

// ─── 13) Login Admin ──────────────────────────────────────────────────────
app.post('/api/login', (req, res) => {
  const { username, password } = req.body;
  if (
    username === process.env.ADMIN_USER &&
    password === process.env.ADMIN_PASS
  ) {
    const token = jwt.sign({ username }, process.env.JWT_SECRET, { expiresIn: '2h' });
    return res.json({ token });
  }
  res.status(401).json({ message: 'Identifiants invalides' });
});

// ─── 14) API Produits & Email ────────────────────────────────────────────
app.post('/api/send-email', async (req, res) => {
  const { name, email, message } = req.body;
  if (!process.env.EMAIL_USER || !process.env.EMAIL_PASS || !process.env.EMAIL_TO) {
    return res.status(500).json({ message: 'Configuration email manquante' });
  }
  const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth:    { user: process.env.EMAIL_USER, pass: process.env.EMAIL_PASS }
  });
  try {
    await transporter.sendMail({
      from:    `"${name}" <${email}>`,
      to:      process.env.EMAIL_TO,
      subject: '📩 Nouveau message',
      html:    `<p>${message}</p>`
    });
    res.json({ success: true });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false });
  }
});

app.get('/api/produits', (_req, res) => Produit.find().then(r => res.json(r)));
app.get('/api/produits/recherche', (req, res) => {
  const q = req.query.q || '';
  Produit.find({ nom: { $regex: q, $options: 'i' } }).then(r => res.json(r));
});
app.get('/api/produits/:id', (req, res) => {
  Produit.findById(req.params.id)
    .then(p => p ? res.json(p) : res.status(404).json({ message: 'Produit introuvable' }));
});

// ─── 15) Route de création de checkout via SumUp ─────────────────────────
app.use('/api/checkout', checkoutRouter);

// ─── 15.1) Ping return_url SumUp (évite 404 sur POST /merci) ─────────────
app.post('/merci', express.urlencoded({ extended: true }), async (req, res) => {
  console.log('SumUp return_url POST ping →', req.body);
  const { id, status } = req.body || {};

  if (id) {
    try {
      await Order.findOneAndUpdate(
        { checkoutId: id },
        { status: status || 'PENDING' },
        { new: true }
      );
    } catch (e) {
      console.error('Erreur maj Order sur /merci:', e.message);
    }
  }

  res.status(204).end();
});

// ─── 16) CRUD Produits protégées ──────────────────────────────────────────
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

// ─── 16 bis) API statut commande ──────────────────────────────────────────
app.get('/api/orders/:ref/status', async (req, res) => {
  try {
    res.set('Cache-Control', 'no-store, no-cache, must-revalidate, proxy-revalidate');
    res.set('Pragma', 'no-cache');
    res.set('Expires', '0');

    const order = await Order.findOne({ ref: req.params.ref }).lean();
    if (!order) return res.status(404).json({ error: 'Order not found' });
    res.json({ status: order.status });
  } catch (e) {
    console.error('Erreur statut commande:', e.message);
    res.status(500).json({ error: 'Server error' });
  }
});

// ─── 17) Fallback SPA ─────────────────────────────────────────────────────
app.get('*', (_req, res) => {
  res.sendFile(path.resolve(__dirname, 'dist', 'index.html'));
});

// ─── 18) Démarrage serveur ────────────────────────────────────────────────
app.listen(PORT, () => {
  console.log(`🚀 Serveur front+API sur port ${PORT} (Sandbox: ${isSandbox})`);
});
