// ============================================
// ERI (ESCALATION RISK INDEX) ENGINE
// Multi-dimensional Conflict Escalation Assessment
// ============================================

import type { ERIAssessment, ERIDimension, KeyDevelopment, Scenario } from '@/types';

// --------------------------------------------
// ERI DIMENSION CONFIGURATION
// --------------------------------------------

export const ERI_DIMENSIONS = {
  military: {
    name: 'Military',
    weight: 0.25,
    indicators: [
      'Troop Movements',
      'Airstrikes',
      'Naval Deployments',
      'Border Fortifications',
      'Weapons Transfers',
    ],
  },
  political: {
    name: 'Political',
    weight: 0.25,
    indicators: [
      'Diplomatic Statements',
      'Sanctions Activity',
      'Leadership Rhetoric',
      'Policy Changes',
      'Alliance Signals',
    ],
  },
  proxy: {
    name: 'Proxy',
    weight: 0.20,
    indicators: [
      'Militia Activity',
      'Armed Group Mobilization',
      'Cross-Border Incidents',
      'Support Operations',
      'Training Exercises',
    ],
  },
  economic: {
    name: 'Economic',
    weight: 0.15,
    indicators: [
      'Oil Price Volatility',
      'Shipping Disruptions',
      'Trade Restrictions',
      'Currency Fluctuations',
      'Resource Competition',
    ],
  },
  diplomatic: {
    name: 'Diplomatic',
    weight: 0.15,
    indicators: [
      'Negotiation Progress',
      'Mediator Engagement',
      'Backchannel Activity',
      'Multilateral Forums',
      'Confidence Building',
    ],
  },
};

// --------------------------------------------
// ERI CLASSIFICATION
// --------------------------------------------

export type ERIClassification = 'Low' | 'Moderate' | 'Elevated' | 'High' | 'Critical';

export function classifyERI(score: number): ERIClassification {
  if (score < 20) return 'Low';
  if (score < 40) return 'Moderate';
  if (score < 60) return 'Elevated';
  if (score < 80) return 'High';
  return 'Critical';
}

export function getERIColor(score: number): string {
  if (score < 20) return '#22c55e'; // green
  if (score < 40) return '#84cc16'; // lime
  if (score < 60) return '#eab308'; // yellow
  if (score < 80) return '#f97316'; // orange
  return '#ef4444'; // red
}

export function getERIBgColor(score: number): string {
  if (score < 20) return 'bg-green-500';
  if (score < 40) return 'bg-lime-500';
  if (score < 60) return 'bg-yellow-500';
  if (score < 80) return 'bg-orange-500';
  return 'bg-red-500';
}

export function getERITextColor(score: number): string {
  if (score < 20) return 'text-green-500';
  if (score < 40) return 'text-lime-500';
  if (score < 60) return 'text-yellow-500';
  if (score < 80) return 'text-orange-500';
  return 'text-red-500';
}

// --------------------------------------------
// ERI CALCULATION
// --------------------------------------------

export interface ERICalculationInput {
  military: number;
  political: number;
  proxy: number;
  economic: number;
  diplomatic: number;
}

export function calculateERI(input: ERICalculationInput): number {
  const overall =
    input.military * ERI_DIMENSIONS.military.weight +
    input.political * ERI_DIMENSIONS.political.weight +
    input.proxy * ERI_DIMENSIONS.proxy.weight +
    input.economic * ERI_DIMENSIONS.economic.weight +
    input.diplomatic * ERI_DIMENSIONS.diplomatic.weight;

  return Math.round(overall);
}

// --------------------------------------------
// TREND ANALYSIS
// --------------------------------------------

export function calculateTrend(
  current: number,
  previous: number
): 'up' | 'down' | 'stable' {
  const diff = current - previous;
  const threshold = 3; // Minimum change to register as trend

  if (diff > threshold) return 'up';
  if (diff < -threshold) return 'down';
  return 'stable';
}

export function getTrendIcon(trend: 'up' | 'down' | 'stable'): string {
  switch (trend) {
    case 'up':
      return '↑';
    case 'down':
      return '↓';
    case 'stable':
      return '→';
  }
}

export function getTrendColor(trend: 'up' | 'down' | 'stable'): string {
  switch (trend) {
    case 'up':
      return 'text-red-500';
    case 'down':
      return 'text-green-500';
    case 'stable':
      return 'text-gray-500';
  }
}

// --------------------------------------------
// SCENARIO PROBABILITY ASSESSMENT
// --------------------------------------------

export function assessScenarioProbability(
  eriScore: number,
  trend: 'up' | 'down' | 'stable'
): {
  stabilization: 'low' | 'moderate' | 'high';
  controlledEscalation: 'low' | 'moderate' | 'high';
  expandedConflict: 'low' | 'moderate' | 'high';
} {
  if (eriScore < 30) {
    return {
      stabilization: 'high',
      controlledEscalation: 'low',
      expandedConflict: 'low',
    };
  }

  if (eriScore < 50) {
    return {
      stabilization: trend === 'down' ? 'high' : 'moderate',
      controlledEscalation: trend === 'up' ? 'moderate' : 'low',
      expandedConflict: 'low',
    };
  }

  if (eriScore < 70) {
    return {
      stabilization: trend === 'down' ? 'moderate' : 'low',
      controlledEscalation: 'high',
      expandedConflict: trend === 'up' ? 'moderate' : 'low',
    };
  }

  return {
    stabilization: 'low',
    controlledEscalation: trend === 'down' ? 'moderate' : 'high',
    expandedConflict: trend === 'up' ? 'high' : 'moderate',
  };
}

// --------------------------------------------
// KEY DEVELOPMENT IMPACT SCORING
// --------------------------------------------

export function calculateDevelopmentImpact(
  development: Partial<KeyDevelopment>
): number {
  let impact = 5; // Base impact

  // Adjust based on escalation impact if provided
  if (development.escalationImpact !== undefined) {
    impact = development.escalationImpact;
  }

  // Keywords that increase impact
  const highImpactKeywords = [
    'attack',
    'strike',
    'invasion',
    'war',
    'casualties',
    'sanctions',
    'embargo',
  ];

  const mediumImpactKeywords = [
    'tension',
    'dispute',
    'protest',
    'deployment',
    'drill',
  ];

  const headline = (development.headline || '').toLowerCase();

  for (const keyword of highImpactKeywords) {
    if (headline.includes(keyword)) {
      impact += 2;
      break;
    }
  }

  for (const keyword of mediumImpactKeywords) {
    if (headline.includes(keyword)) {
      impact += 1;
      break;
    }
  }

  return Math.min(impact, 10);
}

// --------------------------------------------
// INDICATORS TO WATCH GENERATOR
// --------------------------------------------

export function generateIndicatorsToWatch(
  eriScore: number,
  dimensions: ERIDimension[]
): string[] {
  const indicators: string[] = [];

  // High-scoring dimension indicators
  const highDimensions = dimensions.filter((d) => d.score > 60);

  for (const dim of highDimensions) {
    switch (dim.name) {
      case 'Military':
        indicators.push('Troop movement reports');
        indicators.push('Military drill announcements');
        break;
      case 'Political':
        indicators.push('Leadership statements');
        indicators.push('Policy announcements');
        break;
      case 'Proxy':
        indicators.push('Militia activity reports');
        indicators.push('Cross-border incidents');
        break;
      case 'Economic':
        indicators.push('Oil price movements');
        indicators.push('Shipping route updates');
        break;
      case 'Diplomatic':
        indicators.push('Negotiation schedules');
        indicators.push('Mediator engagement');
        break;
    }
  }

  // ERI-level indicators
  if (eriScore > 60) {
    indicators.push('Third-party mediation efforts');
    indicators.push('Regional power statements');
  }

  if (eriScore > 80) {
    indicators.push('Evacuation advisories');
    indicators.push('International organization responses');
  }

  // Remove duplicates and limit
  return [...new Set(indicators)].slice(0, 6);
}

// --------------------------------------------
// ERI HISTORY ANALYSIS
// --------------------------------------------

export function analyzeERITrend(history: ERIAssessment[]): {
  trend: 'rising' | 'falling' | 'stable';
  volatility: number;
  average: number;
  peak: number;
  low: number;
} {
  if (history.length < 2) {
    return {
      trend: 'stable',
      volatility: 0,
      average: history[0]?.overallScore || 0,
      peak: history[0]?.overallScore || 0,
      low: history[0]?.overallScore || 0,
    };
  }

  const scores = history.map((h) => h.overallScore);
  const sorted = [...scores].sort((a, b) => a - b);

  const average = scores.reduce((a, b) => a + b, 0) / scores.length;

  // Calculate volatility (standard deviation)
  const variance = scores.reduce((acc, score) => acc + Math.pow(score - average, 2), 0) / scores.length;
  const volatility = Math.sqrt(variance);

  // Determine trend
  const firstHalf = scores.slice(0, Math.floor(scores.length / 2));
  const secondHalf = scores.slice(Math.floor(scores.length / 2));
  const firstAvg = firstHalf.reduce((a, b) => a + b, 0) / firstHalf.length;
  const secondAvg = secondHalf.reduce((a, b) => a + b, 0) / secondHalf.length;

  let trend: 'rising' | 'falling' | 'stable' = 'stable';
  if (secondAvg - firstAvg > 5) trend = 'rising';
  else if (firstAvg - secondAvg > 5) trend = 'falling';

  return {
    trend,
    volatility: Math.round(volatility * 10) / 10,
    average: Math.round(average),
    peak: sorted[sorted.length - 1],
    low: sorted[0],
  };
}

// --------------------------------------------
// GENERATE NEW ERI ASSESSMENT
// --------------------------------------------

export interface ERIGenerationInput {
  weekNumber: number;
  year: number;
  dimensionScores: ERICalculationInput;
  keyDevelopments: Partial<KeyDevelopment>[];
}

export function generateERIAssessment(input: ERIGenerationInput): ERIAssessment {
  const overallScore = calculateERI(input.dimensionScores);
  const classification = classifyERI(overallScore);

  // Create dimensions with indicators
  const dimensions: ERIDimension[] = [
    {
      name: 'Military',
      score: input.dimensionScores.military,
      weight: ERI_DIMENSIONS.military.weight,
      indicators: ERI_DIMENSIONS.military.indicators.map((name, i) => ({
        id: `m${i}`,
        name,
        value: Math.round(input.dimensionScores.military + (Math.random() * 20 - 10)),
        trend: Math.random() > 0.6 ? 'up' : Math.random() > 0.5 ? 'down' : 'stable',
        description: `Military ${name.toLowerCase()} indicator`,
      })),
    },
    {
      name: 'Political',
      score: input.dimensionScores.political,
      weight: ERI_DIMENSIONS.political.weight,
      indicators: ERI_DIMENSIONS.political.indicators.map((name, i) => ({
        id: `p${i}`,
        name,
        value: Math.round(input.dimensionScores.political + (Math.random() * 20 - 10)),
        trend: Math.random() > 0.6 ? 'up' : Math.random() > 0.5 ? 'down' : 'stable',
        description: `Political ${name.toLowerCase()} indicator`,
      })),
    },
    {
      name: 'Proxy',
      score: input.dimensionScores.proxy,
      weight: ERI_DIMENSIONS.proxy.weight,
      indicators: ERI_DIMENSIONS.proxy.indicators.map((name, i) => ({
        id: `px${i}`,
        name,
        value: Math.round(input.dimensionScores.proxy + (Math.random() * 20 - 10)),
        trend: Math.random() > 0.6 ? 'up' : Math.random() > 0.5 ? 'down' : 'stable',
        description: `Proxy ${name.toLowerCase()} indicator`,
      })),
    },
    {
      name: 'Economic',
      score: input.dimensionScores.economic,
      weight: ERI_DIMENSIONS.economic.weight,
      indicators: ERI_DIMENSIONS.economic.indicators.map((name, i) => ({
        id: `e${i}`,
        name,
        value: Math.round(input.dimensionScores.economic + (Math.random() * 20 - 10)),
        trend: Math.random() > 0.6 ? 'up' : Math.random() > 0.5 ? 'down' : 'stable',
        description: `Economic ${name.toLowerCase()} indicator`,
      })),
    },
    {
      name: 'Diplomatic',
      score: input.dimensionScores.diplomatic,
      weight: ERI_DIMENSIONS.diplomatic.weight,
      indicators: ERI_DIMENSIONS.diplomatic.indicators.map((name, i) => ({
        id: `d${i}`,
        name,
        value: Math.round(input.dimensionScores.diplomatic + (Math.random() * 20 - 10)),
        trend: Math.random() > 0.6 ? 'up' : Math.random() > 0.5 ? 'down' : 'stable',
        description: `Diplomatic ${name.toLowerCase()} indicator`,
      })),
    },
  ];

  // Generate scenarios based on ERI score
  const probabilities = assessScenarioProbability(overallScore, 'stable');
  const scenarios: Scenario[] = [
    {
      id: 's1',
      name: 'Stabilization Path',
      probability: probabilities.stabilization,
      description: 'Diplomatic breakthrough reduces tensions through negotiated settlement',
      triggers: ['Negotiation resumption', 'Third-party mediation success', 'Confidence-building measures'],
    },
    {
      id: 's2',
      name: 'Controlled Escalation',
      probability: probabilities.controlledEscalation,
      description: 'Limited conflict with contained scope and regional involvement',
      triggers: ['Proxy escalation', 'Retaliatory strikes', 'Sanctions expansion'],
    },
    {
      id: 's3',
      name: 'Expanded Regional Conflict',
      probability: probabilities.expandedConflict,
      description: 'Multi-actor involvement broadens conflict beyond initial parameters',
      triggers: ['Alliance activation', 'Critical infrastructure attack', 'Humanitarian crisis'],
    },
  ];

  // Process key developments
  const processedDevelopments: KeyDevelopment[] = input.keyDevelopments.map((kd, i) => ({
    id: `kd${i}`,
    headline: kd.headline || 'Untitled Development',
    whatHappened: kd.whatHappened || '',
    whyItMatters: kd.whyItMatters || '',
    whoBenefits: kd.whoBenefits || '',
    whoLoses: kd.whoLoses || '',
    escalationImpact: kd.escalationImpact || calculateDevelopmentImpact(kd),
  }));

  // Generate indicators to watch
  const indicatorsToWatch = generateIndicatorsToWatch(overallScore, dimensions);

  return {
    id: `eri-${input.year}-${input.weekNumber}`,
    weekNumber: input.weekNumber,
    year: input.year,
    overallScore,
    classification,
    dimensions,
    keyDevelopments: processedDevelopments,
    scenarioOutlook: scenarios,
    indicatorsToWatch,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };
}

// --------------------------------------------
// ERI COMPARISON
// --------------------------------------------

export function compareERI(
  current: ERIAssessment,
  previous: ERIAssessment
): {
  overallChange: number;
  dimensionChanges: Record<string, number>;
  significantShifts: string[];
} {
  const overallChange = current.overallScore - previous.overallScore;

  const dimensionChanges: Record<string, number> = {};
  const significantShifts: string[] = [];

  for (const dim of current.dimensions) {
    const prevDim = previous.dimensions.find((d) => d.name === dim.name);
    if (prevDim) {
      const change = dim.score - prevDim.score;
      dimensionChanges[dim.name] = change;

      if (Math.abs(change) > 10) {
        significantShifts.push(
          `${dim.name}: ${change > 0 ? '+' : ''}${change} points`
        );
      }
    }
  }

  return {
    overallChange,
    dimensionChanges,
    significantShifts,
  };
}
