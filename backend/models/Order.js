// models/Order.js
const mongoose = require("mongoose");

const ItemSchema = new mongoose.Schema(
  {
    id: String,
    name: String,
    category: { type: String, enum: ["bijoux", "vetements"], required: true },
    // Aligné sur le payload du checkout: unit_price + quantity
    unit_price: { type: Number, required: true, min: 0 },
    quantity:   { type: Number, required: true, min: 1 },
    // (optionnel) compat si un jour tu enregistres aussi price/qty
    price: Number,
    qty: Number,
  },
  { _id: false }
);

const OrderSchema = new mongoose.Schema(
  {
    // Référence unique de commande (utilisée par la route)
    ref: { type: String, index: true, unique: true },

    email: { type: String, required: true },

    shippingAddress: {
      fullName: String,
      address1: String,
      address2: String,
      postcode: String,
      city: String,
      country: String,
    },

    items: { type: [ItemSchema], default: [] },

    amounts: {
      subTotal:    { type: Number, required: true, min: 0 },
      shippingFee: { type: Number, required: true, min: 0 },
      total:       { type: Number, required: true, min: 0 },
    },

    currency: { type: String, default: "EUR" },
    channel:  { type: String, default: "sumup" },

    status: {
      type: String,
      enum: ["PENDING", "PAID", "FAILED", "REFUNDED"],
      default: "PENDING",
      index: true,
    },

    // Infos SumUp
    checkoutId: String, // id du checkout SumUp
    raw: {},            // payload brut SumUp (Mixed)

    // Divers
    isEmailSent: { type: Boolean, default: false },
    paidAt: Date,
  },
  { timestamps: { createdAt: "createdAt", updatedAt: "updatedAt" } }
);

// ----- Index utiles pour back-office / requêtes fréquentes -----
OrderSchema.index({ status: 1, createdAt: -1 });
OrderSchema.index({ email: 1, createdAt: -1 });

// ----- Options de sortie propres -----
OrderSchema.set("versionKey", false);
OrderSchema.set("toJSON", { virtuals: true });
OrderSchema.set("toObject", { virtuals: true });

// ----- Virtuels -----
OrderSchema.virtual("totalItems").get(function () {
  return (this.items || []).reduce((s, i) => s + (i.quantity || 0), 0);
});

// ----- Export avec garde anti-OverwriteModelError -----
module.exports =
  mongoose.models.Order || mongoose.model("Order", OrderSchema);
