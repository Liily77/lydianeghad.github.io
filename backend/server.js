// --- IMPORTATIONS ---
require('dotenv').config();
const express = require('express');
const cors = require('cors');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const mongoose = require('mongoose');
const nodemailer = require('nodemailer');

const app = express();
const PORT = process.env.PORT || 3000;

// --- MIDDLEWARES ---
app.use(cors());
app.use(express.json());
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

// 🔵 SERIVRE LES FICHIERS STATIQUES DU FRONT
app.use(express.static(path.resolve(__dirname, '../dist')));

// --- CONNEXION MONGODB ---
mongoose.connect(process.env.MONGODB_URI)
  .then(() => console.log('✅ Connexion MongoDB réussie !'))
  .catch(err => console.error('❌ Erreur de connexion MongoDB :', err));

// --- SCHÉMA PRODUIT ---
const produitSchema = new mongoose.Schema({
  nom: String,
  description: String,
  prix: Number,
  categorie: String,
  images: [String]
});
const Produit = mongoose.model('Produit', produitSchema);

// --- GESTION UPLOAD (MULTER) ---
const uploadDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadDir)) fs.mkdirSync(uploadDir);

const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, uploadDir),
  filename: (req, file, cb) => cb(null, Date.now() + '-' + file.originalname)
});
const upload = multer({ storage });

/* ---------------- ROUTES BACKEND ---------------- */

// ✅ ROUTE CONTACT : ENVOI DE MAIL
app.post('/send-email', async (req, res) => {
  const { name, email, message } = req.body;
  const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: { user: process.env.EMAIL_USER, pass: process.env.EMAIL_PASS }
  });
  try {
    await transporter.sendMail({
      from: `"${name}" <${email}>`,
      to: 'arcenciel.nadege@gmail.com',
      subject: '📩 Nouveau message depuis le site Arc En Ciel',
      html: `
        <h3>Vous avez reçu un message :</h3>
        <p><strong>Nom :</strong> ${name}</p>
        <p><strong>Email :</strong> ${email}</p>
        <p><strong>Message :</strong><br>${message}</p>
      `
    });
    res.status(200).json({ success: true, message: 'Message envoyé avec succès' });
  } catch (error) {
    console.error('❌ Erreur envoi email :', error);
    res.status(500).json({ success: false, message: 'Erreur lors de l’envoi du message' });
  }
});

// ✅ RECHERCHE PRODUIT
app.get('/produits/recherche', async (req, res) => {
  try {
    const produits = await Produit.find({ nom: { $regex: req.query.q || '', $options: 'i' } });
    res.json(produits);
  } catch (err) {
    console.error('❌ Erreur recherche produit :', err);
    res.status(500).json({ message: 'Erreur recherche', erreur: err });
  }
});

// ✅ GET TOUS LES PRODUITS
app.get('/produits', async (req, res) => {
  try {
    res.json(await Produit.find());
  } catch (err) {
    console.error('❌ Erreur chargement produits :', err);
    res.status(500).json({ message: 'Erreur chargement produits', erreur: err });
  }
});

// ✅ GET PRODUIT PAR ID
app.get('/produits/:id', async (req, res) => {
  try {
    const produit = await Produit.findById(req.params.id);
    if (!produit) return res.status(404).json({ message: 'Produit introuvable' });
    res.json(produit);
  } catch (err) {
    console.error('❌ Erreur serveur :', err);
    res.status(500).json({ message: 'Erreur serveur', erreur: err });
  }
});

// ✅ POST : AJOUT PRODUIT
app.post('/produits', upload.array('images'), async (req, res) => {
  try {
    const images = req.files.map(f => `/uploads/${f.filename}`);
    const produit = new Produit({ ...req.body, prix: parseFloat(req.body.prix), images });
    res.status(201).json({ message: '✅ Produit ajouté', produit: await produit.save() });
  } catch (err) {
    console.error('❌ Erreur ajout produit :', err);
    res.status(500).json({ message: 'Erreur ajout produit', erreur: err });
  }
});

// ✅ PUT : MODIFIER PRODUIT
app.put('/produits/:id', async (req, res) => {
  try {
    const produit = await Produit.findByIdAndUpdate(req.params.id, req.body, { new: true });
    if (!produit) return res.status(404).json({ message: 'Produit introuvable' });
    res.json({ message: '✅ Produit modifié', produit });
  } catch (err) {
    console.error('❌ Erreur modification :', err);
    res.status(500).json({ message: 'Erreur modification', erreur: err });
  }
});

// ✅ DELETE : SUPPRIMER PRODUIT
app.delete('/produits/:id', async (req, res) => {
  try {
    const produit = await Produit.findByIdAndDelete(req.params.id);
    if (!produit) return res.status(404).json({ message: 'Produit introuvable' });
    res.json({ message: '🗑 Produit supprimé' });
  } catch (err) {
    console.error('❌ Erreur suppression :', err);
    res.status(500).json({ message: 'Erreur suppression', erreur: err });
  }
});

/* ---------------- CATCH-ALL POUR SERVIR LA SPA ---------------- */
app.get('*', (req, res) => {
  res.sendFile(path.resolve(__dirname, '../dist/index.html'));
});

/* ---------------- LANCEMENT ---------------- */
app.listen(PORT, () => {
  console.log(`🚀 Serveur lancé sur http://localhost:${PORT}`);
});

