 # DataHerd Core Module
"""
DataHerd - Intelligent Cattle Data Cleaning Agent

This module contains the core business logic for the DataHerd system,
including natural language processing, data cleaning, rule management,
and report generation capabilities.
"""

__version__ = "1.0.0"
__author__ = "DataHerd Team"

from .nlp_processor import NLPProcessor, ParsedRule, RuleType
from .data_processor import DataProcessor
from .rule_manager import RuleManager
from .report_generator import ReportGenerator

__all__ = [
    'NLPProcessor',
    'ParsedRule', 
    'RuleType',
    'DataProcessor',
    'RuleManager',
    'ReportGenerator'
]