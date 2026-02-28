// ============================================
// RISK GOVERNANCE ENGINE
// 4-Dimensional Risk Scoring System
// ============================================

import type { RiskScores, RiskFactors, RiskAssessment, ContentItem } from '@/types';

// --------------------------------------------
// RISK WEIGHTS CONFIGURATION
// --------------------------------------------

const RISK_WEIGHTS = {
  legal: {
    namedIndividual: 15,
    criminalAllegation: 25,
    singleAnonymousSource: 20,
    electionPeriod: 10,
    warTopic: 5,
  },
  defamation: {
    namedIndividual: 20,
    criminalAllegation: 30,
    singleAnonymousSource: 25,
    electionPeriod: 5,
    warTopic: 0,
  },
  platform: {
    namedIndividual: 10,
    criminalAllegation: 20,
    singleAnonymousSource: 15,
    electionPeriod: 15,
    warTopic: 25,
    religiousFraming: 30,
    ethnicTension: 30,
    activeConflict: 20,
    terrorismDesignation: 25,
  },
  political: {
    namedIndividual: 10,
    criminalAllegation: 15,
    electionPeriod: 25,
    warTopic: 20,
    religiousFraming: 20,
    ethnicTension: 25,
    activeConflict: 15,
    israelMentioned: 15,
    iranMentioned: 15,
    palestineMentioned: 20,
    usMilitaryInvolved: 10,
  },
};

// Middle-East specific sensitivity boost
const ME_SENSITIVITY_BOOST = 15;

// --------------------------------------------
// RISK CALCULATION FUNCTIONS
// --------------------------------------------

/**
 * Calculate Legal Risk Score (0-100)
 */
export function calculateLegalRisk(factors: RiskFactors): number {
  let score = 0;
  const weights = RISK_WEIGHTS.legal;

  if (factors.namedIndividual) score += weights.namedIndividual;
  if (factors.criminalAllegation) score += weights.criminalAllegation;
  if (factors.singleAnonymousSource) score += weights.singleAnonymousSource;
  if (factors.electionPeriod) score += weights.electionPeriod;
  if (factors.warTopic) score += weights.warTopic;

  // Cap at 100
  return Math.min(score, 100);
}

/**
 * Calculate Defamation Risk Score (0-100)
 */
export function calculateDefamationRisk(factors: RiskFactors): number {
  let score = 0;
  const weights = RISK_WEIGHTS.defamation;

  if (factors.namedIndividual) score += weights.namedIndividual;
  if (factors.criminalAllegation) score += weights.criminalAllegation;
  if (factors.singleAnonymousSource) score += weights.singleAnonymousSource;
  if (factors.electionPeriod) score += weights.electionPeriod;

  // Direct accusations without evidence = maximum risk
  if (factors.criminalAllegation && factors.singleAnonymousSource) {
    score += 20; // Additional penalty
  }

  return Math.min(score, 100);
}

/**
 * Calculate Platform Policy Risk Score (0-100)
 */
export function calculatePlatformRisk(factors: RiskFactors): number {
  let score = 0;
  const weights = RISK_WEIGHTS.platform;

  if (factors.namedIndividual) score += weights.namedIndividual;
  if (factors.criminalAllegation) score += weights.criminalAllegation;
  if (factors.singleAnonymousSource) score += weights.singleAnonymousSource;
  if (factors.electionPeriod) score += weights.electionPeriod;
  if (factors.warTopic) score += weights.warTopic;
  if (factors.religiousFraming) score += weights.religiousFraming;
  if (factors.ethnicTension) score += weights.ethnicTension;
  if (factors.activeConflict) score += weights.activeConflict;
  if (factors.terrorismDesignation) score += weights.terrorismDesignation;

  return Math.min(score, 100);
}

/**
 * Calculate Political Sensitivity Score (0-100)
 */
export function calculatePoliticalSensitivity(factors: RiskFactors): number {
  let score = 0;
  const weights = RISK_WEIGHTS.political;

  if (factors.namedIndividual) score += weights.namedIndividual;
  if (factors.criminalAllegation) score += weights.criminalAllegation;
  if (factors.electionPeriod) score += weights.electionPeriod;
  if (factors.warTopic) score += weights.warTopic;
  if (factors.religiousFraming) score += weights.religiousFraming;
  if (factors.ethnicTension) score += weights.ethnicTension;
  if (factors.activeConflict) score += weights.activeConflict;
  if (factors.israelMentioned) score += weights.israelMentioned;
  if (factors.iranMentioned) score += weights.iranMentioned;
  if (factors.palestineMentioned) score += weights.palestineMentioned;
  if (factors.usMilitaryInvolved) score += weights.usMilitaryInvolved;

  // Middle-East specific boost
  if (factors.israelMentioned || factors.iranMentioned || factors.palestineMentioned) {
    score = Math.min(score + ME_SENSITIVITY_BOOST, 100);
  }

  return Math.min(score, 100);
}

/**
 * Calculate Overall Risk Score (Weighted Average)
 */
export function calculateOverallRisk(scores: Omit<RiskScores, 'overallScore'>): number {
  // Weights for overall calculation
  const weights = {
    legal: 0.30,
    defamation: 0.30,
    platform: 0.20,
    political: 0.20,
  };

  const overall =
    scores.legalRisk * weights.legal +
    scores.defamationRisk * weights.defamation +
    scores.platformRisk * weights.platform +
    scores.politicalSensitivity * weights.political;

  return Math.round(overall);
}

/**
 * Complete Risk Assessment
 */
export function assessRisk(factors: RiskFactors): RiskScores {
  const legalRisk = calculateLegalRisk(factors);
  const defamationRisk = calculateDefamationRisk(factors);
  const platformRisk = calculatePlatformRisk(factors);
  const politicalSensitivity = calculatePoliticalSensitivity(factors);

  const overallScore = calculateOverallRisk({
    legalRisk,
    defamationRisk,
    platformRisk,
    politicalSensitivity,
  });

  return {
    legalRisk,
    defamationRisk,
    platformRisk,
    politicalSensitivity,
    overallScore,
  };
}

// --------------------------------------------
// RISK CLASSIFICATION
// --------------------------------------------

export type RiskLevel = 'Low' | 'Moderate' | 'Elevated' | 'High' | 'Critical';

export function classifyRisk(score: number): RiskLevel {
  if (score <= 20) return 'Low';
  if (score <= 40) return 'Moderate';
  if (score <= 60) return 'Elevated';
  if (score <= 80) return 'High';
  return 'Critical';
}

export function getRiskColor(score: number): string {
  if (score <= 20) return '#22c55e'; // green-500
  if (score <= 40) return '#84cc16'; // lime-500
  if (score <= 60) return '#eab308'; // yellow-500
  if (score <= 80) return '#f97316'; // orange-500
  return '#ef4444'; // red-500
}

export function getRiskBgColor(score: number): string {
  if (score <= 20) return 'bg-green-500/10 text-green-500 border-green-500/20';
  if (score <= 40) return 'bg-lime-500/10 text-lime-500 border-lime-500/20';
  if (score <= 60) return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20';
  if (score <= 80) return 'bg-orange-500/10 text-orange-500 border-orange-500/20';
  return 'bg-red-500/10 text-red-500 border-red-500/20';
}

// --------------------------------------------
// APPROVAL HIERARCHY
// --------------------------------------------

export function getRequiredApprovalLevel(riskScore: number): string {
  if (riskScore <= 20) return 'Junior Editor';
  if (riskScore <= 40) return 'Senior Editor';
  if (riskScore <= 60) return 'Editor-in-Chief';
  return 'Editor-in-Chief + Legal Consultation';
}

export function canApprove(userRole: string, riskScore: number): boolean {
  const roleHierarchy: Record<string, number> = {
    'junior_editor': 20,
    'senior_editor': 40,
    'editor_in_chief': 100,
    'admin': 100,
  };

  const userLevel = roleHierarchy[userRole] || 0;
  return userLevel >= riskScore;
}

// --------------------------------------------
// SAFE MODE ENFORCEMENT
// --------------------------------------------

export function checkSafeModeViolation(
  factors: RiskFactors,
  safeModeEnabled: boolean
): { violated: boolean; reasons: string[] } {
  if (!safeModeEnabled) {
    return { violated: false, reasons: [] };
  }

  const reasons: string[] = [];

  if (factors.criminalAllegation) {
    reasons.push('Criminal allegations not allowed in Safe Mode');
  }
  if (factors.activeConflict) {
    reasons.push('Active conflict analysis restricted in Safe Mode');
  }
  if (factors.singleAnonymousSource) {
    reasons.push('Anonymous sources not allowed in Safe Mode');
  }
  if (factors.religiousFraming) {
    reasons.push('Religious framing prohibited in Safe Mode');
  }

  return {
    violated: reasons.length > 0,
    reasons,
  };
}

// --------------------------------------------
// RISK MITIGATION SUGGESTIONS
// --------------------------------------------

export function getRiskMitigationSuggestions(factors: RiskFactors): string[] {
  const suggestions: string[] = [];

  if (factors.namedIndividual) {
    suggestions.push('Use "alleged" or "reportedly" when mentioning individuals');
    suggestions.push('Include response from accused when available');
  }

  if (factors.criminalAllegation) {
    suggestions.push('Attribute allegations to specific sources');
    suggestions.push('Avoid stating guilt without court verdict');
    suggestions.push('Use neutral language: "accused of" instead of "guilty of"');
  }

  if (factors.singleAnonymousSource) {
    suggestions.push('Seek additional corroborating sources');
    suggestions.push('Clearly state reason for anonymity');
    suggestions.push('Document internal verification process');
  }

  if (factors.warTopic) {
    suggestions.push('Focus on structural analysis, not tactical details');
    suggestions.push('Avoid casualty speculation');
    suggestions.push('Use maps and timelines instead of conflict footage');
  }

  if (factors.religiousFraming || factors.ethnicTension) {
    suggestions.push('Remove religious/ethnic identifiers unless essential');
    suggestions.push('Focus on political/strategic factors');
    suggestions.push('Use neutral terminology');
  }

  if (factors.israelMentioned || factors.iranMentioned || factors.palestineMentioned) {
    suggestions.push('Present multiple perspectives');
    suggestions.push('Attribute claims to specific sources');
    suggestions.push('Avoid taking sides in territorial disputes');
  }

  return suggestions;
}

// --------------------------------------------
// CONTENT ANALYSIS (Auto-detect risk factors from content)
// --------------------------------------------

export function analyzeContentForRiskFactors(
  headline: string,
  summary: string,
  tags: string[]
): RiskFactors {
  const content = (headline + ' ' + summary).toLowerCase();
  const contentTags = tags.map((t) => t.toLowerCase());

  return {
    namedIndividual: /\b(mr\.|mrs\.|ms\.|dr\.|president|prime minister|minister|leader)\s+\w+/i.test(content),
    criminalAllegation: /\b(guilty|crime|criminal|corruption|bribe|fraud|illegal|violation)\b/i.test(content),
    singleAnonymousSource: /\b(anonymous|unnamed|source said|sources said)\b/i.test(content),
    electionPeriod: /\b(election|vote|campaign|polling|ballot)\b/i.test(content),
    warTopic: /\b(war|conflict|attack|strike|military|combat|battle)\b/i.test(content),
    religiousFraming: /\b(muslim|christian|jewish|hindu|sunni|shia|islamic|religious)\b/i.test(content),
    ethnicTension: /\b(ethnic|sectarian|tribal|racial)\b/i.test(content),
    activeConflict: /\b(ongoing|active|current|live|breaking)\b/i.test(content),
    terrorismDesignation: /\b(terrorist|terrorism|militant|extremist)\b/i.test(content),
    israelMentioned: contentTags.includes('israel') || /\bisrael\b/i.test(content),
    iranMentioned: contentTags.includes('iran') || /\biran\b/i.test(content),
    palestineMentioned: contentTags.includes('palestine') || /\bpalestine\b/i.test(content),
    usMilitaryInvolved: /\b(us military|us forces|american troops|pentagon)\b/i.test(content),
  };
}

// --------------------------------------------
// GENERATE RISK ASSESSMENT REPORT
// --------------------------------------------

export function generateRiskAssessmentReport(
  content: ContentItem,
  assessedBy: string
): RiskAssessment {
  const factors = analyzeContentForRiskFactors(
    content.headline,
    content.summary,
    content.tags
  );

  const scores = assessRisk(factors);
  const classification = classifyRisk(scores.overallScore);

  return {
    id: `risk-${Date.now()}`,
    contentId: content.id,
    scores,
    factors,
    assessedAt: new Date().toISOString(),
    assessedBy,
    requiresSeniorReview: scores.overallScore > 40,
    safeModeBlocked: false,
    notes: `Risk Classification: ${classification}. ${getRequiredApprovalLevel(scores.overallScore)} approval required.`,
  };
}
