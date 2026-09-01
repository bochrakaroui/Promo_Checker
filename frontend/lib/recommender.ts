import type { ProductSummary } from './types';

export type UseCase = 'everyday' | 'study' | 'business' | 'programming' | 'creative' | 'gaming';

export interface RecommendationPreferences {
  budget: number;
  useCase: UseCase;
  brand: string;
  minRam: number;
  minStorage: number;
}

export interface ScoredRecommendation {
  product: ProductSummary;
  score: number;
  reasons: string[];
}

export const useCaseDefaults: Record<UseCase, { ram: number; storage: number; cpuTier: number }> = {
  everyday: { ram: 8, storage: 256, cpuTier: 1 },
  study: { ram: 8, storage: 256, cpuTier: 1 },
  business: { ram: 16, storage: 512, cpuTier: 2 },
  programming: { ram: 16, storage: 512, cpuTier: 2 },
  creative: { ram: 16, storage: 512, cpuTier: 3 },
  gaming: { ram: 16, storage: 512, cpuTier: 3 },
};

function getCpuTier(product: ProductSummary): number {
  const text = `${product.cpu_type ?? ''} ${product.model ?? ''} ${product.name ?? ''}`.toLowerCase();

  if (/\b(i9|ryzen\s*9|core\s*ultra\s*9|m[1-4]\s*max)\b/.test(text)) return 4;
  if (/\b(i7|ryzen\s*7|core\s*ultra\s*7|m[1-4]\s*pro|m3|m4)\b/.test(text)) return 3;
  if (/\b(i5|ryzen\s*5|core\s*ultra\s*5|m1|m2|core\s*5)\b/.test(text)) return 2;
  return 1;
}

function productRam(product: ProductSummary): number {
  return product.ram_gb ?? (Number.parseInt(product.ram_size ?? '0', 10) || 0);
}

function productStorage(product: ProductSummary): number {
  return product.storage_gb ?? (Number.parseInt(product.storage_capacity ?? '0', 10) || 0);
}

export function recommendProducts(
  products: ProductSummary[],
  preferences: RecommendationPreferences,
  limit = 3,
): ScoredRecommendation[] {
  const desiredCpuTier = useCaseDefaults[preferences.useCase].cpuTier;

  return products
    .filter((product) => Number.isFinite(product.lowest_price) && product.lowest_price > 0)
    .map((product) => {
      const ram = productRam(product);
      const storage = productStorage(product);
      const cpuTier = getCpuTier(product);
      const reasons: string[] = [];
      let score = 0;

      if (product.lowest_price <= preferences.budget) {
        score += 32;
        reasons.push(`${Math.round(preferences.budget - product.lowest_price)} TND under budget`);
      } else {
        const overBudgetRatio = (product.lowest_price - preferences.budget) / preferences.budget;
        score += Math.max(0, 32 - overBudgetRatio * 80);
        reasons.push(`${Math.round(product.lowest_price - preferences.budget)} TND over budget`);
      }

      score += ram >= preferences.minRam
        ? 20
        : 20 * Math.min(1, ram / preferences.minRam);
      if (ram >= preferences.minRam) reasons.push(`${ram} GB RAM meets your target`);

      score += storage >= preferences.minStorage
        ? 15
        : 15 * Math.min(1, storage / preferences.minStorage);
      if (storage >= preferences.minStorage) reasons.push(`${storage} GB storage meets your target`);

      score += cpuTier >= desiredCpuTier
        ? 18
        : 18 * (cpuTier / desiredCpuTier);
      if (cpuTier >= desiredCpuTier && product.cpu_type) {
        reasons.push(`${product.cpu_type} suits ${preferences.useCase} use`);
      }

      if (preferences.brand) {
        if (product.brand?.toLowerCase() === preferences.brand.toLowerCase()) score += 5;
      } else {
        score += 3;
      }

      const highestPrice = product.highest_price ?? product.lowest_price;
      const savings = highestPrice > product.lowest_price
        ? (highestPrice - product.lowest_price) / highestPrice
        : 0;
      score += Math.min(4, product.store_count) + Math.min(3, savings * 15);
      if (product.store_count > 1) reasons.push(`Compared across ${product.store_count} stores`);

      const useCaseText = `${product.model ?? ''} ${product.name}`.toLowerCase();
      if ((preferences.useCase === 'gaming' || preferences.useCase === 'creative') && /rtx|gtx|radeon|arc\s/.test(useCaseText)) {
        score += 5;
        reasons.push('Dedicated graphics detected');
      }

      return {
        product,
        score: Math.min(100, Math.round(score)),
        reasons: reasons.slice(0, 4),
      };
    })
    .sort((a, b) => b.score - a.score || a.product.lowest_price - b.product.lowest_price)
    .slice(0, limit);
}
