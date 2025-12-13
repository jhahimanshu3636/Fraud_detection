from neo4j import GraphDatabase
from typing import Dict, List, Any, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FraudDetectionEngine:
    """Production fraud detection engine - 100% schema compatible."""
    
    def __init__(self, uri: str, user: str, password: str = None):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()

    def detect_shell_companies_for_company(self, company_id: str, min_chain_length: int = 4, max_invoices: int = 2) -> Dict[str, Any]:
        """Pattern 1: Shell company chains - FIXED SYNTAX."""
        logger.info(f"PATTERN 1: Detecting shell chains for {company_id}")
        
        query = """
        MATCH (auditor:Auditor {risk_level: 'HIGH'})
        MATCH (company:Company)-[:AUDITED_BY]->(auditor)
        MATCH path=(company)-[:SUBSIDIARY_OF*3..10]->(root:Company)
        WHERE ALL(n IN nodes(path) WHERE exists((n)-[:AUDITED_BY]->(:Auditor)))
        WITH DISTINCT auditor, nodes(path) AS chain
        WHERE size(chain) >= $min_chain_length
        UNWIND chain AS comp
        OPTIONAL MATCH (comp)-[:ISSUES_TO]->(inv:Invoice)
        WITH auditor, chain, comp.company_id AS companyId, count(inv) AS invoiceCount
        WITH auditor, chain, collect([companyId, invoiceCount]) AS stats
        WHERE ALL(s IN stats WHERE s[1] <= $max_invoices)
        WITH auditor, chain, stats,
             reduce(total=0, s IN stats | total + s[1]) AS totalInvoices,
             size(chain) AS chainLength
        RETURN auditor.auditor_id AS auditorId,
               auditor.risk_level AS riskLevel,
               [c IN chain | c.company_id] AS chain,
               stats AS companyDetails,
               chainLength, totalInvoices,
               toFloat(totalInvoices)/chainLength AS avgInvoices
        ORDER BY chainLength DESC, avgInvoices ASC
        """
        
        patterns: List[Dict[str, Any]] = []
        with self.driver.session() as session:
            result = session.run(query, min_chain_length=min_chain_length, max_invoices=max_invoices)
            for record in result:
                pattern = {
                    'auditorId': record['auditorId'],
                    'riskLevel': record['riskLevel'],
                    'chain': record['chain'],
                    'chainLength': record['chainLength'],
                    'totalInvoices': record['totalInvoices'],
                    'avgInvoices': round(record['avgInvoices'], 2),
                    'companyDetails': record['companyDetails'],
                    'riskScore': 0.95
                }
                if company_id in pattern['chain']:
                    patterns.append(pattern)
        
        logger.info(f"Pattern 1: Found {len(patterns)} shell chains for {company_id}")
        return {'patterns': patterns, 'riskScore': 0.95 if patterns else 0.0}

    def detect_circular_trade_for_company(self, company_id: str, min_volume: int = 80) -> Dict[str, Any]:
        """Pattern 2: Circular trade cycles - PRODUCTION READY."""
        logger.info(f"PATTERN 2: Detecting circular trade for {company_id}")
        
        base_query = """
        MATCH (c1:Company)-[r1:SUPPLIES]->(c2:Company)
        MATCH (c2)-[r2:SUPPLIES]->(c3:Company) 
        MATCH (c3)-[r3:SUPPLIES]->(c1)
        WHERE c1 <> c2 AND c2 <> c3 AND c1 <> c3
          AND r1.annual_volume >= $min_volume
          AND r2.annual_volume >= $min_volume  
          AND r3.annual_volume >= $min_volume
        WITH [c1.company_id, c2.company_id, c3.company_id] AS cycle,
             [r1.annual_volume, r2.annual_volume, r3.annual_volume] AS volumes
        WITH cycle, reduce(total=0.0, v IN volumes | total + v) AS totalVolume
        OPTIONAL MATCH (comp:Company) WHERE comp.company_id IN cycle
        OPTIONAL MATCH (comp)-[:SUPPLIES]->(ext:Company)
        WHERE NOT ext.company_id IN cycle
        WITH cycle, totalVolume, size(cycle) AS cycleLength,
             count(DISTINCT ext) AS externalConnections
        RETURN cycle, cycleLength, totalVolume,
               totalVolume/cycleLength AS avgVolume,
               externalConnections,
               toFloat(cycleLength)/(cycleLength + externalConnections + 1) AS isolationScore
        ORDER BY isolationScore DESC, avgVolume DESC LIMIT 100
        """
        
        all_patterns: List[Dict[str, Any]] = []
        seen_cycles = set()
        
        with self.driver.session() as session:
            result = session.run(base_query, min_volume=min_volume)
            for record in result:
                cycle_sig = tuple(sorted(record['cycle']))
                if cycle_sig in seen_cycles: continue
                seen_cycles.add(cycle_sig)
                all_patterns.append({
                    'cycle': record['cycle'],
                    'cycleLength': record['cycleLength'],
                    'totalVolume': float(record['totalVolume']),
                    'avgVolume': round(record['avgVolume'], 2),
                    'externalConnections': record['externalConnections'],
                    'isolationScore': round(record['isolationScore'], 3),
                    'riskScore': min(0.95, 0.80 + 0.15 * record['isolationScore'])
                })
        
        target_patterns = [p for p in all_patterns if company_id in p['cycle']]
        logger.info(f"Pattern 2: Found {len(target_patterns)} cycles for {company_id}")
        risk_score = max([p['riskScore'] for p in target_patterns], default=0.0)
        return {'patterns': target_patterns, 'riskScore': risk_score}

    def calculate_shareholder_influence_pagerank(self) -> Dict[str, float]:
        """Pattern 3: PageRank influence - PRODUCTION GDS."""
        logger.info("PATTERN 3: Calculating PageRank")
        influences = {}
        
        with self.driver.session() as session:
            # Drop graph if it exists
            session.run("CALL gds.graph.drop('ownership', false)")
            
            # Create graph projection with correct syntax
            session.run("""
            CALL gds.graph.project(
                'ownership',
                'Shareholder',
                {
                    OWNS_SHARE: {
                        type: 'OWNS_SHARE',
                        properties: 'percentage'
                    }
                }
            )
            """)
            
            # Run PageRank
            result = session.run("""
            CALL gds.pageRank.stream('ownership', {
                maxIterations: 20,
                relationshipWeightProperty: 'percentage'
            })
            YIELD nodeId, score
            WITH gds.util.asNode(nodeId) AS node, score
            WHERE score > 0.01
            RETURN node.shareholder_id AS shareholderId, score
            ORDER BY score DESC
            """)
            
            for record in result:
                influences[record['shareholderId']] = record['score']
            
            # Clean up
            session.run("CALL gds.graph.drop('ownership', false)")
        
        logger.info(f"PageRank: {len(influences)} influential shareholders")
        return influences

    def detect_hidden_influence_for_company(self, company_id: str, min_ownership: float = 25.0, min_concentration: float = 80.0) -> Dict[str, Any]:
        """Pattern 3: Hidden shareholder influence."""
        logger.info(f"PATTERN 3: Hidden influence for {company_id}")
        influence_scores = self.calculate_shareholder_influence_pagerank()
        
        query = """
        MATCH (sh:Shareholder)-[owns:OWNS_SHARE]->(supplier:Company)
        WHERE owns.percentage >= $min_ownership
        MATCH (supplier)-[:SUPPLIES]->(target:Company {company_id: $target_company_id})
        MATCH (supplier)-[:ISSUES_TO]->(inv1:Invoice)<-[:PAYS]-(target)
        WITH sh, supplier, target, owns.percentage AS ownershipPct,
             count(DISTINCT inv1) AS supplierInvoices
        MATCH (target)-[:PAYS]->(inv2:Invoice)
        WITH sh, supplier, target, ownershipPct, supplierInvoices,
             count(DISTINCT inv2) AS totalInvoices
        WHERE toFloat(supplierInvoices)/totalInvoices*100 >= $min_concentration
        AND NOT (sh)-[:SUPPLIES]->(target)
        RETURN sh.shareholder_id AS shareholderId,
               sh.name AS shareholderName,
               sh.type AS shareholderType,
               supplier.company_id AS supplierId,
               supplier.name AS supplierName,
               target.company_id AS targetId,
               target.name AS targetName,
               ownershipPct, supplierInvoices, totalInvoices,
               toFloat(supplierInvoices)/totalInvoices*100 AS concentrationPct
        ORDER BY concentrationPct DESC LIMIT 50
        """
        
        patterns = []
        with self.driver.session() as session:
            result = session.run(query, target_company_id=company_id, 
                               min_ownership=min_ownership, min_concentration=min_concentration)
            for record in result:
                sh_id = record['shareholderId']
                infl = influence_scores.get(sh_id, 0.1)
                opportunity = 0.7 * infl + 0.3 * min(record['ownershipPct']/50, 1.0) + 0.3 * (record['concentrationPct']/100)
                
                patterns.append({
                    **record,
                    'influenceScore': round(infl, 3),
                    'opportunityScore': round(opportunity, 3),
                    'ownershipPct': round(record['ownershipPct'], 2),
                    'concentrationPct': round(record['concentrationPct'], 2)
                })
        
        logger.info(f"Pattern 3: Found {len(patterns)} hidden patterns for {company_id}")
        return {'patterns': patterns, 'opportunityScore': max([p['opportunityScore'] for p in patterns], default=0.0)}

    def analyze_company(self, company_id: str) -> Tuple[float, float, Dict[str, Any]]:
        """Execute all 3 patterns."""
        shell_result = self.detect_shell_companies_for_company(company_id)
        circular_result = self.detect_circular_trade_for_company(company_id)
        hidden_result = self.detect_hidden_influence_for_company(company_id)
        
        risk_score = max(shell_result['riskScore'], circular_result['riskScore'])
        patterns = {
            'pattern1_shell': shell_result['patterns'],
            'pattern2_circular': circular_result['patterns'],
            'pattern3_hidden': hidden_result['patterns']
        }
        
        return risk_score, hidden_result['opportunityScore'], patterns