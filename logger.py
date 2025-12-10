"""
logger.py - Application-wide logging and audit trail
Logs all loan processing decisions with timestamps and applicant details
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Create logs directory if it doesn't exist
LOG_DIR = Path('logs')
LOG_DIR.mkdir(exist_ok=True)

# Configure standard logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / 'app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class AuditTrail:
    """Maintains audit trail of all loan decisions for compliance."""
    
    AUDIT_FILE = LOG_DIR / 'audit_trail.jsonl'
    
    @staticmethod
    def log_phase_transition(
        phone: Optional[str],
        from_phase: int,
        to_phase: int,
        reason: str = ""
    ):
        """Log when applicant moves to next phase."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'event': 'PHASE_TRANSITION',
            'phone': phone or 'anonymous',
            'from_phase': from_phase,
            'to_phase': to_phase,
            'reason': reason
        }
        AuditTrail._write_entry(entry)
        logger.info(f"Phase {from_phase} → {to_phase} for {phone}: {reason}")
    
    @staticmethod
    def log_verification(
        phone: str,
        found: bool,
        credit_score: Optional[int] = None
    ):
        """Log CRM verification attempt."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'event': 'VERIFICATION',
            'phone': phone,
            'found': found,
            'credit_score': credit_score
        }
        AuditTrail._write_entry(entry)
        status = "✅ Found" if found else "❌ Not Found"
        logger.info(f"Verification {status} for {phone} (Score: {credit_score})")
    
    @staticmethod
    def log_decision(
        phone: str,
        decision: str,
        reason: str,
        requested_amount: float,
        pre_approved_limit: float,
        credit_score: int
    ):
        """Log final loan decision."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'event': 'LOAN_DECISION',
            'phone': phone,
            'decision': decision,
            'reason': reason,
            'requested_amount': requested_amount,
            'pre_approved_limit': pre_approved_limit,
            'credit_score': credit_score
        }
        AuditTrail._write_entry(entry)
        logger.info(
            f"Decision [{decision}] for {phone}: "
            f"Amount ₹{requested_amount:,.0f} "
            f"(Limit: ₹{pre_approved_limit:,.0f}, Score: {credit_score})"
        )
    
    @staticmethod
    def log_document_upload(
        phone: str,
        filename: str,
        fraud_status: str
    ):
        """Log document upload and fraud check."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'event': 'DOCUMENT_UPLOAD',
            'phone': phone,
            'filename': filename,
            'fraud_status': fraud_status
        }
        AuditTrail._write_entry(entry)
        logger.info(f"Document upload: {filename} (Fraud: {fraud_status})")
    
    @staticmethod
    def log_sanction_generated(
        phone: str,
        pdf_path: str,
        amount: float
    ):
        """Log sanction letter generation."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'event': 'SANCTION_GENERATED',
            'phone': phone,
            'pdf_path': pdf_path,
            'amount': amount
        }
        AuditTrail._write_entry(entry)
        logger.info(f"Sanction generated for {phone}: ₹{amount:,.0f}")
    
    @staticmethod
    def log_error(
        phone: Optional[str],
        phase: int,
        error_type: str,
        error_message: str
    ):
        """Log errors during processing."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'event': 'ERROR',
            'phone': phone or 'anonymous',
            'phase': phase,
            'error_type': error_type,
            'error_message': error_message
        }
        AuditTrail._write_entry(entry)
        logger.error(f"[Phase {phase}] {error_type}: {error_message}")
    
    @staticmethod
    def _write_entry(entry: Dict[str, Any]):
        """Append entry to JSONL audit file."""
        try:
            with open(AuditTrail.AUDIT_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"Failed to write audit entry: {e}")


class PerformanceMonitor:
    """Track performance metrics for optimization."""
    
    METRICS_FILE = LOG_DIR / 'metrics.jsonl'
    _timers = {}
    
    @staticmethod
    def start_timer(event_name: str):
        """Start timing an event."""
        PerformanceMonitor._timers[event_name] = datetime.now()
    
    @staticmethod
    def end_timer(event_name: str, metadata: Optional[Dict] = None):
        """End timing and log duration."""
        if event_name not in PerformanceMonitor._timers:
            logger.warning(f"Timer {event_name} was never started")
            return
        
        start_time = PerformanceMonitor._timers.pop(event_name)
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        entry = {
            'timestamp': datetime.now().isoformat(),
            'event': event_name,
            'duration_ms': duration_ms,
            'metadata': metadata or {}
        }
        
        try:
            with open(PerformanceMonitor.METRICS_FILE, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            logger.error(f"Failed to write metric: {e}")
        
        if duration_ms > 1000:  # Log slow operations
            logger.warning(f"{event_name} took {duration_ms:.0f}ms (slow)")


# Helper functions for common logging patterns
def log_conversation_start(phone: Optional[str] = None):
    """Log start of new conversation."""
    logger.info(f"=== New Conversation Started (Phone: {phone or 'Anonymous'}) ===")


def log_conversation_end(phone: Optional[str], decision: str):
    """Log end of conversation with final decision."""
    logger.info(f"=== Conversation Ended (Phone: {phone}) - Final Decision: {decision} ===")


def log_phase_message(phase: int, message: str):
    """Log phase-specific messages for debugging."""
    phase_names = {1: "Sales", 2: "Underwriting", 3: "Conditional", 4: "Sanction"}
    logger.debug(f"[Phase {phase}: {phase_names.get(phase)}] {message}")
