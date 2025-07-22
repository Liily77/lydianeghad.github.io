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
const PORT = process.env.PORT || 3001;

// --- MIDDLEWARES ---
app.use(cors());
app.use(express.json());
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

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

/* ---------------- ROUTES ---------------- */

// ✅ ROUTE CONTACT : ENVOI DE MAIL
app.post('/send-email', async (req, res) => {
  const { name, email, message } = req.body;

  const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
      user: process.env.EMAIL_USER, // Ex: tonemail@gmail.com
      pass: process.env.EMAIL_PASS  // Mot de passe d'application
    }
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
    const query = req.query.q;
    if (!query) {
      return res.status(400).json({ message: 'Veuillez fournir un mot-clé' });
    }

    const produits = await Produit.find({
      nom: { $regex: query, $options: 'i' }
    });

    res.json(produits);
  } catch (err) {
    console.error('❌ Erreur recherche produit :', err);
    res.status(500).json({ message: 'Erreur recherche', erreur: err });
  }
});

// ✅ GET TOUS LES PRODUITS
app.get('/produits', async (req, res) => {
  try {
    const produits = await Produit.find();
    res.json(produits);
  } catch (err) {
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
    res.status(500).json({ message: 'Erreur serveur', erreur: err });
  }
});

// ✅ POST : AJOUT PRODUIT
app.post('/produits', upload.array('images'), async (req, res) => {
  try {
    const { nom, description, prix, categorie } = req.body;
    const images = req.files.map(file => `/uploads/${file.filename}`);

    const produit = new Produit({
      nom,
      description,
      prix: parseFloat(prix),
      categorie,
      images
    });

    const produitAjoute = await produit.save();
    res.status(201).json({ message: '✅ Produit ajouté', produit: produitAjoute });
  } catch (err) {
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
    res.status(500).json({ message: 'Erreur suppression', erreur: err });
  }
});

/* ---------------- DÉMARRAGE ---------------- */
app.listen(PORT, () => {
  console.log(`🚀 Serveur lancé sur http://localhost:${PORT}`);
});
