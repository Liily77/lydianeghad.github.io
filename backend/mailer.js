// backend/mailer.js
'use strict';

const nodemailer = require('nodemailer');

/**
 * Retourne l'adresse "from" par défaut.
 * Priorité : MAIL_FROM > BREVO_SMTP_USER
 */
function getDefaultFrom() {
  const mf = (process.env.MAIL_FROM || '').trim();
  if (mf) return mf;

  const brevoUser = (process.env.BREVO_SMTP_USER || '').trim();
  if (brevoUser) return brevoUser;

  throw new Error('MAIL_FROM manquante : définis MAIL_FROM ou BREVO_SMTP_USER dans les variables d’environnement.');
}

/**
 * Construit le transport nodemailer selon le provider.
 * Provider par défaut : Brevo (Sendinblue) via SMTP.
 */
function buildTransport() {
  const provider = (process.env.MAIL_PROVIDER || 'brevo').toLowerCase();

  if (provider === 'brevo') {
    const host = (process.env.BREVO_SMTP_HOST || 'smtp-relay.brevo.com').trim();
    const port = Number(process.env.BREVO_SMTP_PORT || 587);
    const user = (process.env.BREVO_SMTP_USER || '').trim();
    const pass = (process.env.BREVO_SMTP_KEY || '').trim();

    if (!user || !pass) {
      throw new Error('BREVO_SMTP_USER ou BREVO_SMTP_KEY manquant(s)');
    }

    return nodemailer.createTransport({
      host,
      port,
      secure: port === 465, // 465 = TLS implicite; 587 = STARTTLS
      auth: { user, pass },
      tls: { rejectUnauthorized: true },
    });
  }

  // Fallback : Gmail (si jamais)
  const user = (process.env.EMAIL_USER || '').trim();
  const pass = (process.env.EMAIL_PASS || '').trim();
  if (!user || !pass) {
    throw new Error('EMAIL_USER/EMAIL_PASS manquant(s) pour le provider Gmail');
  }

  return nodemailer.createTransport({
    host: 'smtp.gmail.com',
    port: 465,
    secure: true,
    auth: { user, pass },
    tls: { rejectUnauthorized: true },
  });
}

/**
 * Envoi générique d'e-mail (provider-agnostic).
 * - "from" : par défaut MAIL_FROM (ou BREVO_SMTP_USER)
 * - "replyTo" : utile pour que "Répondre" vise l’adresse du client
 */
async function sendMail({ to, subject, html, from, replyTo, text }) {
  if (!to) throw new Error('Paramètre "to" manquant');
  if (!subject) throw new Error('Paramètre "subject" manquant');

  const transporter = buildTransport();
  const mailFrom = (from && from.trim()) ? from.trim() : getDefaultFrom();

  return transporter.sendMail({
    from: mailFrom,
    to,
    subject,
    html,
    text,
    replyTo, // permet à Nadège de répondre directement au client
  });
}

/**
 * Auto-réponse pour le formulaire de contact (accusé de réception).
 * - "to" : e-mail du client
 * - "firstName" : optionnel, pour personnaliser le message
 * Remarque : on met replyTo=EMAIL_TO, ainsi si le client répond,
 * cela revient bien dans la boîte boutique.
 */
async function sendContactAutoReply({ to, firstName = '' }) {
  if (!to) throw new Error('Paramètre "to" manquant pour sendContactAutoReply');

  const subject = 'Arc En Ciel — Merci pour votre message';
  const safeFirst = (firstName || '').toString().trim();
  const html = `
    <p>Bonjour ${safeFirst || ''}</p>
    <p>Merci pour votre message, nous l’avons bien reçu.</p>
    <p>Nous vous répondrons sous 24–48h (jours ouvrés).</p>
    <p>— Arc En Ciel<br>Nadège Dupuis</p>
  `;

  return sendMail({
    to,
    subject,
    html,
    replyTo: (process.env.EMAIL_TO || '').trim() || getDefaultFrom(),
  });
}

module.exports = {
  buildTransport,
  sendMail,
  sendContactAutoReply,
};
