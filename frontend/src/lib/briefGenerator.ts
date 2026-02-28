// ============================================
// WEEKLY INTELLIGENCE BRIEF GENERATOR
// PDF Report Generation System
// ============================================

import type {
  WeeklyBrief,
  ERIAssessment,
  ExecutiveSummary,
  EnergyWatch,
  StakeholderPosition,
  KeyDevelopment,
  Scenario,
} from '@/types';
import { getERIColor } from './eriEngine';

// --------------------------------------------
// BRIEF TEMPLATES
// --------------------------------------------

export const BRIEF_TEMPLATES = {
  coverPage: {
    title: 'Middle-East Strategic Intelligence Brief',
    subtitle: 'Escalation Assessment | Energy Outlook | Diplomatic Signals',
  },
  sections: [
    'Executive Summary',
    'Escalation Risk Index',
    'Key Developments',
    'Energy & Economic Watch',
    'Strategic Stakeholder Positioning',
    'Scenario Outlook',
    'Indicators to Watch',
    'Methodology & Disclaimer',
  ],
};

// --------------------------------------------
// EXECUTIVE SUMMARY GENERATOR
// --------------------------------------------

export function generateExecutiveSummary(
  eri: ERIAssessment,
  previousERI?: ERIAssessment
): ExecutiveSummary {
  const trend = previousERI
    ? eri.overallScore > previousERI.overallScore
      ? 'increased'
      : eri.overallScore < previousERI.overallScore
      ? 'decreased'
      : 'remained stable'
    : 'being assessed';

  const militaryDim = eri.dimensions.find((d) => d.name === 'Military');
  const proxyDim = eri.dimensions.find((d) => d.name === 'Proxy');
  const diplomaticDim = eri.dimensions.find((d) => d.name === 'Diplomatic');

  return {
    whatChanged: `Escalation Risk Index has ${trend} to ${eri.overallScore} (${eri.classification})`,
    whatIsStable: diplomaticDim && diplomaticDim.score < 50
      ? 'Diplomatic channels remain open despite tensions'
      : 'Core economic relationships maintained',
    riskIncreased: militaryDim && militaryDim.score > 60
      ? 'Military activity showing elevated patterns'
      : 'Political rhetoric intensifying',
    riskDecreased: proxyDim && proxyDim.score < 50
      ? 'Proxy militia activity showing de-escalation'
      : 'Economic indicators stabilizing',
    militaryActivity: militaryDim
      ? `${militaryDim.score > 60 ? 'Increased' : 'Stable'} along primary corridors`
      : 'Under assessment',
    proxyActivity: proxyDim
      ? `${proxyDim.score > 60 ? 'Active' : 'Isolated'} activation patterns observed`
      : 'Under assessment',
    diplomaticTrack: diplomaticDim
      ? `${diplomaticDim.score > 50 ? 'Stalled but not collapsed' : 'Active engagement ongoing'}`
      : 'Under assessment',
  };
}

// --------------------------------------------
// ENERGY WATCH GENERATOR
// --------------------------------------------

export function generateEnergyWatch(eri: ERIAssessment): EnergyWatch {
  const economicDim = eri.dimensions.find((d) => d.name === 'Economic');
  const score = economicDim?.score || 50;

  return {
    oilMovement: score > 60
      ? 'Brent crude showing volatility above $85/barrel'
      : 'Oil prices stable within expected range',
    shippingRisk: score > 70
      ? 'Insurance premiums rising for Gulf routes'
      : 'Shipping lanes operating normally',
    sanctionsUpdate: 'No major sanctions developments this week',
    currencyAdjustments: 'Regional currencies showing mixed performance',
    indiaAngle: score > 60
      ? 'India monitoring energy security implications closely'
      : 'India maintaining normal import schedules',
  };
}

// --------------------------------------------
// STAKEHOLDER POSITIONS
// --------------------------------------------

export const DEFAULT_STAKEHOLDERS = [
  'Iran',
  'Israel',
  'Saudi Arabia',
  'United States',
  'China',
  'Russia',
  'UAE',
  'Turkey',
];

export function generateStakeholderPositions(eri: ERIAssessment): StakeholderPosition[] {
  const positions: StakeholderPosition[] = [
    {
      actor: 'Iran',
      currentPosition: eri.overallScore > 60
        ? 'Assertive regional posture'
        : 'Cautious diplomatic engagement',
      weeklyMovement: 'Maintaining current stance',
      escalationImpact: eri.overallScore > 60 ? 7 : 5,
    },
    {
      actor: 'Israel',
      currentPosition: eri.overallScore > 70
        ? 'Heightened security alert'
        : 'Strategic patience approach',
      weeklyMovement: 'Monitoring regional developments',
      escalationImpact: eri.overallScore > 70 ? 8 : 4,
    },
    {
      actor: 'Saudi Arabia',
      currentPosition: 'Balancing regional influence with stability goals',
      weeklyMovement: 'Engaging in backchannel diplomacy',
      escalationImpact: 4,
    },
    {
      actor: 'United States',
      currentPosition: eri.overallScore > 60
        ? 'Deterrence-focused deployment'
        : 'Diplomatic engagement priority',
      weeklyMovement: 'Coordinating with allies',
      escalationImpact: eri.overallScore > 60 ? 6 : 3,
    },
    {
      actor: 'China',
      currentPosition: 'Economic interests protection mode',
      weeklyMovement: 'Expanding energy agreements',
      escalationImpact: 3,
    },
    {
      actor: 'Russia',
      currentPosition: 'Strategic opportunism in region',
      weeklyMovement: 'Deepening defense cooperation',
      escalationImpact: 5,
    },
    {
      actor: 'UAE',
      currentPosition: 'Economic pragmatism with security awareness',
      weeklyMovement: 'Strengthening bilateral ties',
      escalationImpact: 3,
    },
    {
      actor: 'Turkey',
      currentPosition: 'Assertive regional role seeking',
      weeklyMovement: 'Diplomatic initiatives ongoing',
      escalationImpact: 4,
    },
  ];

  return positions;
}

// --------------------------------------------
// SCENARIO OUTLOOK GENERATOR
// --------------------------------------------

export function generateScenarioOutlook(eri: ERIAssessment): Scenario[] {
  return eri.scenarioOutlook;
}

// --------------------------------------------
// COMPLETE BRIEF GENERATOR
// --------------------------------------------

export interface BriefGenerationInput {
  weekNumber: number;
  year: number;
  eriAssessment: ERIAssessment;
  previousERI?: ERIAssessment;
  customDevelopments?: Partial<KeyDevelopment>[];
  version?: string;
}

export function generateWeeklyBrief(input: BriefGenerationInput): WeeklyBrief {
  const executiveSummary = generateExecutiveSummary(input.eriAssessment, input.previousERI);
  const energyWatch = generateEnergyWatch(input.eriAssessment);
  const stakeholderPositions = generateStakeholderPositions(input.eriAssessment);
  const scenarioOutlook = generateScenarioOutlook(input.eriAssessment);

  // Use provided developments or default to ERI developments
  const keyDevelopments = input.customDevelopments && input.customDevelopments.length > 0
    ? input.customDevelopments.map((kd, i) => ({
        id: `kd${i}`,
        headline: kd.headline || `Development ${i + 1}`,
        whatHappened: kd.whatHappened || '',
        whyItMatters: kd.whyItMatters || '',
        whoBenefits: kd.whoBenefits || '',
        whoLoses: kd.whoLoses || '',
        escalationImpact: kd.escalationImpact || 5,
      }))
    : input.eriAssessment.keyDevelopments;

  return {
    id: `brief-${input.year}-${input.weekNumber}`,
    weekNumber: input.weekNumber,
    year: input.year,
    title: BRIEF_TEMPLATES.coverPage.title,
    subtitle: BRIEF_TEMPLATES.coverPage.subtitle,
    eriScore: input.eriAssessment.overallScore,
    version: input.version || '1.0',
    releaseDate: new Date().toISOString(),
    executiveSummary,
    eriSection: input.eriAssessment,
    keyDevelopments,
    energyWatch,
    stakeholderPositions,
    scenarioOutlook,
    indicatorsToWatch: input.eriAssessment.indicatorsToWatch,
    methodology: `This brief uses the Escalation Risk Index (ERI) framework, assessing five dimensions: Military (25%), Political (25%), Proxy (20%), Economic (15%), and Diplomatic (15%). Scores range from 0-100, with classifications: Low (<20), Moderate (20-40), Elevated (40-60), High (60-80), Critical (>80). Analysis is based on open-source intelligence and does not predict specific outcomes.`,
  };
}

// --------------------------------------------
// HTML BRIEF RENDERER (for preview)
// --------------------------------------------

export function renderBriefToHTML(brief: WeeklyBrief): string {
  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>${brief.title} - Week ${brief.weekNumber}</title>
  <style>
    body {
      font-family: 'Georgia', serif;
      line-height: 1.6;
      color: #1a1a1a;
      max-width: 800px;
      margin: 0 auto;
      padding: 40px;
    }
    .cover {
      text-align: center;
      padding: 60px 0;
      border-bottom: 3px solid #0B1F3A;
      margin-bottom: 40px;
    }
    .cover h1 {
      font-size: 28px;
      color: #0B1F3A;
      margin-bottom: 10px;
    }
    .cover .subtitle {
      font-size: 14px;
      color: #5A6A7A;
      margin-bottom: 20px;
    }
    .cover .meta {
      font-size: 12px;
      color: #666;
    }
    .eri-badge {
      display: inline-block;
      padding: 15px 30px;
      background: ${getERIColor(brief.eriScore)};
      color: white;
      font-size: 24px;
      font-weight: bold;
      border-radius: 8px;
      margin: 20px 0;
    }
    h2 {
      color: #0B1F3A;
      border-bottom: 2px solid #C7A84A;
      padding-bottom: 10px;
      margin-top: 40px;
    }
    h3 {
      color: #5A6A7A;
      margin-top: 25px;
    }
    .executive-summary {
      background: #f8f9fa;
      padding: 20px;
      border-left: 4px solid #0B1F3A;
      margin: 20px 0;
    }
    .dimension-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 15px;
      margin: 20px 0;
    }
    .dimension-card {
      background: #f8f9fa;
      padding: 15px;
      border-radius: 6px;
    }
    .dimension-card h4 {
      margin: 0 0 10px 0;
      color: #0B1F3A;
    }
    .score-bar {
      height: 8px;
      background: #e0e0e0;
      border-radius: 4px;
      overflow: hidden;
    }
    .score-fill {
      height: 100%;
      background: ${getERIColor(brief.eriScore)};
      transition: width 0.3s;
    }
    .development {
      background: #fff;
      border: 1px solid #e0e0e0;
      padding: 20px;
      margin: 15px 0;
      border-radius: 6px;
    }
    .development h4 {
      color: #0B1F3A;
      margin-top: 0;
    }
    .stakeholder-table {
      width: 100%;
      border-collapse: collapse;
      margin: 20px 0;
    }
    .stakeholder-table th,
    .stakeholder-table td {
      padding: 12px;
      text-align: left;
      border-bottom: 1px solid #e0e0e0;
    }
    .stakeholder-table th {
      background: #0B1F3A;
      color: white;
    }
    .scenario {
      padding: 15px;
      margin: 10px 0;
      border-left: 4px solid #C7A84A;
      background: #f8f9fa;
    }
    .scenario.probability-high {
      border-left-color: #ef4444;
    }
    .scenario.probability-moderate {
      border-left-color: #eab308;
    }
    .scenario.probability-low {
      border-left-color: #22c55e;
    }
    .indicators-list {
      list-style: none;
      padding: 0;
    }
    .indicators-list li {
      padding: 8px 0;
      border-bottom: 1px dotted #e0e0e0;
    }
    .indicators-list li:before {
      content: "→ ";
      color: #C7A84A;
      font-weight: bold;
    }
    .methodology {
      font-size: 11px;
      color: #666;
      border-top: 1px solid #e0e0e0;
      padding-top: 20px;
      margin-top: 40px;
    }
  </style>
</head>
<body>
  <div class="cover">
    <h1>${brief.title}</h1>
    <div class="subtitle">${brief.subtitle}</div>
    <div class="eri-badge">ERI: ${brief.eriScore}</div>
    <div class="meta">
      Week ${brief.weekNumber}, ${brief.year} | Version ${brief.version}<br>
      Released: ${new Date(brief.releaseDate).toLocaleDateString()}
    </div>
  </div>

  <h2>Executive Summary</h2>
  <div class="executive-summary">
    <p><strong>What Changed:</strong> ${brief.executiveSummary.whatChanged}</p>
    <p><strong>What Is Stable:</strong> ${brief.executiveSummary.whatIsStable}</p>
    <p><strong>Risk Increased:</strong> ${brief.executiveSummary.riskIncreased}</p>
    <p><strong>Risk Decreased:</strong> ${brief.executiveSummary.riskDecreased}</p>
    <p><strong>Military Activity:</strong> ${brief.executiveSummary.militaryActivity}</p>
    <p><strong>Proxy Activity:</strong> ${brief.executiveSummary.proxyActivity}</p>
    <p><strong>Diplomatic Track:</strong> ${brief.executiveSummary.diplomaticTrack}</p>
  </div>

  <h2>Escalation Risk Index</h2>
  <div class="dimension-grid">
    ${brief.eriSection.dimensions.map(d => `
      <div class="dimension-card">
        <h4>${d.name} (${d.score})</h4>
        <div class="score-bar">
          <div class="score-fill" style="width: ${d.score}%"></div>
        </div>
      </div>
    `).join('')}
  </div>

  <h2>Key Developments</h2>
  ${brief.keyDevelopments.map(kd => `
    <div class="development">
      <h4>${kd.headline}</h4>
      <p><strong>What Happened:</strong> ${kd.whatHappened}</p>
      <p><strong>Why It Matters:</strong> ${kd.whyItMatters}</p>
      <p><strong>Who Benefits:</strong> ${kd.whoBenefits}</p>
      <p><strong>Who Loses:</strong> ${kd.whoLoses}</p>
      <p><strong>Escalation Impact:</strong> ${kd.escalationImpact}/10</p>
    </div>
  `).join('')}

  <h2>Energy & Economic Watch</h2>
  <p><strong>Oil Movement:</strong> ${brief.energyWatch.oilMovement}</p>
  <p><strong>Shipping Risk:</strong> ${brief.energyWatch.shippingRisk}</p>
  <p><strong>Sanctions Update:</strong> ${brief.energyWatch.sanctionsUpdate}</p>
  <p><strong>Currency Adjustments:</strong> ${brief.energyWatch.currencyAdjustments}</p>
  ${brief.energyWatch.indiaAngle ? `<p><strong>India Angle:</strong> ${brief.energyWatch.indiaAngle}</p>` : ''}

  <h2>Strategic Stakeholder Positioning</h2>
  <table class="stakeholder-table">
    <thead>
      <tr>
        <th>Actor</th>
        <th>Current Position</th>
        <th>Weekly Movement</th>
        <th>Escalation Impact</th>
      </tr>
    </thead>
    <tbody>
      ${brief.stakeholderPositions.map(sp => `
        <tr>
          <td><strong>${sp.actor}</strong></td>
          <td>${sp.currentPosition}</td>
          <td>${sp.weeklyMovement}</td>
          <td>${sp.escalationImpact}/10</td>
        </tr>
      `).join('')}
    </tbody>
  </table>

  <h2>Scenario Outlook</h2>
  ${brief.scenarioOutlook.map(s => `
    <div class="scenario probability-${s.probability}">
      <h4>${s.name} (${s.probability} probability)</h4>
      <p>${s.description}</p>
      <p><strong>Triggers:</strong> ${s.triggers.join(', ')}</p>
    </div>
  `).join('')}

  <h2>Indicators to Watch Next Week</h2>
  <ul class="indicators-list">
    ${brief.indicatorsToWatch.map(i => `<li>${i}</li>`).join('')}
  </ul>

  <div class="methodology">
    <h3>Methodology & Disclaimer</h3>
    <p>${brief.methodology}</p>
    <p><strong>Disclaimer:</strong> This brief is for informational purposes only and does not constitute investment, legal, or policy advice. All analysis is based on open-source information and represents assessments of probability, not predictions of specific outcomes.</p>
  </div>
</body>
</html>
  `;
}

// --------------------------------------------
// PDF GENERATOR (using browser print)
// --------------------------------------------

export function generatePDF(brief: WeeklyBrief): void {
  const html = renderBriefToHTML(brief);
  const printWindow = window.open('', '_blank');
  if (printWindow) {
    printWindow.document.write(html);
    printWindow.document.close();
    printWindow.print();
  }
}

// --------------------------------------------
// BRIEF COMPARISON
// --------------------------------------------

export function compareBriefs(
  current: WeeklyBrief,
  previous: WeeklyBrief
): {
  eriChange: number;
  newDevelopments: number;
  stakeholderShifts: string[];
} {
  const eriChange = current.eriScore - previous.eriScore;

  // Count new developments (by headline comparison)
  const previousHeadlines = new Set(previous.keyDevelopments.map((kd) => kd.headline));
  const newDevelopments = current.keyDevelopments.filter(
    (kd) => !previousHeadlines.has(kd.headline)
  ).length;

  // Identify stakeholder position shifts
  const stakeholderShifts: string[] = [];
  for (const currentPos of current.stakeholderPositions) {
    const previousPos = previous.stakeholderPositions.find(
      (p) => p.actor === currentPos.actor
    );
    if (previousPos) {
      const impactChange = currentPos.escalationImpact - previousPos.escalationImpact;
      if (Math.abs(impactChange) >= 2) {
        stakeholderShifts.push(
          `${currentPos.actor}: ${impactChange > 0 ? 'Increased' : 'Decreased'} impact (${impactChange > 0 ? '+' : ''}${impactChange})`
        );
      }
    }
  }

  return {
    eriChange,
    newDevelopments,
    stakeholderShifts,
  };
}
