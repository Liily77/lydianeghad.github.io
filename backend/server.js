// backend/server.js

// ─── 1) Dotenv en dev seulement ───────────────────────────────────────────
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

const app  = express();
const PORT = process.env.PORT || 3001;

// ─── 2) Sécurité & rate limiting ──────────────────────────────────────────
app.use(helmet());
app.use(rateLimit({ windowMs: 15 * 60 * 1000, max: 100 }));
app.use(xssClean());
app.use(hpp());
app.use(morgan('combined'));

// ─── 3) CORS global ───────────────────────────────────────────────────────
// Autorise ton front en prod + localhost en dev
app.use(cors({
  origin: true,
  credentials: true
}));

// ─── 4) Servir SPA + uploads avant JSON/API ────────────────────────────────
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));
app.use(express.static(path.resolve(__dirname, '../dist')));
app.use(express.json());

// ─── 5) Connexion MongoDB ──────────────────────────────────────────────────
mongoose.connect(process.env.MONGODB_URI)
  .then(() => console.log('✅ MongoDB connectée !'))
  .catch(err => console.error('❌ Erreur MongoDB :', err));

// ─── 6) Modèle Produit ────────────────────────────────────────────────────
const produitSchema = new mongoose.Schema({
  nom:         { type: String, required: true },
  description: { type: String, required: true },
  prix:        { type: Number, required: true },
  categorie:   { type: String, required: true },
  images:      [String]
}, { timestamps: true });
const Produit = mongoose.model('Produit', produitSchema);

// ─── 7) Multer upload ──────────────────────────────────────────────────────
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

// ─── 8) Auth middleware ────────────────────────────────────────────────────
function authMiddleware(req, res, next) {
  const authHeader = req.headers.authorization;
  if (!authHeader) {
    return res.status(401).json({ message: 'Authentification requise' });
  }
  const token = authHeader.split(' ')[1];
  try {
    req.user = jwt.verify(token, process.env.JWT_SECRET);
    next();
  } catch {
    return res.status(401).json({ message: 'Token invalide' });
  }
}

// ─── 9) Login Admin ───────────────────────────────────────────────────────
app.post('/api/login', (req, res) => {
  const { username, password } = req.body;
  if (username === process.env.ADMIN_USER && password === process.env.ADMIN_PASS) {
    const token = jwt.sign({ username }, process.env.JWT_SECRET, { expiresIn: '2h' });
    return res.json({ token });
  }
  res.status(401).json({ message: 'Identifiants invalides' });
});

// ─── 10) Routes publiques ─────────────────────────────────────────────────
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
      subject: '📩 Nouveau message de contact',
      html:    `<p><strong>Nom :</strong> ${name}</p>
                <p><strong>Email :</strong> ${email}</p>
                <p>${message}</p>`
    });
    res.json({ success: true });
  } catch (err) {
    console.error(err);
    res.status(500).json({ success: false });
  }
});

app.get('/api/produits', async (_req, res) =>
  res.json(await Produit.find())
);
app.get('/api/produits/recherche', async (req, res) => {
  const q = req.query.q || '';
  res.json(await Produit.find({ nom: { $regex: q, $options: 'i' } }));
});
app.get('/api/produits/:id', async (req, res) => {
  const prod = await Produit.findById(req.params.id);
  if (!prod) return res.status(404).json({ message: 'Produit introuvable' });
  res.json(prod);
});

// ─── 11) CRUD protégées (produits) ─────────────────────────────────────────
app.post('/api/produits', authMiddleware, upload.array('images'), async (req, res) => {
  const images = req.files.map(f => `/uploads/${f.filename}`);
  const prod   = new Produit({
    nom:         req.body.nom,
    description: req.body.description,
    prix:        parseFloat(req.body.prix),
    categorie:   req.body.categorie,
    images
  });
  await prod.save();
  res.status(201).json(prod);
});

app.put('/api/produits/:id', authMiddleware, upload.array('images'), async (req, res) => {
  const prod = await Produit.findById(req.params.id);
  if (!prod) return res.status(404).json({ message: 'Produit introuvable' });
  if (req.files.length) {
    for (const imgPath of prod.images) {
      await supprimerFichier(path.join(__dirname, imgPath));
    }
    prod.images = req.files.map(f => `/uploads/${f.filename}`);
  }
  prod.nom         = req.body.nom;
  prod.description = req.body.description;
  prod.prix        = parseFloat(req.body.prix);
  prod.categorie   = req.body.categorie;
  await prod.save();
  res.json(prod);
});

app.delete('/api/produits/:id', authMiddleware, async (req, res) => {
  const prod = await Produit.findByIdAndDelete(req.params.id);
  if (!prod) return res.status(404).json({ message: 'Produit introuvable' });
  for (const imgPath of prod.images) {
    await supprimerFichier(path.join(__dirname, imgPath));
  }
  res.json({ message: 'Produit supprimé' });
});

// ─── 12) Fallback SPA (refresh & front routes) ─────────────────────────────
app.get('*', (_req, res) =>
  res.sendFile(path.resolve(__dirname, '../dist/index.html'))
);

// ─── 13) Lancement du serveur ─────────────────────────────────────────────
app.listen(PORT, () => console.log(`🚀 Serveur sur port ${PORT}`));
