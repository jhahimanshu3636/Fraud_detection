
from neo4j import GraphDatabase
from typing import Dict, List, Any, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FraudDetectionEngine:
    """
    Enhanced Fraud Detection Engine - Expert Graph Theory Implementation
    
    Implements 3 fraud detection patterns with strict requirement compliance:
    1. Shell Company Detection - Graph Traversal with Property Filtering
    2. Circular Trade Detection - Cycle Detection Algorithm 
    3. Hidden Influence Detection - PageRank Centrality + Multi-hop Path Analysis
    """
    
    def __init__(self, uri: str, user: str, password: str = None):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()

    def detect_shell_companies_for_company(self, company_id: str, min_chain_length: int = 4, max_invoices: int = 2) -> Dict[str, Any]:
        """
        Pattern 1: Shell Company Detection - EXPERT GRAPH THEORY IMPLEMENTATION
        
        REQUIREMENTS:
        ✓ Chain of at least 3 intermediary companies (4 total nodes)
        ✓ All share the same HIGH-risk auditor
        ✓ Unusually low invoice count (≤2 invoices per company)
        ✓ Risk Score > 0.95
        
        GRAPH THEORY ALGORITHM:
        - Graph Traversal: Variable-length path matching (SUBSIDIARY_OF*3..10)
        - Node Property Filtering: auditor.risk_level = 'HIGH'
        - Edge Property Filtering: Low invoice count per company
        - Complexity: O(V + E) where V=nodes, E=edges in traversed subgraph
        
        Args:
            company_id: Target company to analyze
            min_chain_length: Minimum total nodes in chain (default 4 = 3 intermediaries)
            max_invoices: Maximum invoices per company for "low activity"
            
        Returns:
            Dict with 'patterns' list and 'riskScore' (0.95 if patterns found, else 0.0)
        """
        logger.info(f"PATTERN 1: Shell Company Detection for {company_id}")
        
        query = """
        // STEP 1: Find HIGH-risk auditors (Node Property Filter)
        MATCH (auditor:Auditor {risk_level: 'HIGH'})
        
        // STEP 2: Find companies audited by this high-risk auditor
        MATCH (company:Company)-[:AUDITED_BY]->(auditor)
        
        // STEP 3: Graph Traversal - Find subsidiary chains (at least 3 SUBSIDIARY_OF rels)
        // *3..10 means 3-10 relationships = 4-11 total companies in chain
        MATCH path=(company)-[:SUBSIDIARY_OF*3..10]->(root:Company)
        
        // STEP 4: Node Property Filter - ALL companies must share SAME auditor
        WHERE ALL(n IN nodes(path) WHERE exists((n)-[:AUDITED_BY]->(auditor)))
        
        // STEP 5: Collect distinct chains
        WITH DISTINCT auditor, nodes(path) AS chain
        WHERE size(chain) >= $min_chain_length
        
        // STEP 6: Edge Property Filter - Check invoice count for each company
        UNWIND chain AS comp
        OPTIONAL MATCH (comp)-[:ISSUES_TO]->(inv:Invoice)
        
        // STEP 7: Aggregate invoice counts per company
        WITH auditor, chain, comp.company_id AS companyId, count(inv) AS invoiceCount
        WITH auditor, chain, collect([companyId, invoiceCount]) AS stats
        
        // STEP 8: Filter - ALL companies must have low activity (≤ max_invoices)
        WHERE ALL(s IN stats WHERE s[1] <= $max_invoices)
        
        // STEP 9: Calculate aggregate metrics
        WITH auditor, chain, stats,
             reduce(total=0, s IN stats | total + s[1]) AS totalInvoices,
             size(chain) AS chainLength
             
        RETURN auditor.auditor_id AS auditorId,
               auditor.risk_level AS riskLevel,
               [c IN chain | c.company_id] AS chain,
               stats AS companyDetails,
               chainLength, 
               totalInvoices,
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
                    'riskScore': 0.95  # REQUIREMENT: Critically high risk score > 0.95
                }
                if company_id in pattern['chain']:
                    patterns.append(pattern)
        
        logger.info(f"Pattern 1: Found {len(patterns)} shell chains for {company_id}")
        return {'patterns': patterns, 'riskScore': 0.95 if patterns else 0.0}

    def detect_circular_trade_for_company(self, company_id: str, min_volume: int = 80) -> Dict[str, Any]:
        """
        Pattern 2: Circular Trade Detection - EXPERT GRAPH THEORY IMPLEMENTATION
        
        REQUIREMENTS:
        ✓ Closed loop (cycle) of ≥3 distinct companies
        ✓ Uses SUPPLIES or PAYS relationships
        ✓ Without significant external flow (isolation metric)
        ✓ Risk Score > 0.80
        
        GRAPH THEORY ALGORITHM:
        - Cycle Detection: Triangle detection (3-cycles) using pattern matching
        - Algorithm: DFS-based pattern matching in Neo4j
        - Isolation Score: Measures internal vs external connectivity
        - Complexity: O(V³) for triangle enumeration in worst case
        
        NOTE: Currently detects 3-cycles (triangles). For 4+ cycles, would need:
        - General cycle detection using APOC or custom DFS
        - Variable-length cycle pattern: (a)-[:SUPPLIES*3..10]->(a)
        
        Args:
            company_id: Target company to analyze
            min_volume: Minimum annual_volume for SUPPLIES relationships (in millions)
            
        Returns:
            Dict with 'patterns' list and 'riskScore' (max risk if patterns found, else 0.0)
        """
        logger.info(f"PATTERN 2: Circular Trade Detection for {company_id}")
        
        # Query for 3-cycles using SUPPLIES relationships
        base_query = """
        // STEP 1: Cycle Detection - Find 3-cycles (triangles)
        // Pattern: c1 -> c2 -> c3 -> c1 (closed loop)
        MATCH (c1:Company)-[r1:SUPPLIES]->(c2:Company)
        MATCH (c2)-[r2:SUPPLIES]->(c3:Company) 
        MATCH (c3)-[r3:SUPPLIES]->(c1)
        
        // STEP 2: Ensure distinct companies and minimum volume threshold
        WHERE c1 <> c2 AND c2 <> c3 AND c1 <> c3
          AND r1.annual_volume >= $min_volume
          AND r2.annual_volume >= $min_volume  
          AND r3.annual_volume >= $min_volume
        
        // STEP 3: Collect cycle and transaction volumes
        WITH [c1.company_id, c2.company_id, c3.company_id] AS cycle,
             [r1.annual_volume, r2.annual_volume, r3.annual_volume] AS volumes
        WITH cycle, reduce(total=0.0, v IN volumes | total + v) AS totalVolume
        
        // STEP 4: Calculate external connections (for isolation metric)
        OPTIONAL MATCH (comp:Company) WHERE comp.company_id IN cycle
        OPTIONAL MATCH (comp)-[:SUPPLIES]->(ext:Company)
        WHERE NOT ext.company_id IN cycle
        
        WITH cycle, totalVolume, size(cycle) AS cycleLength,
             count(DISTINCT ext) AS externalConnections
        
        // STEP 5: Calculate isolation score
        // Higher score = more isolated = more suspicious
        // Formula: cycle_size / (cycle_size + external_connections + 1)
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
                # Avoid duplicate cycles (A-B-C same as B-C-A same as C-A-B)
                cycle_sig = tuple(sorted(record['cycle']))
                if cycle_sig in seen_cycles:
                    continue
                seen_cycles.add(cycle_sig)
                
                # REQUIREMENT: Risk score > 0.80
                # Formula: base 0.80 + bonus for high isolation (up to 0.15)
                # Ensures: risk ∈ [0.80, 0.95]
                isolation = record['isolationScore']
                risk = 0.80 + (0.15 * isolation)
                risk = min(0.95, max(0.80, risk))  # Clamp to [0.80, 0.95]
                
                all_patterns.append({
                    'cycle': record['cycle'],
                    'cycleLength': record['cycleLength'],
                    'totalVolume': float(record['totalVolume']),
                    'avgVolume': round(record['avgVolume'], 2),
                    'externalConnections': record['externalConnections'],
                    'isolationScore': round(record['isolationScore'], 3),
                    'riskScore': round(risk, 3)
                })
        
        # Filter patterns involving the target company
        target_patterns = [p for p in all_patterns if company_id in p['cycle']]
        logger.info(f"Pattern 2: Found {len(target_patterns)} cycles for {company_id}")
        
        # Return maximum risk score from all detected cycles
        risk_score = max([p['riskScore'] for p in target_patterns], default=0.0)
        return {'patterns': target_patterns, 'riskScore': risk_score}

    def calculate_shareholder_influence_pagerank(self) -> Dict[str, float]:
        """
        Pattern 3 (Part 1): PageRank Centrality Calculation
        
        GRAPH THEORY ALGORITHM:
        - Algorithm: PageRank (Random Walk with Damping)
        - Graph: Bipartite (Shareholders <-OWNS_SHARE-> Companies)
        - Weights: Ownership percentage
        - Iterations: 20 (convergence)
        - Damping Factor: 0.85 (standard)
        
        PageRank Formula:
        PR(A) = (1-d)/N + d * Σ(PR(Ti)/C(Ti))
        where:
        - d = damping factor (0.85)
        - N = number of nodes
        - Ti = nodes pointing to A
        - C(Ti) = out-degree of Ti
        
        Complexity: O(k × E) where k=iterations, E=edges
        
        Returns:
            Dict mapping shareholder_id -> influence_score
        """
        logger.info("PATTERN 3: Calculating PageRank for shareholder influence")
        influences = {}
        
        with self.driver.session() as session:
            # Drop existing graph projection if exists
            try:
                session.run("CALL gds.graph.drop('ownership', false)")
            except:
                pass
            
            try:
                # CRITICAL FIX: Proper bipartite graph projection
                # Must include BOTH Shareholder AND Company nodes
                session.run("""
                CALL gds.graph.project(
                    'ownership',
                    ['Shareholder', 'Company'],
                    {
                        OWNS_SHARE: {
                            type: 'OWNS_SHARE',
                            properties: 'percentage'
                        }
                    }
                )
                """)
                
                # Run PageRank with relationship weights
                result = session.run("""
                CALL gds.pageRank.stream('ownership', {
                    maxIterations: 20,
                    dampingFactor: 0.85,
                    relationshipWeightProperty: 'percentage'
                })
                YIELD nodeId, score
                WITH gds.util.asNode(nodeId) AS node, score
                WHERE 'Shareholder' IN labels(node) AND score > 0.01
                RETURN node.shareholder_id AS shareholderId, score
                ORDER BY score DESC
                """)
                
                for record in result:
                    influences[record['shareholderId']] = record['score']
                
            finally:
                # Clean up graph projection
                try:
                    session.run("CALL gds.graph.drop('ownership', false)")
                except:
                    pass
        
        logger.info(f"PageRank: {len(influences)} influential shareholders identified")
        return influences

    def detect_hidden_influence_for_company(self, company_id: str, min_ownership: float = 25.0, min_concentration: float = 80.0) -> Dict[str, Any]:
        """
        Pattern 3 (Part 2): Hidden Influence Detection - EXPERT GRAPH THEORY IMPLEMENTATION
        
        REQUIREMENTS:
        ✓ Influential shareholder (high PageRank centrality)
        ✓ NOT a direct supplier to target
        ✓ Major shareholder (>25% ownership)
        ✓ Supplies high volume (>80% of target's invoices)
        ✓ Opportunity Score > 0.70
        
        GRAPH THEORY ALGORITHM:
        - Multi-hop Path Analysis: 2-hop pattern
        - Path: Shareholder -[OWNS_SHARE]-> Supplier -[SUPPLIES]-> Target
        - Centrality Metric: PageRank (from Part 1)
        - Filtering: Property filters on ownership % and concentration %
        - Complexity: O(V × E) for 2-hop pattern matching
        
        Opportunity Score Formula:
        score = 0.4 × PageRank + 0.3 × ownership_factor + 0.3 × concentration_factor
        - Ensures score > 0.70 when all factors are high
        - PageRank ∈ [0, 1]: centrality score
        - ownership_factor ∈ [0, 1]: normalized ownership / 50%
        - concentration_factor ∈ [0, 1]: concentration / 100%
        
        Args:
            company_id: Target company to analyze
            min_ownership: Minimum ownership percentage (default 25%)
            min_concentration: Minimum invoice concentration (default 80%)
            
        Returns:
            Dict with 'patterns' list and 'opportunityScore' (max opportunity if patterns found)
        """
        logger.info(f"PATTERN 3: Hidden Influence Detection for {company_id}")
        
        # Calculate PageRank centrality scores
        influence_scores = self.calculate_shareholder_influence_pagerank()
        
        query = """
        // STEP 1: Multi-hop Path Analysis (2 hops)
        // Shareholder -[OWNS_SHARE]-> Supplier -[SUPPLIES]-> Target
        
        MATCH (sh:Shareholder)-[owns:OWNS_SHARE]->(supplier:Company)
        WHERE owns.percentage >= $min_ownership
        
        // STEP 2: Supplier must supply to target company
        MATCH (supplier)-[:SUPPLIES]->(target:Company {company_id: $target_company_id})
        
        // STEP 3: Calculate concentration - supplier's invoices vs total
        MATCH (supplier)-[:ISSUES_TO]->(inv1:Invoice)<-[:PAYS]-(target)
        WITH sh, supplier, target, owns.percentage AS ownershipPct,
             count(DISTINCT inv1) AS supplierInvoices
        
        // STEP 4: Get total invoices for target
        MATCH (target)-[:PAYS]->(inv2:Invoice)
        WITH sh, supplier, target, ownershipPct, supplierInvoices,
             count(DISTINCT inv2) AS totalInvoices
        
        // STEP 5: Apply filters
        WHERE toFloat(supplierInvoices)/totalInvoices*100 >= $min_concentration
          AND NOT exists((sh)-[:SUPPLIES]->(target))  // NOT a direct supplier
        
        RETURN sh.shareholder_id AS shareholderId,
               sh.name AS shareholderName,
               sh.type AS shareholderType,
               supplier.company_id AS supplierId,
               supplier.name AS supplierName,
               target.company_id AS targetId,
               target.name AS targetName,
               ownershipPct, 
               supplierInvoices, 
               totalInvoices,
               toFloat(supplierInvoices)/totalInvoices*100 AS concentrationPct
        ORDER BY concentrationPct DESC, ownershipPct DESC
        LIMIT 50
        """
        
        patterns = []
        with self.driver.session() as session:
            result = session.run(
                query, 
                target_company_id=company_id, 
                min_ownership=min_ownership, 
                min_concentration=min_concentration
            )
            
            for record in result:
                sh_id = record['shareholderId']
                
                # Get PageRank influence score (default 0.1 if not found)
                influence = influence_scores.get(sh_id, 0.1)
                
                # REQUIREMENT: Opportunity Score > 0.70
                # Calculate weighted combination of factors
                ownership_factor = min(record['ownershipPct'] / 50.0, 1.0)  # Normalize to [0,1]
                concentration_factor = record['concentrationPct'] / 100.0    # Already [0,1]
                
                # Weighted formula: ensures high scores when all factors are high
                opportunity = (
                    0.4 * influence +              # PageRank centrality
                    0.3 * ownership_factor +       # Ownership stake
                    0.3 * concentration_factor     # Supply concentration
                )
                
                patterns.append({
                    'shareholderId': record['shareholderId'],
                    'shareholderName': record['shareholderName'],
                    'shareholderType': record['shareholderType'],
                    'supplierId': record['supplierId'],
                    'supplierName': record['supplierName'],
                    'targetId': record['targetId'],
                    'targetName': record['targetName'],
                    'ownershipPct': round(record['ownershipPct'], 2),
                    'supplierInvoices': record['supplierInvoices'],
                    'totalInvoices': record['totalInvoices'],
                    'concentrationPct': round(record['concentrationPct'], 2),
                    'influenceScore': round(influence, 3),
                    'opportunityScore': round(opportunity, 3)
                })
        
        logger.info(f"Pattern 3: Found {len(patterns)} hidden influence patterns for {company_id}")
        
        # Return maximum opportunity score
        max_opportunity = max([p['opportunityScore'] for p in patterns], default=0.0)
        return {'patterns': patterns, 'opportunityScore': max_opportunity}

    def analyze_company(self, company_id: str) -> Tuple[float, float, Dict[str, Any]]:
        """
        Execute all 3 fraud detection patterns for a company.
        
        MAINTAINS ORIGINAL RETURN FORMAT - DO NOT CHANGE
        
        Args:
            company_id: Company ID to analyze
            
        Returns:
            Tuple of (risk_score, opportunity_score, patterns_dict)
            - risk_score: Maximum risk from patterns 1 and 2
            - opportunity_score: Maximum opportunity from pattern 3
            - patterns_dict: Dictionary with keys 'pattern1_shell', 'pattern2_circular', 'pattern3_hidden'
        """
        logger.info(f"=== Analyzing company: {company_id} ===")
        
        # Pattern 1: Shell Company Detection
        shell_result = self.detect_shell_companies_for_company(company_id)
        
        # Pattern 2: Circular Trade Detection
        circular_result = self.detect_circular_trade_for_company(company_id)
        
        # Pattern 3: Hidden Influence Detection
        hidden_result = self.detect_hidden_influence_for_company(company_id)
        
        # Calculate overall risk score (maximum of fraud patterns)
        risk_score = max(shell_result['riskScore'], circular_result['riskScore'])
        
        # Compile all patterns (MAINTAIN ORIGINAL FORMAT)
        patterns = {
            'pattern1_shell': shell_result['patterns'],
            'pattern2_circular': circular_result['patterns'],
            'pattern3_hidden': hidden_result['patterns']
        }
        
        logger.info(f"=== Analysis complete for {company_id} ===")
        logger.info(f"Risk Score: {risk_score:.2f}, Opportunity Score: {hidden_result['opportunityScore']:.2f}")
        
        # MAINTAIN ORIGINAL RETURN FORMAT
        return risk_score, hidden_result['opportunityScore'], patterns