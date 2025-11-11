"""
Report generators - Convert AnalysisResult findings into structured reports.
"""

from .report import Report, generate_report
from .corpus_report import CorpusAnalysisReport, generate_corpus_report
from .audit_grid import generate_audit_grid

__all__ = ["Report", "generate_report", "CorpusAnalysisReport", "generate_corpus_report", "generate_audit_grid"]
