// backend/server.js

// 1) Variables d'env en dev
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
app.use(express.json({ limit: '1mb' }));              // IMPORTANT: avant les routes
app.use(express.urlencoded({ extended: true }));       // pour /merci (POST)

// 6) Static
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));
app.use(express.static(path.join(__dirname, 'dist')));

// 7) MongoDB
mongoose.connect(process.env.MONGODB_URI)
  .then(() => console.log('✅ MongoDB connectée !'))
  .catch(err => console.error('❌ Erreur MongoDB :', err));

// 8) Modèles Mongoose
//   - Produit (inline, comme avant)
const produitSchema = new mongoose.Schema({
  nom:         { type: String, required: true },
  description: { type: String, required: true },
  prix:        { type: Number, required: true },
  categorie:   { type: String, required: true },
  images:      [String]
}, { timestamps: true });
const Produit = mongoose.model('Produit', produitSchema);

//   - Order (depuis models/Order.js aligné avec checkout)
require('./models/order'); // enregistre le modèle
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

// 14) Contact email
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
app.use('/api/checkout', checkoutRouter);    // crée le checkout (PENDING)
app.use('/webhooks', webhookRouter);     // marque PAID via webhook

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

// (Optionnel) Si SumUp POST sur /merci côté back, on loggue juste
app.post('/merci', (req, res) => {
  console.log('SumUp return_url POST ping →', req.body);
  res.status(204).end();
});
// Ne PAS rediriger en GET ici : la SPA (Vue) gère /merci.

// 19) Fallback SPA (toutes routes non-API → index.html)
app.get(/^(?!\/api|\/uploads|\/auth|\/webhooks).*/, (_req, res) => {
  res.sendFile(path.resolve(__dirname, 'dist', 'index.html'));
});

// 20) Start
app.listen(PORT, () => {
  console.log(`🚀 Serveur front+API sur port ${PORT} (Sandbox: ${isSandbox})`);
});
