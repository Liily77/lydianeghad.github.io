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
const axios      = require('axios');

// ─── 2) Sandbox vs Production pour SumUp ─────────────────────────────────
const isSandbox     = process.env.USE_SUMUP_SANDBOX === 'true';
const AUTHORIZE_URL = isSandbox
  ? 'https://sandbox.sumup.com/authorize'
  : 'https://api.sumup.com/authorize';
const TOKEN_URL     = isSandbox
  ? 'https://sandbox.sumup.com/token'
  : 'https://api.sumup.com/token';
// Le même endpoint checkout pour sandbox et prod
const CHECKOUT_URL  = isSandbox
  ? 'https://sandbox.sumup.com/v0.1/checkouts'
  : 'https://api.sumup.com/v0.1/checkouts';

// ─── 3) Credentials OAuth & tokens ────────────────────────────────────────
const CLIENT_ID     = isSandbox
  ? process.env.SUMUP_SANDBOX_CLIENT_ID
  : process.env.SUMUP_CLIENT_ID;
const CLIENT_SECRET = isSandbox
  ? process.env.SUMUP_SANDBOX_CLIENT_SECRET
  : process.env.SUMUP_CLIENT_SECRET;
const REDIRECT_URI  = process.env.REDIRECT_URI;
const ACCESS_TOKEN_SANDBOX = process.env.SUMUP_SANDBOX_ACCESS_TOKEN;
const ACCESS_TOKEN_PROD    = process.env.SUMUP_PROD_ACCESS_TOKEN;

// ─── 4) Express setup ─────────────────────────────────────────────────────
const app  = express();
const PORT = process.env.PORT || 3001;

// ─── 5) Sécurité & logs ──────────────────────────────────────────────────
app.use(helmet());
app.use(rateLimit({ windowMs: 15 * 60 * 1000, max: 100 }));
app.use(xssClean());
app.use(hpp());
app.use(morgan('combined'));

// ─── 6) CORS + JSON ───────────────────────────────────────────────────────
app.use(cors({ origin: true, credentials: true }));
app.use(express.json());

// ─── 7) Static + uploads ─────────────────────────────────────────────────
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));
app.use(express.static(path.join(__dirname, 'dist')));

// ─── 8) MongoDB ─────────────────────────────────────────────────────────
mongoose.connect(process.env.MONGODB_URI)
  .then(() => console.log('✅ MongoDB connectée !'))
  .catch(err => console.error('❌ Erreur MongoDB :', err));

// ─── 9) Modèle Produit ───────────────────────────────────────────────────
const produitSchema = new mongoose.Schema({
  nom:         { type: String, required: true },
  description: { type: String, required: true },
  prix:        { type: Number, required: true },
  categorie:   { type: String, required: true },
  images:      [String]
}, { timestamps: true });
const Produit = mongoose.model('Produit', produitSchema);

// ─── 10) Multer & nettoyage ───────────────────────────────────────────────
const uploadDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadDir)) fs.mkdirSync(uploadDir);
const storage = multer.diskStorage({
  destination: (_req, _file, cb) => cb(null, uploadDir),
  filename:    (_req, file, cb) => cb(null, `${Date.now()}-${file.originalname}`)
});
const upload = multer({
  storage,
  limits: { fileSize: 5 * 1024 * 1024 },
  fileFilter(req, file, cb) {
    if (/image\/(jpeg|png|gif)/.test(file.mimetype)) cb(null, true);
    else cb(new Error('Seules JPEG, PNG et GIF sont acceptées'));
  }
});
async function supprimerFichier(fp) {
  try { await fs.promises.unlink(fp); }
  catch (err) { console.error('Erreur suppression', fp, err); }
}

// ─── 11) Auth middleware ─────────────────────────────────────────────────
function authMiddleware(req, res, next) {
  const h = req.headers.authorization;
  if (!h) return res.status(401).json({ message: 'Authentification requise' });
  const token = h.split(' ')[1];
  try { req.user = jwt.verify(token, process.env.JWT_SECRET); next(); }
  catch { return res.status(401).json({ message: 'Token invalide' }); }
}

// ─── 12) Login Admin ──────────────────────────────────────────────────────
app.post('/api/login', (req, res) => {
  const { username, password } = req.body;
  if (username === process.env.ADMIN_USER && password === process.env.ADMIN_PASS) {
    const token = jwt.sign({ username }, process.env.JWT_SECRET, { expiresIn: '2h' });
    return res.json({ token });
  }
  res.status(401).json({ message: 'Identifiants invalides' });
});

// ─── 13) API Produits & Email ────────────────────────────────────────────
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
      from: `"${name}" <${email}>`,
      to:   process.env.EMAIL_TO,
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

// ─── 14) OAuth SumUp ──────────────────────────────────────────────────────
app.get('/auth/connect', (_req, res) => {
  // on ne passe plus le scope
  const params = new URLSearchParams({
    response_type: 'code',
    client_id:     CLIENT_ID,
    redirect_uri:  REDIRECT_URI
  });
  const fullUrl = `${AUTHORIZE_URL}?${params.toString()}`;
  console.log('→ SumUp OAuth URL:', fullUrl);
  res.redirect(fullUrl);
});

// ─── 15) Callback OAuth → échange code→token ──────────────────────────────
app.get('/auth/callback', async (req, res) => {
  try {
    const body = new URLSearchParams({
      grant_type:    'authorization_code',
      client_id:     CLIENT_ID,
      client_secret: CLIENT_SECRET,
      code:          req.query.code,
      redirect_uri:  REDIRECT_URI
    }).toString();

    const { data } = await axios.post(TOKEN_URL, body, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    });

    console.log('→ Access token:', data.access_token);
    // TODO: stocker le token quelque part
    res.redirect('/admin');
  } catch (err) {
    console.error('Échec échange code→token', err.response?.data || err);
    res.status(500).send('Échec connexion SumUp');
  }
});

// ─── 16) Création de checkout SumUp ───────────────────────────────────────
app.post('/api/checkout', async (req, res) => {
  try {
    const total = req.body.items.reduce((sum, i) => sum + i.quantity * i.unit_price, 0);
    const accessToken = isSandbox ? ACCESS_TOKEN_SANDBOX : ACCESS_TOKEN_PROD;
    const response = await axios.post(
      CHECKOUT_URL,
      {
        checkout_reference: `order_${Date.now()}`,
        amount:             total,
        currency:           'EUR',
        shop_name:          'Arc En Ciel',
        description:        'Commande Arc En Ciel'
      },
      {
        headers: {
          Authorization: `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        }
      }
    );
    res.json({ checkoutUrl: response.data.checkout_url });
  } catch (err) {
    console.error('Échec création checkout', err.response?.data || err);
    res.status(500).json({ error: 'Impossible de créer le checkout' });
  }
});

// ─── 17) CRUD Produits protégées ──────────────────────────────────────────
app.post('/api/produits', authMiddleware, upload.array('images'), async (req, res) => {
  const images = req.files.map(f => `/uploads/${f.filename}`);
  const p = new Produit({ ...req.body, prix: parseFloat(req.body.prix), images });
  await p.save();
  res.status(201).json(p);
});
app.put('/api/produits/:id', authMiddleware, upload.array('images'), async (req, res) => {
  const prod = await Produit.findById(req.params.id);
  if (!prod) return res.status(404).json({ message: 'Produit introuvable' });
  if (req.files.length) {
    for (const img of prod.images) await supprimerFichier(path.join(__dirname, img));
    prod.images = req.files.map(f => `/uploads/${f.filename}`);
  }
  Object.assign(prod, {
    nom: req.body.nom,
    description: req.body.description,
    prix: parseFloat(req.body.prix),
    categorie: req.body.categorie
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

// ─── 18) Fallback SPA ─────────────────────────────────────────────────────
app.get('*', (_req, res) => {
  res.sendFile(path.resolve(__dirname, 'dist', 'index.html'));
});

// ─── 19) Démarrage serveur ────────────────────────────────────────────────
app.listen(PORT, () => {
  console.log(`🚀 Serveur front+API sur port ${PORT} (Sandbox: ${isSandbox})`);
});
