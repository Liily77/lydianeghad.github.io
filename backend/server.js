require('dotenv').config();
const express = require('express');
const cors = require('cors');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const mongoose = require('mongoose');
const nodemailer = require('nodemailer');
const morgan = require('morgan');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const xssClean = require('xss-clean');
const hpp = require('hpp');
const jwt = require('jsonwebtoken');

const app = express();
const PORT = process.env.PORT || 3001;

// ─── confiance derrière un proxy (pour express-rate-limit) ───────────────
app.set('trust proxy', 1);

// ─── MIDDLEWARES SÉCURITÉ ─────────────────────────────────────────────────
app.use(helmet());
app.use(
  rateLimit({
    windowMs: 15 * 60 * 1000,
    max: 100,
    message: "Trop de requêtes venant de cette IP, réessayez plus tard."
  })
);
app.use(xssClean());
app.use(hpp());
app.use(morgan('combined'));

// ─── CORS ─────────────────────────────────────────────────────────────────
// on récupère l’URL de ton front et de ton back (prod)
const FRONT = process.env.FRONTEND_URL;                       // ex: https://arc-en-ciel-gl75.onrender.com
const BACK  = process.env.BACKEND_URL || `https://${process.env.RENDER_SERVICE_ID}.onrender.com`;

const whitelist = [
  FRONT,
  BACK,
  'http://localhost:4173',  // preview local
  'http://localhost:5173'   // dev Vite
];

app.use(
  cors({
    origin(origin, callback) {
      if (!origin) return callback(null, true);
      return whitelist.includes(origin)
        ? callback(null, true)
        : callback(new Error(`Origin ${origin} non autorisée par CORS`));
    },
    credentials: true
  })
);

// ─── PARSING & STATIC ─────────────────────────────────────────────────────
app.use(express.json());
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));
app.use(express.static(path.resolve(__dirname, '../dist')));

// ─── MONGO ─────────────────────────────────────────────────────────────────
mongoose
  .connect(process.env.MONGODB_URI)
  .then(() => console.log('✅ MongoDB connectée !'))
  .catch((err) => console.error('❌ Erreur MongoDB :', err));

// ─── SCHÉMA PRODUIT ────────────────────────────────────────────────────────
const produitSchema = new mongoose.Schema({
  nom: String,
  description: String,
  prix: Number,
  categorie: String,
  images: [String]
});
const Produit = mongoose.model('Produit', produitSchema);

// ─── MULTER (upload) ───────────────────────────────────────────────────────
const uploadDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadDir)) fs.mkdirSync(uploadDir);

const storage = multer.diskStorage({
  destination: (_, __, cb) => cb(null, uploadDir),
  filename:    (_, file, cb) => cb(null, Date.now() + '-' + file.originalname)
});
const upload = multer({
  storage,
  limits: { fileSize: 5 * 1024 * 1024 },
  fileFilter(req, file, cb) {
    if (/image\/(jpeg|png|gif)/.test(file.mimetype)) cb(null, true);
    else cb(new Error('Seules JPEG/PNG/GIF acceptées'));
  }
});

async function supprimerFichier(filePath) {
  try {
    await fs.promises.unlink(filePath);
  } catch (e) {
    console.error('Erreur suppression', filePath, e);
  }
}

// ─── AUTH (JWT) ───────────────────────────────────────────────────────────
function authMiddleware(req, res, next) {
  const header = req.headers.authorization;
  if (!header) return res.status(401).json({ message: 'Auth manquante' });
  const token = header.split(' ')[1];
  try {
    req.user = jwt.verify(token, process.env.JWT_SECRET);
    next();
  } catch {
    res.status(401).json({ message: 'Token invalide' });
  }
}

// ─── LOGIN ADMIN ──────────────────────────────────────────────────────────
app.post('/login', (req, res) => {
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

// ─── ROUTES PUBLIQUES ─────────────────────────────────────────────────────
app.post('/send-email', async (req, res) => { /* … implémentation … */ });
app.get('/produits/recherche', async (req, res) => { /* … implémentation … */ });
app.get('/produits', async (_, res) => res.json(await Produit.find()));
app.get('/produits/:id', async (req, res) => { /* … implémentation … */ });

// ─── ROUTES PROTÉGÉES ─────────────────────────────────────────────────────
app.post(
  '/produits',
  authMiddleware,
  upload.array('images'),
  async (req, res) => { /* … implémentation … */ }
);
app.put(
  '/produits/:id',
  authMiddleware,
  upload.array('images'),
  async (req, res) => { /* … implémentation … */ }
);
app.delete('/produits/:id', authMiddleware, async (req, res) => { /* … */ });

// ─── SPA FALLBACK ──────────────────────────────────────────────────────────
app.get('*', (_, res) => {
  res.sendFile(path.resolve(__dirname, '../dist/index.html'));
});

app.listen(PORT, () => console.log(`🚀 Serveur sur port ${PORT}`));
