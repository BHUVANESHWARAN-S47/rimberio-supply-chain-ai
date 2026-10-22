/**
 * Indian Rupee (INR / ₹) Currency Utilities
 * Formats numbers according to Indian numbering system (Lakhs, Crores, etc.)
 */

export const CURRENCY_SYMBOL = '₹';

/**
 * Format a number into Indian Rupees standard format
 * e.g., 145000 -> ₹1,45,000.00
 */
export function formatINR(val, decimals = 2) {
  if (val === null || val === undefined || isNaN(Number(val))) {
    return '₹0.00';
  }
  const num = Number(val);
  return '₹' + num.toLocaleString('en-IN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

/**
 * Shorthand Indian formatting for KPI cards
 * e.g. 1500000 -> ₹15.00 L, 25000000 -> ₹2.50 Cr
 */
export function formatINRShorthand(val) {
  if (val === null || val === undefined || isNaN(Number(val))) {
    return '₹0';
  }
  const num = Math.abs(Number(val));
  const sign = Number(val) < 0 ? '-' : '';

  if (num >= 10000000) {
    return `${sign}₹${(num / 10000000).toFixed(2)} Cr`;
  }
  if (num >= 100000) {
    return `${sign}₹${(num / 100000).toFixed(2)} L`;
  }
  if (num >= 1000) {
    return `${sign}₹${(num / 1000).toFixed(1)}k`;
  }
  return `${sign}₹${num.toFixed(0)}`;
}
