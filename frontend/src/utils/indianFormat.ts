/**
 * Format number in Indian numbering system (lakhs and crores)
 * 1 Lakh = 100,000
 * 1 Crore = 10,000,000
 */
export function formatIndianCurrency(value: number | null | undefined): string {
  if (value === null || value === undefined) return '-';

  const absValue = Math.abs(value);
  const sign = value < 0 ? '-' : '';

  if (absValue >= 10000000) {
    // Crores (≥1 Cr)
    const crores = absValue / 10000000;
    return `${sign}₹${crores.toFixed(2)} Cr`;
  } else if (absValue >= 100000) {
    // Lakhs (≥1 L)
    const lakhs = absValue / 100000;
    return `${sign}₹${lakhs.toFixed(2)} L`;
  } else if (absValue >= 1000) {
    // Thousands
    const thousands = absValue / 1000;
    return `${sign}₹${thousands.toFixed(1)}K`;
  } else {
    return `${sign}₹${absValue.toFixed(0)}`;
  }
}

/**
 * Format for axis labels (shorter format)
 */
export function formatIndianAxisLabel(value: number | null | undefined): string {
  if (value === null || value === undefined || value === 0) return '';

  const absValue = Math.abs(value);

  if (absValue >= 10000000) {
    // Crores
    const crores = absValue / 10000000;
    return `${crores.toFixed(1)} Cr`;
  } else if (absValue >= 100000) {
    // Lakhs
    const lakhs = absValue / 100000;
    return `${lakhs.toFixed(1)} L`;
  } else if (absValue >= 1000) {
    // Thousands
    const thousands = absValue / 1000;
    return `${thousands.toFixed(0)}K`;
  } else {
    return `${absValue.toFixed(0)}`;
  }
}
