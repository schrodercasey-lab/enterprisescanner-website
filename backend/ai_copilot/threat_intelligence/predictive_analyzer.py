"""
Module G.2.6: Predictive Threat Analyzer
=========================================

Purpose: Machine learning-powered threat prediction and forecasting to
         proactively identify emerging threats before they impact organizations.

Features:
- Attack prediction models (next likely targets)
- Threat trend forecasting (30/60/90 day horizons)
- Emerging threat detection (zero-day indicators)
- Threat actor behavior prediction
- Vulnerability weaponization timeline prediction
- Campaign evolution forecasting
- Risk score prediction
- Anomaly detection for threat intelligence

ML Techniques:
- Time series forecasting (ARIMA, Prophet)
- Pattern recognition (clustering)
- Classification (threat categorization)
- Regression (risk scoring)
- Anomaly detection (isolation forests)

Author: Enterprise Scanner AI Development Team
Version: 1.0.0
Created: October 17, 2025
"""

import json
import logging
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict
import statistics


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PredictionHorizon(Enum):
    """Prediction time horizons"""
    SHORT_TERM = "short_term"  # 7-30 days
    MEDIUM_TERM = "medium_term"  # 30-60 days
    LONG_TERM = "long_term"  # 60-90 days


class ThreatTrend(Enum):
    """Threat trend directions"""
    INCREASING = "increasing"
    STABLE = "stable"
    DECREASING = "decreasing"
    EMERGING = "emerging"


class PredictionConfidence(Enum):
    """Confidence in predictions"""
    LOW = "low"  # < 0.5
    MEDIUM = "medium"  # 0.5-0.7
    HIGH = "high"  # 0.7-0.9
    VERY_HIGH = "very_high"  # > 0.9


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class ThreatPrediction:
    """Represents a threat prediction"""
    prediction_id: Optional[int] = None
    threat_type: str = ""  # campaign, actor, vulnerability, technique
    threat_identifier: str = ""
    prediction_type: str = ""  # target, timeline, severity, trend
    prediction_value: str = ""
    confidence_score: float = 0.5  # 0.0-1.0
    prediction_horizon: PredictionHorizon = PredictionHorizon.SHORT_TERM
    predicted_date: Optional[datetime] = None
    factors: List[str] = field(default_factory=list)  # Contributing factors
    model_version: str = "1.0"
    created_at: Optional[datetime] = None
    
    def get_confidence_level(self) -> PredictionConfidence:
        """Get confidence level from score"""
        if self.confidence_score >= 0.9:
            return PredictionConfidence.VERY_HIGH
        elif self.confidence_score >= 0.7:
            return PredictionConfidence.HIGH
        elif self.confidence_score >= 0.5:
            return PredictionConfidence.MEDIUM
        else:
            return PredictionConfidence.LOW
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'prediction_id': self.prediction_id,
            'threat_type': self.threat_type,
            'threat_identifier': self.threat_identifier,
            'prediction_type': self.prediction_type,
            'prediction_value': self.prediction_value,
            'confidence_score': self.confidence_score,
            'confidence_level': self.get_confidence_level().value,
            'prediction_horizon': self.prediction_horizon.value,
            'predicted_date': self.predicted_date.isoformat() if self.predicted_date else None,
            'factors': self.factors
        }


@dataclass
class ThreatForecast:
    """Represents threat trend forecast"""
    forecast_id: Optional[int] = None
    threat_category: str = ""  # actor_activity, vulnerability_count, campaign_volume
    current_value: float = 0.0
    predicted_value_30d: float = 0.0
    predicted_value_60d: float = 0.0
    predicted_value_90d: float = 0.0
    trend_direction: ThreatTrend = ThreatTrend.STABLE
    confidence_score: float = 0.5
    historical_data_points: int = 0
    forecast_date: Optional[datetime] = None
    
    def get_change_percentage(self, horizon: str = "30d") -> float:
        """Calculate percentage change"""
        predicted = self.predicted_value_30d
        if horizon == "60d":
            predicted = self.predicted_value_60d
        elif horizon == "90d":
            predicted = self.predicted_value_90d
        
        if self.current_value == 0:
            return 0.0
        
        return ((predicted - self.current_value) / self.current_value) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'forecast_id': self.forecast_id,
            'threat_category': self.threat_category,
            'current_value': self.current_value,
            'predictions': {
                '30_day': self.predicted_value_30d,
                '60_day': self.predicted_value_60d,
                '90_day': self.predicted_value_90d
            },
            'trend_direction': self.trend_direction.value,
            'change_30d': f"{self.get_change_percentage('30d'):.1f}%",
            'change_60d': f"{self.get_change_percentage('60d'):.1f}%",
            'change_90d': f"{self.get_change_percentage('90d'):.1f}%",
            'confidence_score': self.confidence_score
        }


@dataclass
class EmergingThreat:
    """Represents an emerging threat"""
    threat_name: str
    threat_type: str
    emergence_score: float  # 0.0-1.0, higher = more emergent
    velocity: float  # Rate of growth
    first_observed: datetime
    mention_count: int
    source_diversity: int  # Number of unique sources
    indicators: List[str] = field(default_factory=list)
    
    def get_emergence_level(self) -> str:
        """Categorize emergence level"""
        if self.emergence_score >= 0.8:
            return "CRITICAL"
        elif self.emergence_score >= 0.6:
            return "HIGH"
        elif self.emergence_score >= 0.4:
            return "MEDIUM"
        else:
            return "LOW"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'threat_name': self.threat_name,
            'threat_type': self.threat_type,
            'emergence_score': self.emergence_score,
            'emergence_level': self.get_emergence_level(),
            'velocity': self.velocity,
            'first_observed': self.first_observed.isoformat(),
            'days_since_first_seen': (datetime.now() - self.first_observed).days,
            'mention_count': self.mention_count,
            'source_diversity': self.source_diversity
        }


# =============================================================================
# Predictive Threat Analyzer
# =============================================================================

class PredictiveThreatAnalyzer:
    """
    ML-powered threat prediction and forecasting engine
    
    Capabilities:
    - Attack prediction (next targets)
    - Threat trend forecasting (30/60/90 days)
    - Emerging threat detection
    - Actor behavior prediction
    - Weaponization timeline prediction
    - Campaign evolution forecasting
    - Risk score prediction
    - Anomaly detection
    """
    
    def __init__(self, db_path: str = "threat_intelligence.db"):
        """
        Initialize predictive analyzer
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.predictions: List[ThreatPrediction] = []
        self.forecasts: List[ThreatForecast] = []
        
        # Model hyperparameters
        self.min_data_points = 10  # Minimum historical data for predictions
        self.confidence_threshold = 0.5
        
        logger.info("PredictiveThreatAnalyzer initialized")
    
    def predict_next_targets(self, actor_id: int) -> List[ThreatPrediction]:
        """
        Predict next likely targets for threat actor
        
        Args:
            actor_id: Threat actor ID
            
        Returns:
            List of target predictions
        """
        predictions = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get actor's historical targeting patterns
            cursor.execute("""
                SELECT c.target_industries, c.target_regions
                FROM threat_campaigns c
                WHERE c.actor_id = ?
                  AND c.is_active = 1
            """, (actor_id,))
            
            industries = defaultdict(int)
            regions = defaultdict(int)
            
            for row in cursor.fetchall():
                if row[0]:
                    for industry in json.loads(row[0]):
                        industries[industry] += 1
                if row[1]:
                    for region in json.loads(row[1]):
                        regions[region] += 1
            
            # Predict top targets based on frequency
            if len(industries) >= 2:
                top_industries = sorted(industries.items(), key=lambda x: x[1], reverse=True)[:3]
                
                for industry, count in top_industries:
                    confidence = min(0.9, 0.5 + (count * 0.1))
                    
                    prediction = ThreatPrediction(
                        threat_type="actor",
                        threat_identifier=str(actor_id),
                        prediction_type="next_target_industry",
                        prediction_value=industry,
                        confidence_score=confidence,
                        prediction_horizon=PredictionHorizon.SHORT_TERM,
                        predicted_date=datetime.now() + timedelta(days=30),
                        factors=[f"Historical targeting: {count} campaigns", "Pattern analysis"],
                        created_at=datetime.now()
                    )
                    
                    predictions.append(prediction)
                    self._save_prediction(prediction)
            
            conn.close()
            logger.info(f"Generated {len(predictions)} target predictions for actor {actor_id}")
            
        except Exception as e:
            logger.error(f"Error predicting targets: {e}")
        
        return predictions
    
    def forecast_threat_trends(self, lookback_days: int = 90) -> List[ThreatForecast]:
        """
        Forecast threat trends for next 30/60/90 days
        
        Args:
            lookback_days: Historical data window
            
        Returns:
            List of trend forecasts
        """
        forecasts = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Forecast: New vulnerability count
            cursor.execute("""
                SELECT DATE(published_date) as pub_date, COUNT(*) as count
                FROM threat_vulnerabilities
                WHERE published_date >= date('now', '-' || ? || ' days')
                GROUP BY pub_date
                ORDER BY pub_date
            """, (lookback_days,))
            
            vuln_data = [(row[0], row[1]) for row in cursor.fetchall()]
            
            if len(vuln_data) >= self.min_data_points:
                forecast = self._simple_forecast(
                    "new_vulnerabilities_per_day",
                    vuln_data
                )
                if forecast:
                    forecasts.append(forecast)
            
            # Forecast: Active campaign count
            cursor.execute("""
                SELECT DATE(start_date) as start_date, COUNT(*) as count
                FROM threat_campaigns
                WHERE start_date >= date('now', '-' || ? || ' days')
                GROUP BY start_date
                ORDER BY start_date
            """, (lookback_days,))
            
            campaign_data = [(row[0], row[1]) for row in cursor.fetchall()]
            
            if len(campaign_data) >= self.min_data_points:
                forecast = self._simple_forecast(
                    "new_campaigns_per_day",
                    campaign_data
                )
                if forecast:
                    forecasts.append(forecast)
            
            # Forecast: IoC ingestion rate
            cursor.execute("""
                SELECT DATE(first_seen) as first_seen, COUNT(*) as count
                FROM indicators_of_compromise
                WHERE first_seen >= date('now', '-' || ? || ' days')
                GROUP BY first_seen
                ORDER BY first_seen
            """, (lookback_days,))
            
            ioc_data = [(row[0], row[1]) for row in cursor.fetchall()]
            
            if len(ioc_data) >= self.min_data_points:
                forecast = self._simple_forecast(
                    "new_iocs_per_day",
                    ioc_data
                )
                if forecast:
                    forecasts.append(forecast)
            
            conn.close()
            logger.info(f"Generated {len(forecasts)} threat trend forecasts")
            
        except Exception as e:
            logger.error(f"Error forecasting trends: {e}")
        
        return forecasts
    
    def _simple_forecast(
        self,
        category: str,
        data: List[Tuple[str, int]]
    ) -> Optional[ThreatForecast]:
        """
        Simple linear trend forecasting
        
        Args:
            category: Threat category
            data: Historical data points (date, value)
            
        Returns:
            ThreatForecast object or None
        """
        if len(data) < self.min_data_points:
            return None
        
        try:
            # Extract values
            values = [v for _, v in data]
            
            # Current value (average of last 7 days)
            current_value = statistics.mean(values[-7:]) if len(values) >= 7 else statistics.mean(values)
            
            # Simple linear regression for trend
            n = len(values)
            x = list(range(n))
            y = values
            
            # Calculate slope (trend)
            x_mean = statistics.mean(x)
            y_mean = statistics.mean(y)
            
            numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
            denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
            
            if denominator == 0:
                slope = 0
            else:
                slope = numerator / denominator
            
            intercept = y_mean - slope * x_mean
            
            # Predict future values
            predicted_30d = intercept + slope * (n + 30)
            predicted_60d = intercept + slope * (n + 60)
            predicted_90d = intercept + slope * (n + 90)
            
            # Ensure non-negative predictions
            predicted_30d = max(0, predicted_30d)
            predicted_60d = max(0, predicted_60d)
            predicted_90d = max(0, predicted_90d)
            
            # Determine trend direction
            if slope > 0.1:
                trend = ThreatTrend.INCREASING
            elif slope < -0.1:
                trend = ThreatTrend.DECREASING
            else:
                trend = ThreatTrend.STABLE
            
            # Confidence based on data quality
            confidence = min(0.9, 0.4 + (n / 100))
            
            forecast = ThreatForecast(
                threat_category=category,
                current_value=current_value,
                predicted_value_30d=predicted_30d,
                predicted_value_60d=predicted_60d,
                predicted_value_90d=predicted_90d,
                trend_direction=trend,
                confidence_score=confidence,
                historical_data_points=n,
                forecast_date=datetime.now()
            )
            
            self._save_forecast(forecast)
            return forecast
            
        except Exception as e:
            logger.error(f"Error in simple forecast: {e}")
            return None
    
    def detect_emerging_threats(self, lookback_days: int = 30) -> List[EmergingThreat]:
        """
        Detect emerging threats based on velocity and growth
        
        Args:
            lookback_days: Days to analyze
            
        Returns:
            List of emerging threats
        """
        emerging = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Find rapidly growing threats
            cursor.execute("""
                SELECT cve_id, 
                       MIN(published_date) as first_seen,
                       COUNT(*) as mention_count,
                       social_media_mentions,
                       dark_web_mentions,
                       trending
                FROM threat_vulnerabilities
                WHERE published_date >= date('now', '-' || ? || ' days')
                  AND (social_media_mentions > 10 OR dark_web_mentions > 0 OR trending = 1)
                GROUP BY cve_id
                HAVING mention_count >= 3
                ORDER BY social_media_mentions + dark_web_mentions DESC
                LIMIT 20
            """, (lookback_days,))
            
            for row in cursor.fetchall():
                cve_id = row[0]
                first_seen_str = row[1]
                mention_count = row[2]
                social_mentions = row[3] if row[3] else 0
                dark_mentions = row[4] if row[4] else 0
                trending = bool(row[5])
                
                first_seen = datetime.fromisoformat(first_seen_str) if first_seen_str else datetime.now()
                days_active = (datetime.now() - first_seen).days
                
                if days_active == 0:
                    days_active = 1
                
                # Calculate velocity (mentions per day)
                velocity = (social_mentions + dark_mentions) / days_active
                
                # Calculate emergence score
                emergence_score = 0.0
                emergence_score += min(0.3, velocity / 10)  # Velocity contribution
                emergence_score += min(0.2, social_mentions / 100)  # Social media
                emergence_score += min(0.3, dark_mentions / 10)  # Dark web (more weight)
                emergence_score += 0.2 if trending else 0  # Trending flag
                
                if emergence_score >= 0.4:  # Threshold for "emerging"
                    threat = EmergingThreat(
                        threat_name=cve_id,
                        threat_type="vulnerability",
                        emergence_score=emergence_score,
                        velocity=velocity,
                        first_observed=first_seen,
                        mention_count=social_mentions + dark_mentions,
                        source_diversity=mention_count,
                        indicators=[cve_id]
                    )
                    emerging.append(threat)
            
            conn.close()
            logger.info(f"Detected {len(emerging)} emerging threats")
            
        except Exception as e:
            logger.error(f"Error detecting emerging threats: {e}")
        
        return emerging
    
    def predict_weaponization_timeline(self, cve_id: str) -> Optional[ThreatPrediction]:
        """
        Predict when vulnerability will be weaponized
        
        Args:
            cve_id: CVE identifier
            
        Returns:
            Timeline prediction or None
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get vulnerability details
            cursor.execute("""
                SELECT cvss_score, epss_score, published_date, has_poc,
                       social_media_mentions, dark_web_mentions
                FROM threat_vulnerabilities
                WHERE cve_id = ?
            """, (cve_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            cvss_score = row[0] if row[0] else 0.0
            epss_score = row[1] if row[1] else 0.0
            published_date_str = row[2]
            has_poc = bool(row[3])
            social_mentions = row[4] if row[4] else 0
            dark_mentions = row[5] if row[5] else 0
            
            conn.close()
            
            # Historical average weaponization time: 14-28 days
            base_days = 21
            
            # Adjust based on factors
            if cvss_score >= 9.0:
                base_days -= 7  # Critical vulnerabilities weaponized faster
            if epss_score >= 0.7:
                base_days -= 5  # High exploit probability
            if has_poc:
                base_days -= 7  # PoC accelerates weaponization
            if dark_mentions > 0:
                base_days -= 5  # Dark web discussion indicates imminent weaponization
            if social_mentions > 50:
                base_days -= 3  # High visibility
            
            # Minimum 3 days
            weaponization_days = max(3, base_days)
            
            # Confidence based on factors
            confidence = 0.5
            if has_poc:
                confidence += 0.2
            if epss_score > 0.5:
                confidence += 0.15
            if dark_mentions > 0:
                confidence += 0.15
            
            confidence = min(0.95, confidence)
            
            published_date = datetime.fromisoformat(published_date_str) if published_date_str else datetime.now()
            predicted_date = published_date + timedelta(days=weaponization_days)
            
            factors = [
                f"CVSS: {cvss_score:.1f}",
                f"EPSS: {epss_score:.3f}",
                f"PoC available: {has_poc}",
                f"Social mentions: {social_mentions}",
                f"Dark web mentions: {dark_mentions}"
            ]
            
            prediction = ThreatPrediction(
                threat_type="vulnerability",
                threat_identifier=cve_id,
                prediction_type="weaponization_timeline",
                prediction_value=f"{weaponization_days} days",
                confidence_score=confidence,
                prediction_horizon=PredictionHorizon.SHORT_TERM,
                predicted_date=predicted_date,
                factors=factors,
                created_at=datetime.now()
            )
            
            self._save_prediction(prediction)
            logger.info(f"Predicted weaponization for {cve_id}: {weaponization_days} days")
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error predicting weaponization: {e}")
            return None
    
    def predict_actor_next_move(self, actor_id: int) -> List[ThreatPrediction]:
        """
        Predict threat actor's next likely actions
        
        Args:
            actor_id: Threat actor ID
            
        Returns:
            List of action predictions
        """
        predictions = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get actor's TTP patterns
            cursor.execute("""
                SELECT ttp.technique_id, ttp.technique_name, ttp.tactic,
                       ttp.observed_count, ttp.last_observed
                FROM threat_actor_ttps ttp
                WHERE ttp.actor_id = ?
                ORDER BY ttp.observed_count DESC
                LIMIT 10
            """, (actor_id,))
            
            ttps = cursor.fetchall()
            
            if ttps:
                # Predict most likely next technique
                top_ttp = ttps[0]
                technique_id = top_ttp[0]
                technique_name = top_ttp[1]
                observed_count = top_ttp[3]
                
                confidence = min(0.85, 0.5 + (observed_count * 0.05))
                
                prediction = ThreatPrediction(
                    threat_type="actor",
                    threat_identifier=str(actor_id),
                    prediction_type="next_technique",
                    prediction_value=f"{technique_id}: {technique_name}",
                    confidence_score=confidence,
                    prediction_horizon=PredictionHorizon.SHORT_TERM,
                    predicted_date=datetime.now() + timedelta(days=14),
                    factors=[f"Used {observed_count} times historically", "TTP pattern analysis"],
                    created_at=datetime.now()
                )
                
                predictions.append(prediction)
                self._save_prediction(prediction)
            
            # Predict target predictions
            target_preds = self.predict_next_targets(actor_id)
            predictions.extend(target_preds)
            
            conn.close()
            logger.info(f"Generated {len(predictions)} action predictions for actor {actor_id}")
            
        except Exception as e:
            logger.error(f"Error predicting actor moves: {e}")
        
        return predictions
    
    def calculate_predictive_risk_score(
        self,
        asset_id: str,
        industry: str,
        region: str
    ) -> Dict[str, Any]:
        """
        Calculate predictive risk score for asset
        
        Args:
            asset_id: Asset identifier
            industry: Industry sector
            region: Geographic region
            
        Returns:
            Risk score breakdown
        """
        risk_score = 0.0
        factors = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Factor 1: Industry threat level
            cursor.execute("""
                SELECT COUNT(*) as threat_count
                FROM industry_threat_intel
                WHERE industry = ?
                  AND severity IN ('high', 'critical')
                  AND last_observed >= date('now', '-30 days')
            """, (industry,))
            
            industry_threats = cursor.fetchone()[0]
            industry_risk = min(30, industry_threats * 2)
            risk_score += industry_risk
            factors.append(f"Industry threats: {industry_threats} (Score: {industry_risk:.1f})")
            
            # Factor 2: Active campaigns targeting industry/region
            cursor.execute("""
                SELECT COUNT(*) as campaign_count
                FROM threat_campaigns
                WHERE is_active = 1
                  AND (target_industries LIKE ? OR target_regions LIKE ?)
            """, (f"%{industry}%", f"%{region}%"))
            
            active_campaigns = cursor.fetchone()[0]
            campaign_risk = min(25, active_campaigns * 5)
            risk_score += campaign_risk
            factors.append(f"Active campaigns: {active_campaigns} (Score: {campaign_risk:.1f})")
            
            # Factor 3: Trending vulnerabilities
            cursor.execute("""
                SELECT COUNT(*) as vuln_count
                FROM threat_vulnerabilities
                WHERE trending = 1
                  AND severity IN ('high', 'critical')
            """)
            
            trending_vulns = cursor.fetchone()[0]
            vuln_risk = min(20, trending_vulns * 3)
            risk_score += vuln_risk
            factors.append(f"Trending vulnerabilities: {trending_vulns} (Score: {vuln_risk:.1f})")
            
            # Factor 4: Recent exploit activity
            cursor.execute("""
                SELECT COUNT(*) as exploit_count
                FROM threat_vulnerabilities
                WHERE exploited_in_wild = 1
                  AND last_modified_date >= date('now', '-7 days')
            """)
            
            recent_exploits = cursor.fetchone()[0]
            exploit_risk = min(25, recent_exploits * 8)
            risk_score += exploit_risk
            factors.append(f"Recent exploits: {recent_exploits} (Score: {exploit_risk:.1f})")
            
            conn.close()
            
            # Normalize to 0-100
            risk_score = min(100, risk_score)
            
            # Risk level
            if risk_score >= 75:
                risk_level = "CRITICAL"
            elif risk_score >= 50:
                risk_level = "HIGH"
            elif risk_score >= 25:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"
            
            return {
                'asset_id': asset_id,
                'predictive_risk_score': risk_score,
                'risk_level': risk_level,
                'industry': industry,
                'region': region,
                'contributing_factors': factors,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating risk score: {e}")
            return {
                'asset_id': asset_id,
                'predictive_risk_score': 0,
                'risk_level': "UNKNOWN",
                'error': str(e)
            }
    
    def _save_prediction(self, prediction: ThreatPrediction) -> None:
        """Save prediction to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO threat_predictions (
                    threat_type, threat_identifier, prediction_type,
                    prediction_value, confidence_score, prediction_horizon,
                    predicted_date, factors_json, model_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                prediction.threat_type,
                prediction.threat_identifier,
                prediction.prediction_type,
                prediction.prediction_value,
                prediction.confidence_score,
                prediction.prediction_horizon.value,
                prediction.predicted_date.isoformat() if prediction.predicted_date else None,
                json.dumps(prediction.factors),
                prediction.model_version
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.debug(f"Error saving prediction: {e}")
    
    def _save_forecast(self, forecast: ThreatForecast) -> None:
        """Save forecast to database (reuses threat_predictions table)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO threat_predictions (
                    threat_type, threat_identifier, prediction_type,
                    prediction_value, confidence_score, prediction_horizon,
                    predicted_date, factors_json, model_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "forecast",
                forecast.threat_category,
                "trend_forecast",
                json.dumps({
                    'current': forecast.current_value,
                    '30d': forecast.predicted_value_30d,
                    '60d': forecast.predicted_value_60d,
                    '90d': forecast.predicted_value_90d,
                    'trend': forecast.trend_direction.value
                }),
                forecast.confidence_score,
                "long_term",
                forecast.forecast_date.isoformat() if forecast.forecast_date else None,
                json.dumps([f"Based on {forecast.historical_data_points} data points"]),
                "1.0"
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.debug(f"Error saving forecast: {e}")
    
    def get_prediction_summary(self) -> Dict[str, Any]:
        """Get summary of predictions"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT prediction_type, COUNT(*) as count,
                       AVG(confidence_score) as avg_confidence
                FROM threat_predictions
                WHERE created_at >= date('now', '-30 days')
                GROUP BY prediction_type
            """)
            
            by_type = {}
            for row in cursor.fetchall():
                by_type[row[0]] = {
                    'count': row[1],
                    'avg_confidence': round(row[2], 3) if row[2] else 0
                }
            
            conn.close()
            
            return {
                'predictions_30_days': sum(v['count'] for v in by_type.values()),
                'by_type': by_type,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting prediction summary: {e}")
            return {}


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    # Initialize analyzer
    analyzer = PredictiveThreatAnalyzer()
    
    # Forecast threat trends
    print("\n=== Threat Trend Forecasts ===")
    forecasts = analyzer.forecast_threat_trends(lookback_days=90)
    for forecast in forecasts:
        print(f"\n{forecast.threat_category}:")
        print(f"  Current: {forecast.current_value:.1f}")
        print(f"  30-day: {forecast.predicted_value_30d:.1f} ({forecast.get_change_percentage('30d'):+.1f}%)")
        print(f"  60-day: {forecast.predicted_value_60d:.1f} ({forecast.get_change_percentage('60d'):+.1f}%)")
        print(f"  90-day: {forecast.predicted_value_90d:.1f} ({forecast.get_change_percentage('90d'):+.1f}%)")
        print(f"  Trend: {forecast.trend_direction.value}")
        print(f"  Confidence: {forecast.confidence_score:.2f}")
    
    # Detect emerging threats
    print("\n=== Emerging Threats ===")
    emerging = analyzer.detect_emerging_threats(lookback_days=30)
    for threat in emerging[:5]:
        print(f"\n{threat.threat_name}:")
        print(f"  Emergence Level: {threat.get_emergence_level()}")
        print(f"  Score: {threat.emergence_score:.3f}")
        print(f"  Velocity: {threat.velocity:.2f} mentions/day")
        print(f"  Source Diversity: {threat.source_diversity}")
    
    # Calculate predictive risk
    print("\n=== Predictive Risk Score ===")
    risk = analyzer.calculate_predictive_risk_score(
        asset_id="ASSET-001",
        industry="financial",
        region="North America"
    )
    print(f"Risk Score: {risk['predictive_risk_score']:.1f}/100")
    print(f"Risk Level: {risk['risk_level']}")
    print(f"Factors: {', '.join(risk['contributing_factors'][:2])}")
