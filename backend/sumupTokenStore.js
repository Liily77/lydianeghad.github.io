// backend/sumupTokenStore.js
let _token = null;
let _expiresAt = 0; // timestamp en millisecondes

module.exports = {
  set(token, expiresInSec) {
    _token = token;
    _expiresAt = Date.now() + (Number(expiresInSec || 0) * 1000);
  },
  clear() {
    _token = null;
    _expiresAt = 0;
  },
  get() {
    if (!_token) return null;
    return _token;
  },
  isSet() {
    return Boolean(_token);
  }
};
