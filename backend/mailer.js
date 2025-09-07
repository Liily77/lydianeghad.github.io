// backend/mailer.js
const nodemailer = require('nodemailer');

function buildTransport() {
  const provider = (process.env.MAIL_PROVIDER || 'brevo').toLowerCase();

  if (provider === 'brevo') {
    const host = (process.env.BREVO_SMTP_HOST || 'smtp-relay.brevo.com').trim();
    const port = Number(process.env.BREVO_SMTP_PORT || 587);
    const user = (process.env.BREVO_SMTP_USER || '').trim();
    const pass = (process.env.BREVO_SMTP_KEY  || '').trim();

    return nodemailer.createTransport({
      host,
      port,
      secure: port === 465,
      auth: { user, pass },
    });
  }

  // (fallback Gmail si jamais)
  const user = (process.env.EMAIL_USER || '').trim();
  const pass = (process.env.EMAIL_PASS || '').trim();
  return nodemailer.createTransport({
    host: 'smtp.gmail.com',
    port: 465,
    secure: true,
    auth: { user, pass },
  });
}

async function sendMail({ from, to, subject, html, replyTo }) {
  const transporter = buildTransport();
  return transporter.sendMail({ from, to, subject, html, replyTo });
}

module.exports = { buildTransport, sendMail };
