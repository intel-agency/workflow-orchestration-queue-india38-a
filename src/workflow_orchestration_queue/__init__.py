"""
OS-APOW Workflow Orchestration Queue

A headless agentic orchestration platform that transforms GitHub Issues
into autonomous execution orders.

Architecture: 4-pillar design
- EAR: Event reception (FastAPI webhooks)
- STATE: State management (GitHub Issues + Labels)
- BRAIN: Decision/orchestration (Sentinel)
- HANDS: Action execution (Worker)
"""

__version__ = "0.1.0"
__author__ = "Intel Agency"
