import {
  Shield,
  Car,
  Heart,
  Users,
  Home,
  Building2,
  Activity,
  TrendingUp,
  Brain,
  Zap,
} from "lucide-react";

/** Map icon string names to Lucide components */
const iconMap = {
  car: Car,
  heart: Heart,
  users: Users,
  home: Home,
  building: Building2,
  shield: Shield,
  activity: Activity,
  trending: TrendingUp,
  brain: Brain,
  zap: Zap,
};

export function getBundleIcon(iconName, props = {}) {
  const Icon = iconMap[iconName] || Shield;
  return <Icon {...props} />;
}

/** Bundle color palette for charts */
export const BUNDLE_COLORS = [
  "#3B82F6",
  "#60A5FA",
  "#10B981",
  "#8B5CF6",
  "#34D399",
  "#F59E0B",
  "#FBBF24",
  "#06B6D4",
  "#EC4899",
  "#F472B6",
];

/** Get a CSS gradient for a bundle category */
export function getCategoryGradient(category) {
  const gradients = {
    Auto: "from-blue-500 to-blue-700",
    Health: "from-emerald-500 to-teal-700",
    Family: "from-violet-500 to-purple-700",
    Home: "from-amber-500 to-orange-700",
    Renter: "from-pink-500 to-rose-700",
  };
  return gradients[category] || "from-slate-500 to-slate-700";
}

/** Format currency */
export function formatCurrency(value) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

/** Format percentage */
export function formatPercent(value) {
  return `${value.toFixed(1)}%`;
}
