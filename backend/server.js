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

// ─── MIDDLEWARES DE SÉCURITÉ ───────────────────────────────────────────────────
app.use(helmet());
app.use(rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  message: "Trop de requêtes venant de cette IP, réessayez plus tard."
}));
app.use(xssClean());
app.use(hpp());
app.use(morgan('combined'));

// CORS whitelist
const whitelist = [process.env.FRONTEND_URL || 'http://localhost:5173'];
app.use(cors({
  origin(origin, callback) {
    if (!origin) return callback(null, true);
    return whitelist.includes(origin)
      ? callback(null, true)
      : callback(new Error('Not allowed by CORS'));
  }
}));

app.use(express.json());
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));
app.use(express.static(path.resolve(__dirname, '../dist')));

// ─── CONNEXION MONGODB ────────────────────────────────────────────────────────
mongoose.connect(process.env.MONGODB_URI, {
  useNewUrlParser: true, useUnifiedTopology: true
})
.then(() => console.log('✅ MongoDB connectée !'))
.catch(err => console.error('❌ Erreur MongoDB :', err));

// ─── SCHÉMA & MODELE PRODUIT ─────────────────────────────────────────────────
const produitSchema = new mongoose.Schema({
  nom: String,
  description: String,
  prix: Number,
  categorie: String,
  images: [String]
});
const Produit = mongoose.model('Produit', produitSchema);

// ─── MULTER (upload images) ──────────────────────────────────────────────────
const uploadDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadDir)) fs.mkdirSync(uploadDir);

const storage = multer.diskStorage({
  destination: (_, __, cb) => cb(null, uploadDir),
  filename: (_, file, cb) => cb(null, Date.now() + '-' + file.originalname)
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
  try { await fs.promises.unlink(filePath); }
  catch (e) { console.error('Erreur suppression', filePath, e); }
}

// ─── AUTHENTIFICATION JWT ────────────────────────────────────────────────────
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

// Login admin → renvoie JWT
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

// ─── ROUTES PUBLIQUES ────────────────────────────────────────────────────────
app.post('/send-email', async (req, res) => {
  const { name, email, message } = req.body;
  if (!process.env.EMAIL_USER || !process.env.EMAIL_PASS) {
    return res.status(500).json({ message: 'Email non config.' });
  }
  const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: { user: process.env.EMAIL_USER, pass: process.env.EMAIL_PASS }
  });
  try {
    await transporter.sendMail({
      from: `"${name}" <${email}>`,
      to: process.env.EMAIL_TO,
      subject: '📩 Nouveau message',
      html: `<p><strong>Nom:</strong>${name}</p>
             <p><strong>Email:</strong>${email}</p>
             <p>${message}</p>`
    });
    res.json({ success: true });
  } catch (e) {
    console.error(e);
    res.status(500).json({ success: false });
  }
});

app.get('/produits/recherche', async (req, res) => {
  const q = req.query.q || '';
  const produits = await Produit.find({ nom: { $regex: q, $options: 'i' } });
  res.json(produits);
});

app.get('/produits', async (_, res) => {
  res.json(await Produit.find());
});

app.get('/produits/:id', async (req, res) => {
  const p = await Produit.findById(req.params.id);
  if (!p) return res.status(404).json({ message: 'Introuvable' });
  res.json(p);
});

// ─── ROUTES PROTÉGÉES ───────────────────────────────────────────────────────
app.post('/produits', authMiddleware, upload.array('images'), async (req, res) => {
  const images = req.files.map(f => `/uploads/${f.filename}`);
  const prod = new Produit({ ...req.body, prix: parseFloat(req.body.prix), images });
  await prod.save();
  res.status(201).json(prod);
});

app.put('/produits/:id', authMiddleware, upload.array('images'), async (req, res) => {
  const prod = await Produit.findById(req.params.id);
  if (!prod) return res.status(404).json({ message: 'Introuvable' });
  if (req.files.length) {
    for (let img of prod.images) await supprimerFichier(path.join(__dirname, img));
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

app.delete('/produits/:id', authMiddleware, async (req, res) => {
  const prod = await Produit.findByIdAndDelete(req.params.id);
  if (!prod) return res.status(404).json({ message: 'Introuvable' });
  for (let img of prod.images) await supprimerFichier(path.join(__dirname, img));
  res.json({ message: 'Supprimé' });
});

// Catch‑all pour SPA
app.get('*', (_, res) => {
  res.sendFile(path.resolve(__dirname, '../dist/index.html'));
});

app.listen(PORT, () => console.log(`🚀 Serveur sur port ${PORT}`));
